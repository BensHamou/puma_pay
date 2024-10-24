from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("puma_pay/admin/", admin.site.urls),
    path("", include('account.urls')),
    path("", include('commercial.urls'))
]

handler404 = 'account.views.page_not_found'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)