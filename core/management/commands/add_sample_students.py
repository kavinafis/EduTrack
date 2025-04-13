import random
from faker import Faker
from django.core.management.base import BaseCommand
from accounts.models import User, Student
from course.models import Program
from decimal import Decimal

fake = Faker()

class Command(BaseCommand):
    help = "Add 10 sample students to the database"

    def handle(self, *args, **kwargs):
        program = Program.objects.first()  # Assign the first program as default
        if not program:
            self.stdout.write(self.style.ERROR("No program found. Please create a program first."))
            return

        for i in range(1, 11):
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f"{first_name.lower()}{i}"
            email = f"{username}@example.com"

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "is_student": True,
                },
            )
            if created:
                Student.objects.create(
                    student=user,
                    level="Bachelor",
                    program=program,
                    gpa=Decimal(f"{random.uniform(2.0, 4.0):.2f}"),  # Random GPA between 2.0 and 4.0
                    hours_studied=Decimal(f"{random.uniform(5.0, 20.0):.2f}"),  # Random hours studied between 5 and 20
                    previous_scores=Decimal(f"{random.uniform(50.0, 100.0):.2f}"),  # Random previous scores between 50 and 100
                    extracurricular_activities=random.randint(0, 5),  # Random number of activities between 0 and 5
                    sleep_hours=Decimal(f"{random.uniform(6.0, 10.0):.2f}"),  # Random sleep hours between 6 and 10
                    sample_question_papers_practiced=random.randint(0, 10),  # Random papers practiced between 0 and 10
                )
                self.stdout.write(self.style.SUCCESS(f"Added student: {username}"))
            else:
                self.stdout.write(self.style.WARNING(f"Student {username} already exists."))
