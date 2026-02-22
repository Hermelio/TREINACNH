# Add ibge_id to City model for reliable IBGE deduplication

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0014_seed_cnh_categories'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='ibge_id',
            field=models.IntegerField(
                'Código IBGE',
                null=True,
                blank=True,
                unique=True,
                help_text='Código do município no IBGE (7 dígitos)',
            ),
        ),
        migrations.AddIndex(
            model_name='city',
            index=models.Index(fields=['ibge_id'], name='marketplace_ibge_id_city_idx'),
        ),
    ]
