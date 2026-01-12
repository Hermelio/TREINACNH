#!/usr/bin/env python3
"""
Script para otimizar imagens do site:
- Converte para AVIF e WebP
- Cria versões responsivas
- Mantém PNG como fallback
"""
from PIL import Image
import os
import sys

def optimize_image(input_path, output_dir, sizes=[640, 960, 1280, 1920, 2560]):
    """Otimiza uma imagem gerando versões AVIF, WebP e responsivas"""
    
    if not os.path.exists(input_path):
        print(f"❌ Arquivo não encontrado: {input_path}")
        return
    
    # Criar diretório de saída
    os.makedirs(output_dir, exist_ok=True)
    
    # Abrir imagem original
    img = Image.open(input_path)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    
    print(f"\n🖼️  Processando: {base_name}")
    print(f"   Original: {img.size[0]}x{img.size[1]}")
    
    # Gerar versões responsivas
    for width in sizes:
        # Calcular altura proporcional
        ratio = width / img.size[0]
        height = int(img.size[1] * ratio)
        
        # Redimensionar
        resized = img.resize((width, height), Image.Resampling.LANCZOS)
        
        # AVIF (melhor compressão)
        avif_path = os.path.join(output_dir, f"{base_name}-{width}w.avif")
        try:
            resized.save(avif_path, 'AVIF', quality=80)
            size_kb = os.path.getsize(avif_path) / 1024
            print(f"   ✅ {width}w AVIF: {size_kb:.1f}KB")
        except Exception as e:
            print(f"   ⚠️  AVIF falhou (instale pillow-avif-plugin): {e}")
        
        # WebP (boa compressão)
        webp_path = os.path.join(output_dir, f"{base_name}-{width}w.webp")
        resized.save(webp_path, 'WebP', quality=85, method=6)
        size_kb = os.path.getsize(webp_path) / 1024
        print(f"   ✅ {width}w WebP: {size_kb:.1f}KB")
        
        # PNG otimizado (fallback)
        png_path = os.path.join(output_dir, f"{base_name}-{width}w.png")
        resized.save(png_path, 'PNG', optimize=True)
        size_kb = os.path.getsize(png_path) / 1024
        print(f"   ✅ {width}w PNG: {size_kb:.1f}KB")
    
    print(f"✅ Concluído: {base_name}")

if __name__ == "__main__":
    base_dir = "static/images"
    
    # Otimizar imagens principais
    images_to_optimize = [
        ("static/images/logohome3.png", "static/images/hero"),
        ("static/images/background-site.png", "static/images/backgrounds"),
        ("static/images/logotipoTreinaCNH.png", "static/images/logos"),
    ]
    
    print("🚀 Iniciando otimização de imagens...")
    print("=" * 60)
    
    for input_path, output_dir in images_to_optimize:
        optimize_image(input_path, output_dir)
    
    print("\n" + "=" * 60)
    print("✅ Otimização concluída!")
    print("\n📝 Próximos passos:")
    print("1. Atualizar templates para usar <picture> com srcset")
    print("2. Adicionar preload no <head>")
    print("3. Configurar Nginx para cache e compressão")
