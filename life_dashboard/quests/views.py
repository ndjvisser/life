import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from life_dashboard.quests.forms import HabitForm, QuestForm
from life_dashboard.quests.models import Habit, HabitCompletion, Quest
from life_dashboard.stats.models import Stats

logger = logging.getLogger(__name__)


@login_required
def quest_list(request):
    quests = Quest.objects.filter(user=request.user)
    return render(request, "quests/quest_list.html", {"quests": quests})


@login_required
def quest_detail(request, pk):
    quest = get_object_or_404(Quest, pk=pk, user=request.user)
    return render(request, "quests/quest_detail.html", {"quest": quest})


@login_required
def quest_create(request):
    if request.method == "POST":
        form = QuestForm(request.POST)
        logger.debug("Form data: %s", request.POST)
        if form.is_valid():
            quest = form.save(commit=False)
            quest.user = request.user
            quest.status = "active"
            quest.save()
            messages.success(request, "Quest created successfully!", extra_tags="quest")
            return redirect("quests:quest_list")
        else:
            logger.debug("Form errors: %s", form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = QuestForm()
    return render(request, "quests/quest_form.html", {"form": form, "action": "Create"})


@login_required
def quest_update(request, pk):
    quest = get_object_or_404(Quest, pk=pk, user=request.user)
    if request.method == "POST":
        form = QuestForm(request.POST, instance=quest)
        logger.debug("Form data: %s", request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Quest updated successfully!", extra_tags="quest")
            return redirect("quests:quest_list")
        else:
            logger.debug("Form errors: %s", form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = QuestForm(instance=quest)
    return render(request, "quests/quest_form.html", {"form": form, "action": "Update"})


@login_required
def quest_delete(request, pk):
    quest = get_object_or_404(Quest, pk=pk, user=request.user)
    if request.method == "POST":
        quest.delete()
        messages.success(request, "Quest deleted successfully!", extra_tags="quest")
        return redirect("quests:quest_list")
    return render(request, "quests/quest_confirm_delete.html", {"quest": quest})


@login_required
def complete_quest(request, pk):
    quest = get_object_or_404(Quest, pk=pk, user=request.user)
    if request.method == "POST":
        initial_level = request.user.stats.level
        quest.status = "completed"
        quest.completed_at = timezone.now()
        quest.save()

        # Add experience to user's stats
        request.user.stats.gain_experience(quest.experience_reward)

        # Check if level up occurred
        if request.user.stats.level > initial_level:
            messages.success(
                request, f"Quest completed! Level up to {request.user.stats.level}!"
            )
            return redirect("dashboard:level_up")
        else:
            messages.success(request, "Quest completed!")
            return redirect("quests:quest_list")
    return render(request, "quests/quest_detail.html", {"quest": quest})


@login_required
def habit_list(request):
    habits = Habit.objects.filter(user=request.user)
    return render(request, "quests/habit_list.html", {"habits": habits})


@login_required
def habit_detail(request, pk):
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    completions = habit.completions.all().order_by("-date")[:10]
    return render(
        request,
        "quests/habit_detail.html",
        {"habit": habit, "completions": completions},
    )


@login_required
def habit_create(request):
    if request.method == "POST":
        form = HabitForm(request.POST)
        if form.is_valid():
            habit = form.save(commit=False)
            habit.user = request.user
            # Ensure experience_reward is an integer
            habit.experience_reward = int(form.cleaned_data.get("experience_reward", 0))
            habit.save()
            messages.success(request, "Habit created successfully!")
            return redirect("quests:habit_list")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = HabitForm()
    return render(request, "quests/habit_form.html", {"form": form})


@login_required
def habit_update(request, pk):
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    if request.method == "POST":
        form = HabitForm(request.POST, instance=habit)
        if form.is_valid():
            form.save()
            messages.success(request, "Habit updated successfully!")
            return redirect("quests:habit_list")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = HabitForm(instance=habit)
    return render(request, "quests/habit_form.html", {"form": form})


@login_required
def habit_delete(request, pk):
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    if request.method == "POST":
        habit.delete()
        messages.success(request, "Habit deleted successfully!")
        return redirect("quests:habit_list")
    return render(request, "quests/habit_confirm_delete.html", {"habit": habit})


@login_required
def complete_habit(request, habit_id):
    """Complete a habit and award experience points."""
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)

    # Create completion record with correct fields
    HabitCompletion.objects.create(
        habit=habit,
        date=timezone.now().date(),
        experience_gained=habit.experience_reward,
    )

    # Update habit streak
    habit.current_streak += 1
    if habit.current_streak > habit.longest_streak:
        habit.longest_streak = habit.current_streak
    habit.save()

    # Award experience points
    try:
        # Get or create stats for the user
        stats, created = Stats.objects.get_or_create(user=request.user)
        old_level = stats.level
        stats.gain_experience(habit.experience_reward)

        # Check for level up
        if stats.level > old_level:
            messages.success(
                request,
                f"Level up! You are now level {stats.level}",
                extra_tags="level-up",
            )

        messages.success(
            request, f"Habit '{habit.name}' completed! +{habit.experience_reward} XP"
        )
    except Exception as e:
        messages.error(request, f"Error updating stats: {str(e)}")

    return redirect("quests:habit_detail", pk=habit.id)


@login_required
def quest_complete(request, quest_id):
    quest = get_object_or_404(Quest, id=quest_id, user=request.user)
    if request.method == "POST":
        quest.complete()
        messages.success(request, "Quest completed successfully!")
        return redirect("quests:quest_detail", quest_id=quest.id)
    return redirect("quests:quest_detail", quest_id=quest.id)
