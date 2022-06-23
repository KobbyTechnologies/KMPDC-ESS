from django.urls import path
from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('dashboard', views.dashboard, name="dashboard"),
    path('canvas', views.Canvas, name="canvas"),
    path('details/<str:pk>/', views.details, name="details")

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
