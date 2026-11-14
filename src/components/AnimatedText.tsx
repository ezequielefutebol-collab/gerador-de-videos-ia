import React from "react";
import { useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";
import { TextBlock } from "../types/index";

interface Props extends TextBlock {
  style?: React.CSSProperties;
}

export const AnimatedText: React.FC<Props> = ({
  text,
  delay = 0,
  animation = "slideUp",
  fontSize = 72,
  color = "#ffffff",
  fontWeight = "bold",
  style,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({
    fps,
    frame: frame - delay,
    config: { damping: 80, stiffness: 100, mass: 0.8 },
    durationInFrames: 20,
  });

  if (animation === "typewriter") {
    const chars = Math.floor(
      interpolate(frame - delay, [0, 25], [0, text.length], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })
    );
    return (
      <div style={{ fontSize, color, fontWeight, ...style }}>
        {text.slice(0, chars)}
        {chars < text.length && (
          <span style={{ opacity: frame % 20 < 10 ? 1 : 0 }}>|</span>
        )}
      </div>
    );
  }

  let animStyle: React.CSSProperties = {};

  if (animation === "slideUp") {
    const y = interpolate(progress, [0, 1], [80, 0]);
    const opacity = interpolate(progress, [0, 0.3], [0, 1], {
      extrapolateRight: "clamp",
    });
    animStyle = { transform: `translateY(${y}px)`, opacity };
  } else if (animation === "fadeIn") {
    animStyle = { opacity: progress };
  } else if (animation === "scale") {
    const scale = interpolate(progress, [0, 1], [0.5, 1]);
    const opacity = interpolate(progress, [0, 0.3], [0, 1], {
      extrapolateRight: "clamp",
    });
    animStyle = { transform: `scale(${scale})`, opacity };
  } else if (animation === "bounce") {
    const bounceProgress = spring({
      fps,
      frame: frame - delay,
      config: { damping: 25, stiffness: 400, mass: 0.4 },
      durationInFrames: 25,
    });
    const scale = interpolate(bounceProgress, [0, 1], [0, 1]);
    animStyle = { transform: `scale(${scale})` };
  }

  return (
    <div
      style={{
        fontSize,
        color,
        fontWeight,
        lineHeight: 1.15,
        textAlign: "center",
        ...animStyle,
        ...style,
      }}
    >
      {text}
    </div>
  );
};
