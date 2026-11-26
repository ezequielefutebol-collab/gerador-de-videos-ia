# 🎬 Gerador de Vídeos de Receitas

Sistema automatizado que transforma o nome de qualquer receita em um vídeo profissional vertical (1080x1920) pronto para TikTok, Instagram Reels e YouTube Shorts.

## Como usar

### 1. Instale as dependências (apenas uma vez)

```bash
pip3 install flask anthropic edge-tts gtts requests pillow moviepy --break-system-packages
```

### 2. Inicie o servidor

```bash
cd gerador-de-videos-ia
python3 app.py
```

### 3. Acesse no navegador

```
http://localhost:5000
```

Digite o nome de uma receita e clique em **Gerar Vídeo**.

---

## Ativar qualidade máxima (opcional)

### Claude AI — receitas personalizadas para qualquer prato

1. Acesse https://console.anthropic.com/
2. Crie uma conta e gere uma API Key
3. No terminal, antes de iniciar:
   ```bash
   export ANTHROPIC_API_KEY="sua-chave-aqui"
   python3 app.py
   ```

### Pexels — imagens reais de alta qualidade

1. Acesse https://www.pexels.com/api/
2. Crie conta gratuita e gere API Key
3. No terminal:
   ```bash
   export PEXELS_API_KEY="sua-chave-aqui"
   python3 app.py
   ```

**Sem essas chaves**, o sistema funciona com receitas embutidas e visuais gerados localmente.

---

## O que o sistema faz automaticamente

1. Cria receita completa com ingredientes e etapas
2. Divide em 6-10 cenas com narração
3. Gera voz em português brasileiro (gTTS / Google)
4. Busca imagens ou gera fundos cinematográficos
5. Adiciona legendas sincronizadas estilo TikTok
6. Gera trilha sonora e efeitos sonoros
7. Aplica efeito Ken Burns (zoom + movimentos de câmera)
8. Renderiza vídeo MP4 final com FFmpeg

## Estrutura do projeto

```
gerador-de-videos-ia/
├── app.py               # Interface web Flask
├── config.py            # Configurações e API keys
├── src/
│   ├── pipeline.py      # Orquestrador principal
│   ├── recipe_generator.py   # Gera receita e roteiro
│   ├── tts_engine.py         # Síntese de voz
│   ├── visual_provider.py    # Imagens e visuais
│   ├── subtitle_generator.py # Legendas animadas
│   ├── audio_composer.py     # Mixagem de áudio
│   └── video_composer.py     # Composição de vídeo
└── output/              # Vídeos gerados
```

## Formato de saída

- Resolução: 1080×1920 (9:16 vertical)
- FPS: 30
- Codec: H.264
- Áudio: AAC 192kbps
- Duração: 45-75 segundos (adaptável)
