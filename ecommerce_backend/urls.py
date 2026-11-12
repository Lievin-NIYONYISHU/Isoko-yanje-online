from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# Importation de nos vues de pages depuis l'application core
from core.views import (
    deconnexion_commercant,
    page_accueil,
    page_a_propos,
    page_connexion_commercant,
    page_contact_admin,
    page_site,
    tableau_commercant,
)

from core.views import envoyer_message, page_accueil, page_connexion_commercant, page_site
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')), 
    
    # --- Vos vraies adresses de site web gérées par Django ---
    path('', page_accueil, name='accueil'), # L'adresse racine http://127.0.0
    path('a-propos/', page_a_propos, name='a_propos'),
    path('contact/', page_contact_admin, name='contact_admin'),
    path('site/', page_site, name='site_produits'),
    path('messages/envoyer/', envoyer_message, name='envoyer_message'),
    path('connexion-commercant/', page_connexion_commercant, name='connexion_commercant'),
    path('commercant/', tableau_commercant, name='tableau_commercant'),
    path('deconnexion-commercant/', deconnexion_commercant, name='deconnexion_commercant'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
