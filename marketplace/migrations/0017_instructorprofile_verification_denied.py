# Add verification_denied and verification_denied_at to InstructorProfile

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0016_pioneer_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='instructorprofile',
            name='verification_denied',
            field=models.BooleanField(
                'Verificação Negada',
                default=False,
                help_text='Admin marcou verificação como não autorizada pelo Detran',
            ),
        ),
        migrations.AddField(
            model_name='instructorprofile',
            name='verification_denied_at',
            field=models.DateTimeField(
                'Data da Negação',
                null=True,
                blank=True,
                help_text='Data e hora em que a verificação foi negada pelo admin',
            ),
        ),
    ]
