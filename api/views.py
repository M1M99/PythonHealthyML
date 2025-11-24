from django.shortcuts import render, redirect
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import r2_score, accuracy_score
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc, confusion_matrix
import seaborn as sns

from Helper.utils import train_model, plot_to_base64
from .forms import ExcelUploadForm, PasientForm
from django.contrib import messages
from api.models import Pasient
from sklearn.preprocessing import LabelEncoder

def dashboard(request):
    context = Pasient.objects.all()
    return render(request,'ui/dashboard.html',{'context':context})


def upload_excel(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            try :
                df = pd.read_excel(file)
                for _, row in df.iterrows():
                    Pasient.objects.create(
                        age=row['Age'],
                        bmi=row['BMI'],
                        glucose_level=row['GlucoseLevel'],
                        blood_pressure=row['BloodPressure'],
                        family_history=bool(row['FamilyHistory']),
                        exercise_level=row['ExerciseLevel'],
                        outcome=bool(row['Outcome'])
                    )
                messages.success(request, 'Excel Upload Successful')
                return redirect('upload_excel')
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
    else:
        form = ExcelUploadForm()
    return render(request, 'ui/upload_excel.html', {'form': form})


def add_pasient(request):
    if request.method == 'POST':
        form = PasientForm(request.POST)
        if form.is_valid():
            user_data = form.cleaned_data
            print("Form valid ")

            pasients = Pasient.objects.all()
            if pasients.exists():
                df_train = pd.DataFrame.from_records(
                    pasients.values(
                        'age','bmi','glucose_level','blood_pressure','family_history','exercise_level','outcome'
                    )
                )

                le = LabelEncoder()
                df_train['ExerciseLevelEncoded'] = le.fit_transform(df_train['exercise_level'])

                X_train = df_train[['age','bmi','glucose_level','blood_pressure','family_history','ExerciseLevelEncoded']]
                y_train = df_train['outcome']

                # clf = DecisionTreeClassifier() ##via decsiontree
                clf = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
                clf.fit(X_train, y_train)

                user_df = pd.DataFrame([user_data])
                user_df['ExerciseLevelEncoded'] = le.transform(user_df['exercise_level'])

                prediction = clf.predict(user_df[['age','bmi','glucose_level','blood_pressure','family_history','ExerciseLevelEncoded']])[0]
                y_pred_train = clf.predict(X_train)
                acc = accuracy_score(y_train, y_pred_train)
                print(f"Training accuracy: {acc}")
            else:
                prediction = False

            Pasient.objects.create(
                age=user_data['age'],
                bmi=user_data['bmi'],
                glucose_level=user_data['glucose_level'],
                blood_pressure=user_data['blood_pressure'],
                family_history=user_data['family_history'],
                exercise_level=user_data['exercise_level'],
                outcome=prediction
            )
            pred_prob = clf.predict_proba(
                user_df[['age', 'bmi', 'glucose_level', 'blood_pressure', 'family_history', 'ExerciseLevelEncoded']])[0][1]
            messages.success(request, f"Pasient added! Predicted outcome: {prediction},Percentage {float(pred_prob).__round__(5)}")
            return redirect('add_pasient')
        else:
            print(form.errors)
    else:
        form = PasientForm()

    return render(request, 'ui/add_pasient.html', {'form': form})


def roc_curve_view(request):
    clf, X, y, y_prob, _ = train_model()
    if clf is None:
        return render(request, 'ui/no_data.html')

    fpr, tpr, _ = roc_curve(y, y_prob)
    roc_auc = auc(fpr, tpr)
    plt.figure()
    plt.plot(fpr, tpr)
    plt.plot([0, 1], [0, 1], '--', color='gray')
    plt.title(f"ROC Curve (AUC={roc_auc:.2f})")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    chart = plot_to_base64()
    return render(request, 'ui/roc.html', {'chart': chart})


def feature_importance_view(request):
    clf, X, y, _, _ = train_model()
    if clf is None:
        return render(request,'ui/no_data.html')

    importance = clf.feature_importances_
    features = X.columns
    plt.figure(figsize=(7,4))
    plt.bar(features, importance)
    plt.title("Feature Importance")
    plt.xticks(rotation=45)
    chart = plot_to_base64()
    return render(request,'ui/feature_importance.html', {'chart': chart})


def model_comparison_view(request):
    clf_gb, X, y, y_prob_gb, _ = train_model('gbc')
    clf_rf, _, _, y_prob_rf, _ = train_model('rf')
    auc_gb = auc(*roc_curve(y, y_prob_gb)[:2])
    auc_rf = auc(*roc_curve(y, y_prob_rf)[:2])
    models = ['GradientBoosting','RandomForest']
    aucs = [auc_gb, auc_rf]
    plt.figure(figsize=(5,4))
    plt.bar(models, aucs, color=['red','blue'])
    plt.title("Model Comparison (AUC)")
    chart = plot_to_base64()
    return render(request,'ui/model_comparison.html', {'chart': chart})



def risk_prediction_view(request):
    if request.method == 'POST':
        form = PasientForm(request.POST)
        if form.is_valid():
            user_data = form.cleaned_data
            pasients = Pasient.objects.all()
            if pasients.exists():
                df_train = pd.DataFrame.from_records(
                    pasients.values(
                        'age','bmi','glucose_level','blood_pressure','family_history','exercise_level','outcome'
                    )
                )
                le = LabelEncoder()
                df_train['ExerciseLevelEncoded'] = le.fit_transform(df_train['exercise_level'])
                X_train = df_train[['age','bmi','glucose_level','blood_pressure','family_history','ExerciseLevelEncoded']]
                y_train = df_train['outcome']
                clf = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
                clf.fit(X_train, y_train)

                user_df = pd.DataFrame([user_data])
                user_df['ExerciseLevelEncoded'] = le.transform(user_df['exercise_level'])
                pred_prob = clf.predict_proba(user_df[['age','bmi','glucose_level','blood_pressure','family_history','ExerciseLevelEncoded']])[0][1]
                risk_percent = int(pred_prob * 100)

            else:
                risk_percent = 0

            return render(request, 'ui/risk_prediction.html', {'risk': risk_percent})
    else:
        form = PasientForm()

    return render(request, 'ui/add_pasient.html', {'form': form})



def correlation_heatmap_view(request):
    pasients = Pasient.objects.all()
    if not pasients.exists():
        return render(request,'ui/no_data.html')
    df = pd.DataFrame.from_records(pasients.values('age','bmi','glucose_level','blood_pressure','family_history','outcome'))
    plt.figure(figsize=(7,5))
    sns.heatmap(df.corr(), annot=True, cmap='coolwarm')
    plt.title("Correlation Heatmap")
    chart = plot_to_base64()
    return render(request,'ui/correlation_heatmap.html', {'chart': chart})