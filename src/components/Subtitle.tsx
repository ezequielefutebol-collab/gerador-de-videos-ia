import React from "react";
import { useCurrentFrame, interpolate } from "remotion";

interface Props {
  text: string;
  startFrame: number;
  endFrame: number;
  fontSize?: number;
  color?: string;
  backgroundColor?: string;
  position?: "top" | "bottom" | "center";
}

export const Subtitle: React.FC<Props> = ({
  text,
  startFrame,
  endFrame,
  fontSize = 32,
  color = "#ffffff",
  backgroundColor = "rgba(0,0,0,0.75)",
  position = "bottom",
}) => {
  const frame = useCurrentFrame();

  if (frame < startFrame || frame > endFrame) return null;

  const opacity = interpolate(
    frame,
    [startFrame, startFrame + 6, endFrame - 6, endFrame],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const posStyle: React.CSSProperties =
    position === "top"
      ? { top: 70 }
      : position === "center"
      ? { top: "50%", transform: "translateY(-50%)" }
      : { bottom: 90 };

  return (
    <div
      style={{
        position: "absolute",
        left: 48,
        right: 48,
        ...posStyle,
        opacity,
        textAlign: "center",
        fontSize,
        color,
        backgroundColor,
        padding: "14px 24px",
        borderRadius: 10,
        fontFamily: "'Arial', sans-serif",
        lineHeight: 1.45,
      }}
    >
      {text}
    </div>
  );
};
