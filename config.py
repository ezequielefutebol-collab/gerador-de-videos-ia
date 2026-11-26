import os

# =============================================================================
# CONFIGURAÇÃO DO SISTEMA
# Para ativar funcionalidades avançadas, insira suas chaves de API abaixo
# ou defina como variáveis de ambiente.
# =============================================================================

# ANTHROPIC (Claude AI) — para gerar receita e roteiro com IA
# Obtenha em: https://console.anthropic.com/
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# PEXELS — para buscar vídeos e imagens de alta qualidade (gratuito)
# Obtenha em: https://www.pexels.com/api/
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

# =============================================================================
# CONFIGURAÇÕES DO VÍDEO
# =============================================================================
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 30
VIDEO_FORMAT = "mp4"

# Duração padrão por cena (em segundos) — ajustado automaticamente
SCENE_DURATION_DEFAULT = 5.0
SCENE_DURATION_MIN = 3.0
SCENE_DURATION_MAX = 10.0

# Pasta de saída dos vídeos
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")

# =============================================================================
# CONFIGURAÇÕES DE ÁUDIO
# =============================================================================
# Volume da trilha sonora (0.0 a 1.0) — a voz fica em cima
MUSIC_VOLUME = 0.15
# Volume dos efeitos sonoros
SFX_VOLUME = 0.4
# Volume da narração
NARRATION_VOLUME = 1.0

# Voz do edge-tts para português brasileiro
# Opções: pt-BR-FranciscaNeural (feminina), pt-BR-AntonioNeural (masculino)
TTS_VOICE = "pt-BR-FranciscaNeural"
TTS_RATE = "+5%"   # velocidade (+5% ligeiramente mais rápido)
TTS_PITCH = "+0Hz"  # tom neutro

# =============================================================================
# FONTES
# =============================================================================
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SUBTITLE_SIZE = 52
FONT_TITLE_SIZE = 80
