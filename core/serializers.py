from rest_framework import serializers
from .models import User, ProfilCommercant, Produit

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'is_commercant', 'is_client']

class ProfilCommercantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ProfilCommercant
        fields = [
            'id', 'user', 'nom_boutique', 'description_boutique', 'logo_boutique',
            'nif', 'ville_ou_province', 'commune', 'quartier', 'avenue_ou_rue',
            'point_de_repere', 'telephone', 'telephone_visible',
            'page_facebook', 'page_instagram', 'type_produits'
        ]

class ProduitSerializer(serializers.ModelSerializer):
    commercant_details = ProfilCommercantSerializer(source='commercant', read_only=True)

    class Meta:
        model = Produit
        fields = [
            'id', 'commercant', 'commercant_details', 'nom', 
            'description', 'prix', 'photo', 'est_disponible', 'date_publication'
        ]
        read_only_fields = ['commercant', 'date_publication']
