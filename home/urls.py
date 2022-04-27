from django.urls import path

from .views import HomePageView, AboutPageView, ContactPageView, DashboardPageView

# app_name = 'home'

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('about/', AboutPageView.as_view(), name='about'),
    path('contact/', ContactPageView.as_view(), name='contact'),
    path('dashboard/', DashboardPageView.as_view(), name='dashboard'),
]
