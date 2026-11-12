from pathlib import Path
from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIClient
from urllib.parse import unquote

from .models import Message, ProfilCommercant, Produit, User


class CommercantFlowTests(TestCase):
	def setUp(self):
		self.registration_data = {
			'action': 'inscription',
			'username': 'boutique_test',
			'password': 'UnMotDePasseSolide123!',
			'nom': 'Ndayizeye',
			'prenom': 'Aline',
			'nom_boutique': 'Boutique Test',
			'nif': 'NIF-TEST-1',
			'ville_ou_province': 'Bujumbura',
			'commune': 'Mukaza',
			'quartier': 'Rohero',
			'avenue_ou_rue': 'Avenue Test',
			'point_de_repere': 'Pres du marche',
			'telephone': '+25779123456',
			'type_produits': 'Mode',
		}

	def test_registration_creates_pending_profile_without_user_access(self):
		response = self.client.post('/connexion-commercant/', self.registration_data)

		self.assertRedirects(response, '/connexion-commercant/')
		profile = ProfilCommercant.objects.get(nif='NIF-TEST-1')
		self.assertIsNone(profile.user)
		self.assertFalse(User.objects.filter(username='boutique_test').exists())
		self.assertNotIn('_auth_user_id', self.client.session)

	def test_commercant_sees_only_own_products(self):
		owner = User.objects.create_user(username='owner', password='password123', is_commercant=True)
		other = User.objects.create_user(username='other', password='password123', is_commercant=True)
		owner_profile = self._create_profile(owner, 'NIF-OWNER')
		other_profile = self._create_profile(other, 'NIF-OTHER')
		own_product = Produit.objects.create(commercant=owner_profile, nom='Produit personnel', prix=100)
		other_product = Produit.objects.create(commercant=other_profile, nom='Produit autre', prix=200)
		self.client.force_login(owner)

		response = self.client.get('/commercant/')

		self.assertContains(response, own_product.nom)
		self.assertNotContains(response, other_product.nom)
		forbidden_delete = self.client.post('/commercant/', {
			'action': 'supprimer_produit',
			'produit_id': other_product.id,
		})
		self.assertEqual(forbidden_delete.status_code, 404)

	def test_commercant_can_edit_own_product_details(self):
		owner = User.objects.create_user(username='editor', password='password123', is_commercant=True)
		other = User.objects.create_user(username='other_editor', password='password123', is_commercant=True)
		owner_profile = self._create_profile(owner, 'NIF-EDITOR')
		other_profile = self._create_profile(other, 'NIF-OTHER-EDITOR')
		product = Produit.objects.create(commercant=owner_profile, nom='Ancien nom', prix=100, description='Ancienne description')

		self.client.force_login(owner)
		response = self.client.post('/commercant/', {
			'action': 'modifier_produit',
			'produit_id': product.id,
			'nom': 'Nouveau nom',
			'prix': '250.50',
			'description': 'Nouvelle description',
		})

		self.assertRedirects(response, '/commercant/')
		product.refresh_from_db()
		self.assertEqual(product.nom, 'Nouveau nom')
		self.assertEqual(str(product.prix), '250.50')
		self.assertEqual(product.description, 'Nouvelle description')

		self.client.force_login(other)
		forbidden_edit = self.client.post('/commercant/', {
			'action': 'modifier_produit',
			'produit_id': product.id,
			'nom': 'Modification interdite',
			'prix': '1',
			'description': 'Modification interdite',
		})
		self.assertEqual(forbidden_edit.status_code, 404)

	def test_client_message_is_saved_and_prepared_for_whatsapp(self):
		user = User.objects.create_user(username='seller', password='password123', is_commercant=True)
		profile = self._create_profile(user, 'NIF-WHATSAPP')
		product = Produit.objects.create(commercant=profile, nom='Sac artisanal', prix=25000)

		response = self.client.post('/messages/envoyer/', {
			'produit_id': product.id,
			'nom_client': 'Aline',
			'contact_client': '+257 71 234 567',
			'contenu': 'Je voudrais connaître la disponibilité.',
		})

		self.assertEqual(response.status_code, 302)
		self.assertIn('https://wa.me/25779123456?text=', response['Location'])
		self.assertEqual(Message.objects.count(), 1)
		self.assertIn('Sac artisanal', unquote(response['Location']))

	def test_demo_catalog_uses_all_unique_local_product_photos(self):
		response = self.client.get('/site/')

		self.assertEqual(response.status_code, 200)
		produits_demo = response.context['produits_demo']
		self.assertEqual(len(produits_demo), 21)
		photos = [produit['photo'] for produit in produits_demo]
		self.assertEqual(len(photos), len(set(photos)))
		for photo in photos:
			with self.subTest(photo=photo):
				self.assertTrue(
					(Path(settings.MEDIA_ROOT) / 'produits_photos' / unquote(photo)).is_file()
				)

	def test_commercant_api_is_readable_but_writes_require_staff(self):
		profile = self._create_profile(
			User.objects.create_user(username='api_seller', password='password123', is_commercant=True),
			'NIF-API',
		)
		client = APIClient()

		self.assertEqual(client.get('/api/commercant/').status_code, 200)
		self.assertEqual(client.delete(f'/api/commercant/{profile.id}/').status_code, 403)

		staff = User.objects.create_user(username='api_staff', password='password123', is_staff=True)
		client.force_authenticate(user=staff)
		self.assertEqual(client.delete(f'/api/commercant/{profile.id}/').status_code, 204)
		self.assertFalse(ProfilCommercant.objects.filter(pk=profile.id).exists())

	def _create_profile(self, user, nif):
		return ProfilCommercant.objects.create(
			user=user,
			nom='Nom',
			prenom='Prenom',
			nom_boutique=user.username,
			nif=nif,
			commune='Mukaza',
			quartier='Rohero',
			avenue_ou_rue='Avenue Test',
			point_de_repere='Marche',
			telephone='+25779123456',
			type_produits='Mode',
		)
