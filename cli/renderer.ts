import path from "path";
import { bundle } from "@remotion/bundler";
import { renderMedia, selectComposition } from "@remotion/renderer";
import { VideoConfig, VideoStyle } from "../src/types/index.js";
import { addAudioToVideo, optimizeForReels } from "./ffmpeg.js";
import { existsSync, mkdirSync } from "fs";

const COMPOSITION_MAP: Record<VideoStyle, string> = {
  motivacional: "MotivationalReel",
  cinematografico: "CinematicReel",
  minimalista: "MinimalistReel",
  energia: "EnergyReel",
};

export async function renderVideo(
  config: VideoConfig,
  onProgress?: (pct: number) => void
): Promise<string> {
  const outDir = path.dirname(config.outputPath);
  if (!existsSync(outDir)) mkdirSync(outDir, { recursive: true });

  const entryPoint = path.resolve("src/index.ts");
  const compositionId = COMPOSITION_MAP[config.style];

  // Bundle the Remotion project
  const bundled = await bundle({
    entryPoint,
    webpackOverride: (cfg) => cfg,
  });

  // Select and configure the composition
  const composition = await selectComposition({
    serveUrl: bundled,
    id: compositionId,
    inputProps: config as unknown as Record<string, unknown>,
  });

  const fps = composition.fps ?? 30;
  const durationInFrames = config.durationInSeconds * fps;

  // Render video (without music — added via FFmpeg after)
  const tempOutput = config.musicPath
    ? config.outputPath.replace(".mp4", "_noaudio.mp4")
    : config.outputPath;

  await renderMedia({
    composition: { ...composition, durationInFrames },
    serveUrl: bundled,
    codec: "h264",
    outputLocation: tempOutput,
    inputProps: config as unknown as Record<string, unknown>,
    onProgress: ({ progress }) => onProgress?.(Math.round(progress * 100)),
  });

  // Mix in music via FFmpeg if provided
  if (config.musicPath) {
    await addAudioToVideo(
      tempOutput,
      config.musicPath,
      config.outputPath,
      config.musicVolume ?? 0.8
    );
  } else {
    // Re-encode to ensure social media compatibility
    const optimized = config.outputPath.replace(".mp4", "_final.mp4");
    await optimizeForReels(tempOutput, optimized);
    return optimized;
  }

  return config.outputPath;
}
