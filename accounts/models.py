from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    class Role(models.TextChoices):
        PRINCIPAL = "PRINCIPAL", "Principal"
        TEACHER = "TEACHER", "Teacher"
        STUDENT = "STUDENT", "Student"
        OFFICE = "OFFICE", "Office Team"
        PT_SIR = "PT_SIR", "PT Sir"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
    )