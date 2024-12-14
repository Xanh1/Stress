from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Ingrese un correo válido')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'superuser')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('student', 'Alumno'),
        ('teacher', 'Profesor'),
        ('superuser', 'Superusuario'),
    ]
    
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    dni = models.CharField(max_length=20, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"


class Course(models.Model):
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='teaching_courses', limit_choices_to={'role': 'teacher'})
    students = models.ManyToManyField('CustomUser', related_name='enrolled_courses', blank=True, limit_choices_to={'role': 'student'})

    def __str__(self):
        return self.name


class StressTest(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='stress_tests')

    def __str__(self):
        return self.title


class Question(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('multiple_choice', 'Opción múltiple'),
        ('scale', 'Escala'),
    ]

    text = models.CharField(max_length=255)
    stress_test = models.ForeignKey(StressTest, on_delete=models.CASCADE, related_name='questions')

    def __str__(self):
        return self.text


class ResponseOption(models.TextChoices):
    NUNCA = 'NUNCA', 'Nunca'
    RARA_VEZ = 'RARA_VEZ', 'Rara vez'
    A_VECES = 'A_VECES', 'A veces'
    CASI_SIEMPRE = 'CASI_SIEMPRE', 'Casi siempre'
    SIEMPRE = 'SIEMPRE', 'Siempre'


class StudentResponse(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='responses', limit_choices_to={'role': 'student'})
    stress_test = models.ForeignKey(StressTest, on_delete=models.CASCADE, related_name='responses')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Respuesta de {self.student.email} para {self.stress_test.title}"


class ResponseDetail(models.Model):
    student_response = models.ForeignKey(StudentResponse, on_delete=models.CASCADE, related_name='details')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=15, choices=ResponseOption.choices)

    def __str__(self):
        return f"Respuesta a {self.question.text} -> {self.get_selected_option_display()}"

class Task(models.Model):
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='tasks')
    description = models.TextField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.name
