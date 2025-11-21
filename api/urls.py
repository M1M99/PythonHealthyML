from django.urls import path
from .views import dashboard, upload_excel, add_pasient

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('dashboard', dashboard,name='dashboard'),
    path('upload/',upload_excel,name="upload_excel"),
    path('add/', add_pasient, name='add_pasient'),
]
