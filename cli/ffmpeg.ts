import { exec } from "child_process";
import { promisify } from "util";
import { existsSync } from "fs";

const execAsync = promisify(exec);

export async function addAudioToVideo(
  videoPath: string,
  audioPath: string,
  outputPath: string,
  volume = 0.8
): Promise<void> {
  if (!existsSync(audioPath)) {
    throw new Error(`Arquivo de áudio não encontrado: ${audioPath}`);
  }
  const cmd = [
    "ffmpeg",
    `-i "${videoPath}"`,
    `-i "${audioPath}"`,
    `-filter_complex "[1:a]volume=${volume}[a]"`,
    `-map 0:v`,
    `-map "[a]"`,
    `-c:v copy`,
    `-c:a aac`,
    `-b:a 192k`,
    `-shortest`,
    `-y "${outputPath}"`,
  ].join(" ");

  await execAsync(cmd);
}

export async function optimizeForReels(
  inputPath: string,
  outputPath: string
): Promise<void> {
  // Optimize for Instagram/TikTok: H.264, AAC, correct pixel format
  const cmd = [
    "ffmpeg",
    `-i "${inputPath}"`,
    `-c:v libx264`,
    `-preset fast`,
    `-crf 20`,
    `-pix_fmt yuv420p`,
    `-c:a aac`,
    `-b:a 192k`,
    `-movflags +faststart`,
    `-y "${outputPath}"`,
  ].join(" ");

  await execAsync(cmd);
}

export async function checkFfmpeg(): Promise<boolean> {
  try {
    await execAsync("ffmpeg -version");
    return true;
  } catch {
    return false;
  }
}
