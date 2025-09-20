import logging

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.shortcuts import redirect, render

from life_dashboard.achievements.models import UserAchievement
from life_dashboard.dashboard.forms import (
    UserProfileForm,
    UserRegistrationForm,
)
from life_dashboard.dashboard.models import UserProfile
from life_dashboard.journals.models import JournalEntry
from life_dashboard.quests.models import Habit, Quest
from life_dashboard.stats.infrastructure.models import CoreStatModel

from .domain.value_objects import ProfileUpdateData
from .queries.profile_queries import ProfileQueries

# Import new service layer
from .services import get_user_service

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
    """
    Handle user registration: display the registration form on GET and process form submissions on POST.

    On POST, validates a UserRegistrationForm; if valid, delegates user creation to the user service (get_user_service().register_user), logs the new user in, and redirects to the dashboard. If the service call fails an error message is added and the form is re-rendered. If the form is invalid, validation errors are added to the messages framework and the form is re-rendered. On GET, renders an empty registration form.

    Parameters:
        request (HttpRequest): Django request object for the current request/response cycle.

    Returns:
        HttpResponse: Renders the registration template or redirects to the dashboard after successful registration.
    """
    if request.method == "POST":
        logger.debug("Registration POST data: %s", request.POST)
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            logger.debug("Form is valid, creating user")
            try:
                # Use service layer for user registration
                user_service = get_user_service()
                user_id, profile = user_service.register_user(
                    username=form.cleaned_data["username"],
                    email=form.cleaned_data["email"],
                    password=form.cleaned_data["password1"],
                    first_name=form.cleaned_data.get("first_name", ""),
                    last_name=form.cleaned_data.get("last_name", ""),
                )
                logger.debug("User created via service: %s", profile.username)

                # Get Django user for login
                from django.contrib.auth import get_user_model

                User = get_user_model()
                user = User.objects.get(id=user_id)
                login(request, user)

                return redirect("dashboard:dashboard")
            except Exception:
                logger.exception(
                    "Error during user registration for username: %s",
                    form.cleaned_data.get("username", "unknown"),
                )
                messages.error(
                    request,
                    "An error occurred during registration. Please try again or contact support.",
                )
                # Let the atomic block handle rollback implicitly by
                # re-rendering the form
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
    """
    Render and handle the user profile page.

    On GET: fetches a structured profile summary via ProfileQueries, ensures the user's CoreStat and UserProfile exist, loads recent achievements and journal entries, and returns the profile page with a UserProfileForm populated from the user's profile.

    On POST: builds a ProfileUpdateData from submitted form fields and delegates the update to the user service (get_user_service().update_profile). On successful update redirects back to the profile page with a success message; on failure records an error message and re-renders the page.

    Behavior notes:
    - If ProfileQueries.get_profile_summary returns no data, the view adds an error message and redirects to the dashboard.
    - CoreStat is created if missing.
    - Uses Django messages for user feedback and relies on the service layer for profile mutations.
    Parameters:
        request (HttpRequest): Django request object for the current user/session.
    Returns:
        HttpResponse: rendered profile page or a redirect response.
    """
    user = request.user

    # Use queries for read-only data
    profile_data = ProfileQueries.get_profile_summary(user.id)
    if not profile_data:
        messages.error(request, "Profile not found")
        return redirect("dashboard:dashboard")

    # Safely get or create core stats
    try:
        core_stats = user.core_stats
    except CoreStatModel.DoesNotExist:
        core_stats, created = CoreStatModel.objects.get_or_create(user=user)

    achievements = UserAchievement.objects.filter(user=user).select_related(
        "achievement"
    )
    recent_entries = JournalEntry.objects.filter(user=user).order_by("-created_at")[:5]

    if request.method == "POST":
        logger.debug("Processing profile update POST request")
        try:
            # Use service layer for profile updates
            user_service = get_user_service()
            update_data = ProfileUpdateData(
                first_name=request.POST.get("first_name"),
                last_name=request.POST.get("last_name"),
                email=request.POST.get("email"),
                bio=request.POST.get("bio", ""),
                location=request.POST.get("location", ""),
            )

            updated_profile = user_service.update_profile(user.id, update_data)
            logger.debug("Updated profile via service: %s", updated_profile.username)

            messages.success(
                request, "Profile updated successfully", extra_tags="profile"
            )
            return redirect("dashboard:profile")
        except Exception:
            logger.exception("Error updating profile for user %s", user.username)
            messages.error(
                request,
                "An error occurred while updating your profile. Please try again or contact support.",
            )

    # Create form with initial data (still using Django form for now)
    user_profile, _ = UserProfile.objects.get_or_create(user=user)
    form = UserProfileForm(instance=user_profile)

    context = {
        "user": user,
        "user_profile": user_profile,
        "profile_data": profile_data,  # Add structured profile data
        "core_stats": core_stats,
        "achievements": achievements,
        "recent_entries": recent_entries,
        "form": form,
    }
    return render(request, "dashboard/profile.html", context)


@login_required
def level_up(request):
    return render(request, "dashboard/level_up.html")
