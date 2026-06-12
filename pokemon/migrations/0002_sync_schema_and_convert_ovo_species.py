import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('pokemon', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.RenameField(
                    model_name='tipopokemon',
                    old_name='nome',
                    new_name='name',
                ),
                migrations.RenameField(
                    model_name='tipopokemon',
                    old_name='valor_base_geracao',
                    new_name='base_generation_value',
                ),
                migrations.RenameField(
                    model_name='especie',
                    old_name='nome',
                    new_name='name',
                ),
                migrations.RenameField(
                    model_name='especie',
                    old_name='estagio_evolucao',
                    new_name='evolution_stage',
                ),
                migrations.RenameField(
                    model_name='especie',
                    old_name='tipos',
                    new_name='types',
                ),
                migrations.AlterField(
                    model_name='especie',
                    name='types',
                    field=models.ManyToManyField(related_name='species', to='pokemon.tipopokemon'),
                ),
                migrations.RenameField(
                    model_name='box',
                    old_name='nome',
                    new_name='name',
                ),
                migrations.RenameField(
                    model_name='box',
                    old_name='perfil_treinador',
                    new_name='trainer_profile',
                ),
                migrations.RenameField(
                    model_name='pokemoninstancia',
                    old_name='apelido',
                    new_name='nickname',
                ),
                migrations.RenameField(
                    model_name='pokemoninstancia',
                    old_name='data_nascimento',
                    new_name='birth_date',
                ),
                migrations.RenameField(
                    model_name='pokemoninstancia',
                    old_name='especie',
                    new_name='species',
                ),
                migrations.AlterField(
                    model_name='pokemoninstancia',
                    name='box',
                    field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pokemon_instances', to='pokemon.box'),
                ),
                migrations.AlterField(
                    model_name='pokemoninstancia',
                    name='species',
                    field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='instances', to='pokemon.especie'),
                ),
                migrations.RenameField(
                    model_name='ovo',
                    old_name='nome',
                    new_name='name',
                ),
                migrations.RenameField(
                    model_name='ovo',
                    old_name='preco',
                    new_name='price',
                ),
                migrations.RenameField(
                    model_name='ovo',
                    old_name='perfil_treinador',
                    new_name='trainer_profile',
                ),
                migrations.RenameField(
                    model_name='ovo',
                    old_name='tipo',
                    new_name='type',
                ),
                migrations.AlterField(
                    model_name='ovo',
                    name='trainer_profile',
                    field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='eggs', to='accounts.perfiltreinador'),
                ),
                migrations.AlterField(
                    model_name='ovo',
                    name='type',
                    field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='eggs', to='pokemon.tipopokemon'),
                ),
                migrations.RemoveField(
                    model_name='ovo',
                    name='especie',
                ),
                migrations.AddField(
                    model_name='ovo',
                    name='species',
                    field=models.ManyToManyField(related_name='eggs', to='pokemon.especie'),
                ),
            ],
        ),
        migrations.RunSQL(
            sql='''
                CREATE TABLE IF NOT EXISTS pokemon_ovo_species (
                    id BIGSERIAL PRIMARY KEY,
                    ovo_id BIGINT NOT NULL REFERENCES pokemon_ovo(id) DEFERRABLE INITIALLY DEFERRED,
                    especie_id BIGINT NOT NULL REFERENCES pokemon_especie(id) DEFERRABLE INITIALLY DEFERRED,
                    UNIQUE (ovo_id, especie_id)
                );
            ''',
            reverse_sql='DROP TABLE IF EXISTS pokemon_ovo_species;',
        ),
        migrations.RunSQL(
            sql='''
                INSERT INTO pokemon_ovo_species (ovo_id, especie_id)
                SELECT id, species_id
                FROM pokemon_ovo
                WHERE species_id IS NOT NULL
                ON CONFLICT (ovo_id, especie_id) DO NOTHING;
            ''',
            reverse_sql='''
                UPDATE pokemon_ovo o
                SET species_id = s.especie_id
                FROM (
                    SELECT DISTINCT ON (ovo_id) ovo_id, especie_id
                    FROM pokemon_ovo_species
                    ORDER BY ovo_id, id
                ) s
                WHERE o.id = s.ovo_id;
            ''',
        ),
        migrations.RunSQL(
            sql='ALTER TABLE pokemon_ovo DROP COLUMN IF EXISTS species_id CASCADE;',
            reverse_sql='ALTER TABLE pokemon_ovo ADD COLUMN IF NOT EXISTS species_id BIGINT;',
        ),
    ]
