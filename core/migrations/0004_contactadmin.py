from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_produit_photo'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactAdmin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=120)),
                ('contact', models.CharField(max_length=120)),
                ('sujet', models.CharField(max_length=180)),
                ('contenu', models.TextField()),
                ('date_envoi', models.DateTimeField(auto_now_add=True)),
                ('est_traite', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Contact administrateur',
                'verbose_name_plural': 'Contacts administrateurs',
                'ordering': ['-date_envoi'],
            },
        ),
    ]
