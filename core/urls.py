from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProfilCommercantViewSet, ProduitViewSet

# Le routeur de Django REST Framework génère automatiquement toutes les routes standards de l'API
router = DefaultRouter()
router.register(r'commercant', ProfilCommercantViewSet, basename='api-commercant')
router.register(r'produits', ProduitViewSet, basename='api-produits')

urlpatterns = [
    path('', include(router.urls)),
]
