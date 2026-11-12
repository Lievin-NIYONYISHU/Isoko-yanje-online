from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import ContactAdmin, Message, User, ProfilCommercant, Produit

admin.site.register(User, UserAdmin)

@admin.register(ProfilCommercant)
class ProfilCommercantAdmin(admin.ModelAdmin):
    # On affiche les colonnes clés pour suivre facilement nos commerçants au Burundi
    list_display = ('nom_boutique', 'nom', 'prenom', 'nif', 'statut_acces', 'quartier', 'telephone')
    search_fields = ('nom_boutique', 'nif', 'quartier', 'telephone')
    list_filter = ('ville_ou_province', 'quartier', 'type_produits')

    @admin.display(description="Accès")
    def statut_acces(self, obj):
        return "Autorisé" if obj.user_id else "En attente"

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom', 'commercant', 'prix', 'est_disponible', 'date_publication')
    list_filter = ('est_disponible', 'date_publication')
    search_fields = ('nom', 'commercant__nom_boutique')
    list_editable = ('est_disponible', 'prix')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('nom_client', 'contact_client', 'produit', 'commercant', 'est_lu', 'date_envoi')
    list_filter = ('est_lu', 'date_envoi')
    search_fields = ('nom_client', 'contact_client', 'contenu', 'produit__nom', 'commercant__nom_boutique')
    list_editable = ('est_lu',)


@admin.register(ContactAdmin)
class ContactAdminAdmin(admin.ModelAdmin):
    list_display = ('nom', 'contact', 'sujet', 'est_traite', 'date_envoi')
    list_filter = ('est_traite', 'date_envoi')
    search_fields = ('nom', 'contact', 'sujet', 'contenu')
