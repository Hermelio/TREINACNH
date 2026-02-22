# Expand CategoryCNH.code to support multi-char codes (AB, AC, AD, AE, ACC, etc.)
# Also add sort_order field for consistent display ordering everywhere.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0012_citygeocache'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categorycnh',
            name='code',
            field=models.CharField(
                'Código',
                max_length=5,
                unique=True,
                help_text='Código oficial da categoria CNH (ex: A, B, AB, ACC)',
            ),
        ),
        migrations.AddField(
            model_name='categorycnh',
            name='sort_order',
            field=models.PositiveSmallIntegerField(
                'Ordem de exibição',
                default=99,
                help_text='Menor número = exibido primeiro',
            ),
        ),
        migrations.AlterModelOptions(
            name='categorycnh',
            options={
                'ordering': ['sort_order', 'code'],
                'verbose_name': 'Categoria CNH',
                'verbose_name_plural': 'Categorias CNH',
            },
        ),
    ]
