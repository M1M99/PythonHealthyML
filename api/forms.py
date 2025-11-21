from django import forms

from api.models import Pasient


class ExcelUploadForm(forms.Form):
    file = forms.FileField(label="Upload Excel File")

class HealthyMLForm(forms.Form):
    file = forms.FileField(label="Upload Healthy ML")

class PasientForm(forms.ModelForm):
    class Meta:
        model = Pasient
        fields = ['age', 'bmi', 'glucose_level', 'blood_pressure', 'family_history', 'exercise_level']
