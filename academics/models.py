from django.db import models


class AcademicYear(models.Model):

    name = models.CharField(max_length=20, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class SchoolClass(models.Model):

    name = models.CharField(max_length=50, unique=True)
    display_order = models.PositiveIntegerField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Section(models.Model):

    name = models.CharField(max_length=20)

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name="sections",
    )

    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.PROTECT,
        related_name="sections",
    )

    capacity = models.PositiveIntegerField(default=40)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["academic_year", "school_class", "name"],
                name="unique_section_per_class_year",
            )
        ]

    def __str__(self):
        return f"{self.school_class.name} - {self.name} ({self.academic_year.name})"


class Subject(models.Model):

    name = models.CharField(max_length=100)

    code = models.CharField(
        max_length=20,
        unique=True,
    )

    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.name}"