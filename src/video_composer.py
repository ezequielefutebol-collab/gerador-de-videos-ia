"""
Compositor de vídeo: gera frames com Ken Burns, transições e legendas,
depois renderiza com FFmpeg.
"""
import os
import sys
import math
import tempfile
import subprocess
import shutil
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config
from src.visual_provider import obter_visual_cena, gerar_frame_ingredientes
from src.subtitle_generator import desenhar_legenda, gerar_frames_legenda

W = config.VIDEO_WIDTH
H = config.VIDEO_HEIGHT
FPS = config.VIDEO_FPS


def _aplicar_ken_burns(img: Image.Image, frame_idx: int, total_frames: int,
                        tipo: str = "zoom_in") -> Image.Image:
    """Aplica efeito Ken Burns (zoom + pan lento) no frame."""
    if total_frames <= 1:
        return img

    t = frame_idx / max(total_frames - 1, 1)

    # Zoom suave
    if tipo == "zoom_in":
        escala = 1.0 + 0.08 * t        # 1.0 → 1.08
        pan_x = 0.5                      # centro
        pan_y = 0.5 + 0.02 * t          # sobe levemente
    elif tipo == "zoom_out":
        escala = 1.08 - 0.08 * t        # 1.08 → 1.0
        pan_x = 0.5
        pan_y = 0.52 - 0.02 * t
    elif tipo == "pan_right":
        escala = 1.05
        pan_x = 0.48 + 0.04 * t         # desloca para direita
        pan_y = 0.5
    elif tipo == "pan_left":
        escala = 1.05
        pan_x = 0.52 - 0.04 * t
        pan_y = 0.5
    else:  # static
        return img

    # Calcula crop
    new_w = int(W / escala)
    new_h = int(H / escala)

    x0 = int((W - new_w) * pan_x)
    y0 = int((H - new_h) * pan_y)
    x0 = max(0, min(x0, W - new_w))
    y0 = max(0, min(y0, H - new_h))

    cropped = img.crop((x0, y0, x0 + new_w, y0 + new_h))
    return cropped.resize((W, H), Image.LANCZOS)


def _transicao_fade(frame_a: Image.Image, frame_b: Image.Image, t: float) -> Image.Image:
    """Fade entre dois frames (t de 0.0 a 1.0)."""
    return Image.blend(frame_a, frame_b, t)


def _transicao_dissolve(frame_a: Image.Image, frame_b: Image.Image, t: float) -> Image.Image:
    """Dissolve suave — igual ao fade mas com curva s."""
    t_suave = t * t * (3 - 2 * t)  # smoothstep
    return Image.blend(frame_a, frame_b, t_suave)


def _frame_intro(titulo: str, subtitulo: str, t: float) -> Image.Image:
    """Gera frame de intro animado com título."""
    img = Image.new("RGB", (W, H), (10, 5, 2))
    draw = ImageDraw.Draw(img)

    # Gradiente de fundo quente
    for y in range(H):
        v = y / H
        r = int(15 + 25 * v)
        g = int(5 + 10 * v)
        b = int(2 + 5 * v)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    try:
        font_title = ImageFont.truetype(config.FONT_BOLD, config.FONT_TITLE_SIZE)
        font_sub = ImageFont.truetype(config.FONT_REGULAR, 46)
    except:
        font_title = font_sub = ImageFont.load_default()

    # Animação de slide-up
    offset_y = int(80 * (1 - min(t * 3, 1.0)))
    alpha = min(int(255 * t * 2), 255)

    # Linha decorativa
    line_w = int(W * 0.7 * min(t * 2, 1.0))
    draw.rectangle([(W//2 - line_w//2, H//2 - 60), (W//2 + line_w//2, H//2 - 55)],
                   fill=(255, 200, 50))

    # Título
    bbox = font_title.getbbox(titulo)
    tw = bbox[2] - bbox[0]
    # Quebra se muito longo
    palavras = titulo.split()
    linhas = []
    linha = ""
    for p in palavras:
        teste = f"{linha} {p}".strip()
        if font_title.getbbox(teste)[2] < W - 100:
            linha = teste
        else:
            if linha:
                linhas.append(linha)
            linha = p
    if linha:
        linhas.append(linha)

    y_start = H//2 - 40 + offset_y
    for i, l in enumerate(linhas):
        bw = font_title.getbbox(l)[2]
        x = (W - bw) // 2
        # Sombra
        draw.text((x+3, y_start + i*95 + 3), l, font=font_title, fill=(0, 0, 0, 100))
        draw.text((x, y_start + i*95), l, font=font_title, fill=(255, 255, 255))

    return img


def gerar_cenas_video(receita: dict, dir_frames: str, callback=None) -> dict:
    """
    Gera todos os frames do vídeo cena por cena.
    Retorna dict com metadados de timing para sincronização de áudio.
    """
    cenas = receita.get("cenas", [])
    titulo = receita.get("titulo", "Receita")
    ingredientes = receita.get("ingredientes", [])

    os.makedirs(dir_frames, exist_ok=True)

    # Tipos de movimento por tipo de cena
    movimentos = {
        "gancho":       ["zoom_out", "zoom_in"],
        "ingredientes": ["zoom_in", "pan_right"],
        "preparacao":   ["zoom_in", "pan_left"],
        "processo":     ["zoom_in", "zoom_out"],
        "detalhe":      ["zoom_in", "zoom_in"],
        "finalizacao":  ["pan_right", "zoom_in"],
        "resultado":    ["zoom_out", "zoom_in"],
        "encerramento": ["zoom_in", "zoom_in"],
    }

    # Transições entre cenas
    FADE_FRAMES = int(FPS * 0.5)  # 0.5s de transição

    frame_total = 0
    timings = []  # (cena_id, frame_inicio, frame_fim)
    frames_buffer = []  # (numero_frame, imagem)

    # Pré-carrega os visuais
    print(f"[Video] Preparando {len(cenas)} cenas...")

    visuais = []
    for i, cena in enumerate(cenas):
        tipo = cena.get("tipo", "processo")
        busca = cena.get("busca_visual", tipo + " food")

        if tipo == "ingredientes" and i < 3:
            visual = gerar_frame_ingredientes(ingredientes, W, H)
        else:
            visual = obter_visual_cena(tipo, busca, i)

        visuais.append(visual)
        if callback:
            callback(f"Preparando cena {i+1}/{len(cenas)}...", (i+1)/len(cenas)*0.3)

    # Gera os frames
    frame_num = 0

    for cena_idx, cena in enumerate(cenas):
        tipo = cena.get("tipo", "processo")
        duracao = float(cena.get("duracao_seg", config.SCENE_DURATION_DEFAULT))
        narracao = cena.get("narracao", "")

        # Clamp duração
        duracao = max(config.SCENE_DURATION_MIN, min(duracao, config.SCENE_DURATION_MAX))
        total_frames_cena = int(duracao * FPS)

        visual_base = visuais[cena_idx]

        # Escolhe movimento
        opcoes_mov = movimentos.get(tipo, ["zoom_in"])
        movimento = opcoes_mov[cena_idx % len(opcoes_mov)]

        # Próximo visual para transição
        proximo_visual = visuais[cena_idx + 1] if cena_idx + 1 < len(visuais) else None

        timing_inicio = frame_num

        for f in range(total_frames_cena):
            img = _aplicar_ken_burns(visual_base, f, total_frames_cena, movimento)

            # Fade-out nos últimos frames (transição para próxima cena)
            if proximo_visual is not None and f >= total_frames_cena - FADE_FRAMES:
                t_fade = (f - (total_frames_cena - FADE_FRAMES)) / FADE_FRAMES
                proximo_mov = movimentos.get(
                    cenas[cena_idx+1].get("tipo", "processo") if cena_idx+1 < len(cenas) else tipo,
                    ["zoom_in"]
                )[0]
                img_next = _aplicar_ken_burns(proximo_visual, 0, total_frames_cena, proximo_mov)
                img = _transicao_dissolve(img, img_next, t_fade)

            # Legenda
            progresso_cena = f / total_frames_cena
            fade_progresso = gerar_frames_legenda(narracao, total_frames_cena, FPS)
            img = desenhar_legenda(img, narracao, fade_progresso[f])

            # Salva frame
            frame_path = os.path.join(dir_frames, f"frame_{frame_num:06d}.jpg")
            img.save(frame_path, quality=92)
            frame_num += 1

        timings.append({
            "cena_id": cena.get("id", cena_idx+1),
            "tipo": tipo,
            "frame_inicio": timing_inicio,
            "frame_fim": frame_num,
            "tempo_inicio": timing_inicio / FPS,
            "tempo_fim": frame_num / FPS,
            "efeito_sonoro": cena.get("efeito_sonoro", ""),
            "narracao": narracao
        })

        progresso = 0.3 + (cena_idx+1)/len(cenas) * 0.4
        if callback:
            callback(f"Renderizando cena {cena_idx+1}/{len(cenas)}...", progresso)

        print(f"[Video] Cena {cena_idx+1}/{len(cenas)} — {tipo} — {total_frames_cena} frames")

    return {
        "total_frames": frame_num,
        "duracao_total": frame_num / FPS,
        "timings": timings
    }


def renderizar_video_final(
    dir_frames: str,
    audio_path: str,
    caminho_saida: str,
    callback=None
) -> str:
    """
    Renderiza os frames JPEG + áudio em um vídeo MP4 final com FFmpeg.
    """
    if callback:
        callback("Renderizando vídeo final...", 0.85)

    print(f"[Video] Renderizando com FFmpeg...")

    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-pattern_type", "glob",
        "-i", os.path.join(dir_frames, "frame_*.jpg"),
        "-i", audio_path,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        caminho_saida
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"[Video] Erro FFmpeg: {result.stderr[-1000:]}")
        raise RuntimeError(f"Erro ao renderizar: {result.stderr[-300:]}")

    tamanho = os.path.getsize(caminho_saida) / (1024*1024)
    print(f"[Video] Vídeo salvo: {caminho_saida} ({tamanho:.1f} MB)")

    if callback:
        callback("Vídeo concluído!", 1.0)

    return caminho_saida
