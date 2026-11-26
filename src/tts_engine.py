"""
Motor de síntese de voz usando gTTS (Google TTS — gratuito, sem API key).
Fallback: silêncio se offline.
"""
import os
import sys
import subprocess
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config

# Configura certificados para o proxy do ambiente
os.environ.setdefault("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt")
os.environ.setdefault("REQUESTS_CA_BUNDLE", "/root/.ccr/ca-bundle.crt")


def sintetizar_voz(texto: str, caminho_saida: str = None) -> str:
    """
    Sintetiza texto em áudio MP3 usando gTTS.
    Retorna o caminho do arquivo de áudio gerado.
    """
    if caminho_saida is None:
        tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        caminho_saida = tmp.name
        tmp.close()

    texto_limpo = _preparar_texto(texto)

    try:
        from gtts import gTTS
        tts = gTTS(texto_limpo, lang="pt", tld="com.br", slow=False)
        tts.save(caminho_saida)
        return caminho_saida
    except Exception as e:
        print(f"[TTS] Erro gTTS: {e}. Usando silêncio.")
        return _criar_silencio(caminho_saida, _estimar_duracao(texto))


def _preparar_texto(texto: str) -> str:
    """Prepara o texto para melhor síntese de voz."""
    texto = texto.replace("*", "").replace("#", "").replace("_", " ")
    return texto.strip()


def _estimar_duracao(texto: str) -> float:
    """Estima duração do áudio pela quantidade de palavras (~2.5 palavras/segundo)."""
    palavras = len(texto.split())
    return max(2.0, palavras / 2.5)


def _criar_silencio(caminho: str, duracao_seg: float) -> str:
    """Cria arquivo de áudio silencioso usando ffmpeg."""
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"anullsrc=r=44100:cl=mono",
        "-t", str(duracao_seg),
        "-c:a", "libmp3lame",
        caminho
    ]
    subprocess.run(cmd, capture_output=True)
    return caminho


def obter_duracao_audio(caminho: str) -> float:
    """Retorna a duração de um arquivo de áudio em segundos."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", caminho],
        capture_output=True, text=True
    )
    try:
        return float(result.stdout.strip())
    except:
        return 3.0
