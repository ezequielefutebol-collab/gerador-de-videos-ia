import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";

export const Letterbox: React.FC<{ barHeight?: number }> = ({
  barHeight = 90,
}) => (
  <AbsoluteFill style={{ pointerEvents: "none" }}>
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        right: 0,
        height: barHeight,
        background: "#000",
      }}
    />
    <div
      style={{
        position: "absolute",
        bottom: 0,
        left: 0,
        right: 0,
        height: barHeight,
        background: "#000",
      }}
    />
  </AbsoluteFill>
);

export const Vignette: React.FC<{ intensity?: number }> = ({
  intensity = 0.75,
}) => (
  <AbsoluteFill
    style={{
      background: `radial-gradient(ellipse at center, transparent 45%, rgba(0,0,0,${intensity}) 100%)`,
      pointerEvents: "none",
    }}
  />
);

export const FadeTransition: React.FC<{
  startFrame: number;
  endFrame: number;
  color?: string;
}> = ({ startFrame, endFrame, color = "#000000" }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [startFrame, endFrame], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill
      style={{ background: color, opacity, pointerEvents: "none" }}
    />
  );
};

export const FadeIn: React.FC<{
  startFrame?: number;
  endFrame?: number;
  color?: string;
}> = ({ startFrame = 0, endFrame = 15, color = "#000000" }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [startFrame, endFrame], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill
      style={{ background: color, opacity, pointerEvents: "none" }}
    />
  );
};

export const GlowLine: React.FC<{
  color?: string;
  delay?: number;
  width?: number;
}> = ({ color = "#ff6b35", delay = 0, width = 220 }) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame - delay, [0, 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const lineWidth = interpolate(progress, [0, 1], [0, width]);
  return (
    <div
      style={{
        height: 4,
        width: lineWidth,
        background: color,
        boxShadow: `0 0 10px ${color}, 0 0 25px ${color}`,
        borderRadius: 2,
      }}
    />
  );
};

export const FlashEffect: React.FC<{ delay?: number }> = ({ delay = 0 }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame - delay, [0, 2, 8], [1, 0.6, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill
      style={{ background: "#ffffff", opacity, pointerEvents: "none" }}
    />
  );
};
