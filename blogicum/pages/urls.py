from django.urls import path

from . import views

app_name = 'pages'

urlpatterns = [
    path('about/', views.AboutTempalateView.as_view(), name='about'),
    path('rules/', views.RulesTempalateView.as_view(), name='rules'),
]
