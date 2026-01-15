# Generated migration for scheduling system

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('marketplace', '0009_add_instructor_statistics'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='category',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='leads',
                to='marketplace.categorycnh',
                verbose_name='Categoria CNH Desejada'
            ),
        ),
        migrations.AlterField(
            model_name='lead',
            name='status',
            field=models.CharField(
                choices=[
                    ('NEW', 'Novo'),
                    ('CONTACTED', 'Contatado'),
                    ('SCHEDULED', 'Agendado'),
                    ('COMPLETED', 'Aulas Finalizadas'),
                    ('CLOSED', 'Fechado'),
                    ('SPAM', 'Spam')
                ],
                default='NEW',
                max_length=20,
                verbose_name='Status'
            ),
        ),
        migrations.CreateModel(
            name='InstructorAvailability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weekday', models.IntegerField(
                    choices=[
                        (0, 'Segunda-feira'),
                        (1, 'Terça-feira'),
                        (2, 'Quarta-feira'),
                        (3, 'Quinta-feira'),
                        (4, 'Sexta-feira'),
                        (5, 'Sábado'),
                        (6, 'Domingo')
                    ],
                    help_text='0=Segunda, 6=Domingo',
                    verbose_name='Dia da Semana'
                )),
                ('start_time', models.TimeField(verbose_name='Horário Inicial')),
                ('end_time', models.TimeField(verbose_name='Horário Final')),
                ('is_active', models.BooleanField(default=True, verbose_name='Ativo')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('instructor', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='availabilities',
                    to='marketplace.instructorprofile',
                    verbose_name='Instrutor'
                )),
            ],
            options={
                'verbose_name': 'Disponibilidade do Instrutor',
                'verbose_name_plural': 'Disponibilidades dos Instrutores',
                'ordering': ['weekday', 'start_time'],
                'unique_together': {('instructor', 'weekday', 'start_time')},
                'indexes': [
                    models.Index(fields=['instructor', 'weekday', 'is_active'], name='marketplace_instru_weekday_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appointment_date', models.DateField(verbose_name='Data da Aula')),
                ('start_time', models.TimeField(verbose_name='Horário Inicial')),
                ('end_time', models.TimeField(verbose_name='Horário Final')),
                ('duration_hours', models.DecimalField(
                    decimal_places=1,
                    default=1.0,
                    help_text='Duração da aula em horas',
                    max_digits=3,
                    verbose_name='Duração (horas)'
                )),
                ('is_confirmed', models.BooleanField(default=False, verbose_name='Confirmado')),
                ('is_completed', models.BooleanField(default=False, verbose_name='Concluído')),
                ('is_cancelled', models.BooleanField(default=False, verbose_name='Cancelado')),
                ('cancellation_reason', models.TextField(blank=True, verbose_name='Motivo do Cancelamento')),
                ('notes', models.TextField(blank=True, help_text='Observações sobre a aula', verbose_name='Observações')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('instructor', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='appointments',
                    to='marketplace.instructorprofile',
                    verbose_name='Instrutor'
                )),
                ('lead', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='appointments',
                    to='marketplace.lead',
                    verbose_name='Lead'
                )),
                ('student_user', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='appointments',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Aluno'
                )),
            ],
            options={
                'verbose_name': 'Agendamento',
                'verbose_name_plural': 'Agendamentos',
                'ordering': ['appointment_date', 'start_time'],
                'indexes': [
                    models.Index(fields=['instructor', 'appointment_date'], name='marketplace_instru_appt_idx'),
                    models.Index(fields=['student_user', 'appointment_date'], name='marketplace_student_appt_idx'),
                    models.Index(fields=['is_confirmed', 'is_cancelled'], name='marketplace_appt_status_idx'),
                ],
            },
        ),
    ]
