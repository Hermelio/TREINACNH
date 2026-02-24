# Add is_pioneer and pioneer_free_until to InstructorProfile (closed-list benefit)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0015_city_ibge_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='instructorprofile',
            name='is_pioneer',
            field=models.BooleanField(
                'Instrutor Pioneiro',
                default=False,
                db_index=True,
                help_text='Concedido manualmente a instrutores pioneiros cadastrados na lista fechada',
            ),
        ),
        migrations.AddField(
            model_name='instructorprofile',
            name='pioneer_free_until',
            field=models.DateField(
                'Plano Grátis até (Pioneiro)',
                null=True,
                blank=True,
                help_text='Data até a qual o pioneiro possui plano gratuito (60 dias)',
            ),
        ),
        migrations.AddIndex(
            model_name='instructorprofile',
            index=models.Index(fields=['is_pioneer'], name='marketplace_pioneer_idx'),
        ),
    ]
