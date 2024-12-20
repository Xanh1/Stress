from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from .models import Task, Course, StressTest, Question, ResponseOption, StudentResponse, ResponseDetail
from datetime import date
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.db.models import Count, Q
from django.http import Http404


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

@login_required
def dashboard(request):
    user = request.user
    courses = request.user.enrolled_courses.all()
    tasks = Task.objects.filter(course__in=courses, due_date__gte=date.today()).order_by('due_date')
    
    stress = user.stress
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

    tasks_filter = Prefetch(
        'tasks',
        queryset=Task.objects.filter(due_date__gte=date.today()),
        to_attr='filtered_tasks'
    )

    courses = request.user.enrolled_courses.prefetch_related(tasks_filter).all()

    for course in courses:
        for task in course.filtered_tasks:
            days_left = (task.due_date - date.today()).days
            if days_left > 7:
                task.color = 'bg-good'  # Verde
            elif 3 <= days_left <= 7:
                task.color = 'bg-dangerr'  # Amarillo
            else:
                task.color = 'bg-dying'  # Rojo

    return render(request, 'dashboard/dash_task.html', {'courses': courses})


@login_required
def student_tests(request):
    # Obtener todos los cursos que el estudiante está tomando
    courses = Course.objects.filter(students=request.user)

    # Definir una consulta de prefetch que obtiene los tests de los cursos con la anotación 'has_taken'
    stress_tests_with_annotations = StressTest.objects.annotate(
        has_taken=Count(
            'responses',
            filter=Q(responses__student=request.user)
        )
    )

    # Usar Prefetch para incluir los tests anotados en cada curso
    courses = courses.prefetch_related(Prefetch('stress_tests', queryset=stress_tests_with_annotations))

    # Pasar los cursos al template
    return render(request, 'dashboard/dash_test.html', {'courses': courses})

@login_required
def test_view(request, test_id):
    test = get_object_or_404(StressTest, id=test_id)
    questions = test.questions.all()

    if request.method == 'POST':
        # Verifica que el usuario sea un estudiante
        if request.user.role != 'student':
            raise Http404("Solo los estudiantes pueden responder este test.")

        # Verifica si ya respondió
        if StudentResponse.objects.filter(student=request.user, stress_test=test).exists():
            return redirect('student_tests')

        # Crear la respuesta del estudiante
        student_response = StudentResponse.objects.create(
            student=request.user,
            stress_test=test
        )

        total_score = 0
        for question in questions:
            selected_option_value = request.POST.get(f'question_{question.id}')
            if selected_option_value and selected_option_value.isdigit():
                # Suma los valores de las opciones seleccionadas
                total_score += int(selected_option_value)
                ResponseDetail.objects.create(
                    student_response=student_response,
                    question=question,
                    selected_option=selected_option_value
                )
            else:
                # Si falta alguna respuesta, elimina la respuesta parcial y regresa un error
                student_response.delete()
                return render(request, 'test/test.html', {
                    'test': test,
                    'questions': questions,
                    'opts': ResponseOption.choices,
                    'error': f"Debe responder todas las preguntas correctamente."
                })

        
        # Actualiza el nivel de estrés del usuario como entero
        request.user.stress = total_score
        request.user.save()

        return redirect('student_tests')

    return render(request, 'test/test.html', {
        'test': test,
        'questions': questions,
        'opts': ResponseOption.choices,
    })
