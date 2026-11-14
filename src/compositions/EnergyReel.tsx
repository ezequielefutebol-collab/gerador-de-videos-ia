import React from "react";
import {
  AbsoluteFill,
  Sequence,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  Audio,
} from "remotion";
import { VideoConfig } from "../types/index";
import { themes } from "../styles/themes";
import { BackgroundMedia } from "../components/BackgroundMedia";
import { AnimatedText } from "../components/AnimatedText";
import { Subtitle } from "../components/Subtitle";
import {
  Vignette,
  FadeTransition,
  FadeIn,
  FlashEffect,
} from "../components/Effects";

const PulsingBorder: React.FC<{ color: string }> = ({ color }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(
    frame % 30,
    [0, 15, 30],
    [0.4, 1, 0.4]
  );
  return (
    <AbsoluteFill
      style={{
        border: `6px solid ${color}`,
        opacity,
        pointerEvents: "none",
        boxSizing: "border-box",
      }}
    />
  );
};

export const EnergyReel: React.FC<VideoConfig> = (props) => {
  const { durationInFrames } = useVideoConfig();
  const theme = themes.energia;
  const framesPerPhrase = Math.floor(durationInFrames / props.phrases.length);

  return (
    <AbsoluteFill style={{ background: "#000", fontFamily: theme.fontFamily }}>
      <BackgroundMedia
        imagePath={props.backgroundImage}
        videoPath={props.backgroundVideo}
        colors={theme.backgroundColors}
        overlayOpacity={theme.overlayOpacity}
        kenBurns
        kenBurnsDirection="in"
      />
      <Vignette intensity={0.5} />
      <PulsingBorder color={theme.accentColor} />

      {props.phrases.map((phrase, i) => (
        <Sequence
          key={i}
          from={i * framesPerPhrase}
          durationInFrames={framesPerPhrase}
        >
          <AbsoluteFill
            style={{
              justifyContent: "center",
              alignItems: "center",
              flexDirection: "column",
              gap: 20,
              padding: "0 48px",
            }}
          >
            <FlashEffect delay={0} />
            <AnimatedText
              {...phrase}
              delay={phrase.delay ?? 5}
              animation={phrase.animation ?? "bounce"}
              fontSize={phrase.fontSize ?? theme.titleSize}
              color={phrase.color ?? theme.textColor}
              fontWeight={phrase.fontWeight ?? "900"}
              style={{
                textTransform: "uppercase",
                letterSpacing: 3,
                textShadow: `0 0 20px ${theme.accentColor}, 0 4px 15px rgba(0,0,0,0.8)`,
              }}
            />
          </AbsoluteFill>
        </Sequence>
      ))}

      {props.subtitle && (
        <Subtitle
          text={props.subtitle}
          startFrame={15}
          endFrame={durationInFrames - 10}
          fontSize={theme.subtitleSize}
          color="#000"
          backgroundColor={theme.accentColor}
          position="bottom"
        />
      )}

      {props.musicPath && (
        <Audio src={props.musicPath} volume={props.musicVolume ?? 0.9} />
      )}

      <FadeIn startFrame={0} endFrame={8} />
      <FadeTransition
        startFrame={durationInFrames - 15}
        endFrame={durationInFrames}
      />
    </AbsoluteFill>
  );
};
