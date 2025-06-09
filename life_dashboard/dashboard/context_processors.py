from quests.models import Quest, Habit

def user_quests_and_habits(request):
    if request.user.is_authenticated:
        quests = Quest.objects.filter(user=request.user).order_by('-created_at')[:5]
        habits = Habit.objects.filter(user=request.user).order_by('-created_at')[:5]
        return {
            'user_quests': quests,
            'user_habits': habits,
        }
    return {
        'user_quests': [],
        'user_habits': [],
    } 