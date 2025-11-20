from django.urls import path
from . import views

urlpatterns = [
    path('first_session/', views.first_session, name='first_session'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout, name='logout'),
]