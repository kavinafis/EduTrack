import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)

from accounts.decorators import admin_required, lecturer_required
from accounts.models import User, Student
from .forms import SessionForm, SemesterForm, NewsAndEventsForm
from .models import NewsAndEvents, ActivityLog, Session, Semester

import pickle
from django.http import JsonResponse
from django.shortcuts import render
from accounts.models import Student
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from course.models import Course  # Import the Course model
from result.models import TakenCourse  # Import the TakenCourse model
from decimal import Decimal


# ########################################################
# News & Events
# ########################################################
@login_required
def home_view(request):
    logger.debug(f"Home view accessed by {request.user}")
    items = NewsAndEvents.objects.all().order_by("-updated_date")
    context = {
        "title": "News & Events",
        "items": items,
    }
    return render(request, "core/index.html", context)


@login_required
@admin_required
def dashboard_view(request):
    logs = ActivityLog.objects.all().order_by("-created_at")[:10]
    gender_count = Student.get_gender_count()
    context = {
        "student_count": User.objects.get_student_count(),
        "lecturer_count": User.objects.get_lecturer_count(),
        "superuser_count": User.objects.get_superuser_count(),
        "males_count": gender_count["M"],
        "females_count": gender_count["F"],
        "logs": logs,
    }
    return render(request, "core/dashboard.html", context)


@login_required
def post_add(request):
    if request.method == "POST":
        form = NewsAndEventsForm(request.POST)
        title = form.cleaned_data.get("title", "Post") if form.is_valid() else None
        if form.is_valid():
            form.save()
            messages.success(request, f"{title} has been uploaded.")
            return redirect("home")
        messages.error(request, "Please correct the error(s) below.")
    else:
        form = NewsAndEventsForm()
    return render(request, "core/post_add.html", {"title": "Add Post", "form": form})


@login_required
@lecturer_required
def edit_post(request, pk):
    instance = get_object_or_404(NewsAndEvents, pk=pk)
    if request.method == "POST":
        form = NewsAndEventsForm(request.POST, instance=instance)
        title = form.cleaned_data.get("title", "Post") if form.is_valid() else None
        if form.is_valid():
            form.save()
            messages.success(request, f"{title} has been updated.")
            return redirect("home")
        messages.error(request, "Please correct the error(s) below.")
    else:
        form = NewsAndEventsForm(instance=instance)
    return render(request, "core/post_add.html", {"title": "Edit Post", "form": form})


@login_required
@lecturer_required
def delete_post(request, pk):
    post = get_object_or_404(NewsAndEvents, pk=pk)
    post_title = post.title
    post.delete()
    messages.success(request, f"{post_title} has been deleted.")
    return redirect("home")


# ########################################################
# Session
# ########################################################
@login_required
@lecturer_required
def session_list_view(request):
    """Show list of all sessions"""
    sessions = Session.objects.all().order_by("-is_current_session", "-session")
    return render(request, "core/session_list.html", {"sessions": sessions})


@login_required
@lecturer_required
def session_add_view(request):
    """Add a new session"""
    if request.method == "POST":
        form = SessionForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.get("is_current_session"):
                unset_current_session()
            form.save()
            messages.success(request, "Session added successfully.")
            return redirect("session_list")
    else:
        form = SessionForm()
    return render(request, "core/session_update.html", {"form": form})


@login_required
@lecturer_required
def session_update_view(request, pk):
    session = get_object_or_404(Session, pk=pk)
    if request.method == "POST":
        form = SessionForm(request.POST, instance=session)
        if form.is_valid():
            if form.cleaned_data.get("is_current_session"):
                unset_current_session()
            form.save()
            messages.success(request, "Session updated successfully.")
            return redirect("session_list")
    else:
        form = SessionForm(instance=session)
    return render(request, "core/session_update.html", {"form": form})


@login_required
@lecturer_required
def session_delete_view(request, pk):
    session = get_object_or_404(Session, pk=pk)
    if session.is_current_session:
        messages.error(request, "You cannot delete the current session.")
    else:
        session.delete()
        messages.success(request, "Session successfully deleted.")
    return redirect("session_list")


def unset_current_session():
    """Unset current session"""
    current_session = Session.objects.filter(is_current_session=True).first()
    if current_session:
        current_session.is_current_session = False
        current_session.save()


# ########################################################
# Semester
# ########################################################
@login_required
@lecturer_required
def semester_list_view(request):
    semesters = Semester.objects.all().order_by("-is_current_semester", "-semester")
    return render(request, "core/semester_list.html", {"semesters": semesters})


@login_required
@lecturer_required
def semester_add_view(request):
    if request.method == "POST":
        form = SemesterForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.get("is_current_semester"):
                unset_current_semester()
                unset_current_session()
            form.save()
            messages.success(request, "Semester added successfully.")
            return redirect("semester_list")
    else:
        form = SemesterForm()
    return render(request, "core/semester_update.html", {"form": form})


@login_required
@lecturer_required
def semester_update_view(request, pk):
    semester = get_object_or_404(Semester, pk=pk)
    if request.method == "POST":
        form = SemesterForm(request.POST, instance=semester)
        if form.is_valid():
            if form.cleaned_data.get("is_current_semester"):
                unset_current_semester()
                unset_current_session()
            form.save()
            messages.success(request, "Semester updated successfully!")
            return redirect("semester_list")
    else:
        form = SemesterForm(instance=semester)
    return render(request, "core/semester_update.html", {"form": form})


@login_required
@lecturer_required
def semester_delete_view(request, pk):
    semester = get_object_or_404(Semester, pk=pk)
    if semester.is_current_semester:
        messages.error(request, "You cannot delete the current semester.")
    else:
        semester.delete()
        messages.success(request, "Semester successfully deleted.")
    return redirect("semester_list")


def unset_current_semester():
    """Unset current semester"""
    current_semester = Semester.objects.filter(is_current_semester=True).first()
    if current_semester:
        current_semester.is_current_semester = False
        current_semester.save()


@method_decorator(csrf_exempt, name='dispatch')
@login_required
def performance_prediction_view(request):
    logger.debug(f"Performance prediction view accessed by {request.user}")
    try:
        if request.method == "POST":
            data = json.loads(request.body)
            student_id = data.get("student_id")
            if not student_id:
                logger.error("Student ID is missing in the request.")
                return JsonResponse({"error": "Student ID is required."}, status=400)

            try:
                student = Student.objects.get(pk=student_id)
                model_path = "s:/Python/Capstone Project Student Performance/EduTrack/models/performance_model.pkl"
                logger.debug(f"Loading model from {model_path}")
                with open(model_path, "rb") as model_file:
                    model = pickle.load(model_file)

                # Ensure student has level and program
                if not student.level or not student.program:
                    logger.error(
                        f"Student with ID {student_id} is missing level or program."
                    )
                    return JsonResponse(
                        {
                            "error": "Student level or program is missing.",
                            "details": "Please ensure the student is assigned a valid level and program.",
                        },
                        status=400,
                    )

                # Handle missing gpa attribute
                gpa = getattr(student, "gpa", None)
                if gpa is None:
                    logger.debug(f"Calculating GPA for student with ID {student_id}.")
                    taken_courses = student.takencourse_set.all()
                    total_points = sum(tc.point for tc in taken_courses)
                    total_credits = sum(tc.course.credit for tc in taken_courses)

                    if total_credits == 0:
                        logger.warning(
                            f"Student with ID {student_id} ({student.student.get_full_name}) has no registered courses with credits. Attempting to assign default credits."
                        )
                        # Assign default credits
                        default_course = Course.objects.filter(
                            level=student.level, program=student.program, credit__gt=0
                        ).first()
                        if not default_course:
                            logger.warning(
                                f"No valid default course found for student with ID {student_id} ({student.student.get_full_name}). Creating a fallback default course."
                            )
                            default_course = Course.objects.create(
                                title="Default Course",
                                code="DEFAULT101",
                                credit=3,
                                program=student.program,
                                level=student.level,
                                semester="First",
                                summary="Fallback default course for GPA calculation.",
                            )
                            logger.info(
                                f"Fallback default course '{default_course.title}' created and assigned to student {student_id}."
                            )

                        TakenCourse.objects.create(
                            student=student, course=default_course, point=0
                        )
                        total_credits = default_course.credit
                        logger.info(
                            f"Default course '{default_course.title}' assigned to student {student_id}."
                        )

                    if total_credits > 0:
                        gpa = round(total_points / total_credits, 2)
                        logger.debug(f"Calculated GPA for student {student_id}: {gpa}")
                    else:
                        logger.error(
                            f"Student with ID {student_id} ({student.student.get_full_name}) still has no credits. Unable to calculate GPA."
                        )
                        return JsonResponse(
                            {
                                "error": "Student GPA cannot be calculated.",
                                "details": f"The student {student.student.get_full_name} has no registered courses with credits.",
                            },
                            status=400,
                        )

                # Ensure all required attributes are present
                hours_studied = getattr(student, "hours_studied", 0.00)
                previous_scores = getattr(student, "previous_scores", 0.00)
                extracurricular_activities = getattr(student, "extracurricular_activities", 0)
                sleep_hours = getattr(student, "sleep_hours", 9.00)
                sample_question_papers_practiced = getattr(student, "sample_question_papers_practiced", 0)

                input_data = [
                    hours_studied,
                    previous_scores,
                    extracurricular_activities,
                    sleep_hours,
                    sample_question_papers_practiced,
                ]
                logger.debug(f"Input data for prediction: {input_data}")
                prediction = round(model.predict([input_data])[0], 2)  # Round to 2 decimal places
                logger.info(f"Prediction result: {prediction}")
                return JsonResponse({
                    "prediction": prediction,
                    "input_data": {
                        "hours_studied": hours_studied,
                        "previous_scores": previous_scores,
                        "extracurricular_activities": extracurricular_activities,
                        "sleep_hours": sleep_hours,
                        "sample_question_papers_practiced": sample_question_papers_practiced,
                    }
                })

            except Student.DoesNotExist:
                logger.error(f"Student with ID {student_id} not found.")
                return JsonResponse({"error": "Student not found."}, status=404)
            except FileNotFoundError:
                logger.error(f"Model file not found at {model_path}.")
                return JsonResponse({"error": "Model file not found."}, status=500)
            except Exception as e:
                logger.exception(f"Unexpected error during prediction: {str(e)}")
                return JsonResponse({"error": "Prediction failed.", "message": str(e)}, status=500)

    except json.JSONDecodeError:
        logger.error("Invalid JSON data received.")
        return JsonResponse({"error": "Invalid JSON data."}, status=400)
    except Exception as e:
        logger.exception(f"Unexpected error: {str(e)}")
        return JsonResponse({"error": "An unexpected error occurred.", "message": str(e)}, status=500)

    students = Student.objects.all().select_related('program').order_by('student__username')
    logger.debug(f"Number of students retrieved: {students.count()}")
    return render(request, "core/performance_prediction.html", {"students": students})


@login_required
@admin_required
def add_sample_students(request):
    """Add 10 sample students to the database."""
    from accounts.models import User, Student
    from course.models import Program

    program = Program.objects.first()  # Assign the first program as default
    if not program:
        messages.error(request, "No program found. Please create a program first.")
        return redirect("dashboard")

    students_data = [
        {"username": f"student{i}", "first_name": f"First{i}", "last_name": f"Last{i}", "email": f"student{i}@example.com"}
        for i in range(1, 11)
    ]

    for student_data in students_data:
        user, created = User.objects.get_or_create(
            username=student_data["username"],
            defaults={
                "first_name": student_data["first_name"],
                "last_name": student_data["last_name"],
                "email": student_data["email"],
                "is_student": True,
            },
        )
        if created:
            Student.objects.create(
                student=user,
                level="Bachelor",
                program=program,
                gpa=Decimal("0.00"),
                hours_studied=Decimal("7.00"),
                previous_scores=Decimal("99.00"),
                extracurricular_activities=1,
                sleep_hours=Decimal("9.00"),
                sample_question_papers_practiced=5,
            )

    messages.success(request, "10 sample students have been added successfully.")
    return redirect("performance_prediction_view")
