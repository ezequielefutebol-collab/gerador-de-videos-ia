"""
Provedor de visuais: busca imagens do Pexels ou gera imagens localmente com PIL.
"""
import os
import sys
import json
import hashlib
import requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config

CACHE_DIR = Path("/tmp/visuais_cache")
CACHE_DIR.mkdir(exist_ok=True)


# Paleta de cores para gradientes por tipo de cena
PALETTES = {
    "gancho":      [(20, 10, 5), (60, 30, 10)],
    "ingredientes": [(10, 30, 20), (30, 80, 50)],
    "preparacao":  [(25, 15, 5), (70, 40, 15)],
    "processo":    [(30, 10, 5), (90, 40, 10)],
    "detalhe":     [(15, 10, 5), (50, 30, 10)],
    "finalizacao": [(20, 10, 5), (60, 25, 10)],
    "resultado":   [(10, 5, 2), (40, 15, 5)],
    "encerramento":[(5, 5, 10), (20, 20, 40)],
}

DEFAULT_PALETTE = [(10, 10, 10), (40, 20, 5)]


def _cache_key(query: str) -> str:
    return hashlib.md5(query.encode()).hexdigest()


def buscar_pexels_foto(query: str, width=1080, height=1920) -> str | None:
    """Busca uma foto no Pexels e salva em cache."""
    if not config.PEXELS_API_KEY:
        return None

    cache_file = CACHE_DIR / f"pexels_{_cache_key(query)}.jpg"
    if cache_file.exists():
        return str(cache_file)

    try:
        headers = {"Authorization": config.PEXELS_API_KEY}
        params = {"query": query, "per_page": 5, "orientation": "portrait"}
        resp = requests.get(
            "https://api.pexels.com/v1/search",
            headers=headers, params=params, timeout=10
        )
        data = resp.json()

        if data.get("photos"):
            foto = data["photos"][0]
            url = foto["src"].get("portrait") or foto["src"]["large2x"]
            img_data = requests.get(url, timeout=15).content
            with open(cache_file, "wb") as f:
                f.write(img_data)
            return str(cache_file)
    except Exception as e:
        print(f"[Pexels] Erro: {e}")

    return None


def gerar_fundo_cinematografico(tipo_cena: str, width=1080, height=1920) -> Image.Image:
    """Gera um fundo escuro cinematográfico com gradiente e textura."""
    palette = PALETTES.get(tipo_cena, DEFAULT_PALETTE)
    c1, c2 = palette

    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)

    # Gradiente vertical suave
    for y in range(height):
        t = y / height
        r = int(c1[0] + (c2[0] - c1[0]) * t)
        g = int(c1[1] + (c2[1] - c1[1]) * t)
        b = int(c1[2] + (c2[2] - c1[2]) * t)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Adiciona granulado sutil para textura cinematográfica
    arr = np.array(img, dtype=np.int16)
    noise = np.random.randint(-8, 9, arr.shape, dtype=np.int16)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr)

    # Vinheta nas bordas (escurece bordas)
    vignette = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    vdraw = ImageDraw.Draw(vignette)
    steps = 120
    for i in range(steps):
        alpha = int(180 * (1 - i/steps)**2)
        margin = i * 4
        vdraw.rectangle(
            [margin, margin, width-margin, height-margin],
            outline=(0, 0, 0, alpha)
        )
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, vignette).convert("RGB")

    return img


def aplicar_foto_na_cena(foto_path: str, width=1080, height=1920) -> Image.Image:
    """Aplica a foto com crop inteligente e overlay cinematográfico."""
    foto = Image.open(foto_path).convert("RGB")

    # Crop central para 9:16
    fw, fh = foto.size
    target_ratio = width / height
    foto_ratio = fw / fh

    if foto_ratio > target_ratio:
        # Foto mais larga: crop nos lados
        new_w = int(fh * target_ratio)
        x0 = (fw - new_w) // 2
        foto = foto.crop((x0, 0, x0 + new_w, fh))
    else:
        # Foto mais alta: crop em cima/baixo
        new_h = int(fw / target_ratio)
        y0 = (fh - new_h) // 2
        foto = foto.crop((0, y0, fw, y0 + new_h))

    foto = foto.resize((width, height), Image.LANCZOS)

    # Overlay escuro na parte inferior (onde fica a legenda)
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)

    # Gradiente escuro embaixo
    for y in range(height//2, height):
        t = (y - height//2) / (height//2)
        alpha = int(160 * t**1.5)
        odraw.line([(0, y), (width, y)], fill=(0, 0, 0, alpha))

    # Vinheta lateral
    for i in range(80):
        alpha = int(100 * (1 - i/80)**1.5)
        odraw.line([(i, 0), (i, height)], fill=(0, 0, 0, alpha))
        odraw.line([(width-i, 0), (width-i, height)], fill=(0, 0, 0, alpha))

    foto = foto.convert("RGBA")
    foto = Image.alpha_composite(foto, overlay).convert("RGB")

    # Boost de saturação e contraste leve
    from PIL import ImageEnhance
    foto = ImageEnhance.Contrast(foto).enhance(1.15)
    foto = ImageEnhance.Color(foto).enhance(1.2)

    return foto


def obter_visual_cena(tipo_cena: str, busca_visual: str, indice: int = 0) -> Image.Image:
    """Obtém o visual para uma cena: Pexels ou gerado localmente."""
    w, h = config.VIDEO_WIDTH, config.VIDEO_HEIGHT

    # Tenta Pexels primeiro
    foto_path = buscar_pexels_foto(busca_visual, w, h)
    if foto_path:
        try:
            return aplicar_foto_na_cena(foto_path, w, h)
        except Exception as e:
            print(f"[Visual] Erro ao processar foto: {e}")

    # Fallback: fundo gerado
    return gerar_fundo_cinematografico(tipo_cena, w, h)


def gerar_frame_ingredientes(ingredientes: list, width=1080, height=1920) -> Image.Image:
    """Gera um frame visual mostrando lista de ingredientes."""
    img = gerar_fundo_cinematografico("ingredientes", width, height)
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype(config.FONT_BOLD, 70)
        font_item = ImageFont.truetype(config.FONT_REGULAR, 46)
        font_qty = ImageFont.truetype(config.FONT_BOLD, 46)
    except:
        font_title = font_item = font_qty = ImageFont.load_default()

    # Título
    draw.text((width//2, 200), "INGREDIENTES", font=font_title,
              fill=(255, 220, 50), anchor="mm")

    # Linha decorativa
    draw.rectangle([80, 250, width-80, 255], fill=(255, 220, 50, 180))

    # Lista de ingredientes
    y = 320
    for i, ing in enumerate(ingredientes[:10]):
        bullet = "•"
        item = ing.get("item", "").capitalize()
        qty = ing.get("quantidade", "")

        # Bullet colorido
        draw.text((90, y), bullet, font=font_item, fill=(255, 180, 30))
        # Item
        draw.text((130, y), item, font=font_item, fill=(255, 255, 255))
        # Quantidade (alinhada à direita)
        draw.text((width-90, y), qty, font=font_qty, fill=(255, 220, 100), anchor="ra")

        y += 72
        if y > height - 200:
            break

    return img
