from django.shortcuts import render, redirect
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import r2_score, accuracy_score
from sklearn.tree import DecisionTreeClassifier

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

            messages.success(request, f"Pasient added! Predicted outcome: {prediction}")
            return redirect('add_pasient')
        else:
            print(form.errors)
    else:
        form = PasientForm()

    return render(request, 'ui/add_pasient.html', {'form': form})
