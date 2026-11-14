import chalk from "chalk";
import ora from "ora";
import prompts from "prompts";
import path from "path";
import { existsSync } from "fs";
import { renderVideo } from "./renderer";
import { checkFfmpeg } from "./ffmpeg";
import { VideoConfig, VideoStyle, TextAnimation } from "../src/types/index";

const STYLE_LABELS: Record<VideoStyle, string> = {
  motivacional: "💜 Motivacional — Texto impactante, gradiente vibrante",
  cinematografico: "🎬 Cinematográfico — Dark, letterbox, elegante",
  minimalista: "⚪ Minimalista — Limpo, tipografia moderna",
  energia: "⚡ Energia — Cores vibrantes, animações rápidas",
};

const ANIMATION_LABELS: Record<TextAnimation, string> = {
  slideUp: "Slide Up — desliza de baixo para cima",
  fadeIn: "Fade In — aparece gradualmente",
  scale: "Scale — cresce do centro",
  typewriter: "Typewriter — digita letra por letra",
  bounce: "Bounce — salta na tela",
};

async function askPhrases(): Promise<
  Array<{ text: string; animation: TextAnimation }>
> {
  const phrases: Array<{ text: string; animation: TextAnimation }> = [];
  let adding = true;

  while (adding) {
    const { text } = await prompts({
      type: "text",
      name: "text",
      message: `Texto da frase ${phrases.length + 1} (Enter para parar de adicionar):`,
    });

    if (!text || text.trim() === "") {
      adding = false;
      break;
    }

    const { animation } = await prompts({
      type: "select",
      name: "animation",
      message: "Animação desta frase:",
      choices: Object.entries(ANIMATION_LABELS).map(([value, title]) => ({
        title,
        value,
      })),
    });

    phrases.push({ text: text.trim(), animation: animation as TextAnimation });

    if (phrases.length >= 5) {
      console.log(chalk.yellow("  Máximo de 5 frases atingido."));
      adding = false;
    }
  }

  return phrases.length > 0
    ? phrases
    : [{ text: "Acredite em você!", animation: "slideUp" }];
}

async function main() {
  console.log(
    chalk.bold.magenta("\n╔══════════════════════════════════════╗")
  );
  console.log(
    chalk.bold.magenta("║   🎬 Gerador de Vídeos — Reels/TikTok ║")
  );
  console.log(
    chalk.bold.magenta("╚══════════════════════════════════════╝\n")
  );

  // Check FFmpeg
  const hasFfmpeg = await checkFfmpeg();
  if (!hasFfmpeg) {
    console.log(
      chalk.red("  ✗ FFmpeg não encontrado. Instale com: apt install ffmpeg")
    );
    process.exit(1);
  }

  const { style } = await prompts({
    type: "select",
    name: "style",
    message: "Escolha o estilo do vídeo:",
    choices: (Object.keys(STYLE_LABELS) as VideoStyle[]).map((v) => ({
      title: STYLE_LABELS[v],
      value: v,
    })),
  });

  if (!style) process.exit(0);

  const { duration } = await prompts({
    type: "number",
    name: "duration",
    message: "Duração do vídeo em segundos (10–30):",
    initial: 15,
    validate: (v) =>
      v >= 10 && v <= 30 ? true : "Digite um valor entre 10 e 30",
  });

  console.log(chalk.cyan("\n  📝 Adicione as frases do vídeo:"));
  console.log(chalk.gray("  (Pressione Enter em branco para finalizar)\n"));
  const phrases = await askPhrases();

  const { subtitle } = await prompts({
    type: "text",
    name: "subtitle",
    message: "Legenda/Subtitle (opcional, Enter para pular):",
  });

  const { backgroundImage } = await prompts({
    type: "text",
    name: "backgroundImage",
    message: "Caminho da imagem de fundo (opcional, Enter para usar gradiente):",
  });

  const { backgroundVideo } = await prompts({
    type: "text",
    name: "backgroundVideo",
    message: "Caminho do vídeo de fundo (opcional, Enter para pular):",
  });

  const { musicPath } = await prompts({
    type: "text",
    name: "musicPath",
    message: "Caminho da música (MP3/WAV, opcional, Enter para pular):",
  });

  let musicVolume: number | undefined;
  if (musicPath && musicPath.trim() !== "") {
    const { vol } = await prompts({
      type: "number",
      name: "vol",
      message: "Volume da música (0.0–1.0):",
      initial: 0.8,
      float: true,
      round: 2,
    });
    musicVolume = vol;
  }

  const { outputName } = await prompts({
    type: "text",
    name: "outputName",
    message: "Nome do arquivo de saída (sem extensão):",
    initial: `reel_${style}_${Date.now()}`,
  });

  const config: VideoConfig = {
    style: style as VideoStyle,
    phrases,
    subtitle: subtitle?.trim() || undefined,
    backgroundImage:
      backgroundImage?.trim()
        ? path.resolve(backgroundImage.trim())
        : undefined,
    backgroundVideo:
      backgroundVideo?.trim()
        ? path.resolve(backgroundVideo.trim())
        : undefined,
    musicPath: musicPath?.trim() ? path.resolve(musicPath.trim()) : undefined,
    musicVolume,
    durationInSeconds: duration ?? 15,
    outputPath: path.resolve(`output/${outputName || "reel"}.mp4`),
  };

  // Validate paths
  for (const field of ["backgroundImage", "backgroundVideo", "musicPath"] as const) {
    if (config[field] && !existsSync(config[field] as string)) {
      console.log(
        chalk.yellow(`  ⚠ ${field} não encontrado, ignorando: ${config[field]}`)
      );
      (config as unknown as Record<string, unknown>)[field] = undefined;
    }
  }

  console.log(chalk.bold("\n  📋 Resumo:"));
  console.log(chalk.gray(`  Estilo:    ${STYLE_LABELS[config.style]}`));
  console.log(chalk.gray(`  Duração:   ${config.durationInSeconds}s`));
  console.log(chalk.gray(`  Frases:    ${config.phrases.length}`));
  console.log(chalk.gray(`  Saída:     ${config.outputPath}\n`));

  const { confirm } = await prompts({
    type: "confirm",
    name: "confirm",
    message: "Iniciar renderização?",
    initial: true,
  });

  if (!confirm) {
    console.log(chalk.gray("  Cancelado."));
    process.exit(0);
  }

  const spinner = ora({
    text: "Compilando projeto Remotion...",
    color: "magenta",
  }).start();

  try {
    const outputPath = await renderVideo(config, (pct) => {
      spinner.text = `Renderizando: ${pct}%`;
    });

    spinner.succeed(chalk.green(`\n  ✅ Vídeo gerado com sucesso!`));
    console.log(chalk.bold.cyan(`\n  📁 Arquivo: ${outputPath}\n`));
    console.log(
      chalk.gray("  Dimensões: 1080×1920 (9:16) | Formato: MP4 | Codec: H.264")
    );
    console.log(chalk.gray("  Pronto para upload no Instagram Reels e TikTok!\n"));
  } catch (err) {
    spinner.fail(chalk.red("Erro durante a renderização"));
    console.error(chalk.red(String(err)));
    process.exit(1);
  }
}

main();
