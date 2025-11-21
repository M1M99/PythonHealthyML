from django.db import models

class Pasient(models.Model):
    AGE_CHOICES = [(i, i) for i in range(0, 121)]  # 0-120 yaş
    EXERCISE_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    age = models.PositiveIntegerField()
    bmi = models.FloatField()
    glucose_level = models.FloatField()
    blood_pressure = models.FloatField()
    family_history = models.BooleanField()
    exercise_level = models.CharField(max_length=6, choices=EXERCISE_CHOICES)
    outcome = models.BooleanField()

    def __str__(self):
        return f"Pasient {self.id} - Age: {self.age}, Outcome: {self.outcome}"
