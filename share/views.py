import os
from django.http import FileResponse, Http404
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, render
from rest_framework import generics, permissions
from rest_framework.generics import ListAPIView
from .models import File, Share
from django.contrib.auth import get_user_model
from webpush import send_user_notification
from .serializers import FileSerializer, ShareSerializer


class FileUploadView(generics.CreateAPIView):
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ShareCreateView(generics.CreateAPIView):
    serializer_class = ShareSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        recipient_id = self.request.data.get('recipient')
        recipient_user = None
        if recipient_id:
            try:
                User = get_user_model()
                recipient_user = User.objects.get(id=recipient_id)
            except User.DoesNotExist:
                pass # Handle case where recipient user doesn't exist

        share = serializer.save(recipient=recipient_user)
        link = self.request.build_absolute_uri(f'/download/{share.token}/')

        if recipient_user:
            payload = {"head": "New file shared with you!", "body": f"From: {self.request.user.username}\nFile: {share.file.upload.name.split('/')[-1]}\nMessage: {share.message}", "url": link}
            send_user_notification(user=recipient_user, payload=payload, ttl=1000)


class UserListView(ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = get_user_model().objects.all()

from django.http import FileResponse

def download_file(request, token):
    share = get_object_or_404(Share, token=token)
    file_path = share.file.upload.path
    return FileResponse(open(file_path, 'rb'),
                        as_attachment=True,
                        filename=os.path.basename(file_path))
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import File
from django.conf import settings

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"
    login_url = '/admin/login/'
    redirect_field_name = 'redirect_to'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        owned_files = File.objects.filter(owner=self.request.user).order_by("-uploaded_at")
        shared_shares = Share.objects.filter(recipient=self.request.user).select_related('file')
        shared_files = [share.file for share in shared_shares]

        all_files = {}
        for f in owned_files:
            all_files[f.id] = {'file': f, 'size': f.upload.size, 'is_owned': True}

        for f in shared_files:
            if f.id not in all_files:
                all_files[f.id] = {'file': f, 'size': f.upload.size, 'is_owned': False}

        # Convert dictionary values to a list for template iteration
        ctx["files"] = list(all_files.values())
        # Sort files by uploaded_at (descending) for consistent ordering
        ctx["files"].sort(key=lambda x: x['file'].uploaded_at, reverse=True)
        ctx["vapid_public_key"] = settings.WEBPUSH_SETTINGS["VAPID_PUBLIC_KEY"]
        return ctx

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import File

@login_required
@require_POST
def delete_file(request, pk):
    try:
        f = File.objects.get(pk=pk, owner=request.user)
        f.delete()  # șterge atât obiectul cât și fișierul fizic
        return JsonResponse({'status': 'ok'})
    except File.DoesNotExist:
        return JsonResponse({'status': 'not_found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'msg': str(e)}, status=500)
from django.conf import settings
def dashboard(request):
    ...
    return render(request, "dashboard.html", {
        "files": files,
        "vapid_public_key": settings.WEBPUSH_SETTINGS["VAPID_PUBLIC_KEY"]
    })
