"""
Management command to activate the "Instrutor Pioneiro" benefit.

REGRA ABSOLUTA: O benefício é aplicado SOMENTE para os nomes desta lista fechada.
Nenhum outro instrutor, antigo ou futuro, recebe o benefício automaticamente.

Usage:
    python manage.py activate_pioneers          # dry-run   (apenas mostra o que faria)
    python manage.py activate_pioneers --apply  # aplica as mudanças
"""
from datetime import timedelta, date

from django.core.management.base import BaseCommand
from django.utils import timezone

from marketplace.models import InstructorProfile


# -------------------------------------------------------------------------
# LISTA FECHADA — NÃO altere sem aprovação explícita do time.
# -------------------------------------------------------------------------
PIONEER_NAMES = [
    "Juliano Rosa de Oliveira",
    "Dalmo Santos Monteiro",
    "Cleo Roberto Elibio Roldão",
    "Lauri Luiz Ribeiro Ferreira",
    "Rodrigo Alves de Mello Ribeiro",
    "Leonardo de Oliveira",
    "Merilyn Kelly de Moraes Zanini",
    "Humberto Carloa Rosinholo",
    "Paulo Kazuhiro Handa",
    "Edimar de Souza",
    "Alessandro Tiago de Barros",
    "Diogo Ricardo Sampietri",
    "Anderson Guimarães",
]

# Normalize once for fast comparison
PIONEER_NAMES_NORMALIZED = {n.strip().casefold() for n in PIONEER_NAMES}

PIONEER_DAYS = 60


class Command(BaseCommand):
    help = (
        "Ativa o benefício 'Instrutor Pioneiro' SOMENTE para a lista fechada de nomes. "
        "Por padrão executa em dry-run (--apply para persistir)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply',
            action='store_true',
            default=False,
            help='Aplica as mudanças no banco. Sem esta flag, roda em dry-run.',
        )

    # ------------------------------------------------------------------
    def handle(self, *args, **options):
        apply = options['apply']
        today = timezone.now().date()
        free_until = today + timedelta(days=PIONEER_DAYS)

        self.stdout.write(self.style.HTTP_INFO(
            f"\n{'=' * 60}\n"
            f"  Ativação de Instrutores Pioneiros\n"
            f"  Modo: {'APLICAR' if apply else 'DRY-RUN (use --apply para persistir)'}\n"
            f"  Pioneiros na lista: {len(PIONEER_NAMES)}\n"
            f"  Plano gratuito até: {free_until}\n"
            f"{'=' * 60}\n"
        ))

        # Track which names from the list were matched
        matched_names: set[str] = set()
        activated = 0
        already_pioneer = 0
        skipped_not_list = 0

        # Iterate over ALL InstructorProfiles — we verify role via profile existence
        for profile in InstructorProfile.objects.select_related('user').iterator():
            full_name = profile.user.get_full_name().strip()
            normalized = full_name.casefold()

            if normalized not in PIONEER_NAMES_NORMALIZED:
                skipped_not_list += 1
                continue

            # --- Name matched ---
            matched_names.add(normalized)

            if profile.is_pioneer:
                # Already a pioneer — check date (never reduce)
                if profile.pioneer_free_until and profile.pioneer_free_until >= free_until:
                    self.stdout.write(
                        f"  [OK] {full_name} — já é pioneiro até {profile.pioneer_free_until} (não alterado)"
                    )
                    already_pioneer += 1
                else:
                    # Extend / set date
                    if apply:
                        profile.pioneer_free_until = free_until
                        profile.save(update_fields=['pioneer_free_until'])
                    self.stdout.write(self.style.SUCCESS(
                        f"  [{'ATUALIZADO' if apply else 'SIMULADO'}] {full_name} — "
                        f"pioneer_free_until → {free_until}"
                    ))
                    activated += 1
            else:
                # Activate pioneer
                if apply:
                    profile.is_pioneer = True
                    profile.pioneer_free_until = free_until
                    profile.save(update_fields=['is_pioneer', 'pioneer_free_until'])
                self.stdout.write(self.style.SUCCESS(
                    f"  [{'ATIVADO' if apply else 'SIMULADO'}] {full_name} — "
                    f"is_pioneer=True, pioneer_free_until={free_until}"
                ))
                activated += 1

        # --- Report names from list NOT found in the DB ---
        not_found = []
        for original_name in PIONEER_NAMES:
            if original_name.strip().casefold() not in matched_names:
                not_found.append(original_name)

        self.stdout.write('\n' + '-' * 60)
        self.stdout.write(f"  Encontrados e processados : {len(matched_names)}")
        self.stdout.write(f"  Ativados / atualizados    : {activated}")
        self.stdout.write(f"  Já eram pioneiros (ok)    : {already_pioneer}")
        self.stdout.write(f"  Ignorados (fora da lista) : {skipped_not_list}")

        if not_found:
            self.stdout.write(self.style.WARNING(
                f"\n  ⚠️  {len(not_found)} nome(s) da lista NÃO encontrados no banco:"
            ))
            for name in not_found:
                self.stdout.write(self.style.WARNING(f"      - {name}"))
            self.stdout.write(self.style.WARNING(
                "  Verifique se o nome foi cadastrado de outra forma (acentuação, abreviação, etc.)."
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                "\n  ✅ Todos os nomes da lista foram encontrados no banco."
            ))

        self.stdout.write('-' * 60)

        if not apply:
            self.stdout.write(self.style.HTTP_INFO(
                "\n  ℹ️  DRY-RUN concluído. Nenhum dado foi alterado.\n"
                "  Para aplicar: python manage.py activate_pioneers --apply\n"
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                "\n  ✅ Benefícios aplicados com sucesso.\n"
            ))
