from django.urls import path

from life_dashboard.dashboard import views

app_name = "dashboard"

urlpatterns = [
    path("", views.index, name="dashboard"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile, name="profile"),
]
