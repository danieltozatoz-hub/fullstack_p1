"""URL configuration for biblioteca project."""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Login / logout (o logout do Django 5 só aceita POST)
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # API REST (DRF): tudo sob /api/, separado das páginas
    path('api/', include('biblioteca.api_urls')),
    path('api-auth/', include('rest_framework.urls')),  # login da Browsable API

    # Páginas
    path('', RedirectView.as_view(pattern_name='dashboard', permanent=False)),
    path('', include('acervo.urls')),
    path('', include('usuarios.urls')),
    path('', include('emprestimos.urls')),
]
