"""
Gerador de legendas estilo redes sociais — modernas, sincronizadas, com destaque.
"""
import os
import sys
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config

# Palavras que devem ser destacadas em amarelo
PALAVRAS_DESTAQUE = {
    "perfeito", "incrível", "delicioso", "maravilhoso", "fácil", "simples",
    "rápido", "secreto", "truque", "dica", "importante", "atenção",
    "pronto", "beleza", "olha", "veja"
}


def _carregar_fonte(tamanho: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    try:
        path = config.FONT_BOLD if bold else config.FONT_REGULAR
        return ImageFont.truetype(path, tamanho)
    except:
        return ImageFont.load_default()


def _quebrar_texto(texto: str, font: ImageFont.FreeTypeFont, max_width: int) -> list:
    """Quebra texto em linhas que cabem na largura."""
    palavras = texto.split()
    linhas = []
    linha_atual = ""

    for palavra in palavras:
        teste = f"{linha_atual} {palavra}".strip()
        bbox = font.getbbox(teste)
        largura = bbox[2] - bbox[0]

        if largura <= max_width:
            linha_atual = teste
        else:
            if linha_atual:
                linhas.append(linha_atual)
            linha_atual = palavra

    if linha_atual:
        linhas.append(linha_atual)

    return linhas


def desenhar_legenda(
    frame: Image.Image,
    texto: str,
    progresso: float = 1.0,
    tamanho_fonte: int = None
) -> Image.Image:
    """
    Desenha legenda estilo TikTok no frame.
    progresso: 0.0-1.0 para animação de fade-in
    """
    if not texto or not texto.strip():
        return frame

    if tamanho_fonte is None:
        tamanho_fonte = config.FONT_SUBTITLE_SIZE

    img = frame.copy()
    w, h = img.size
    draw = ImageDraw.Draw(img)

    font = _carregar_fonte(tamanho_fonte)
    max_width = int(w * 0.85)
    linhas = _quebrar_texto(texto, font, max_width)

    # Mede altura total
    line_height = tamanho_fonte + 12
    total_height = len(linhas) * line_height + 24

    # Posição: 72% da altura (acima da zona de segurança inferior)
    y_base = int(h * 0.72)

    # Fundo semi-transparente por trás das legendas
    padding_x, padding_y = 30, 18

    for i, linha in enumerate(linhas):
        bbox = font.getbbox(linha)
        lw = bbox[2] - bbox[0]
        lh = bbox[3] - bbox[1]
        x = (w - lw) // 2
        y = y_base + i * line_height

        # Fundo escuro arredondado
        bg_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        bg_draw = ImageDraw.Draw(bg_layer)
        rx0 = x - padding_x
        ry0 = y - padding_y // 2
        rx1 = x + lw + padding_x
        ry1 = y + lh + padding_y // 2
        alpha_bg = int(190 * progresso)
        bg_draw.rounded_rectangle(
            [rx0, ry0, rx1, ry1],
            radius=12,
            fill=(0, 0, 0, alpha_bg)
        )
        img = img.convert("RGBA")
        img = Image.alpha_composite(img, bg_layer)
        draw = ImageDraw.Draw(img)

        # Renderiza cada palavra com destaque
        palavras_linha = linha.split()
        x_cursor = x
        for palavra in palavras_linha:
            palavra_lower = palavra.lower().strip(".,!?;:")

            # Cor da palavra
            if palavra_lower in PALAVRAS_DESTAQUE:
                cor_texto = (255, 230, 50, int(255 * progresso))
                # Sombra mais pronunciada para palavras destacadas
                sombra_offset = 3
            else:
                cor_texto = (255, 255, 255, int(255 * progresso))
                sombra_offset = 2

            # Sombra (stroke simulado)
            for dx in range(-sombra_offset, sombra_offset+1):
                for dy in range(-sombra_offset, sombra_offset+1):
                    if abs(dx) + abs(dy) <= sombra_offset + 1:
                        draw.text(
                            (x_cursor + dx, y + dy),
                            palavra + " ",
                            font=font,
                            fill=(0, 0, 0, int(180 * progresso))
                        )

            draw.text((x_cursor, y), palavra + " ", font=font, fill=cor_texto)

            # Avança cursor
            pw = font.getbbox(palavra + " ")[2]
            x_cursor += pw

    return img.convert("RGB")


def gerar_frames_legenda(
    texto: str,
    total_frames: int,
    fps: int = 30
) -> list:
    """
    Retorna lista de (progresso, texto) para cada frame.
    O texto aparece gradualmente com fade-in no início e fade-out no final.
    """
    frames_info = []
    fade_frames = min(int(fps * 0.4), total_frames // 4)

    for i in range(total_frames):
        # Fade-in
        if i < fade_frames:
            prog = i / fade_frames
        # Fade-out
        elif i >= total_frames - fade_frames:
            prog = (total_frames - i) / fade_frames
        else:
            prog = 1.0

        frames_info.append(prog)

    return frames_info
