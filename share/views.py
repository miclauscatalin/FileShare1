import os
from django.http import FileResponse, Http404
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import File, Share
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
        share = serializer.save()
        link = self.request.build_absolute_uri(f'/download/{share.token}/')
        send_mail(
            subject='Ai primit un fișier',
            message=f'Mesaj: {share.message}\nDescarcă: {link}',
            from_email=None,
            recipient_list=[self.request.user.email],
        )

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
        ctx["files"] = File.objects.filter(owner=self.request.user).order_by("-uploaded_at")
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
