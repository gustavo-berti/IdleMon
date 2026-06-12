from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('pokemon', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OvoInventario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantidade', models.PositiveIntegerField(default=1)),
                ('ovo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inventarios', to='pokemon.ovo')),
                ('trainer_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ovo_inventario', to='accounts.perfiltreinador')),
            ],
            options={
                'unique_together': {('trainer_profile', 'ovo')},
            },
        ),
    ]