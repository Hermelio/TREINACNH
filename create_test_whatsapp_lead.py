"""
Script para criar um lead de teste com status CONTACTED (via WhatsApp).
Testa a contabilização de contatos WhatsApp no painel do instrutor.
"""
import os
import sys
import django
from django.utils import timezone

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treinacnh.settings')
django.setup()

from django.contrib.auth import get_user_model
from marketplace.models import Lead, InstructorProfile, LeadStatusChoices
from core.models import City

User = get_user_model()

def create_whatsapp_lead():
    """Cria um lead de teste simulando contato via WhatsApp"""
    
    # Buscar um instrutor
    try:
        instructor = InstructorProfile.objects.select_related('user').first()
        if not instructor:
            print("❌ Nenhum instrutor encontrado!")
            return
        
        print(f"✅ Instrutor encontrado: {instructor.user.get_full_name()} (ID: {instructor.id})")
    except Exception as e:
        print(f"❌ Erro ao buscar instrutor: {e}")
        return
    
    # Buscar um aluno (student)
    try:
        student = User.objects.filter(profile__role='STUDENT').first()
        if not student:
            print("⚠️  Nenhum aluno encontrado, criando lead sem usuário associado")
            student = None
        else:
            print(f"✅ Aluno encontrado: {student.get_full_name()} (ID: {student.id})")
    except Exception as e:
        print(f"⚠️  Erro ao buscar aluno: {e}, criando lead sem usuário")
        student = None
    
    # Buscar cidade do instrutor
    city = instructor.city
    if city:
        print(f"✅ Cidade: {city.name}")
    
    # Criar o lead com status CONTACTED
    try:
        lead = Lead.objects.create(
            student_user=student,
            instructor=instructor,
            city=city,
            contact_name=student.get_full_name() if student else "Teste Aluno WhatsApp",
            contact_phone="+5511999887766",
            message="Contato via WhatsApp",
            status=LeadStatusChoices.CONTACTED,
        )
        
        print(f"\n🎉 LEAD DE TESTE CRIADO COM SUCESSO!")
        print(f"   ID: {lead.id}")
        print(f"   Aluno: {lead.contact_name}")
        print(f"   Telefone: {lead.contact_phone}")
        print(f"   Instrutor: {instructor.user.get_full_name()}")
        print(f"   Status: {lead.get_status_display()}")
        print(f"   Criado em: {lead.created_at}")
        print(f"\n✅ Este lead deve aparecer no painel do instrutor em:")
        print(f"   /marketplace/meus-contatos/")
        
    except Exception as e:
        print(f"❌ Erro ao criar lead: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_whatsapp_lead()
