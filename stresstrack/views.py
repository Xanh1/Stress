from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .models import Task
from datetime import date
from .forms import CustomUserCreationForm, CustomAuthenticationForm


def home(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, request.POST)
        if form.is_valid():
            print('entrando aca perros')
            email = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'index.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('home')

def register(request):
    form_register = CustomUserCreationForm()
    form_login = CustomAuthenticationForm()

    if request.method == 'POST':
        if 'form-register' in request.POST:
            form_register = CustomUserCreationForm(request.POST)
            if form_register.is_valid():
                user = form_register.save()
                login(request, user)
                return redirect('home')

        elif 'form-login' in request.POST:
            form_login = CustomAuthenticationForm(request, data=request.POST)
            if form_login.is_valid():
                email = form_login.cleaned_data['username']
                password = form_login.cleaned_data['password']
                user = authenticate(request, email=email, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('dashboard')

    return render(request, 'register.html', {'form_register': form_register, 'form_login': form_login})

from datetime import date
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Task

@login_required
def dashboard(request):
    user = request.user
    courses = request.user.enrolled_courses.all()
    tasks = Task.objects.filter(course__in=courses, due_date__gte=date.today()).order_by('due_date')
    
    stress = 61
    color = ""

    if 0 <= stress <= 20:
        color = 'bg-good'
    elif 20 < stress <= 40:
        color = 'bg-not-bad'
    elif 40 < stress <= 60:
        color = 'bg-dangerr'
    elif 60 < stress <= 100:
        color = 'bg-dying'

    if tasks.exists():
        closest_task = tasks.first()
        task_info = {
            'title': closest_task.name,
            'date': closest_task.due_date
        }
    else:
        task_info = {
            'title': "No hay tareas asignadas",
            'date': "N/A"
        }
    
    context = {
        'name': user.first_name or "Usuario",
        'task': task_info,
        'color': color,
        'stress': stress,
    }

    return render(request, 'dashboard/dashboard.html', context)


@login_required
def dash_task(request):
    courses = request.user.enrolled_courses.prefetch_related('tasks').all()

    for course in courses:
        for task in course.tasks.all():
            days_left = (task.due_date - date.today()).days
            if days_left > 7:
                task.color = 'bg-good'  # Verde
            elif 3 <= days_left <= 7:
                task.color = 'bg-dangerr'  # Amarillo
            else:
                task.color = 'bg-dying'  # Rojo

    return render(request, 'dashboard/dash_task.html', {'courses': courses})

