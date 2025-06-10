from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from life_dashboard.quests.forms import HabitForm, QuestForm
from life_dashboard.quests.models import Habit, Quest


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
        if form.is_valid():
            quest = form.save(commit=False)
            quest.user = request.user
            quest.save()
            messages.success(request, "Quest created successfully!")
            return redirect("quests:quest_detail", pk=quest.pk)
    else:
        form = QuestForm()
    return render(request, "quests/quest_form.html", {"form": form, "action": "Create"})


@login_required
def quest_update(request, pk):
    quest = get_object_or_404(Quest, pk=pk, user=request.user)
    if request.method == "POST":
        form = QuestForm(request.POST, instance=quest)
        if form.is_valid():
            form.save()
            messages.success(request, "Quest updated successfully!")
            return redirect("quests:quest_detail", pk=quest.pk)
    else:
        form = QuestForm(instance=quest)
    return render(request, "quests/quest_form.html", {"form": form, "action": "Update"})


@login_required
def quest_delete(request, pk):
    quest = get_object_or_404(Quest, pk=pk, user=request.user)
    if request.method == "POST":
        quest.delete()
        messages.success(request, "Quest deleted successfully!")
        return redirect("quests:quest_list")
    return render(request, "quests/quest_confirm_delete.html", {"quest": quest})


@login_required
def habit_list(request):
    habits = Habit.objects.filter(user=request.user)
    return render(request, "quests/habit_list.html", {"habits": habits})


@login_required
def habit_detail(request, pk):
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    completions = habit.completions.all().order_by("-completed_at")[:10]
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
            habit.save()
            messages.success(request, "Habit created successfully!")
            return redirect("quests:habit_detail", pk=habit.pk)
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
            return redirect("quests:habit_detail", pk=habit.pk)
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
def complete_habit(request, pk):
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    if request.method == "POST":
        count = int(request.POST.get("count", 1))
        habit.complete(count)
        messages.success(request, "Habit completed successfully!")
        return redirect("quests:habit_detail", pk=habit.pk)
    return redirect("quests:habit_detail", pk=habit.pk)
