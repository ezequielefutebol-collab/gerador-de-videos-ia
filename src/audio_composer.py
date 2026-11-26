"""
Compositor de áudio: trilha sonora, efeitos sonoros e narração.
Usa FFmpeg para mixagem profissional.
"""
import os
import sys
import subprocess
import tempfile
import math
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config

ASSETS_DIR = Path(__file__).parent.parent / "assets"
SFX_DIR = ASSETS_DIR / "sfx"
MUSIC_DIR = ASSETS_DIR / "music"


def gerar_musica_sintetizada(duracao: float, caminho_saida: str, estilo: str = "upbeat") -> str:
    """Gera trilha sonora sintética com FFmpeg (tons harmônicos + ritmo)."""

    # Progressões diferentes por estilo
    estilos = {
        "upbeat": {
            "freqs": [220, 277, 330, 415],  # Am pentatônica
            "tempo": 120,
            "envelope": "0:0.1:1:0.8:0.9:0.6:1:0"
        },
        "calm": {
            "freqs": [196, 247, 294, 370],  # Gm
            "tempo": 90,
            "envelope": "0:0.2:1:0.7:0.9:0.5:1:0"
        },
        "energetic": {
            "freqs": [261, 329, 392, 523],  # C maior
            "tempo": 140,
            "envelope": "0:0.05:1:0.9:0.9:0.7:1:0"
        }
    }

    estilo_config = estilos.get("upbeat")
    for key in estilos:
        if key in estilo.lower():
            estilo_config = estilos[key]
            break

    freqs = estilo_config["freqs"]

    # Gera múltiplas camadas de áudio com FFmpeg
    # Camada principal: arpejo suave
    notas_arq = []

    for i, freq in enumerate(freqs):
        tmpf = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmpf.close()

        # Oscilador com envelope ADSR simplificado
        volume = 0.12 if i == 0 else 0.07

        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"sine=frequency={freq}:sample_rate=44100",
            "-t", str(duracao),
            "-af", f"volume={volume},afade=t=in:st=0:d=0.5,afade=t=out:st={duracao-1}:d=1",
            tmpf.name
        ]
        subprocess.run(cmd, capture_output=True)
        notas_arq.append(tmpf.name)

    # Adiciona um beat suave (bump a 60 Hz)
    bump_arq = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    bump_arq.close()
    bpm = estilo_config["tempo"]
    beat_period = 60.0 / bpm

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"sine=frequency=60:sample_rate=44100",
        "-t", str(duracao),
        "-af", f"volume=0.08,afade=t=in:st=0:d=1,afade=t=out:st={duracao-1}:d=1",
        bump_arq.name
    ]
    subprocess.run(cmd, capture_output=True)
    notas_arq.append(bump_arq.name)

    # Mixtura todas as camadas
    inputs = []
    for arq in notas_arq:
        inputs += ["-i", arq]

    n = len(notas_arq)
    amix = f"amix=inputs={n}:duration=first:normalize=0"

    cmd = [
        "ffmpeg", "-y",
    ] + inputs + [
        "-filter_complex", amix,
        "-t", str(duracao),
        caminho_saida
    ]
    subprocess.run(cmd, capture_output=True)

    # Limpa temporários
    for arq in notas_arq:
        try:
            os.unlink(arq)
        except:
            pass

    return caminho_saida


def gerar_efeito_sonoro(tipo: str, caminho_saida: str, duracao: float = 1.0) -> str:
    """Gera efeitos sonoros sintéticos com FFmpeg."""

    efeitos = {
        "knife_cutting": _gerar_sfx_corte,
        "frying":        _gerar_sfx_fritura,
        "mixing":        _gerar_sfx_mistura,
        "water_pour":    _gerar_sfx_agua,
        "sizzle":        _gerar_sfx_fritura,
        "chop":          _gerar_sfx_corte,
    }

    gerador = efeitos.get(tipo)
    if gerador:
        return gerador(caminho_saida, duracao)

    # Efeito genérico: swoosh suave
    return _gerar_sfx_generico(caminho_saida, duracao)


def _gerar_sfx_corte(caminho: str, duracao: float = 0.3) -> str:
    """Som de faca cortando."""
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"sine=frequency=1200:sample_rate=44100",
        "-t", str(duracao),
        "-af", f"volume=0.3,afade=t=in:st=0:d=0.02,afade=t=out:st={duracao*0.3}:d={duracao*0.7}",
        caminho
    ]
    subprocess.run(cmd, capture_output=True)
    return caminho


def _gerar_sfx_fritura(caminho: str, duracao: float = 2.0) -> str:
    """Som de fritura (ruído branco filtrado)."""
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"anoisesrc=color=white:amplitude=0.3:sample_rate=44100",
        "-t", str(duracao),
        "-af", f"bandpass=frequency=2000:width_type=o:w=2,volume=0.2,"
               f"afade=t=in:st=0:d=0.3,afade=t=out:st={duracao-0.5}:d=0.5",
        caminho
    ]
    subprocess.run(cmd, capture_output=True)
    return caminho


def _gerar_sfx_mistura(caminho: str, duracao: float = 1.5) -> str:
    """Som de mistura."""
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"anoisesrc=color=pink:amplitude=0.2:sample_rate=44100",
        "-t", str(duracao),
        "-af", f"volume=0.15,afade=t=in:st=0:d=0.1,afade=t=out:st={duracao-0.3}:d=0.3",
        caminho
    ]
    subprocess.run(cmd, capture_output=True)
    return caminho


def _gerar_sfx_agua(caminho: str, duracao: float = 1.0) -> str:
    """Som de água sendo despejada."""
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"anoisesrc=color=brown:amplitude=0.4:sample_rate=44100",
        "-t", str(duracao),
        "-af", f"highpass=f=800,volume=0.2,"
               f"afade=t=in:st=0:d=0.1,afade=t=out:st={duracao-0.2}:d=0.2",
        caminho
    ]
    subprocess.run(cmd, capture_output=True)
    return caminho


def _gerar_sfx_generico(caminho: str, duracao: float = 0.5) -> str:
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"sine=frequency=440:sample_rate=44100",
        "-t", str(duracao),
        "-af", f"volume=0.1,afade=t=out:st=0:d={duracao}",
        caminho
    ]
    subprocess.run(cmd, capture_output=True)
    return caminho


def mixar_trilha_completa(
    narracao_path: str,
    musica_path: str,
    sfx_entries: list,  # [(path, timestamp_seg), ...]
    caminho_saida: str,
    duracao_total: float
) -> str:
    """
    Mixa narração + música + efeitos sonoros em um único arquivo.

    sfx_entries: lista de (path_sfx, momento_em_segundos)
    """
    inputs = []
    filtros = []
    idx = 0

    # Narração
    inputs += ["-i", narracao_path]
    filtros.append(f"[{idx}:a]volume={config.NARRATION_VOLUME}[narr]")
    idx += 1

    # Música de fundo
    inputs += ["-i", musica_path]
    filtros.append(
        f"[{idx}:a]volume={config.MUSIC_VOLUME},"
        f"afade=t=in:st=0:d=1.5,"
        f"afade=t=out:st={duracao_total-2}:d=2[mus]"
    )
    idx += 1

    streams_para_mix = ["[narr]", "[mus]"]

    # Efeitos sonoros
    for i, (sfx_path, timestamp) in enumerate(sfx_entries):
        if not os.path.exists(sfx_path):
            continue
        inputs += ["-i", sfx_path]
        label = f"sfx{i}"
        filtros.append(
            f"[{idx}:a]volume={config.SFX_VOLUME},"
            f"adelay={int(timestamp*1000)}|{int(timestamp*1000)}[{label}]"
        )
        streams_para_mix.append(f"[{label}]")
        idx += 1

    n_streams = len(streams_para_mix)
    streams_str = "".join(streams_para_mix)
    filtros.append(
        f"{streams_str}amix=inputs={n_streams}:duration=first:normalize=0[out]"
    )

    filter_complex = ";".join(filtros)

    cmd = [
        "ffmpeg", "-y",
    ] + inputs + [
        "-filter_complex", filter_complex,
        "-map", "[out]",
        "-t", str(duracao_total),
        "-c:a", "aac", "-b:a", "192k",
        caminho_saida
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[Audio] Erro na mixagem: {result.stderr[-500:]}")
        # Fallback: retorna só a narração
        cmd2 = [
            "ffmpeg", "-y", "-i", narracao_path,
            "-c:a", "aac", "-b:a", "192k",
            caminho_saida
        ]
        subprocess.run(cmd2, capture_output=True)

    return caminho_saida
