import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def rename_balance_column_if_needed(apps, schema_editor):
    table_name = 'accounts_perfiltreinador'
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        columns = {
            col.name
            for col in connection.introspection.get_table_description(cursor, table_name)
        }

    if 'saldo_moedas' in columns and 'coin_balance' not in columns:
        schema_editor.execute(
            f'ALTER TABLE "{table_name}" RENAME COLUMN "saldo_moedas" TO "coin_balance"'
        )


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(rename_balance_column_if_needed, migrations.RunPython.noop),
            ],
            state_operations=[
                migrations.RenameField(
                    model_name='perfiltreinador',
                    old_name='saldo_moedas',
                    new_name='coin_balance',
                ),
                migrations.AlterField(
                    model_name='perfiltreinador',
                    name='user',
                    field=models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='trainer_profile',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
