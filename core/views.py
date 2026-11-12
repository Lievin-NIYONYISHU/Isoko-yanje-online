from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ContactAdmin, Message, ProfilCommercant, Produit, User
from .serializers import ProfilCommercantSerializer, ProduitSerializer
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from urllib.parse import quote


class ProduitPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or (
            request.user.is_authenticated and request.user.is_commercant
        )


class ProfilCommercantPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or (
            request.user.is_authenticated and request.user.is_staff
        )


# 1. API pour la gestion et la consultation des Commerçants
class ProfilCommercantViewSet(viewsets.ModelViewSet):
    queryset = ProfilCommercant.objects.all()
    serializer_class = ProfilCommercantSerializer
    permission_classes = [ProfilCommercantPermission]

# 2. API pour la gestion et la consultation des Produits (ex: Vos chaussures)
class ProduitViewSet(viewsets.ModelViewSet):
    serializer_class = ProduitSerializer
    permission_classes = [ProduitPermission]

    def get_queryset(self):
        """
        RÈGLE DE SÉCURITÉ : Cette fonction filtre automatiquement le catalogue.
        Elle renvoie UNIQUEMENT les produits disponibles (est_disponible=True).
        Dès qu'un produit passe à False, il disparait du site pour les clients.
        """
        if self.request.user.is_authenticated and self.request.user.is_commercant:
            return Produit.objects.filter(
                commercant__user=self.request.user
            ).order_by('-date_publication')
        return Produit.objects.filter(est_disponible=True).order_by('-date_publication')

    def perform_create(self, serializer):
        profil = get_object_or_404(ProfilCommercant, user=self.request.user)
        serializer.save(commercant=profil)

    @action(detail=True, methods=['post'], url_path='marquer-vendu')
    def marquer_comme_vendu(self, request, pk=None):
        """
        Action personnalisée de l'API : Quand le client achète, le frontend appelle cette route
        pour retirer instantanément le produit du catalogue sans le supprimer de la base.
        """
        produit = self.get_object()
        produit.est_disponible = False
        produit.save(update_fields=['est_disponible'])
        return Response(
            {"message": f"Le produit '{produit.nom}' a été retiré du catalogue avec succès."},
            status=status.HTTP_200_OK
        )


# Afficher la page d'accueil
def page_accueil(request):
    return render(request, 'index.html')


def page_a_propos(request):
    return render(request, 'a_propos.html')


def page_contact_admin(request):
    if request.method == 'POST':
        nom = request.POST.get('nom', '').strip()
        contact = request.POST.get('contact', '').strip()
        sujet = request.POST.get('sujet', '').strip()
        contenu = request.POST.get('contenu', '').strip()
        if nom and contact and sujet and contenu:
            ContactAdmin.objects.create(nom=nom, contact=contact, sujet=sujet, contenu=contenu)
            messages.success(request, "Votre message a bien été transmis aux administrateurs.")
        else:
            messages.error(request, "Veuillez remplir tous les champs du formulaire.")
    return render(request, 'contact_admin.html')


def page_site(request):
    produits = Produit.objects.filter(est_disponible=True).select_related('commercant').order_by('-date_publication')
    recherche = request.GET.get('q', '').strip()
    categorie = request.GET.get('categorie', '').strip()
    if recherche:
        produits = produits.filter(
            Q(nom__icontains=recherche)
            | Q(description__icontains=recherche)
            | Q(commercant__nom_boutique__icontains=recherche)
        )
    if categorie:
        produits = produits.filter(commercant__type_produits__icontains=categorie)
    produits_demo = [
        {
            'nom': 'Baskets urbaines',
            'description': 'Chaussures confortables pour tous les jours.',
            'prix': '85000',
            'categorie': 'Mode',
            'couleur': 'from-orange-400 to-rose-500',
            'boutique': 'Boutique Bujumbura',
            'photo': 'chaussure%20urbain.jfif',
        },
        {
            'nom': 'Sac artisanal du Burundi',
            'description': 'Sac élégant fabriqué localement à la main.',
            'prix': '45000',
            'categorie': 'Artisanat',
            'couleur': 'from-amber-400 to-orange-600',
            'boutique': 'Créations Rohero',
            'photo': 'sac%20urbain.jfif',
        },
        {
            'nom': 'Smartphone Android',
            'description': 'Téléphone fiable avec double carte SIM.',
            'prix': '390000',
            'categorie': 'Électronique',
            'couleur': 'from-cyan-400 to-blue-600',
            'boutique': 'Tech Mukaza',
            'photo': 'smartfone.jfif',
        },
        {
            'nom': 'Chemise en coton',
            'description': 'Chemise légère et confortable, plusieurs tailles.',
            'prix': '35000',
            'categorie': 'Mode',
            'couleur': 'from-emerald-400 to-teal-600',
            'boutique': 'Style Gitega',
            'photo': 'chemise.jfif',
        },
        {
            'nom': 'Ensemble enfant',
            'description': 'Ensemble confortable pour enfant, haut et short.',
            'prix': '40000',
            'categorie': 'Mode',
            'boutique': 'Mode junior',
            'photo': 'IMG-20260328-WA0144.jpg',
        },
        {
            'nom': 'Ensemble de sport rouge',
            'description': 'Ensemble de sport deux pièces avec baskets assorties.',
            'prix': '75000',
            'categorie': 'Mode',
            'boutique': 'Style Bujumbura',
            'photo': 'WhatsApp_Image_2026-09-14_at_19.28.27.jpeg',
        },
        {
            'nom': 'Housse de fauteuil à fleurs bleues',
            'description': 'Housse textile décorative à motif floral bleu.',
            'prix': '55000',
            'categorie': 'Maison',
            'boutique': 'Maison et déco',
            'photo': 'WhatsApp_Image_2026-09-15_at_06.21.06.jpeg',
        },
        {
            'nom': 'Robe chemise vert olive',
            'description': 'Robe élégante à coupe chemise et ceinture.',
            'prix': '65000',
            'categorie': 'Mode',
            'boutique': 'Élégance Gitega',
            'photo': 'WhatsApp_Image_2026-09-15_at_09.08.19.jpeg',
        },
        {
            'nom': 'Robe rayée noire et marron',
            'description': 'Robe en maille rayée, présentée en deux coloris.',
            'prix': '60000',
            'categorie': 'Mode',
            'boutique': 'Prêt-à-porter',
            'photo': 'WhatsApp_Image_2026-09-15_at_10.09.22.jpeg',
        },
        {
            'nom': 'Robe rayée verte',
            'description': 'Robe élégante à rayures vertes et blanches.',
            'prix': '60000',
            'categorie': 'Mode',
            'boutique': 'Prêt-à-porter',
            'photo': 'WhatsApp_Image_2026-09-15_at_10.09.23.jpeg',
        },
        {
            'nom': 'Robe fleurie',
            'description': 'Robe à imprimé floral, disponible en plusieurs coloris.',
            'prix': '70000',
            'categorie': 'Mode',
            'boutique': 'Mode & couleurs',
            'photo': 'WhatsApp_Image_2026-09-15_at_10.10.06.jpeg',
        },
        {
            'nom': 'Huile végétale en bidon',
            'description': 'Huile végétale en grand format pour la cuisine.',
            'prix': '30000',
            'categorie': 'Alimentation',
            'boutique': 'Marché local',
            'photo': 'amames.jpg',
        },
        {
            'nom': 'Baskets montantes noir et blanc',
            'description': 'Baskets montantes au style décontracté.',
            'prix': '80000',
            'categorie': 'Mode',
            'boutique': 'Chaussures urbaines',
            'photo': 'b018af52d01249aaa9cb6c91b2e4b2c0.webp',
        },
        {
            'nom': 'Bottines en cuir marron',
            'description': 'Bottines marron pour un style élégant au quotidien.',
            'prix': '95000',
            'categorie': 'Mode',
            'boutique': 'Chaussures urbaines',
            'photo': 'b3.jpg',
        },
        {
            'nom': 'Huile de coton',
            'description': 'Huile en bidon, format familial.',
            'prix': '45000',
            'categorie': 'Alimentation',
            'boutique': 'Marché local',
            'photo': 'coton1.jpg',
        },
        {
            'nom': 'Baskets blanches',
            'description': 'Baskets blanches polyvalentes et faciles à assortir.',
            'prix': '85000',
            'categorie': 'Mode',
            'boutique': 'Chaussures urbaines',
            'photo': 'f1.jpg',
        },
        {
            'nom': 'Jupe plissée beige',
            'description': 'Jupe évasée beige à taille élastique.',
            'prix': '45000',
            'categorie': 'Mode',
            'boutique': 'Style Bujumbura',
            'photo': 'images.jpg',
        },
        {
            'nom': 'Baskets montantes sport',
            'description': 'Baskets montantes de sport noir et rouge.',
            'prix': '110000',
            'categorie': 'Mode',
            'boutique': 'Chaussures urbaines',
            'photo': 'j1.jpg',
        },
        {
            'nom': 'Pantalon cargo beige',
            'description': 'Pantalon cargo beige avec poches latérales.',
            'prix': '55000',
            'categorie': 'Mode',
            'boutique': 'Style Bujumbura',
            'photo': 'p.jpg',
        },
        {
            'nom': 'Pantalon cargo kaki',
            'description': 'Pantalon cargo kaki, coupe décontractée.',
            'prix': '60000',
            'categorie': 'Mode',
            'boutique': 'Style Bujumbura',
            'photo': 'p4.jpg',
        },
        {
            'nom': 'Séjour détente avec piscine',
            'description': 'Offre de démonstration inspirée de la photo. Prix indicatif.',
            'prix': '120000',
            'categorie': 'Services',
            'boutique': 'Séjours au Burundi',
            'photo': 'unnamed.webp',
        },
    ]
    return render(request, 'site.html', {
        'produits': produits,
        'produits_demo': produits_demo if not produits.exists() else [],
        'media_url': '/media/',
        'recherche': recherche,
        'categorie': categorie,
    })


def envoyer_message(request):
    if request.method != 'POST':
        return redirect('site_produits')
    produit = get_object_or_404(Produit, pk=request.POST.get('produit_id'), est_disponible=True)
    nom_client = request.POST.get('nom_client', '').strip()
    contact_client = request.POST.get('contact_client', '').strip()
    contenu = request.POST.get('contenu', '').strip()
    if nom_client and contact_client and contenu:
        Message.objects.create(
            produit=produit,
            commercant=produit.commercant,
            nom_client=nom_client,
            contact_client=contact_client,
            contenu=contenu,
        )
        telephone = produit.commercant.telephone.replace(' ', '').replace('-', '')
        if telephone.startswith('+'):
            telephone = telephone[1:]
        elif not telephone.startswith('257'):
            telephone = f'257{telephone}'

        message_whatsapp = (
            f"Bonjour, je suis {nom_client}.\n"
            f"Je vous contacte au sujet de votre produit « {produit.nom} ».\n"
            f"Mon contact : {contact_client}\n\n"
            f"{contenu}"
        )
        return redirect(f"https://wa.me/{telephone}?text={quote(message_whatsapp)}")
    return redirect(f"{reverse('site_produits')}?message=envoye")

# Afficher l'espace connexion/inscription du commerçant
def page_connexion_commercant(request):
    if request.user.is_authenticated and request.user.is_commercant:
        return redirect('tableau_commercant')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'connexion':
            user = authenticate(
                request,
                username=request.POST.get('username', '').strip(),
                password=request.POST.get('password', ''),
            )
            if user is not None and user.is_commercant:
                login(request, user)
                return redirect('tableau_commercant')
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
        elif action == 'inscription':
            nif = request.POST.get('nif', '').strip()
            if ProfilCommercant.objects.filter(nif=nif).exists():
                messages.error(request, "Ce NIF est déjà enregistré.")
            else:
                ProfilCommercant.objects.create(
                    nom=request.POST.get('nom', '').strip(),
                    prenom=request.POST.get('prenom', '').strip(),
                    nom_boutique=request.POST.get('nom_boutique', '').strip(),
                    nif=nif,
                    ville_ou_province=request.POST.get('ville_ou_province', 'Bujumbura').strip(),
                    commune=request.POST.get('commune', '').strip(),
                    quartier=request.POST.get('quartier', '').strip(),
                    avenue_ou_rue=request.POST.get('avenue_ou_rue', '').strip(),
                    point_de_repere=request.POST.get('point_de_repere', '').strip(),
                    telephone=request.POST.get('telephone', '').strip(),
                    type_produits=request.POST.get('type_produits', '').strip(),
                )
                messages.success(request, "Votre demande a été envoyée. Un administrateur créera votre accès après validation.")
                return redirect('connexion_commercant')
    return render(request, 'connexion_commercant.html')


@login_required(login_url='connexion_commercant')
def tableau_commercant(request):
    if not request.user.is_commercant:
        logout(request)
        return redirect('connexion_commercant')

    profil = get_object_or_404(ProfilCommercant, user=request.user)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'ajouter_produit':
            nom = request.POST.get('nom', '').strip()
            prix = request.POST.get('prix', '').strip()
            if nom and prix:
                Produit.objects.create(
                    commercant=profil,
                    nom=nom,
                    description=request.POST.get('description', '').strip(),
                    prix=prix,
                    photo=request.FILES.get('photo'),
                )
                messages.success(request, "Le produit a été ajouté à votre boutique.")
            else:
                messages.error(request, "Le nom et le prix du produit sont obligatoires.")
        elif action == 'modifier_produit':
            produit = get_object_or_404(Produit, pk=request.POST.get('produit_id'), commercant=profil)
            nom = request.POST.get('nom', '').strip()
            prix = request.POST.get('prix', '').strip()
            if nom and prix:
                produit.nom = nom
                produit.prix = prix
                produit.description = request.POST.get('description', '').strip()
                produit.save(update_fields=['nom', 'prix', 'description'])
                messages.success(request, "Les informations du produit ont été mises à jour.")
            else:
                messages.error(request, "Le nom et le prix du produit sont obligatoires.")
        elif action == 'supprimer_produit':
            produit = get_object_or_404(Produit, pk=request.POST.get('produit_id'), commercant=profil)
            produit.delete()
            messages.success(request, "Le produit a été retiré de votre boutique.")
        elif action == 'changer_disponibilite':
            produit = get_object_or_404(Produit, pk=request.POST.get('produit_id'), commercant=profil)
            produit.est_disponible = not produit.est_disponible
            produit.save(update_fields=['est_disponible'])
        return redirect('tableau_commercant')

    return render(request, 'tableau_commercant.html', {
        'profil': profil,
        'produits': profil.produits.all().order_by('-date_publication'),
        'messages_recus': profil.messages.select_related('produit').all(),
    })


def deconnexion_commercant(request):
    logout(request)
    return redirect('connexion_commercant')
        
