from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated and not request.path.startswith("/admin/"):
            if request.path not in [
                reverse("dashboard:login"),
                reverse("dashboard:register"),
            ]:
                messages.warning(request, "Please log in to access this page.")
                return redirect("dashboard:login")
        return self.get_response(request)
