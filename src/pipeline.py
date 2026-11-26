"""
Pipeline principal: orquestra todas as etapas de criação do vídeo.
"""
import os
import sys
import json
import tempfile
import shutil
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config
from src.recipe_generator import gerar_receita
from src.tts_engine import sintetizar_voz, obter_duracao_audio
from src.audio_composer import (
    gerar_musica_sintetizada, gerar_efeito_sonoro, mixar_trilha_completa
)
from src.video_composer import gerar_cenas_video, renderizar_video_final

os.makedirs(config.OUTPUT_DIR, exist_ok=True)


def executar_pipeline(nome_receita: str, callback=None) -> dict:
    """
    Pipeline completo: nome_receita → vídeo MP4 final.

    callback(mensagem, progresso_0_a_1) é chamado em cada etapa.
    Retorna dict com 'sucesso', 'video_path', 'receita', 'duracao', 'erro'.
    """

    def prog(msg, p):
        print(f"[Pipeline] {msg} ({int(p*100)}%)")
        if callback:
            callback(msg, p)

    dir_temp = tempfile.mkdtemp(prefix="receita_video_")

    try:
        # ─────────────────────────────────────────
        # ETAPA 1: Gerar receita e roteiro
        # ─────────────────────────────────────────
        prog("Criando receita e roteiro...", 0.02)
        receita = gerar_receita(nome_receita)

        titulo = receita.get("titulo", nome_receita)
        cenas = receita.get("cenas", [])

        prog(f"Receita: {titulo} — {len(cenas)} cenas", 0.05)

        # ─────────────────────────────────────────
        # ETAPA 2: Narração por cena
        # ─────────────────────────────────────────
        prog("Gerando narração por voz...", 0.08)

        narracoes = []  # (path_audio, duracao, timestamp)
        tempo_acumulado = 0.0

        for i, cena in enumerate(cenas):
            texto = cena.get("narracao", "")
            if not texto:
                narracoes.append(None)
                continue

            arq = os.path.join(dir_temp, f"narracao_{i:02d}.mp3")
            sintetizar_voz(texto, arq)
            dur = obter_duracao_audio(arq)

            # Ajusta duração da cena para corresponder à narração (+ margem)
            cena["duracao_seg"] = max(dur + 1.0, cena.get("duracao_seg", 5.0))

            narracoes.append({"path": arq, "duracao": dur, "timestamp": tempo_acumulado})
            tempo_acumulado += cena["duracao_seg"]

            prog(f"Voz cena {i+1}/{len(cenas)}...", 0.08 + (i+1)/len(cenas)*0.12)

        duracao_total = tempo_acumulado
        prog(f"Duração total: {duracao_total:.1f}s", 0.20)

        # ─────────────────────────────────────────
        # ETAPA 3: Concatenar narrações
        # ─────────────────────────────────────────
        prog("Montando faixa de narração...", 0.22)
        narracao_completa = os.path.join(dir_temp, "narracao_completa.mp3")
        _concatenar_audios(narracoes, narracao_completa, duracao_total)

        # ─────────────────────────────────────────
        # ETAPA 4: Efeitos sonoros
        # ─────────────────────────────────────────
        prog("Gerando efeitos sonoros...", 0.25)
        sfx_entries = []

        for i, (cena, info_narracao) in enumerate(zip(cenas, narracoes)):
            sfx_tipo = cena.get("efeito_sonoro", "")
            if not sfx_tipo or info_narracao is None:
                continue

            sfx_path = os.path.join(dir_temp, f"sfx_{i:02d}.wav")
            timestamp = info_narracao["timestamp"] + 0.3
            gerar_efeito_sonoro(sfx_tipo, sfx_path, duracao=1.5)
            sfx_entries.append((sfx_path, timestamp))

        # ─────────────────────────────────────────
        # ETAPA 5: Trilha sonora
        # ─────────────────────────────────────────
        prog("Gerando trilha sonora...", 0.28)
        musica_path = os.path.join(dir_temp, "musica.wav")
        estilo = receita.get("musica_estilo", "upbeat cooking")
        gerar_musica_sintetizada(duracao_total + 2, musica_path, estilo)

        # ─────────────────────────────────────────
        # ETAPA 6: Mixagem de áudio
        # ─────────────────────────────────────────
        prog("Mixando áudio final...", 0.32)
        audio_final = os.path.join(dir_temp, "audio_final.aac")
        mixar_trilha_completa(
            narracao_completa,
            musica_path,
            sfx_entries,
            audio_final,
            duracao_total
        )

        # ─────────────────────────────────────────
        # ETAPA 7: Gerar frames de vídeo
        # ─────────────────────────────────────────
        prog("Gerando frames do vídeo...", 0.35)
        dir_frames = os.path.join(dir_temp, "frames")

        def frame_callback(msg, p):
            prog(msg, 0.35 + p * 0.45)

        metadados = gerar_cenas_video(receita, dir_frames, callback=frame_callback)

        # ─────────────────────────────────────────
        # ETAPA 8: Renderização final
        # ─────────────────────────────────────────
        prog("Renderizando vídeo final...", 0.82)

        # Nome do arquivo de saída
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_seguro = nome_receita.lower()
        for c in " /\\:*?\"<>|":
            nome_seguro = nome_seguro.replace(c, "_")
        video_filename = f"{nome_seguro}_{timestamp_str}.mp4"
        video_path = os.path.join(config.OUTPUT_DIR, video_filename)

        renderizar_video_final(dir_frames, audio_final, video_path, callback=frame_callback)

        prog("Vídeo criado com sucesso!", 1.0)

        return {
            "sucesso": True,
            "video_path": video_path,
            "video_filename": video_filename,
            "receita": receita,
            "duracao": metadados["duracao_total"],
            "total_frames": metadados["total_frames"],
            "titulo": titulo,
            "erro": None
        }

    except Exception as e:
        import traceback
        erro = f"{type(e).__name__}: {e}"
        print(f"[Pipeline] ERRO: {erro}")
        traceback.print_exc()
        return {
            "sucesso": False,
            "video_path": None,
            "video_filename": None,
            "receita": None,
            "duracao": 0,
            "titulo": nome_receita,
            "erro": erro
        }

    finally:
        # Limpeza dos arquivos temporários
        try:
            shutil.rmtree(dir_temp, ignore_errors=True)
        except:
            pass


def _concatenar_audios(narracoes: list, caminho_saida: str, duracao_total: float):
    """Concatena narrações com silêncios entre elas usando FFmpeg."""
    import subprocess

    # Cria arquivo de lista para ffmpeg
    lista_path = caminho_saida + ".txt"
    linhas = []

    for info in narracoes:
        if info is None:
            continue
        linhas.append(f"file '{info['path']}'")

    if not linhas:
        # Cria silêncio
        cmd = [
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", f"anullsrc=r=44100:cl=mono",
            "-t", str(duracao_total),
            "-c:a", "libmp3lame",
            caminho_saida
        ]
        subprocess.run(cmd, capture_output=True)
        return

    with open(lista_path, "w") as f:
        f.write("\n".join(linhas))

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", lista_path,
        "-c:a", "copy",
        caminho_saida
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    try:
        os.unlink(lista_path)
    except:
        pass

    if result.returncode != 0:
        # Fallback: concatenação simples via amix
        inputs = []
        for info in narracoes:
            if info:
                inputs += ["-i", info["path"]]

        n = len([i for i in narracoes if i])
        cmd2 = [
            "ffmpeg", "-y",
        ] + inputs + [
            "-filter_complex",
            f"concat=n={n}:v=0:a=1[out]",
            "-map", "[out]",
            caminho_saida
        ]
        subprocess.run(cmd2, capture_output=True)
