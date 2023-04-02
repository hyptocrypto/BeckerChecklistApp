from BeckerChecklistApp import settings
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("checklist.urls")),
    path(
        "auth/login/",
        auth_views.LoginView.as_view(template_name="registration/login.jinja"),
        name="login",
    ),
    path(
        "auth/logout/",
        auth_views.LogoutView.as_view(next_page=settings.LOGOUT_REDIRECT_URL),
        name="logout",
    ),
]
