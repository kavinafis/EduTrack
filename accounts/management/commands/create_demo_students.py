from django.core.management.base import BaseCommand
from faker import Faker
from accounts.models import User, Student
from course.models import Program

class Command(BaseCommand):
    help = "Create demo students with random details"

    def handle(self, *args, **kwargs):
        fake = Faker()
        programs = Program.objects.all()

        if not programs.exists():
            self.stdout.write(self.style.ERROR("No programs found. Add programs first."))
            return

        for _ in range(10):  # Create 10 demo students
            user = User.objects.create_user(
                username=fake.user_name(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                password="password123",
                is_student=True,
            )
            Student.objects.create(
                student=user,
                level=fake.random_element(elements=["Bachelor", "Master"]),
                program=fake.random_element(elements=programs),
            )

        self.stdout.write(self.style.SUCCESS("10 demo students created successfully."))
