from django.urls import path

from life_dashboard.quests import views

app_name = "quests"

urlpatterns = [
    # Quest URLs
    path("", views.quest_list, name="quest_list"),
    path("quests/create/", views.quest_create, name="quest_create"),
    path("quests/<int:pk>/", views.quest_detail, name="quest_detail"),
    path("quests/<int:pk>/update/", views.quest_update, name="quest_update"),
    path("quests/<int:pk>/delete/", views.quest_delete, name="quest_delete"),
    path("quests/<int:pk>/complete/", views.complete_quest, name="complete_quest"),
    # Habit URLs
    path("habits/", views.habit_list, name="habit_list"),
    path("habits/create/", views.habit_create, name="habit_create"),
    path("habits/<int:pk>/", views.habit_detail, name="habit_detail"),
    path("habits/<int:pk>/update/", views.habit_update, name="habit_update"),
    path("habits/<int:pk>/delete/", views.habit_delete, name="habit_delete"),
    path(
        "habits/<int:habit_id>/complete/", views.complete_habit, name="complete_habit"
    ),
]
