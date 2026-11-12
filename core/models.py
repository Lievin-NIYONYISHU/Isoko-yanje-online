from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

# 1. Gestion des rôles utilisateurs
class User(AbstractUser):
    is_commercant = models.BooleanField(default=False)
    is_client = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

# 2. Profil du Commerçant avec Localisation Urbaine Précise
class ProfilCommercant(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        related_name='profil_commercant',
        blank=True,
        null=True,
        help_text="L'administrateur associe ce profil à un utilisateur autorisé.",
    )
    
    # Identité
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    nom_boutique = models.CharField(max_length=150, verbose_name="Nom de la Boutique")
    description_boutique = models.TextField(blank=True, help_text="Décrivez votre activité")
    logo_boutique = models.ImageField(upload_to='logos_boutiques/', blank=True, null=True)
    nif = models.CharField(max_length=50, unique=True, verbose_name="NIF")
    
    # --- NOUVELLE LOCALISATION PRÉCISE ---
    ville_ou_province = models.CharField(max_length=100, default="Bujumbura", verbose_name="Ville / Province")
    commune = models.CharField(max_length=100, help_text="Ex: Mukaza, Ntahangwa, Muha, Gitega...")
    quartier = models.CharField(max_length=100, help_text="Ex: Rohero, Kamenge, Kinindo, Nyakabiga...")
    avenue_ou_rue = models.CharField(max_length=150, help_text="Ex: Avenue de la J.R.R, Rue du Commerce...")
    point_de_repere = models.CharField(max_length=255, help_text="Ex: En face de l'Hôtel Horizon, Près de la cathédrale...")
    
    # Contacts
    phone_regex = RegexValidator(
        regex=r'^\+?(257)?\d{8}$',
        message="Le numéro doit être au format burundais valide. Ex: +25779XXXXXX ou 79XXXXXX."
    )
    telephone = models.CharField(validators=[phone_regex], max_length=20, help_text="Ex: +25779XXXXXX")
    telephone_visible = models.BooleanField(default=False, help_text="Afficher le numéro aux clients")
    
    page_facebook = models.URLField(blank=True, null=True, help_text="Lien Facebook (optionnel)")
    page_instagram = models.URLField(blank=True, null=True, help_text="Lien Instagram (optionnel)")
    type_produits = models.CharField(max_length=255, help_text="Ex: Shoes, Clothing")
    date_inscription = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom_boutique} - {self.quartier} ({self.point_de_repere})"

# 3. Structure pour les produits
class Produit(models.Model):
    commercant = models.ForeignKey(ProfilCommercant, on_delete=models.CASCADE, related_name='produits')
    nom = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2, help_text="Prix en BIF")
    photo = models.ImageField(upload_to='produits_photos/', blank=True, null=True)
    est_disponible = models.BooleanField(default=True)
    date_publication = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} - {self.prix} BIF"


class Message(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='messages')
    commercant = models.ForeignKey(ProfilCommercant, on_delete=models.CASCADE, related_name='messages')
    nom_client = models.CharField(max_length=120)
    contact_client = models.CharField(max_length=120)
    contenu = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    est_lu = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_envoi']

    def __str__(self):
        return f"Message de {self.nom_client} pour {self.produit.nom}"


class ContactAdmin(models.Model):
    nom = models.CharField(max_length=120)
    contact = models.CharField(max_length=120)
    sujet = models.CharField(max_length=180)
    contenu = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    est_traite = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_envoi']
        verbose_name = "Contact administrateur"
        verbose_name_plural = "Contacts administrateurs"

    def __str__(self):
        return f"{self.sujet} - {self.nom}"
