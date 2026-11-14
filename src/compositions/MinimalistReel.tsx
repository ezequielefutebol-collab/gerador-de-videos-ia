import React from "react";
import { AbsoluteFill, Sequence, useVideoConfig, Audio } from "remotion";
import { VideoConfig } from "../types/index.js";
import { themes } from "../styles/themes.js";
import { BackgroundMedia } from "../components/BackgroundMedia.js";
import { AnimatedText } from "../components/AnimatedText.js";
import { Subtitle } from "../components/Subtitle.js";
import { FadeTransition, FadeIn } from "../components/Effects.js";

export const MinimalistReel: React.FC<VideoConfig> = (props) => {
  const { durationInFrames } = useVideoConfig();
  const theme = themes.minimalista;
  const framesPerPhrase = Math.floor(durationInFrames / props.phrases.length);

  return (
    <AbsoluteFill
      style={{ background: theme.backgroundColors[0], fontFamily: theme.fontFamily }}
    >
      <BackgroundMedia
        imagePath={props.backgroundImage}
        videoPath={props.backgroundVideo}
        colors={theme.backgroundColors}
        overlayOpacity={theme.overlayOpacity}
        kenBurns={false}
      />

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
              gap: 28,
              padding: "0 72px",
            }}
          >
            <div
              style={{
                width: 40,
                height: 2,
                background: theme.accentColor,
                marginBottom: 8,
              }}
            />
            <AnimatedText
              {...phrase}
              delay={phrase.delay ?? 10}
              animation={phrase.animation ?? "slideUp"}
              fontSize={phrase.fontSize ?? theme.titleSize}
              color={phrase.color ?? theme.textColor}
              fontWeight={phrase.fontWeight ?? "normal"}
              style={{
                letterSpacing: -1,
                lineHeight: 1.2,
              }}
            />
            <div
              style={{
                width: 40,
                height: 2,
                background: theme.accentColor,
                marginTop: 8,
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
          backgroundColor="rgba(0,0,0,0.08)"
          position="bottom"
        />
      )}

      {props.musicPath && (
        <Audio src={props.musicPath} volume={props.musicVolume ?? 0.7} />
      )}

      <FadeIn startFrame={0} endFrame={10} color="#ffffff" />
      <FadeTransition
        startFrame={durationInFrames - 15}
        endFrame={durationInFrames}
        color="#ffffff"
      />
    </AbsoluteFill>
  );
};
