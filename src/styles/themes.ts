import { Theme, VideoStyle } from "../types/index.js";

export const themes: Record<VideoStyle, Theme> = {
  motivacional: {
    backgroundColors: ["#1a0533", "#3d0575", "#6b0fba"],
    textColor: "#ffffff",
    accentColor: "#ff6b35",
    fontFamily: "'Impact', 'Arial Black', sans-serif",
    titleSize: 86,
    subtitleSize: 36,
    overlayOpacity: 0.35,
  },
  cinematografico: {
    backgroundColors: ["#0a0a0a", "#1a1a2e", "#0d0d1a"],
    textColor: "#f0e6d3",
    accentColor: "#c9a84c",
    fontFamily: "'Georgia', 'Times New Roman', serif",
    titleSize: 68,
    subtitleSize: 28,
    overlayOpacity: 0.6,
  },
  minimalista: {
    backgroundColors: ["#f8f8f8", "#eeeeee"],
    textColor: "#111111",
    accentColor: "#333333",
    fontFamily: "'Helvetica Neue', 'Arial', sans-serif",
    titleSize: 72,
    subtitleSize: 32,
    overlayOpacity: 0.05,
  },
  energia: {
    backgroundColors: ["#ff0040", "#ff6b00", "#ffd100"],
    textColor: "#ffffff",
    accentColor: "#00ffdd",
    fontFamily: "'Arial Black', 'Impact', sans-serif",
    titleSize: 92,
    subtitleSize: 38,
    overlayOpacity: 0.2,
  },
};
