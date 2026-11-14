import React from "react";
import { AbsoluteFill, Sequence, useVideoConfig, Audio } from "remotion";
import { VideoConfig } from "../types/index.js";
import { themes } from "../styles/themes.js";
import { BackgroundMedia } from "../components/BackgroundMedia.js";
import { AnimatedText } from "../components/AnimatedText.js";
import { Subtitle } from "../components/Subtitle.js";
import {
  Vignette,
  Letterbox,
  FadeTransition,
  FadeIn,
} from "../components/Effects.js";

export const CinematicReel: React.FC<VideoConfig> = (props) => {
  const { durationInFrames } = useVideoConfig();
  const theme = themes.cinematografico;
  const framesPerPhrase = Math.floor(durationInFrames / props.phrases.length);

  return (
    <AbsoluteFill style={{ background: "#000", fontFamily: theme.fontFamily }}>
      <BackgroundMedia
        imagePath={props.backgroundImage}
        videoPath={props.backgroundVideo}
        colors={theme.backgroundColors}
        overlayOpacity={theme.overlayOpacity}
        kenBurns
        kenBurnsDirection="out"
      />
      <Vignette intensity={0.8} />

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
              padding: "90px 70px",
            }}
          >
            <AnimatedText
              {...phrase}
              delay={phrase.delay ?? 12}
              animation={phrase.animation ?? "fadeIn"}
              fontSize={phrase.fontSize ?? theme.titleSize}
              color={phrase.color ?? theme.textColor}
              fontWeight={phrase.fontWeight ?? "normal"}
              style={{
                fontStyle: "italic",
                letterSpacing: 1,
                textShadow: "0 2px 10px rgba(0,0,0,0.9)",
                lineHeight: 1.3,
              }}
            />
            <div
              style={{
                width: 60,
                height: 1,
                background: theme.accentColor,
                marginTop: 12,
              }}
            />
          </AbsoluteFill>
        </Sequence>
      ))}

      {props.subtitle && (
        <Subtitle
          text={props.subtitle}
          startFrame={20}
          endFrame={durationInFrames - 10}
          fontSize={theme.subtitleSize}
          color={theme.textColor}
          backgroundColor="rgba(0,0,0,0.65)"
          position="bottom"
        />
      )}

      {props.musicPath && (
        <Audio src={props.musicPath} volume={props.musicVolume ?? 0.6} />
      )}

      <Letterbox barHeight={90} />
      <FadeIn startFrame={0} endFrame={18} />
      <FadeTransition
        startFrame={durationInFrames - 20}
        endFrame={durationInFrames}
      />
    </AbsoluteFill>
  );
};
