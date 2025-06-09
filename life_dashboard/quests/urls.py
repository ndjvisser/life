from django.urls import path

from life_dashboard.quests import views

app_name = "quests"

urlpatterns = [
    # Quest URLs
    path("quests/", views.quest_list, name="quest_list"),
    path("quests/<int:pk>/", views.quest_detail, name="quest_detail"),
    path("quests/create/", views.quest_create, name="quest_create"),
    path("quests/<int:pk>/update/", views.quest_update, name="quest_update"),
    # Habit URLs
    path("habits/", views.habit_list, name="habit_list"),
    path("habits/<int:pk>/", views.habit_detail, name="habit_detail"),
    path("habits/create/", views.habit_create, name="habit_create"),
    path("habits/<int:pk>/update/", views.habit_update, name="habit_update"),
    path("habits/<int:pk>/complete/", views.complete_habit, name="complete_habit"),
]
