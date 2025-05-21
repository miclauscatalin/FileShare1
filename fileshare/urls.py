from django.contrib import admin
from django.urls import path
from share.views import (
    FileUploadView, ShareCreateView, download_file, DashboardView
    , UserListView)
from django.contrib.auth import views as auth_views
from share.views import delete_file
from django.urls import include
urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="/login/"), name="logout"),
    path("", DashboardView.as_view(), name="dashboard"),
    path("admin/", admin.site.urls),
    path("api/upload/", FileUploadView.as_view(), name="api-upload"),
    path("api/share/", ShareCreateView.as_view(), name="api-share"),
    path("download/<uuid:token>/", download_file, name="download-file"),
    path("api/delete/<int:pk>/", delete_file, name="api-delete-file"),
    path('webpush/', include('webpush.urls')),
    path('api/users/', UserListView.as_view(), name='api-users'),
]
