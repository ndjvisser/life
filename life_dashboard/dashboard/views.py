from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .models import Stats
from .forms import StatsForm
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from core_stats.models import CoreStat
from life_stats.models import LifeStat, LifeStatCategory
from quests.models import Quest, Habit
from skills.models import Skill, SkillCategory
from achievements.models import UserAchievement
from journals.models import JournalEntry


# Create your views here.
@login_required
def dashboard(request):
    # Get user's core stats
    core_stats, created = CoreStat.objects.get_or_create(user=request.user)
    
    # Get life stats by category
    life_stat_categories = LifeStatCategory.objects.all()
    life_stats = {}
    for category in life_stat_categories:
        life_stats[category] = LifeStat.objects.filter(user=request.user, category=category)
    
    # Get active quests
    active_quests = Quest.objects.filter(
        user=request.user,
        status__in=['NOT_STARTED', 'IN_PROGRESS']
    ).order_by('-quest_type', 'due_date')[:5]
    
    # Get daily habits
    daily_habits = Habit.objects.filter(
        user=request.user,
        frequency='DAILY'
    ).order_by('-current_streak')
    
    # Get skills by category
    skill_categories = SkillCategory.objects.all()
    skills = {}
    for category in skill_categories:
        skills[category] = Skill.objects.filter(user=request.user, category=category)
    
    # Get recent achievements
    recent_achievements = UserAchievement.objects.filter(
        user=request.user
    ).order_by('-unlocked_at')[:5]
    
    # Get recent journal entries
    recent_entries = JournalEntry.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]
    
    context = {
        'core_stats': core_stats,
        'life_stat_categories': life_stat_categories,
        'life_stats': life_stats,
        'active_quests': active_quests,
        'daily_habits': daily_habits,
        'skill_categories': skill_categories,
        'skills': skills,
        'recent_achievements': recent_achievements,
        'recent_entries': recent_entries,
    }
    
    return render(request, 'dashboard/dashboard.html', context)


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
