export type VideoStyle = "motivacional" | "cinematografico" | "minimalista" | "energia";

export type TextAnimation = "slideUp" | "fadeIn" | "scale" | "typewriter" | "bounce";

export interface TextBlock {
  text: string;
  delay?: number;
  animation?: TextAnimation;
  fontSize?: number;
  color?: string;
  fontWeight?: "normal" | "bold" | "900";
}

export interface VideoConfig {
  style: VideoStyle;
  phrases: TextBlock[];
  subtitle?: string;
  backgroundImage?: string;
  backgroundVideo?: string;
  musicPath?: string;
  musicVolume?: number;
  durationInSeconds: number;
  outputPath: string;
}

export interface Theme {
  backgroundColors: string[];
  textColor: string;
  accentColor: string;
  fontFamily: string;
  titleSize: number;
  subtitleSize: number;
  overlayOpacity: number;
}
