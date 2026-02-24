#!/usr/bin/env python3
"""
Script simples para processar imagem hero diretamente no servidor.
Não precisa de Django, apenas PIL.
"""
from PIL import Image
import os

def process_image():
    input_path = "hero-instructor-clean.jpg"
    output_dir = "static/images/hero"
    base_name = "logohome3.1"
    
    if not os.path.exists(input_path):
        print("❌ Imagem não encontrada: hero-instructor-clean.jpg")
        return False
    
    os.makedirs(output_dir, exist_ok=True)
    
    img = Image.open(input_path)
    print(f"🖼️  Processando: {img.size[0]}x{img.size[1]}")
    
    sizes = [640, 960, 1280, 1920, 2560]
    
    for width in sizes:
        ratio = width / img.size[0]
        height = int(img.size[1] * ratio)
        resized = img.resize((width, height), Image.Resampling.LANCZOS)
        
        # AVIF
        try:
            avif_path = os.path.join(output_dir, f"{base_name}-{width}w.avif")
            resized.save(avif_path, 'AVIF', quality=80)
            print(f"✅ {width}w AVIF")
        except:
            print(f"⚠️ {width}w AVIF falhou (sem suporte)")
        
        # WebP
        webp_path = os.path.join(output_dir, f"{base_name}-{width}w.webp")
        resized.save(webp_path, 'WebP', quality=85)
        print(f"✅ {width}w WebP")
        
        # PNG
        png_path = os.path.join(output_dir, f"{base_name}-{width}w.png")
        resized.save(png_path, 'PNG', optimize=True)
        print(f"✅ {width}w PNG")
    
    print("\n✅ Imagens processadas!")
    return True

if __name__ == "__main__":
    process_image()
