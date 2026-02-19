# Generated migration for adding instructor statistics

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0007_remove_studentlead_accept_marketing_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lead',
            name='status',
            field=models.CharField(
                choices=[
                    ('NEW', 'Novo'),
                    ('CONTACTED', 'Contatado'),
                    ('COMPLETED', 'Aulas Finalizadas'),
                    ('CLOSED', 'Fechado'),
                    ('SPAM', 'Spam')
                ],
                default='NEW',
                max_length=20,
                verbose_name='Status'
            ),
        ),
        migrations.AddField(
            model_name='instructorprofile',
            name='total_students',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Número de alunos que finalizaram aulas',
                verbose_name='Total de Alunos'
            ),
        ),
        migrations.AddField(
            model_name='instructorprofile',
            name='average_rating',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Média de avaliações (1.00 a 5.00)',
                max_digits=3,
                null=True,
                verbose_name='Média de Avaliações'
            ),
        ),
        migrations.AddField(
            model_name='instructorprofile',
            name='total_reviews',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Número total de avaliações recebidas',
                verbose_name='Total de Avaliações'
            ),
        ),
    ]
