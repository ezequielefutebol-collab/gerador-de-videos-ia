"""
Provedor de visuais com integração completa ao Pexels.

Com PEXELS_API_KEY:
  - Busca fotos e vídeos reais de alta qualidade
  - Múltiplas tentativas com queries alternativas
  - Extração de frames de vídeos Pexels para cenas dinâmicas
  - Cache persistente em disco

Sem PEXELS_API_KEY:
  - Fundos cinematográficos gerados localmente com PIL
"""
import os
import sys
import hashlib
import subprocess
import requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config

CACHE_DIR = Path("/tmp/visuais_cache")
CACHE_DIR.mkdir(exist_ok=True)

W = config.VIDEO_WIDTH
H = config.VIDEO_HEIGHT

# ─────────────────────────────────────────────────────────────
# Paletas de fundo para fallback
# ─────────────────────────────────────────────────────────────
PALETTES = {
    "gancho":       [(18, 8, 3),  (55, 25, 8)],
    "ingredientes": [(8, 25, 15), (25, 70, 40)],
    "preparacao":   [(22, 12, 4), (65, 35, 12)],
    "processo":     [(28, 8, 3),  (85, 35, 8)],
    "detalhe":      [(12, 8, 3),  (45, 25, 8)],
    "finalizacao":  [(18, 8, 3),  (55, 20, 8)],
    "resultado":    [(8, 4, 2),   (35, 12, 4)],
    "encerramento": [(4, 4, 8),   (18, 18, 35)],
}
DEFAULT_PALETTE = [(8, 8, 8), (35, 18, 4)]

# ─────────────────────────────────────────────────────────────
# Queries alternativas por tipo de cena (fallback progressivo)
# ─────────────────────────────────────────────────────────────
QUERIES_FALLBACK = {
    "gancho":       ["food photography close up", "gourmet dish", "restaurant food"],
    "ingredientes": ["fresh ingredients kitchen", "cooking ingredients flat lay", "fresh vegetables herbs"],
    "preparacao":   ["chef knife cutting", "food preparation kitchen", "cooking prep"],
    "processo":     ["cooking pan stove", "chef cooking kitchen", "food cooking fire"],
    "detalhe":      ["food texture close up", "cooking detail macro", "food macro photography"],
    "finalizacao":  ["food plating chef", "cooking finishing dish", "gourmet plating"],
    "resultado":    ["beautiful food plate", "gourmet food photography", "restaurant dish"],
    "encerramento": ["delicious food closeup", "food fork bite", "food table served"],
}


def _chave_cache(texto: str) -> str:
    return hashlib.md5(texto.encode()).hexdigest()[:16]


# ─────────────────────────────────────────────────────────────
# PEXELS — FOTOS
# ─────────────────────────────────────────────────────────────

def _pexels_headers() -> dict:
    return {"Authorization": config.PEXELS_API_KEY}


def buscar_pexels_foto(query: str, indice: int = 0) -> str | None:
    """
    Busca foto no Pexels para a query dada.
    Retorna caminho local do arquivo JPG em cache, ou None.
    indice permite variar a foto para cenas diferentes com a mesma query.
    """
    if not config.PEXELS_API_KEY:
        return None

    cache_key = _chave_cache(f"{query}_{indice}")
    cache_file = CACHE_DIR / f"foto_{cache_key}.jpg"
    if cache_file.exists() and cache_file.stat().st_size > 5000:
        return str(cache_file)

    try:
        resp = requests.get(
            "https://api.pexels.com/v1/search",
            headers=_pexels_headers(),
            params={"query": query, "per_page": 15, "orientation": "portrait"},
            timeout=12
        )
        if resp.status_code != 200:
            print(f"[Pexels Foto] HTTP {resp.status_code} para: {query}")
            return None

        fotos = resp.json().get("photos", [])
        if not fotos:
            return None

        # Rotaciona entre os resultados usando o índice da cena
        foto = fotos[indice % len(fotos)]
        # Pega a maior resolução disponível para portrait
        url = (foto["src"].get("portrait")
               or foto["src"].get("large2x")
               or foto["src"].get("large"))

        img_bytes = requests.get(url, timeout=20).content
        with open(cache_file, "wb") as f:
            f.write(img_bytes)

        print(f"[Pexels Foto] ✓ {query!r} → foto {indice % len(fotos) + 1}/{len(fotos)}")
        return str(cache_file)

    except Exception as e:
        print(f"[Pexels Foto] Erro: {e}")
        return None


# ─────────────────────────────────────────────────────────────
# PEXELS — VÍDEOS
# ─────────────────────────────────────────────────────────────

def buscar_pexels_video(query: str, indice: int = 0) -> str | None:
    """
    Busca um vídeo curto no Pexels (HD, orientação portrait ou landscape).
    Retorna caminho do arquivo MP4 em cache, ou None.
    """
    if not config.PEXELS_API_KEY:
        return None

    cache_key = _chave_cache(f"video_{query}_{indice}")
    cache_file = CACHE_DIR / f"video_{cache_key}.mp4"
    if cache_file.exists() and cache_file.stat().st_size > 50000:
        return str(cache_file)

    try:
        resp = requests.get(
            "https://api.pexels.com/videos/search",
            headers=_pexels_headers(),
            params={"query": query, "per_page": 10, "orientation": "portrait"},
            timeout=12
        )
        if resp.status_code != 200:
            print(f"[Pexels Video] HTTP {resp.status_code} para: {query}")
            return None

        videos = resp.json().get("videos", [])
        if not videos:
            # Tenta sem filtro de orientação
            resp2 = requests.get(
                "https://api.pexels.com/videos/search",
                headers=_pexels_headers(),
                params={"query": query, "per_page": 10},
                timeout=12
            )
            videos = resp2.json().get("videos", []) if resp2.status_code == 200 else []

        if not videos:
            return None

        video = videos[indice % len(videos)]

        # Escolhe arquivo de melhor qualidade ≤ 1080p (evita 4K pesado)
        video_files = video.get("video_files", [])
        # Ordena por qualidade: prefere SD/HD, evita 4K
        hd_files = [v for v in video_files if v.get("height", 0) <= 1080]
        if not hd_files:
            hd_files = video_files

        # Pega o de maior resolução dentre os permitidos
        melhor = max(hd_files, key=lambda v: v.get("height", 0) * v.get("width", 0))
        url = melhor.get("link")
        if not url:
            return None

        print(f"[Pexels Video] Baixando {query!r} ({melhor.get('width')}×{melhor.get('height')})...")
        vid_bytes = requests.get(url, timeout=60, stream=True)
        with open(cache_file, "wb") as f:
            for chunk in vid_bytes.iter_content(chunk_size=1024 * 256):
                f.write(chunk)

        print(f"[Pexels Video] ✓ salvo ({cache_file.stat().st_size // 1024} KB)")
        return str(cache_file)

    except Exception as e:
        print(f"[Pexels Video] Erro: {e}")
        return None


def extrair_frames_video(video_path: str, duracao_cena: float, fps: int = None) -> list[Image.Image]:
    """
    Extrai frames de um vídeo Pexels para usar na cena.
    Retorna lista de imagens PIL já redimensionadas para 1080×1920.
    """
    if fps is None:
        fps = config.VIDEO_FPS

    total_frames_necessarios = int(duracao_cena * fps)

    # Descobre duração do vídeo fonte
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", video_path],
        capture_output=True, text=True
    )
    try:
        duracao_video = float(result.stdout.strip())
    except:
        duracao_video = 10.0

    frames = []
    cache_subdir = CACHE_DIR / f"frames_{_chave_cache(video_path + str(fps))}"

    # Verifica se frames já estão em cache
    if cache_subdir.exists():
        frame_files = sorted(cache_subdir.glob("frame_*.jpg"))
        if len(frame_files) >= total_frames_necessarios:
            for f in frame_files[:total_frames_necessarios]:
                try:
                    img = Image.open(f).convert("RGB")
                    frames.append(img)
                except:
                    pass
            if frames:
                return frames

    # Extrai frames com FFmpeg
    cache_subdir.mkdir(exist_ok=True)

    # Calcula taxa de extração para cobrir a duração da cena
    # Se o vídeo for mais curto que a cena, vai fazer loop
    taxa = fps

    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1",    # loop infinito se o vídeo for curto
        "-i", video_path,
        "-t", str(duracao_cena + 0.5),
        "-vf", f"fps={taxa},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}",
        "-q:v", "3",
        str(cache_subdir / "frame_%05d.jpg")
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"[Video Frames] FFmpeg erro: {result.stderr[-300:]}")
        return []

    frame_files = sorted(cache_subdir.glob("frame_*.jpg"))
    for f in frame_files[:total_frames_necessarios]:
        try:
            img = Image.open(f).convert("RGB")
            frames.append(img)
        except:
            pass

    print(f"[Video Frames] {len(frames)} frames extraídos de {Path(video_path).name}")
    return frames


# ─────────────────────────────────────────────────────────────
# PROCESSAMENTO DE IMAGEM
# ─────────────────────────────────────────────────────────────

def aplicar_foto_na_cena(foto_path: str) -> Image.Image:
    """Recorta, redimensiona e aplica tratamento cinematográfico na foto."""
    foto = Image.open(foto_path).convert("RGB")
    fw, fh = foto.size
    target_ratio = W / H

    # Smart crop centrado
    if fw / fh > target_ratio:
        new_w = int(fh * target_ratio)
        x0 = (fw - new_w) // 2
        foto = foto.crop((x0, 0, x0 + new_w, fh))
    else:
        new_h = int(fw / target_ratio)
        y0 = (fh - new_h) // 2
        foto = foto.crop((0, y0, fw, y0 + new_h))

    foto = foto.resize((W, H), Image.LANCZOS)
    foto = _aplicar_tratamento_cinematografico(foto)
    return foto


def _aplicar_tratamento_cinematografico(img: Image.Image) -> Image.Image:
    """Aplica gradiente escuro, vinheta e correção de cor cinematográfica."""
    # Boost leve de contraste e saturação
    img = ImageEnhance.Contrast(img).enhance(1.12)
    img = ImageEnhance.Color(img).enhance(1.18)
    img = ImageEnhance.Brightness(img).enhance(0.92)

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Gradiente escuro progressivo na metade inferior (área da legenda)
    for y in range(H // 2, H):
        t = (y - H // 2) / (H // 2)
        alpha = int(190 * (t ** 1.6))
        draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))

    # Gradiente no topo (mais suave)
    for y in range(0, H // 6):
        t = 1 - (y / (H // 6))
        alpha = int(100 * (t ** 1.5))
        draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))

    # Vinheta lateral suave
    for i in range(100):
        alpha = int(80 * ((1 - i / 100) ** 2))
        draw.line([(i, 0), (i, H)], fill=(0, 0, 0, alpha))
        draw.line([(W - i, 0), (W - i, H)], fill=(0, 0, 0, alpha))

    img = img.convert("RGBA")
    img = Image.alpha_composite(img, overlay)
    return img.convert("RGB")


def _aplicar_tratamento_em_frame(img: Image.Image) -> Image.Image:
    """Versão leve do tratamento para frames de vídeo (já redimensionados pelo FFmpeg)."""
    img = ImageEnhance.Contrast(img).enhance(1.08)
    img = ImageEnhance.Color(img).enhance(1.12)

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    for y in range(H // 2, H):
        t = (y - H // 2) / (H // 2)
        alpha = int(190 * (t ** 1.6))
        draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))

    img = img.convert("RGBA")
    img = Image.alpha_composite(img, overlay)
    return img.convert("RGB")


# ─────────────────────────────────────────────────────────────
# FALLBACK — FUNDO GERADO LOCALMENTE
# ─────────────────────────────────────────────────────────────

def gerar_fundo_cinematografico(tipo_cena: str, width=W, height=H) -> Image.Image:
    """Gera fundo escuro cinematográfico com gradiente, textura e vinheta."""
    palette = PALETTES.get(tipo_cena, DEFAULT_PALETTE)
    c1, c2 = palette

    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)

    for y in range(height):
        t = y / height
        r = int(c1[0] + (c2[0] - c1[0]) * t)
        g = int(c1[1] + (c2[1] - c1[1]) * t)
        b = int(c1[2] + (c2[2] - c1[2]) * t)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Granulado cinematográfico
    arr = np.array(img, dtype=np.int16)
    noise = np.random.randint(-6, 7, arr.shape, dtype=np.int16)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr)

    # Vinheta
    vignette = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    vdraw = ImageDraw.Draw(vignette)
    for i in range(100):
        alpha = int(160 * ((1 - i / 100) ** 2))
        margin = i * 4
        vdraw.rectangle([margin, margin, width - margin, height - margin],
                        outline=(0, 0, 0, alpha))
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, vignette).convert("RGB")

    return img


# ─────────────────────────────────────────────────────────────
# PONTO DE ENTRADA PRINCIPAL
# ─────────────────────────────────────────────────────────────

class VisualCena:
    """
    Encapsula o visual de uma cena.
    Pode ser:
      - frames_video: lista de Image.Image (de vídeo Pexels — mais dinâmico)
      - imagem_base: Image.Image única (foto Pexels ou fundo gerado)
    """
    def __init__(self):
        self.frames_video: list[Image.Image] = []
        self.imagem_base: Image.Image | None = None
        self.fonte = "gerado"  # "video_pexels" | "foto_pexels" | "gerado"

    def tem_video(self) -> bool:
        return len(self.frames_video) > 0

    def get_frame(self, indice: int, total: int) -> Image.Image:
        """Retorna o frame correto para o índice dado (com loop se necessário)."""
        if self.frames_video:
            idx = indice % len(self.frames_video)
            return self.frames_video[idx]
        return self.imagem_base


def obter_visual_cena(tipo_cena: str, busca_visual: str, indice: int = 0,
                      duracao_cena: float = 6.0) -> VisualCena:
    """
    Obtém o visual para uma cena.
    Ordem de preferência:
      1. Vídeo Pexels (mais dinâmico)
      2. Foto Pexels
      3. Fundo gerado localmente
    """
    visual = VisualCena()

    if config.PEXELS_API_KEY:
        # ── Tenta vídeo primeiro ──────────────────────────────────
        queries_video = [busca_visual] + QUERIES_FALLBACK.get(tipo_cena, [])[:2]

        for q in queries_video:
            video_path = buscar_pexels_video(q, indice)
            if video_path:
                frames = extrair_frames_video(video_path, duracao_cena)
                if frames:
                    # Aplica tratamento cinematográfico leve nos frames
                    visual.frames_video = [_aplicar_tratamento_em_frame(f) for f in frames]
                    visual.fonte = "video_pexels"
                    print(f"[Visual] ✓ Vídeo Pexels — cena '{tipo_cena}' ({len(frames)} frames)")
                    return visual
            # Pequena pausa entre tentativas para não saturar a API
            # (já está cacheado na 2ª vez)

        # ── Fallback: foto ────────────────────────────────────────
        queries_foto = [busca_visual] + QUERIES_FALLBACK.get(tipo_cena, [])[:3]

        for q in queries_foto:
            foto_path = buscar_pexels_foto(q, indice)
            if foto_path:
                try:
                    visual.imagem_base = aplicar_foto_na_cena(foto_path)
                    visual.fonte = "foto_pexels"
                    print(f"[Visual] ✓ Foto Pexels — cena '{tipo_cena}' query={q!r}")
                    return visual
                except Exception as e:
                    print(f"[Visual] Erro ao processar foto: {e}")

    # ── Fallback final: fundo gerado ──────────────────────────────
    visual.imagem_base = gerar_fundo_cinematografico(tipo_cena)
    visual.fonte = "gerado"
    return visual


def gerar_frame_ingredientes(ingredientes: list, background: Image.Image | None = None) -> Image.Image:
    """
    Gera frame de ingredientes.
    Se background for fornecido (foto Pexels), usa-o como fundo escurecido.
    """
    if background is not None:
        # Escurece bastante para o texto ficar legível
        img = background.copy()
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 160))
        img = img.convert("RGBA")
        img = Image.alpha_composite(img, overlay).convert("RGB")
    else:
        img = gerar_fundo_cinematografico("ingredientes")

    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype(config.FONT_BOLD, 72)
        font_item  = ImageFont.truetype(config.FONT_REGULAR, 48)
        font_qty   = ImageFont.truetype(config.FONT_BOLD, 48)
    except:
        font_title = font_item = font_qty = ImageFont.load_default()

    # ── Título ────────────────────────────────────────────────────
    # Sombra
    draw.text((W // 2 + 3, 203), "INGREDIENTES", font=font_title,
              fill=(0, 0, 0, 160), anchor="mm")
    draw.text((W // 2, 200), "INGREDIENTES", font=font_title,
              fill=(255, 220, 50), anchor="mm")

    # Linha decorativa
    draw.rectangle([80, 252, W - 80, 258], fill=(255, 220, 50))

    # ── Lista ─────────────────────────────────────────────────────
    y = 300
    for ing in ingredientes[:10]:
        item = ing.get("item", "").capitalize()
        qty  = ing.get("quantidade", "")

        # Sombra do texto
        draw.text((133, y + 2), item, font=font_item, fill=(0, 0, 0, 140))
        draw.text((W - 88, y + 2), qty, font=font_qty, fill=(0, 0, 0, 140), anchor="ra")

        # Bullet + item + quantidade
        draw.text((90, y), "•", font=font_item, fill=(255, 180, 30))
        draw.text((130, y), item, font=font_item, fill=(255, 255, 255))
        draw.text((W - 90, y), qty, font=font_qty, fill=(255, 220, 100), anchor="ra")

        y += 76
        if y > H - 220:
            break

    return img
