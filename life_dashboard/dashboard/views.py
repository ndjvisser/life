import logging

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.shortcuts import redirect, render

from life_dashboard.achievements.models import UserAchievement
from life_dashboard.core_stats.models import CoreStat
from life_dashboard.dashboard.forms import (
    UserProfileForm,
    UserRegistrationForm,
)
from life_dashboard.dashboard.models import UserProfile
from life_dashboard.journals.models import JournalEntry
from life_dashboard.quests.models import Habit, Quest

logger = logging.getLogger(__name__)


@login_required
def dashboard(request):
    user = request.user
    user_profile, created = UserProfile.objects.get_or_create(user=user)
    quests = Quest.objects.filter(user=user).order_by("-created_at")[:5]
    habits = Habit.objects.filter(user=user).order_by("-created_at")[:5]
    context = {
        "profile": user_profile,
        "quests": quests,
        "habits": habits,
    }

    return render(request, "dashboard/dashboard.html", context)


@transaction.atomic
def register(request):
    if request.method == "POST":
        logger.debug("Registration POST data: %s", request.POST)
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            logger.debug("Form is valid, creating user")
            try:
                user = form.save()
                logger.debug("User created: %s", user.username)
                # Create user profile if it doesn't exist
                profile, created = UserProfile.objects.get_or_create(user=user)
                logger.debug("Profile %s", "created" if created else "already exists")
                # Log the user in
                login(request, user)
                logger.debug("User logged in")
                messages.success(request, "Registration successful!")
                logger.debug("Redirecting to dashboard")
                return redirect("dashboard:dashboard")
            except Exception as e:
                logger.error("Error during user creation: %s", str(e))
                messages.error(request, f"Error during registration: {str(e)}")
        else:
            logger.debug("Form errors: %s", form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserRegistrationForm()
    return render(request, "dashboard/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect("dashboard:dashboard")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "dashboard/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.success(request, "Logout successful!")
    return redirect("dashboard:login")


@login_required
def profile(request):
    user = request.user
    user_profile, created = UserProfile.objects.get_or_create(user=user)

    # Safely get or create core stats
    try:
        core_stats = user.core_stats
    except CoreStat.DoesNotExist:
        core_stats, created = CoreStat.objects.get_or_create(user=user)

    achievements = UserAchievement.objects.filter(user=user).select_related(
        "achievement"
    )
    recent_entries = JournalEntry.objects.filter(user=user).order_by("-created_at")[:5]

    if request.method == "POST":
        logger.debug("Processing profile update POST request")
        # Update User model fields - single source of truth
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.email = request.POST.get("email", user.email)
        user.save()
        logger.debug("Updated User model: %s %s", user.first_name, user.last_name)

        messages.success(request, "Profile updated successfully", extra_tags="profile")
        return redirect("dashboard:profile")

    # Create form with initial data
    form = UserProfileForm(instance=user_profile)

    context = {
        "user": user,
        "user_profile": user_profile,
        "core_stats": core_stats,
        "achievements": achievements,
        "recent_entries": recent_entries,
        "form": form,
    }
    return render(request, "dashboard/profile.html", context)


@login_required
def level_up(request):
    return render(request, "dashboard/level_up.html")
