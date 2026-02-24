#!/usr/bin/env python3
"""
Script para processar a nova imagem do hero sem logos de terceiros.
"""
from PIL import Image
import os

def process_hero_image():
    """Processa a nova imagem do hero"""
    
    # A imagem está no workspace como attachment
    # Precisamos usar o caminho correto
    input_path = "hero-instructor-clean.jpg"
    output_dir = "static/images/hero"
    base_name = "logohome3.1"
    
    if not os.path.exists(input_path):
        print(f"❌ Imagem não encontrada: {input_path}")
        print("⚠️  Por favor, salve a imagem anexada como 'hero-instructor-clean.jpg' no diretório raiz do projeto")
        return False
    
    os.makedirs(output_dir, exist_ok=True)
    
    img = Image.open(input_path)
    print(f"\n🖼️  Processando nova imagem hero")
    print(f"   Original: {img.size[0]}x{img.size[1]}")
    
    # Salvar versão original
    original_path = os.path.join(output_dir, f"{base_name}-original.png")
    img.save(original_path, 'PNG', quality=100)
    print(f"   ✅ Original salvo: {original_path}")
    
    # Tamanhos para responsividade
    sizes = [640, 960, 1280, 1920, 2560]
    
    for width in sizes:
        ratio = width / img.size[0]
        height = int(img.size[1] * ratio)
        resized = img.resize((width, height), Image.Resampling.LANCZOS)
        
        # AVIF
        avif_path = os.path.join(output_dir, f"{base_name}-{width}w.avif")
        try:
            resized.save(avif_path, 'AVIF', quality=80)
            size_kb = os.path.getsize(avif_path) / 1024
            print(f"   ✅ {width}w AVIF: {size_kb:.1f}KB")
        except Exception as e:
            print(f"   ⚠️  AVIF falhou: {e}")
        
        # WebP
        webp_path = os.path.join(output_dir, f"{base_name}-{width}w.webp")
        resized.save(webp_path, 'WebP', quality=85, method=6)
        size_kb = os.path.getsize(webp_path) / 1024
        print(f"   ✅ {width}w WebP: {size_kb:.1f}KB")
        
        # PNG (fallback)
        png_path = os.path.join(output_dir, f"{base_name}-{width}w.png")
        resized.save(png_path, 'PNG', optimize=True)
        size_kb = os.path.getsize(png_path) / 1024
        print(f"   ✅ {width}w PNG: {size_kb:.1f}KB")
    
    print(f"\n✅ Imagens processadas com sucesso em: {output_dir}")
    print(f"\n📋 Próximos passos:")
    print(f"   1. Verifique as imagens geradas")
    print(f"   2. Execute: scp -r static/images/hero/logohome3.1-* root@72.61.36.89:/var/www/TREINACNH/static/images/hero/")
    print(f"   3. Reinicie o servidor")
    
    return True

if __name__ == "__main__":
    print("=" * 70)
    print("PROCESSAMENTO DE IMAGEM HERO - SEM LOGOS DE TERCEIROS")
    print("=" * 70)
    
    # Instruções para o usuário
    print("\n📝 INSTRUÇÕES:")
    print("   1. Salve a imagem anexada como 'hero-instructor-clean.jpg' no diretório raiz")
    print("   2. Execute este script novamente")
    print()
    
    if process_hero_image():
        print("\n" + "=" * 70)
        print("✅ PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("❌ ERRO NO PROCESSAMENTO")
        print("=" * 70)
