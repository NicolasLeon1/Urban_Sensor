from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('first_session/', views.first_session, name='first_session'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout, name='logout'),
    path('reset_password/', views.password_reset, name='password_reset'),
    path('reset_password_sent/', views.password_reset_done, name='password_reset_done'),
    path('reset/', views.password_reset_confirm, name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="register/password_reset_complete.html"), name='password_reset_complete'),
    path('reenviar_codigo/', views.reenviar_codigo, name='reenviar_codigo'),
]