import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  Img,
  OffthreadVideo,
} from "remotion";

interface Props {
  imagePath?: string;
  videoPath?: string;
  colors?: string[];
  overlayOpacity?: number;
  kenBurns?: boolean;
  kenBurnsDirection?: "in" | "out";
}

export const BackgroundMedia: React.FC<Props> = ({
  imagePath,
  videoPath,
  colors = ["#1a0533", "#6b0fba"],
  overlayOpacity = 0.4,
  kenBurns = true,
  kenBurnsDirection = "in",
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const scale = kenBurns
    ? interpolate(
        frame,
        [0, durationInFrames],
        kenBurnsDirection === "in" ? [1, 1.18] : [1.18, 1]
      )
    : 1;

  const gradient = `linear-gradient(135deg, ${colors.join(", ")})`;

  return (
    <AbsoluteFill>
      {videoPath ? (
        <OffthreadVideo
          src={videoPath}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            transform: `scale(${scale})`,
          }}
        />
      ) : imagePath ? (
        <Img
          src={imagePath}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            transform: `scale(${scale})`,
            transformOrigin: "center center",
          }}
        />
      ) : (
        <div style={{ width: "100%", height: "100%", background: gradient }} />
      )}
      <AbsoluteFill
        style={{ background: `rgba(0,0,0,${overlayOpacity})` }}
      />
    </AbsoluteFill>
  );
};
