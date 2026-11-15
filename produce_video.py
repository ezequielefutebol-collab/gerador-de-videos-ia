#!/usr/bin/env python3
"""
Produtor de Vídeo: Construção Prédio 40 Andares
Formato: Vertical 1080x1920, ~65 segundos, MP4
"""

import os, sys, math, random, subprocess, wave, struct, time
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SCRATCHPAD = "/tmp/claude-0/-home-user-gerador-de-videos-ia/a4b805ec-f54c-5f2b-b26b-cd97a5532e84/scratchpad"
OUTPUT_FILE = f"{SCRATCHPAD}/predio_40_andares.mp4"
AUDIO_FILE  = f"{SCRATCHPAD}/narration.wav"
MUSIC_FILE  = f"{SCRATCHPAD}/music.wav"
MIX_FILE    = f"{SCRATCHPAD}/audio_mix.wav"

os.makedirs(SCRATCHPAD, exist_ok=True)

# ── Dimensões ──────────────────────────────────────────────────────
W, H, FPS = 1080, 1920, 30
HORIZON_Y  = 1370
BLD_CX     = 540
BLD_W      = 420
N_FLOORS   = 40
FLOOR_H    = 30
BLD_L      = BLD_CX - BLD_W // 2    # 330
BLD_R      = BLD_CX + BLD_W // 2    # 750
BLD_BOTTOM = HORIZON_Y - 15          # 1355
BLD_FULL_H = N_FLOORS * FLOOR_H      # 1200
BLD_FULL_TOP = BLD_BOTTOM - BLD_FULL_H  # 155

# ── Fonte ──────────────────────────────────────────────────────────
FONT_PATHS = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf",
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]

def get_font(size):
    for p in FONT_PATHS:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

# ── Silhueta da cidade (constante) ──────────────────────────────────
CITY_BLDS = [
    (0,55,85),(50,70,130),(115,50,105),(160,90,85),(245,65,160),
    (305,50,115),(350,80,95),(425,55,70),(475,75,185),(545,55,100),
    (595,70,125),(660,85,85),(740,60,165),(795,75,105),(865,55,90),
    (915,70,115),(980,55,95),(1030,70,135),(1095,55,90),
]

# ── Helpers de cor ─────────────────────────────────────────────────
def lerp(a, b, t):
    return int(a + (b - a) * t)

def lerp_color(c1, c2, t):
    return (lerp(c1[0], c2[0], t), lerp(c1[1], c2[1], t), lerp(c1[2], c2[2], t))

# ── Desenho do céu ─────────────────────────────────────────────────
SKY = {
    'dawn':   ((210,95,55),(255,185,130)),
    'day':    ((25,90,170),(130,195,235)),
    'golden': ((210,140,45),(255,205,135)),
    'night':  ((5,10,28),(18,30,65)),
}

def draw_sky(draw, sky_type):
    top, bot = SKY[sky_type]
    for y in range(H):
        t = y / (H - 1)
        c = lerp_color(top, bot, t)
        draw.line([(0, y), (W, y)], fill=c)

# ── Silhueta da cidade ─────────────────────────────────────────────
def draw_city(draw, sky_type):
    if sky_type == 'night':
        bld_c = (18, 22, 48)
        win_c = (200, 175, 90)
    elif sky_type == 'golden':
        bld_c = (70, 50, 35)
        win_c = None
    else:
        bld_c = (155, 185, 210)
        win_c = None

    rng = random.Random(42)
    for (bx, bw, bh) in CITY_BLDS:
        by = HORIZON_Y - bh
        draw.rectangle([bx, by, bx + bw, HORIZON_Y], fill=bld_c)
        if win_c and bh > 60:
            for wy2 in range(by + 8, HORIZON_Y - 8, 14):
                for wx2 in range(bx + 6, bx + bw - 6, 11):
                    if rng.random() < 0.45:
                        draw.rectangle([wx2, wy2, wx2+5, wy2+7], fill=win_c)

# ── Solo / terreno ─────────────────────────────────────────────────
GROUND_COLORS = {
    'empty':        ((140,110,80),(110,85,60)),
    'clearing':     ((130,105,75),(100,80,55)),
    'excavation':   ((115,88,60),(85,65,42)),
    'foundation':   ((140,130,120),(110,100,90)),
    'construction': ((145,135,125),(115,105,95)),
    'finished':     ((80,115,70),(60,90,55)),
}

def draw_ground(draw, scene_type):
    top_c, bot_c = GROUND_COLORS.get(scene_type, GROUND_COLORS['construction'])
    for y in range(HORIZON_Y, H):
        t = (y - HORIZON_Y) / max(H - HORIZON_Y - 1, 1)
        c = lerp_color(top_c, bot_c, t)
        draw.line([(0, y), (W, y)], fill=c)

# ── Escavação ──────────────────────────────────────────────────────
def draw_pit(draw):
    pl, pr = BLD_L - 60, BLD_R + 60
    pt, pb = HORIZON_Y - 25, HORIZON_Y + 170
    draw.polygon([(pl, pt),(pr, pt),(pr-30, pb),(pl+30, pb)], fill=(88,63,38))
    draw.rectangle([pl+30, pb-25, pr-30, pb], fill=(68,48,28))
    # montes de terra
    draw.ellipse([pl-100, HORIZON_Y-50, pl+40, HORIZON_Y+15], fill=(138,108,78))
    draw.ellipse([pr-40, HORIZON_Y-55, pr+120, HORIZON_Y+15], fill=(138,108,78))

def draw_foundation(draw):
    draw_pit(draw)
    # laje de concreto no fundo
    draw.rectangle([BLD_L-15, HORIZON_Y+80, BLD_R+15, HORIZON_Y+165], fill=(160,155,150))
    # estacas de aço
    for i in range(9):
        x = BLD_L + i * (BLD_W // 8)
        draw.rectangle([x-2, HORIZON_Y-20, x+2, HORIZON_Y+160], fill=(90,95,100))
    # ferragem horizontal
    for yo in range(10, 160, 25):
        draw.rectangle([BLD_L-15, HORIZON_Y+yo, BLD_R+15, HORIZON_Y+yo+2], fill=(90,95,100))

# ── Maquinário ─────────────────────────────────────────────────────
def draw_bulldozer(draw, x=BLD_CX-120):
    bx = x
    draw.rectangle([bx, HORIZON_Y-82, bx+150, HORIZON_Y-30], fill=(255,175,0))
    draw.rectangle([bx+55, HORIZON_Y-115, bx+110, HORIZON_Y-82], fill=(220,155,0))
    draw.rectangle([bx-5, HORIZON_Y-30, bx+155, HORIZON_Y-10], fill=(70,60,50))
    draw.rectangle([bx-55, HORIZON_Y-74, bx+2, HORIZON_Y-16], fill=(190,180,170))
    draw.rectangle([bx+58, HORIZON_Y-112, bx+107, HORIZON_Y-85], fill=(140,195,225))

def draw_excavator(draw, x=BLD_CX+80):
    ex = x
    draw.rectangle([ex, HORIZON_Y-100, ex+170, HORIZON_Y-32], fill=(255,175,0))
    draw.rectangle([ex+90, HORIZON_Y-130, ex+155, HORIZON_Y-100], fill=(220,155,0))
    draw.rectangle([ex-5, HORIZON_Y-32, ex+175, HORIZON_Y-12], fill=(70,60,50))
    # braço
    draw.line([(ex+120, HORIZON_Y-100),(ex+180, HORIZON_Y-190)], fill=(175,165,155), width=14)
    draw.line([(ex+180, HORIZON_Y-190),(ex+215, HORIZON_Y-130)], fill=(175,165,155), width=11)
    pts = [(ex+210,HORIZON_Y-130),(ex+245,HORIZON_Y-130),(ex+240,HORIZON_Y-98),(ex+205,HORIZON_Y-98)]
    draw.polygon(pts, fill=(155,145,135))

# ── Guindaste (tower crane) ────────────────────────────────────────
def draw_crane(draw, floors_built):
    if floors_built < 4:
        return
    crane_top_y = BLD_BOTTOM - (floors_built + 4) * FLOOR_H
    crane_base_y = BLD_BOTTOM
    crane_x = BLD_R + 25

    # torre (listrada vermelho/amarelo)
    stripe_h = 18
    for cy in range(crane_top_y, crane_base_y, stripe_h*2):
        y1a = min(cy+stripe_h, crane_base_y)
        if y1a > cy:
            draw.rectangle([crane_x-9, cy, crane_x+9, y1a], fill=(220,55,25))
        y0b = cy+stripe_h
        y1b = min(cy+stripe_h*2, crane_base_y)
        if y1b > y0b:
            draw.rectangle([crane_x-9, y0b, crane_x+9, y1b], fill=(240,185,0))

    # lança horizontal
    boom_len = 210
    draw.rectangle([crane_x-boom_len, crane_top_y-9, crane_x+90, crane_top_y+9],
                   fill=(220,55,25))
    # contrapeso
    draw.rectangle([crane_x+45, crane_top_y, crane_x+88, crane_top_y+28],
                   fill=(190,45,20))
    # cabo
    cable_x = crane_x - boom_len + 80
    cable_bot = max(crane_top_y+40, BLD_BOTTOM - floors_built * FLOOR_H + 30)
    draw.line([(cable_x, crane_top_y), (cable_x, cable_bot)], fill=(160,160,160), width=2)
    draw.ellipse([cable_x-5, cable_bot-5, cable_x+5, cable_bot+12], fill=(150,150,150))

# ── Andaimes ───────────────────────────────────────────────────────
def draw_scaffolding(draw, floors_built):
    if floors_built < 4:
        return
    top_y = BLD_BOTTOM - floors_built * FLOOR_H
    sx = BLD_R + 5
    # horizontais
    for f in range(floors_built):
        y = BLD_BOTTOM - (f+1) * FLOOR_H
        draw.line([(sx, y), (sx+28, y)], fill=(175,165,155), width=2)
    # verticais
    for vx in [sx+5, sx+15, sx+27]:
        draw.line([(vx, top_y), (vx, BLD_BOTTOM)], fill=(175,165,155), width=1)

# ── Árvores ────────────────────────────────────────────────────────
def draw_trees(draw):
    trees = [(175,HORIZON_Y-18),(260,HORIZON_Y-12),(820,HORIZON_Y-18),(900,HORIZON_Y-12),
             (140,HORIZON_Y-8),(940,HORIZON_Y-8)]
    for (tx, ty) in trees:
        draw.rectangle([tx-5, ty, tx+5, ty+42], fill=(95,65,38))
        draw.ellipse([tx-38, ty-65, tx+38, ty+18], fill=(45,110,45))
        draw.ellipse([tx-28, ty-82, tx+28, ty-5], fill=(55,135,55))

# ── Estrelas e lua ─────────────────────────────────────────────────
def draw_night_elements(draw):
    rng = random.Random(77)
    for _ in range(220):
        sx = rng.randint(0, W)
        sy = rng.randint(0, int(HORIZON_Y * 0.72))
        b = rng.randint(140, 255)
        r = rng.randint(0, 1)
        draw.rectangle([sx, sy, sx+r, sy+r], fill=(b, b, b))
    # lua
    draw.ellipse([810, 55, 880, 128], fill=(240,240,215))
    draw.ellipse([835, 60, 862, 100], fill=(225,225,200))

# ── Cercado de obra ────────────────────────────────────────────────
def draw_fence(draw):
    fy = HORIZON_Y - 5
    for fx in range(BLD_L-70, BLD_R+70, 42):
        draw.rectangle([fx, fy-72, fx+5, fy], fill=(255,145,0))
    draw.rectangle([BLD_L-70, fy-50, BLD_R+70, fy-46], fill=(255,145,0))
    draw.rectangle([BLD_L-70, fy-30, BLD_R+70, fy-26], fill=(255,145,0))

# ── Prédio ─────────────────────────────────────────────────────────
def draw_building(draw, n_floors, style='construction', rng_seed=0):
    if n_floors == 0:
        return
    top_y = BLD_BOTTOM - n_floors * FLOOR_H
    n_win = 8
    col_w = 16
    win_area_l = BLD_L + col_w
    win_area_w = BLD_W - col_w * 2
    cell_w = win_area_w // n_win
    win_w = cell_w - 3
    slab_h = 5

    rng = random.Random(rng_seed)

    # Fundo do edifício
    if style == 'construction':
        bkg = (155, 150, 145)
    elif style == 'glass':
        bkg = (45, 105, 165)
    else:  # night
        bkg = (18, 22, 42)

    draw.rectangle([BLD_L, top_y, BLD_R, BLD_BOTTOM], fill=bkg)

    # Sombra lateral (lado direito mais escuro para profundidade)
    shade_w = 30
    for sx in range(shade_w):
        alpha = int(40 * (sx / shade_w))
        sc = (max(0, bkg[0]-40+sx*2), max(0, bkg[1]-40+sx*2), max(0, bkg[2]-40+sx*2))
    # lado direito mais escuro
    draw.rectangle([BLD_R-32, top_y, BLD_R, BLD_BOTTOM], fill=(
        max(0, bkg[0]-35), max(0, bkg[1]-35), max(0, bkg[2]-35)))

    for floor in range(n_floors):
        ft = BLD_BOTTOM - (floor+1)*FLOOR_H
        fb = BLD_BOTTOM - floor*FLOOR_H
        wt = ft + slab_h
        wb = fb - 2
        wh = wb - wt

        # Laje
        draw.rectangle([BLD_L, ft, BLD_R, ft+slab_h], fill=(118,113,108))
        # Colunas laterais
        draw.rectangle([BLD_L, ft, BLD_L+col_w, fb], fill=(128,122,118))
        draw.rectangle([BLD_R-col_w, ft, BLD_R, fb], fill=(105,100,95))

        for w in range(n_win):
            wx = win_area_l + w*cell_w + 1
            wy = wt

            if style == 'construction':
                draw.rectangle([wx, wy, wx+win_w, wy+wh], fill=(52,47,42))
                # detalhe de aço (linhas horizontais)
                if wh > 10:
                    for gy in range(wy+3, wy+wh-3, 7):
                        draw.line([(wx+2, gy),(wx+win_w-2, gy)], fill=(72,68,65), width=1)

            elif style == 'glass':
                # gradiente azul glass
                for gy in range(wy, wy+wh):
                    t2 = (gy - wy) / max(wh-1, 1)
                    r2 = lerp(45, 70, t2)
                    g2 = lerp(125, 155, t2)
                    b2 = lerp(195, 215, t2)
                    draw.line([(wx, gy),(wx+win_w, gy)], fill=(r2,g2,b2))
                # reflexo diagonal (canto superior esquerdo)
                ref_w = win_w // 3
                ref_h = wh // 2
                for ry2 in range(wy, wy+ref_h):
                    t3 = (ry2 - wy) / max(ref_h-1, 1)
                    rx_end = wx + int(ref_w * (1 - t3*0.6))
                    draw.line([(wx, ry2),(rx_end, ry2)], fill=(130,195,240))

            else:  # night
                lit = rng.random() < 0.42
                if lit:
                    # janela acesa — gradiente quente
                    for gy in range(wy, wy+wh):
                        t2 = (gy - wy) / max(wh-1, 1)
                        draw.point((wx, gy), fill=(255, lerp(230,195,t2), lerp(100,60,t2)))
                    draw.rectangle([wx, wy, wx+win_w, wy+wh], fill=(255,215,88))
                    # brilho suave
                    for expand in range(3, 0, -1):
                        gc = (255, lerp(215,120, expand/3), lerp(88,20,expand/3))
                        draw.rectangle([wx-expand, wy-expand, wx+win_w+expand, wy+wh+expand],
                                       outline=gc)
                else:
                    draw.rectangle([wx, wy, wx+win_w, wy+wh], fill=(12,16,32))

    # Borda vertical esquerda (highlight)
    draw.rectangle([BLD_L, top_y, BLD_L+3, BLD_BOTTOM], fill=(180,175,170))

# ── Legenda ────────────────────────────────────────────────────────
def add_subtitle(img, text, font_size=58):
    overlay = Image.new('RGBA', img.size, (0,0,0,0))
    d = ImageDraw.Draw(overlay)
    max_text_w = W - 100  # margem de 50px cada lado

    lines = text.strip().split('\n')
    # Ajustar fonte para caber na largura
    fs = font_size
    while fs > 28:
        font = get_font(fs)
        too_wide = False
        for line in lines:
            try:
                bbox = d.textbbox((0,0), line, font=font)
                tw = bbox[2] - bbox[0]
            except:
                tw = len(line) * (fs // 2)
            if tw > max_text_w:
                too_wide = True
                break
        if not too_wide:
            break
        fs -= 4

    font = get_font(fs)
    lh = fs + 14
    total_h = len(lines) * lh + 32
    bar_top = H - total_h - 95
    d.rectangle([45, bar_top, W-45, H-80], fill=(0,0,0,185))

    for i, line in enumerate(lines):
        y = bar_top + 16 + i * lh
        try:
            bbox = d.textbbox((0,0), line, font=font)
            tw = bbox[2] - bbox[0]
        except:
            tw = len(line) * (fs // 2)
        x = (W - tw) // 2
        d.text((x+2, y+2), line, fill=(0,0,0,200), font=font)
        d.text((x, y), line, fill=(255,255,255,255), font=font)

    out = Image.alpha_composite(img.convert('RGBA'), overlay)
    return out.convert('RGB')

def add_title_card(img, text, y_pos=None, color=(255,215,50)):
    overlay = Image.new('RGBA', img.size, (0,0,0,0))
    d = ImageDraw.Draw(overlay)
    font = get_font(88)
    lines = text.strip().split('\n')
    lh = 100
    total_h = len(lines) * lh
    if y_pos is None:
        y_pos = H // 2 - total_h // 2
    for i, line in enumerate(lines):
        y = y_pos + i * lh
        try:
            bbox = d.textbbox((0,0), line, font=font)
            tw = bbox[2] - bbox[0]
        except:
            tw = len(line) * 44
        x = (W - tw) // 2
        d.text((x+3, y+3), line, fill=(0,0,0,200), font=font)
        d.text((x, y), line, fill=color+(255,), font=font)
    out = Image.alpha_composite(img.convert('RGBA'), overlay)
    return out.convert('RGB')

# ── Gerador de cena ───────────────────────────────────────────────
def generate_frame(n_floors, sky_type, scene_type, style='construction', rng_seed=0):
    img = Image.new('RGB', (W, H), (100,150,200))
    draw = ImageDraw.Draw(img)

    draw_sky(draw, sky_type)
    draw_city(draw, sky_type)

    if sky_type == 'night':
        draw_night_elements(draw)

    draw_ground(draw, scene_type)

    # Elementos específicos de cena
    if scene_type == 'clearing':
        draw_bulldozer(draw)
        draw_fence(draw)
    elif scene_type == 'excavation':
        draw_pit(draw)
        draw_excavator(draw)
    elif scene_type == 'foundation':
        draw_foundation(draw)
    elif scene_type in ('construction',):
        draw_fence(draw)
        if n_floors > 0:
            draw_scaffolding(draw, n_floors)
            draw_crane(draw, n_floors)
    elif scene_type == 'finished':
        draw_trees(draw)

    draw_building(draw, n_floors, style=style, rng_seed=rng_seed)

    # Nuvens (dia e amanhecer) — forma realista com múltiplas elipses
    if sky_type in ('day', 'dawn'):
        cloud_color = (240,243,248) if sky_type == 'day' else (255,230,210)
        cloud_specs = [
            (160, 100, [(0,0,120,55),(-40,15,80,40),(40,15,90,40),(-15,30,100,45)]),
            (540, 155, [(0,0,150,60),(-50,18,100,42),(50,18,110,42),(-20,32,120,48),(30,28,80,36)]),
            (870, 90,  [(0,0,130,52),(-45,16,88,38),(45,16,95,38),(-18,28,110,44)]),
            (300, 230, [(0,0,100,45),(-35,14,70,35),(35,14,75,35),(-15,24,85,38)]),
        ]
        for (cx, cy, parts) in cloud_specs:
            for (dx, dy, pw, ph) in parts:
                x, y = cx+dx, cy+dy
                draw.ellipse([x-pw//2, y-ph//2, x+pw//2, y+ph//2], fill=cloud_color)

    return img

# ── Áudio TTS ─────────────────────────────────────────────────────
NARRATION_SEGMENTS = [
    # (início_s, texto)
    (0.0,  "Você acredita que tudo isso começou com um terreno vazio?"),
    (3.2,  "Era apenas um terreno. Vazio. Silencioso. Com um potencial imenso."),
    (8.5,  "As máquinas chegaram. E a transformação começou."),
    (13.8, "Escavações profundas. Preparando o terreno para algo extraordinário."),
    (19.5, "As fundações foram lançadas. A base que sustentará quarenta andares."),
    (25.2, "Aço e concreto se uniram. Uma sinfonia de engenharia e precisão."),
    (30.5, "Os primeiros andares ganharam forma. O horizonte começou a mudar."),
    (36.0, "Andar por andar. O prédio crescia desafiando o céu."),
    (41.5, "Quarenta andares. Uma estrutura colossal erguida onde antes só havia terra."),
    (47.0, "A fachada de vidro tomou forma. Refletindo a luz e o futuro da cidade."),
    (53.5, "Os acabamentos finais. O paisagismo. A vida chegando ao redor."),
    (58.5, "Quarenta andares. Uma obra gigantesca. E tudo começou com um simples terreno vazio."),
]

def try_gtts_segment(text, path):
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang='pt', tld='com.br', slow=False)
        mp3_path = path.replace('.wav', '.mp3')
        tts.save(mp3_path)
        # Converter mp3 → wav
        subprocess.run(['ffmpeg', '-y', '-i', mp3_path, '-ar', '44100', '-ac', '1', path],
                       capture_output=True, timeout=30)
        os.remove(mp3_path)
        return os.path.exists(path) and os.path.getsize(path) > 1000
    except Exception as e:
        print(f"gTTS falhou: {e}")
        return False

def generate_silence_wav(path, duration_s, sample_rate=44100):
    n = int(duration_s * sample_rate)
    data = b'\x00\x00' * n
    with wave.open(path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(data)

# ── Música ambiente ────────────────────────────────────────────────
def generate_music(duration_s, path, sample_rate=44100):
    print("Gerando música ambiente...")
    t = np.linspace(0, duration_s, int(duration_s * sample_rate), endpoint=False)

    # Drone de baixo
    bass = 0.18 * np.sin(2*np.pi*55*t) + 0.10 * np.sin(2*np.pi*110*t)

    # Pad (pad cinematográfico com harmônicos)
    pad = (0.09 * np.sin(2*np.pi*220*t) +
           0.07 * np.sin(2*np.pi*330*t) +
           0.05 * np.sin(2*np.pi*440*t) +
           0.03 * np.sin(2*np.pi*550*t))

    # Modulação suave (vibrato)
    lfo = 0.4 + 0.6 * np.sin(2*np.pi*0.07*t)
    pad *= lfo

    # Crescimento dramático (cresce nos últimos 20s)
    grow_env = np.ones_like(t)
    t_start_grow = max(0, duration_s - 22)
    idx_grow = int(t_start_grow * sample_rate)
    grow_len = len(t) - idx_grow
    if grow_len > 0:
        grow_env[idx_grow:] = np.linspace(1.0, 2.5, grow_len)

    # Envelope geral (fade in 2s, fade out 2s)
    fade_len = int(2 * sample_rate)
    env = np.ones_like(t)
    env[:fade_len] = np.linspace(0, 1, fade_len)
    env[-fade_len:] = np.linspace(1, 0, fade_len)

    music = (bass + pad) * grow_env * env
    music = music / np.max(np.abs(music) + 1e-9) * 0.6  # normaliza

    # Adiciona percussão suave (clique a cada ~4 beats, BPM~70)
    beat_interval = int(sample_rate * 60 / 70)
    for idx_b in range(0, len(t), beat_interval):
        click_len = int(0.04 * sample_rate)
        end_b = min(idx_b + click_len, len(t))
        decay = np.exp(-np.linspace(0, 8, end_b-idx_b))
        music[idx_b:end_b] += 0.08 * np.sin(2*np.pi*180*np.linspace(0, 0.04, end_b-idx_b)) * decay

    music = np.clip(music, -1, 1)
    pcm = (music * 32767).astype(np.int16)

    with wave.open(path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm.tobytes())
    print(f"  Música salva: {path}")

# ── Mix de áudio ──────────────────────────────────────────────────
def mix_audio(narration_path, music_path, output_path, total_dur):
    """Mixa narração (volume alto) com música de fundo (volume baixo)."""
    # Verificar se a narração existe e tem conteúdo
    has_narration = os.path.exists(narration_path) and os.path.getsize(narration_path) > 5000

    if has_narration:
        cmd = [
            'ffmpeg', '-y',
            '-i', music_path,
            '-i', narration_path,
            '-filter_complex',
            f'[0:a]volume=0.22,apad=pad_dur={total_dur}[m];'
            f'[1:a]volume=1.4,apad=pad_dur={total_dur}[n];'
            f'[m][n]amix=inputs=2:duration=first:dropout_transition=2[out]',
            '-map', '[out]',
            '-t', str(total_dur),
            '-ar', '44100', '-ac', '2',
            output_path
        ]
    else:
        print("  Sem narração, usando apenas música")
        cmd = [
            'ffmpeg', '-y',
            '-i', music_path,
            '-filter_complex', f'[0:a]volume=0.8,apad=pad_dur={total_dur}[out]',
            '-map', '[out]',
            '-t', str(total_dur),
            '-ar', '44100', '-ac', '2',
            output_path
        ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        print(f"  Aviso mix: {result.stderr[-300:]}")
    return os.path.exists(output_path)

# ── Montagem final com FFmpeg (via pipe) ──────────────────────────
def write_video_ffmpeg(frame_gen, total_frames, audio_path, output_path, fps=FPS):
    """Envia frames PIL via pipe para o FFmpeg e gera o MP4 final."""
    cmd = [
        'ffmpeg', '-y',
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-s', f'{W}x{H}',
        '-pix_fmt', 'rgb24',
        '-r', str(fps),
        '-i', 'pipe:0',
        '-i', audio_path,
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-crf', '18',
        '-pix_fmt', 'yuv420p',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-movflags', '+faststart',
        '-shortest',
        output_path
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

    start_t = time.time()
    for fi, (frame_img, _) in enumerate(frame_gen):
        proc.stdin.write(frame_img.tobytes())
        if fi % 150 == 0:
            pct = fi / total_frames * 100
            elapsed = time.time() - start_t
            fps_actual = fi / max(elapsed, 0.001)
            eta = (total_frames - fi) / max(fps_actual, 0.1)
            print(f"  Frame {fi}/{total_frames} ({pct:.0f}%)  ETA: {eta:.0f}s")

    proc.stdin.close()
    stderr = proc.stderr.read().decode('utf-8', errors='replace')
    proc.wait()
    if proc.returncode != 0:
        print(f"FFmpeg erro: {stderr[-500:]}")
    else:
        print(f"  Vídeo salvo: {output_path}")
    return proc.returncode == 0

# ── Definição das cenas ───────────────────────────────────────────
# Cada cena: (dur_s, sky, scene_type, style, floor_start, floor_end, subtitle, special)
SCENES = [
    # Gancho: prédio finalizado primeiro
    (3.0,  'golden', 'finished',    'glass',         40, 40, 'Você acredita que tudo isso\ncomeçou com um terreno vazio?', 'title_hook'),
    # Terreno vazio
    (5.0,  'dawn',   'empty',       'construction',   0,  0, 'Era apenas um terreno.\nVazio. Silencioso.', ''),
    # Limpeza
    (5.0,  'dawn',   'clearing',    'construction',   0,  0, 'As máquinas chegaram.\nA transformação começou.', ''),
    # Escavação
    (5.5,  'day',    'excavation',  'construction',   0,  0, 'Escavações profundas.\nPreparando o futuro.', ''),
    # Fundações
    (5.5,  'day',    'foundation',  'construction',   0,  0, 'As fundações foram lançadas.\nA base de tudo.', ''),
    # Cresce 1→6
    (5.0,  'day',    'construction','construction',   1,  6, 'Aço e concreto unidos.\nEngenharia e precisão.', 'grow'),
    # Cresce 6→14
    (5.0,  'day',    'construction','construction',   6, 14, 'Os primeiros andares.\nO horizonte começa a mudar.', 'grow'),
    # Cresce 14→26
    (5.0,  'day',    'construction','construction',  14, 26, 'Andar por andar.\nDesafiando o céu.', 'grow'),
    # Cresce 26→40
    (5.0,  'day',    'construction','construction',  26, 40, 'Quarenta andares.\nUma estrutura colossal.', 'grow'),
    # Fachada de vidro
    (6.0,  'day',    'construction','glass',         40, 40, 'A fachada de vidro.\nRefletindo o futuro.', ''),
    # Acabamentos e paisagismo
    (5.0,  'golden', 'finished',   'glass',          40, 40, 'Os acabamentos finais.\nA vida chegando ao redor.', ''),
    # Noite — finalização
    (10.0, 'night',  'finished',   'night',          40, 40, 'Quarenta andares. Uma obra gigantesca.\nE tudo começou com um terreno vazio.', 'night_title'),
]

TOTAL_DURATION = sum(s[0] for s in SCENES)
TOTAL_FRAMES   = int(TOTAL_DURATION * FPS)

def frame_generator():
    """Gera todos os frames do vídeo como imagens PIL."""
    rng_night = random.Random(55)  # seed fixo para janelas noturnas

    for (dur, sky, scene_type, style, fl_start, fl_end, subtitle, special) in SCENES:
        n_frames_scene = int(dur * FPS)

        for fi in range(n_frames_scene):
            t = fi / max(n_frames_scene - 1, 1)

            # Calcular número de andares para este frame
            if special == 'grow':
                n_floors = int(fl_start + (fl_end - fl_start) * t)
            else:
                n_floors = fl_end

            # Seed para janelas noturnas (fixo dentro da cena)
            seed = rng_night.randint(0, 999) if fi == 0 else seed

            img = generate_frame(n_floors, sky, scene_type, style, rng_seed=seed)
            img = add_subtitle(img, subtitle)

            # Cards especiais
            if special == 'title_hook' and fi < n_frames_scene * 0.9:
                pass  # legenda já está
            elif special == 'night_title' and fi > n_frames_scene * 0.55:
                img = add_title_card(img, 'DO ZERO\nAO IMPOSSÍVEL.', y_pos=H//2 - 160)

            yield img, fi

def main():
    print("=" * 60)
    print("PRODUÇÃO: Prédio 40 Andares")
    print(f"Resolução: {W}x{H} | Duração: {TOTAL_DURATION:.1f}s | FPS: {FPS}")
    print(f"Total de frames: {TOTAL_FRAMES}")
    print("=" * 60)

    # 1. Gerar música
    generate_music(TOTAL_DURATION + 2, MUSIC_FILE)

    # 2. Gerar narração TTS
    print("\nGerando narração TTS...")
    full_text = " ".join(t for _, t in NARRATION_SEGMENTS)
    tts_ok = try_gtts_segment(full_text, AUDIO_FILE)
    if not tts_ok:
        print("  TTS não disponível — usando silêncio")
        generate_silence_wav(AUDIO_FILE, TOTAL_DURATION + 2)

    # 3. Mixar áudio
    print("\nMixando áudio...")
    mix_ok = mix_audio(AUDIO_FILE, MUSIC_FILE, MIX_FILE, TOTAL_DURATION + 1)
    audio_to_use = MIX_FILE if mix_ok else MUSIC_FILE

    # 4. Gerar e encodar vídeo
    print(f"\nGerando vídeo ({TOTAL_FRAMES} frames)...")
    t0 = time.time()
    ok = write_video_ffmpeg(frame_generator(), TOTAL_FRAMES, audio_to_use, OUTPUT_FILE)
    elapsed = time.time() - t0
    print(f"\nTempo total: {elapsed:.1f}s")

    if ok and os.path.exists(OUTPUT_FILE):
        size_mb = os.path.getsize(OUTPUT_FILE) / 1_048_576
        print(f"\n✓ VÍDEO GERADO COM SUCESSO!")
        print(f"  Arquivo: {OUTPUT_FILE}")
        print(f"  Tamanho: {size_mb:.1f} MB")
        print(f"  Duração: {TOTAL_DURATION:.1f}s")
    else:
        print("\n✗ Falha na geração do vídeo")
        sys.exit(1)

if __name__ == '__main__':
    main()
