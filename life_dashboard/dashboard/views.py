from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.shortcuts import redirect, render

from life_dashboard.achievements.models import UserAchievement
from life_dashboard.dashboard.forms import (
    UserRegistrationForm,
)
from life_dashboard.dashboard.models import UserProfile
from life_dashboard.journals.models import JournalEntry
from life_dashboard.quests.models import Habit, Quest


# Create your views here.
@login_required
def dashboard(request):
    user = request.user
    profile = user.profile
    quests = Quest.objects.filter(user=user).order_by("-created_at")[:5]
    habits = Habit.objects.filter(user=user).order_by("-created_at")[:5]
    context = {
        "profile": profile,
        "quests": quests,
        "habits": habits,
    }

    return render(request, "dashboard/dashboard.html", context)


@transaction.atomic
def register(request):
    if request.method == "POST":
        print(f"[DEBUG] Registration POST data: {request.POST}")
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            print("[DEBUG] Form is valid, creating user")
            try:
                user = form.save()
                print(f"[DEBUG] User created: {user.username}")
                # Create user profile if it doesn't exist
                profile, created = UserProfile.objects.get_or_create(user=user)
                print(f"[DEBUG] Profile {'created' if created else 'already exists'}")
                # Log the user in
                login(request, user)
                print("[DEBUG] User logged in")
                messages.success(request, "Registration successful!")
                print("[DEBUG] Redirecting to dashboard")
                return redirect("dashboard:dashboard")
            except Exception as e:
                print(f"[DEBUG] Error during user creation: {str(e)}")
                messages.error(request, f"Error during registration: {str(e)}")
        else:
            print(f"[DEBUG] Form errors: {form.errors}")
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
    user_profile = UserProfile.objects.get_or_create(user=user)[0]

    # Safely get or create core stats
    try:
        core_stats = user.core_stats
    except Exception:
        from life_dashboard.stats.models import Stats

        core_stats, created = Stats.objects.get_or_create(user=user)

    achievements = UserAchievement.objects.filter(user=user).select_related(
        "achievement"
    )
    recent_entries = JournalEntry.objects.filter(user=user).order_by("-created_at")[:5]

    if request.method == "POST":
        print("[DEBUG] Processing profile update POST request")
        # Update User model fields
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.email = request.POST.get("email", user.email)
        user.save()
        print(f"[DEBUG] Updated User model: {user.first_name} {user.last_name}")

        # Update UserProfile model fields
        user_profile.first_name = user.first_name
        user_profile.last_name = user.last_name
        user_profile.email = user.email
        user_profile.save()
        print(
            f"[DEBUG] Updated UserProfile model: {user_profile.first_name} "
            f"{user_profile.last_name}"
        )

        messages.success(request, "Profile updated successfully", extra_tags="profile")
        return redirect("dashboard:profile")

    context = {
        "user": user,
        "user_profile": user_profile,
        "core_stats": core_stats,
        "achievements": achievements,
        "recent_entries": recent_entries,
    }
    return render(request, "dashboard/profile.html", context)


@login_required
def level_up(request):
    return render(request, "dashboard/level_up.html")
