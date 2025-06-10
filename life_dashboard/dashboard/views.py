from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render

from life_dashboard.achievements.models import UserAchievement
from life_dashboard.core_stats.models import CoreStat
from life_dashboard.dashboard.forms import UserProfileForm, UserRegistrationForm
from life_dashboard.journals.models import JournalEntry
from life_dashboard.life_stats.models import LifeStat, LifeStatCategory
from life_dashboard.quests.models import Habit, Quest
from life_dashboard.skills.models import Skill, SkillCategory


# Create your views here.
@login_required
def dashboard(request):
    # Get user's core stats
    core_stats, created = CoreStat.objects.get_or_create(user=request.user)

    # Get life stats by category
    life_stat_categories = LifeStatCategory.objects.all()
    life_stats = {}
    for category in life_stat_categories:
        life_stats[category] = LifeStat.objects.filter(
            user=request.user, category=category
        )

    # Get active quests
    active_quests = Quest.objects.filter(
        user=request.user, status__in=["NOT_STARTED", "IN_PROGRESS"]
    ).order_by("-quest_type", "due_date")[:5]

    # Get daily habits
    daily_habits = Habit.objects.filter(user=request.user, frequency="DAILY").order_by(
        "-current_streak"
    )

    # Get skills by category
    skill_categories = SkillCategory.objects.all()
    skills = {}
    for category in skill_categories:
        skills[category] = Skill.objects.filter(user=request.user, category=category)

    # Get recent achievements
    recent_achievements = UserAchievement.objects.filter(user=request.user).order_by(
        "-unlocked_at"
    )[:5]

    # Get recent journal entries
    recent_entries = JournalEntry.objects.filter(user=request.user).order_by(
        "-created_at"
    )[:5]

    # Get recent quests and habits (from index view)
    recent_quests = Quest.objects.filter(user=request.user).order_by("-created_at")[:5]
    recent_habits = Habit.objects.filter(user=request.user).order_by("-created_at")[:5]

    context = {
        "core_stats": core_stats,
        "life_stat_categories": life_stat_categories,
        "life_stats": life_stats,
        "active_quests": active_quests,
        "daily_habits": daily_habits,
        "skill_categories": skill_categories,
        "skills": skills,
        "recent_achievements": recent_achievements,
        "recent_entries": recent_entries,
        "recent_quests": recent_quests,
        "recent_habits": recent_habits,
    }

    return render(request, "dashboard/dashboard.html", context)


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect("dashboard:dashboard")
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
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("dashboard:profile")
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, "dashboard/profile.html", {"form": form})
