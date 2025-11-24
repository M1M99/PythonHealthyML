import base64
from io import BytesIO

import pandas as pd
from matplotlib import pyplot as plt
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

from api.models import Pasient

def train_model(model_type='gbc'):
    pasients = Pasient.objects.all()
    if not pasients.exists():
        return None, None, None, None

    df = pd.DataFrame.from_records(
        pasients.values('age','bmi','glucose_level','blood_pressure','family_history','exercise_level','outcome')
    )

    le = LabelEncoder()
    df['ExerciseLevelEncoded'] = le.fit_transform(df['exercise_level'])

    X = df[['age','bmi','glucose_level','blood_pressure','family_history','ExerciseLevelEncoded']]
    y = df['outcome']

    if model_type=='gbc':
        clf = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
    elif model_type=='rf':
        clf = RandomForestClassifier(n_estimators=100, random_state=42)
    else:
        clf = GradientBoostingClassifier(n_estimators=100, random_state=42)

    clf.fit(X, y)
    y_pred = clf.predict(X)
    y_prob = clf.predict_proba(X)[:,1]

    return clf, X, y, y_prob, le



def plot_to_base64():
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)
    image_png = buffer.getvalue()
    graphic = base64.b64encode(image_png).decode('utf-8')
    return graphic