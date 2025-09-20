from urllib.parse import urlencode

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_view_names = {"dashboard:login", "dashboard:register"}

    def __call__(self, request):
        match = getattr(request, "resolver_match", None)
        view_name = match.view_name if match else None

        namespaces = match.namespaces if match else []
        is_admin_view = False
        if match:
            is_admin_view = (
                match.app_name == "admin"
                or "admin" in namespaces
                or (view_name or "").startswith("admin:")
            )

        if request.user.is_authenticated or is_admin_view or view_name in self.exempt_view_names:
            return self.get_response(request)

        if request.method in {"GET", "HEAD"}:
            messages.warning(request, "Please log in to access this page.")

        login_url = reverse("dashboard:login")
        params = urlencode({"next": request.get_full_path()})
        return redirect(f"{login_url}?{params}")
