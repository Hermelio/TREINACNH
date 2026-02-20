# Generated manually 2026-02-20
# Adds cnh_categories ManyToManyField to accounts.Profile

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_profile_is_profile_complete_default_false'),
        ('marketplace', '0010_scheduling_system'),   # latest marketplace migration; CategoryCNH defined in 0001
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='cnh_categories',
            field=models.ManyToManyField(
                blank=True,
                help_text='Categorias de CNH que o aluno deseja obter',
                related_name='student_profiles',
                to='marketplace.categorycnh',
                verbose_name='Categorias CNH de Interesse',
            ),
        ),
    ]
