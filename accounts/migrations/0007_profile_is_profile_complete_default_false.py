# Generated manually 2026-02-20
# Changes default from True → False.
# Data migration: explicitly marks all pre-existing profiles as complete
# so no one is forced through the role-selection screen after deploy.

from django.db import migrations, models


def mark_existing_profiles_complete(apps, schema_editor):
    """All profiles that existed before this migration already chose a role
    (either via registration form or via the adapter default).
    Lock them in as complete so only brand-new OAuth users get False."""
    Profile = apps.get_model('accounts', 'Profile')
    Profile.objects.filter(is_profile_complete=False).update(is_profile_complete=True)


def reverse_noop(apps, schema_editor):
    pass  # No meaningful undo for a data backfill


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_profile_is_profile_complete'),
    ]

    operations = [
        # 1. Bulk-update existing rows first (while default is still True in DB)
        migrations.RunPython(mark_existing_profiles_complete, reverse_noop),

        # 2. Now change the column default to False
        migrations.AlterField(
            model_name='profile',
            name='is_profile_complete',
            field=models.BooleanField(
                default=False,
                help_text='Usuário informou se é aluno ou instrutor. False para novos usuários via Google.',
                verbose_name='Cadastro Completo',
            ),
        ),
    ]
