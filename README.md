# 🎬 Gerador de Vídeos IA — Reels & TikTok

Sistema automatizado de criação de vídeos verticais (9:16) para **Instagram Reels** e **TikTok**, com animações de texto, efeitos cinematográficos, transições e suporte a música.

---

## ✨ Funcionalidades

| Recurso | Detalhe |
|---|---|
| **4 estilos visuais** | Motivacional, Cinematográfico, Minimalista, Energia |
| **Animações de texto** | slideUp, fadeIn, scale, typewriter, bounce |
| **Efeito Ken Burns** | Zoom suave no fundo (imagem ou vídeo) |
| **Efeitos cinematográficos** | Letterbox, vignette, glow lines, flash |
| **Transições** | Fade in/out no início e fim do vídeo |
| **Legendas** | Subtítulo com fade automático |
| **Música** | Mix via FFmpeg (MP3, WAV, AAC) |
| **Exportação** | MP4 H.264, otimizado para redes sociais |
| **Formato** | 1080×1920 (9:16) vertical, 10–30 segundos |
| **CLI interativa** | Interface de perguntas guiadas |
| **Remotion Studio** | Preview em tempo real no navegador |

---

## 📦 Pré-requisitos

- **Node.js** 18+ (recomendado 20+)
- **FFmpeg** instalado no sistema
- **npm** 8+

### Instalar FFmpeg

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows (Chocolatey)
choco install ffmpeg
```

---

## 🚀 Instalação

```bash
git clone https://github.com/seu-usuario/gerador-de-videos-ia.git
cd gerador-de-videos-ia
npm install
```

---

## 🎮 Uso

### 1. Interface CLI (recomendado)

```bash
npm run generate
```

O assistente vai perguntar:
1. **Estilo** do vídeo
2. **Duração** (10–30 segundos)
3. **Frases** e animação de cada uma
4. **Legenda** opcional
5. **Imagem/vídeo de fundo** (opcional)
6. **Música** (opcional)
7. **Nome do arquivo de saída**

O vídeo é salvo em `output/`.

---

### 2. Remotion Studio (preview visual)

```bash
npm run studio
```

Abre o navegador em `http://localhost:3000` com preview em tempo real.
Você pode editar as props diretamente pelo painel da interface.

---

### 3. Render direto pelo CLI do Remotion

```bash
# Renderiza com as props padrão de cada estilo
npm run render:motivacional
npm run render:cinematografico
npm run render:minimalista
npm run render:energia
```

---

## 🎨 Estilos de Vídeo

### 💜 Motivacional
- Fundo: gradiente roxo/azul (ou imagem com Ken Burns)
- Texto: Impact em caixa alta, branco
- Detalhe: linha laranja com glow
- Animação padrão: **slideUp**

### 🎬 Cinematográfico
- Fundo: escuro (ou imagem desfocada)
- Texto: Georgia itálico, bege claro
- Detalhe: barra dourada, letterbox preto
- Animação padrão: **fadeIn**

### ⚪ Minimalista
- Fundo: branco/cinza claro
- Texto: Helvetica fino, preto
- Detalhe: linhas finas cinza
- Animação padrão: **slideUp**

### ⚡ Energia
- Fundo: gradiente laranja/vermelho/amarelo
- Texto: Arial Black em caixa alta, branco
- Detalhe: borda ciano pulsante, flash na entrada
- Animação padrão: **bounce**

---

## 📁 Estrutura do Projeto

```
gerador-de-videos-ia/
├── src/
│   ├── index.ts                   # Entry point Remotion
│   ├── Root.tsx                   # Registra as composições
│   ├── types/index.ts             # Tipos TypeScript
│   ├── styles/themes.ts           # Configuração dos 4 temas
│   ├── components/
│   │   ├── AnimatedText.tsx       # Animações de texto
│   │   ├── BackgroundMedia.tsx    # Fundo com Ken Burns
│   │   ├── Effects.tsx            # Letterbox, vignette, glow, flash
│   │   └── Subtitle.tsx           # Legendas com fade
│   └── compositions/
│       ├── MotivationalReel.tsx   # Estilo motivacional
│       ├── CinematicReel.tsx      # Estilo cinematográfico
│       ├── MinimalistReel.tsx     # Estilo minimalista
│       └── EnergyReel.tsx         # Estilo energia
├── cli/
│   ├── index.ts                   # CLI interativa (prompts)
│   ├── renderer.ts                # Renderização via Remotion
│   └── ffmpeg.ts                  # Mixagem de áudio via FFmpeg
├── assets/
│   ├── backgrounds/               # Coloque imagens/vídeos aqui
│   └── music/                     # Coloque músicas aqui
└── output/                        # Vídeos gerados
```

---

## ⚙️ Personalização via Código

Edite `src/styles/themes.ts` para mudar cores, fontes e tamanhos de cada estilo.

Exemplo — mudar a cor de destaque do estilo Motivacional:
```typescript
motivacional: {
  accentColor: "#00ff88",  // verde neon
  titleSize: 96,            // texto maior
  ...
}
```

---

## 🤖 Integração Futura com IA

O projeto está preparado para integração com APIs de geração por IA.
O tipo `VideoConfig` em `src/types/index.ts` aceita toda a configuração necessária.

Exemplo de integração com OpenAI para gerar frases automaticamente:

```typescript
// future: src/ai/generator.ts
import OpenAI from "openai";

export async function generatePhrases(tema: string): Promise<string[]> {
  const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
  const response = await openai.chat.completions.create({
    model: "gpt-4o",
    messages: [
      {
        role: "user",
        content: `Gere 3 frases motivacionais curtas sobre: ${tema}. Uma por linha.`,
      },
    ],
  });
  return response.choices[0].message.content?.split("\n").filter(Boolean) ?? [];
}
```

Para integrar com APIs de vídeo IA (Runway, Kling, Pika):

```typescript
// future: src/ai/video-generator.ts
export async function generateBackgroundVideo(prompt: string): Promise<string> {
  // Chame a API aqui e retorne o caminho do vídeo
  // O resultado é passado como backgroundVideo no VideoConfig
}
```

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Versão | Uso |
|---|---|---|
| [Remotion](https://remotion.dev) | 4.x | Composição de vídeo com React |
| FFmpeg | 6.x | Mixagem de áudio e otimização |
| TypeScript | 5.x | Tipagem estática |
| React | 18.x | Componentes visuais |
| tsx | 4.x | Execução TypeScript no Node |

---

## 📄 Licença

MIT
