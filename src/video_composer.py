"""
Compositor de vídeo.

Com vídeos Pexels: usa frames reais do vídeo (sem Ken Burns artificial).
Com fotos Pexels ou fundo gerado: aplica efeito Ken Burns para dar movimento.
Sempre aplica transições dissolve entre cenas e legendas animadas.
"""
import os
import sys
import subprocess
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config
from src.visual_provider import (
    obter_visual_cena, gerar_frame_ingredientes, VisualCena
)
from src.subtitle_generator import desenhar_legenda, gerar_frames_legenda

W = config.VIDEO_WIDTH
H = config.VIDEO_HEIGHT
FPS = config.VIDEO_FPS

# Tipos de movimento Ken Burns por tipo de cena
MOVIMENTOS = {
    "gancho":       ["zoom_out", "zoom_in"],
    "ingredientes": ["zoom_in",  "pan_right"],
    "preparacao":   ["zoom_in",  "pan_left"],
    "processo":     ["zoom_in",  "zoom_out"],
    "detalhe":      ["zoom_in",  "zoom_in"],
    "finalizacao":  ["pan_right","zoom_in"],
    "resultado":    ["zoom_out", "zoom_in"],
    "encerramento": ["zoom_in",  "zoom_in"],
}


# ─────────────────────────────────────────────────────────────
# Ken Burns (usado só quando não há vídeo real)
# ─────────────────────────────────────────────────────────────

def _ken_burns(img: Image.Image, frame_idx: int, total_frames: int,
               tipo: str = "zoom_in") -> Image.Image:
    """Aplica zoom/pan suave na imagem estática."""
    if total_frames <= 1:
        return img

    t = frame_idx / max(total_frames - 1, 1)

    if tipo == "zoom_in":
        escala = 1.0 + 0.09 * t
        px, py = 0.5, 0.5 + 0.02 * t
    elif tipo == "zoom_out":
        escala = 1.09 - 0.09 * t
        px, py = 0.5, 0.52 - 0.02 * t
    elif tipo == "pan_right":
        escala = 1.06
        px, py = 0.47 + 0.06 * t, 0.5
    elif tipo == "pan_left":
        escala = 1.06
        px, py = 0.53 - 0.06 * t, 0.5
    else:
        return img

    new_w = int(W / escala)
    new_h = int(H / escala)
    x0 = max(0, min(int((W - new_w) * px), W - new_w))
    y0 = max(0, min(int((H - new_h) * py), H - new_h))

    cropped = img.crop((x0, y0, x0 + new_w, y0 + new_h))
    return cropped.resize((W, H), Image.LANCZOS)


# ─────────────────────────────────────────────────────────────
# Transição dissolve suave
# ─────────────────────────────────────────────────────────────

def _dissolve(img_a: Image.Image, img_b: Image.Image, t: float) -> Image.Image:
    """Dissolve suave entre dois frames (t: 0→1)."""
    t_s = t * t * (3 - 2 * t)  # smoothstep
    return Image.blend(img_a, img_b, t_s)


# ─────────────────────────────────────────────────────────────
# Geração de cenas
# ─────────────────────────────────────────────────────────────

def gerar_cenas_video(receita: dict, dir_frames: str, callback=None) -> dict:
    """
    Gera todos os frames do vídeo cena por cena.
    Suporta frames de vídeo reais (Pexels) e Ken Burns para fotos/fundos.
    """
    cenas      = receita.get("cenas", [])
    ingredientes = receita.get("ingredientes", [])
    os.makedirs(dir_frames, exist_ok=True)

    # ── Pré-carrega visuais ───────────────────────────────────────
    print(f"[Video] Carregando visuais para {len(cenas)} cenas...")
    visuais: list[VisualCena] = []

    for i, cena in enumerate(cenas):
        tipo  = cena.get("tipo", "processo")
        busca = cena.get("busca_visual", tipo + " food")
        dur   = float(cena.get("duracao_seg", config.SCENE_DURATION_DEFAULT))
        dur   = max(config.SCENE_DURATION_MIN, min(dur, config.SCENE_DURATION_MAX))

        v = obter_visual_cena(tipo, busca, indice=i, duracao_cena=dur + 1.0)

        # Cena de ingredientes: sobreposição de texto sobre fundo
        if tipo == "ingredientes":
            bg = v.imagem_base  # pode ser foto Pexels ou None
            v.imagem_base = gerar_frame_ingredientes(ingredientes, background=bg)
            v.frames_video = []  # não usa vídeo para ingredientes (texto precisa ser legível)

        visuais.append(v)
        prog = 0.3 + (i + 1) / len(cenas) * 0.15
        if callback:
            callback(f"Preparando cena {i+1}/{len(cenas)} [{v.fonte}]...", prog)

    # ── Renderiza frames ──────────────────────────────────────────
    FADE_FRAMES = int(FPS * 0.45)
    frame_num = 0
    timings   = []

    for ci, cena in enumerate(cenas):
        tipo     = cena.get("tipo", "processo")
        dur      = float(cena.get("duracao_seg", config.SCENE_DURATION_DEFAULT))
        dur      = max(config.SCENE_DURATION_MIN, min(dur, config.SCENE_DURATION_MAX))
        narracao = cena.get("narracao", "")

        total_frames_cena = int(dur * FPS)
        visual_atual      = visuais[ci]
        visual_proximo    = visuais[ci + 1] if ci + 1 < len(cenas) else None

        # Escolhe movimento Ken Burns para este tipo
        opcoes = MOVIMENTOS.get(tipo, ["zoom_in"])
        movimento = opcoes[ci % len(opcoes)]

        # Progressos para fade das legendas
        fade_prog = gerar_frames_legenda(narracao, total_frames_cena, FPS)

        timing_inicio = frame_num

        for f in range(total_frames_cena):
            # ── Frame base da cena ────────────────────────────────
            if visual_atual.tem_video():
                # Vídeo Pexels: usa frame real
                frame = visual_atual.get_frame(f, total_frames_cena)
            else:
                # Foto/fundo: Ken Burns
                frame = _ken_burns(visual_atual.imagem_base, f, total_frames_cena, movimento)

            # ── Transição dissolve para próxima cena ──────────────
            if visual_proximo is not None and f >= total_frames_cena - FADE_FRAMES:
                t_fade = (f - (total_frames_cena - FADE_FRAMES)) / FADE_FRAMES

                if visual_proximo.tem_video():
                    frame_next = visual_proximo.get_frame(0, total_frames_cena)
                else:
                    mov_next = MOVIMENTOS.get(
                        cenas[ci + 1].get("tipo", "processo"),
                        ["zoom_in"]
                    )[(ci + 1) % len(MOVIMENTOS.get(cenas[ci + 1].get("tipo", "processo"), ["zoom_in"]))]
                    frame_next = _ken_burns(visual_proximo.imagem_base, 0,
                                            total_frames_cena, mov_next)

                frame = _dissolve(frame, frame_next, t_fade)

            # ── Legendas animadas ─────────────────────────────────
            frame = desenhar_legenda(frame, narracao, fade_prog[f])

            # ── Salva frame ───────────────────────────────────────
            frame_path = os.path.join(dir_frames, f"frame_{frame_num:06d}.jpg")
            frame.save(frame_path, quality=92, optimize=False)
            frame_num += 1

        timings.append({
            "cena_id":       cena.get("id", ci + 1),
            "tipo":          tipo,
            "fonte_visual":  visual_atual.fonte,
            "frame_inicio":  timing_inicio,
            "frame_fim":     frame_num,
            "tempo_inicio":  timing_inicio / FPS,
            "tempo_fim":     frame_num / FPS,
            "efeito_sonoro": cena.get("efeito_sonoro", ""),
            "narracao":      narracao,
        })

        prog = 0.45 + (ci + 1) / len(cenas) * 0.35
        if callback:
            callback(f"Cena {ci+1}/{len(cenas)} — {visual_atual.fonte}...", prog)

        print(f"[Video] Cena {ci+1}/{len(cenas)} — {tipo} [{visual_atual.fonte}] — {total_frames_cena} frames")

    return {
        "total_frames":  frame_num,
        "duracao_total": frame_num / FPS,
        "timings":       timings,
    }


# ─────────────────────────────────────────────────────────────
# Renderização final com FFmpeg
# ─────────────────────────────────────────────────────────────

def renderizar_video_final(dir_frames: str, audio_path: str,
                           caminho_saida: str, callback=None) -> str:
    """Renderiza os frames JPEG + áudio em MP4 final."""
    if callback:
        callback("Renderizando vídeo final com FFmpeg...", 0.86)

    print("[Video] Renderizando com FFmpeg...")

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
        caminho_saida,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[Video] Erro FFmpeg:\n{result.stderr[-800:]}")
        raise RuntimeError(f"Renderização falhou: {result.stderr[-300:]}")

    tamanho = os.path.getsize(caminho_saida) / (1024 * 1024)
    print(f"[Video] ✓ Salvo: {caminho_saida} ({tamanho:.1f} MB)")

    if callback:
        callback("Vídeo concluído!", 1.0)

    return caminho_saida
