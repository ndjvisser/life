from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .models import Stats
from .forms import StatsForm


# Create your views here.
from django.shortcuts import render
from .models import Stats  # Assuming you have a Stats model


@login_required
def dashboard(request):
    # Fetch the stats for the logged-in user, or create default stats if none exist
    stats, created = Stats.objects.get_or_create(user=request.user)
    
    stat_list = [
        {"name": "Strength", "value": stats.strength, "icon": "fitness_center"},
        {"name": "Agility", "value": stats.agility, "icon": "directions_run"},
        {"name": "Endurance", "value": stats.endurance, "icon": "favorite"},
        {"name": "Intelligence", "value": stats.intelligence, "icon": "school"},
        {"name": "Charisma", "value": stats.charisma, "icon": "record_voice_over"},
        {"name": "Wisdom", "value": stats.wisdom, "icon": "lightbulb"},
        ]
    
    if request.method == 'POST':
        form = StatsForm(request.POST, instance=stats)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = StatsForm(instance=stats)
    
    return render(request,
                  'dashboard/dashboard.html',
                  {
                      'stats': stats,
                      'stat_list': stat_list,
                      'form': form}
                  )


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
