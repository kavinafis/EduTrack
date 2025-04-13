from django.core.management.base import BaseCommand
from accounts.models import Student

class Command(BaseCommand):
    help = "Delete students with first names starting with 'First'"

    def handle(self, *args, **kwargs):
        students_to_delete = Student.objects.filter(student__first_name__startswith="First")
        count = students_to_delete.count()
        if count == 0:
            self.stdout.write(self.style.WARNING("No students found with first names starting with 'First'."))
        else:
            students_to_delete.delete()
            self.stdout.write(self.style.SUCCESS(f"Deleted {count} students with first names starting with 'First'."))
