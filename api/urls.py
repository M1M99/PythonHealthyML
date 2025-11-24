from django.urls import path
from .views import dashboard, upload_excel, add_pasient, roc_curve_view, feature_importance_view, model_comparison_view, \
    risk_prediction_view, correlation_heatmap_view

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('dashboard', dashboard,name='dashboard'),
    path('upload/',upload_excel,name="upload_excel"),
    path('add/', add_pasient, name='add_pasient'),
    path('roc/',roc_curve_view,name='roc_curve_view'),
    path('feature-importance/', feature_importance_view, name='feature_importance'),
    path('model_comparison_view/', model_comparison_view, name='model_comparison_view'),
    path('risk_prediction_view/', risk_prediction_view, name='risk_prediction_view'),
    path('correlation_heatmap_view/', correlation_heatmap_view, name='correlation_heatmap_view'),
]
