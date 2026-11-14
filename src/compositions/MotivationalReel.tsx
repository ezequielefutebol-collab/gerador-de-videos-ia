import React from "react";
import {
  AbsoluteFill,
  Sequence,
  useVideoConfig,
  Audio,
} from "remotion";
import { VideoConfig } from "../types/index";
import { themes } from "../styles/themes";
import { BackgroundMedia } from "../components/BackgroundMedia";
import { AnimatedText } from "../components/AnimatedText";
import { Subtitle } from "../components/Subtitle";
import {
  Vignette,
  GlowLine,
  FadeTransition,
  FadeIn,
} from "../components/Effects";

export const MotivationalReel: React.FC<VideoConfig> = (props) => {
  const { durationInFrames } = useVideoConfig();
  const theme = themes.motivacional;
  const fps = 30;
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
      <Vignette intensity={0.65} />

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
              gap: 24,
              padding: "0 60px",
            }}
          >
            <AnimatedText
              {...phrase}
              delay={phrase.delay ?? 8}
              animation={phrase.animation ?? "slideUp"}
              fontSize={phrase.fontSize ?? theme.titleSize}
              color={phrase.color ?? theme.textColor}
              fontWeight={phrase.fontWeight ?? "900"}
              style={{
                textTransform: "uppercase",
                letterSpacing: 2,
                textShadow: "0 4px 20px rgba(0,0,0,0.6)",
              }}
            />
            <Sequence from={phrase.delay ?? 8}>
              <GlowLine color={theme.accentColor} delay={8} width={240} />
            </Sequence>
          </AbsoluteFill>
        </Sequence>
      ))}

      {props.subtitle && (
        <Subtitle
          text={props.subtitle}
          startFrame={20}
          endFrame={durationInFrames - 10}
          fontSize={theme.subtitleSize}
          position="bottom"
        />
      )}

      {props.musicPath && (
        <Audio
          src={props.musicPath}
          volume={props.musicVolume ?? 0.8}
          startFrom={0}
        />
      )}

      <FadeIn startFrame={0} endFrame={12} />
      <FadeTransition
        startFrame={durationInFrames - 20}
        endFrame={durationInFrames}
      />
    </AbsoluteFill>
  );
};
