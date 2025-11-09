from django.shortcuts import render, redirect
from django.contrib import messages
from register.decorators import *

def home(request):
    return redirect('login')

@login_required
def pre_check_profile(request):
    pass

@login_required
def check_profile(request):
    pass

@secpla_required
def main_admin(request):
    return render(request, 'core/dashboard_admin.html')