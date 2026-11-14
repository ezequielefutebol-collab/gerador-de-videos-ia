import React from "react";
import { Composition, staticFile } from "remotion";
import { MotivationalReel } from "./compositions/MotivationalReel";
import { CinematicReel } from "./compositions/CinematicReel";
import { MinimalistReel } from "./compositions/MinimalistReel";
import { EnergyReel } from "./compositions/EnergyReel";
import { CarCinematic } from "./compositions/CarCinematic";
import { VideoConfig } from "./types/index";

type AnyProps = Record<string, unknown>;
const asComp = <T,>(c: React.FC<T>) => c as unknown as React.ComponentType<AnyProps>;

const baseProps: VideoConfig = {
  style: "motivacional",
  phrases: [
    { text: "Acredite em você!", animation: "slideUp", delay: 8 },
    { text: "O futuro pertence a você.", animation: "fadeIn", delay: 10 },
  ],
  durationInSeconds: 15,
  outputPath: "output/video.mp4",
};

export const RemotionRoot: React.FC = () => (
  <>
    <Composition
      id="MotivationalReel"
      component={asComp(MotivationalReel)}
      fps={30}
      width={1080}
      height={1920}
      durationInFrames={450}
      defaultProps={baseProps as unknown as AnyProps}
      calculateMetadata={async ({ props }) => ({
        durationInFrames: (props as unknown as VideoConfig).durationInSeconds * 30,
      })}
    />
    <Composition
      id="CinematicReel"
      component={asComp(CinematicReel)}
      fps={30}
      width={1080}
      height={1920}
      durationInFrames={450}
      defaultProps={{ ...baseProps, style: "cinematografico" } as unknown as AnyProps}
      calculateMetadata={async ({ props }) => ({
        durationInFrames: (props as unknown as VideoConfig).durationInSeconds * 30,
      })}
    />
    <Composition
      id="MinimalistReel"
      component={asComp(MinimalistReel)}
      fps={30}
      width={1080}
      height={1920}
      durationInFrames={450}
      defaultProps={{ ...baseProps, style: "minimalista" } as unknown as AnyProps}
      calculateMetadata={async ({ props }) => ({
        durationInFrames: (props as unknown as VideoConfig).durationInSeconds * 30,
      })}
    />
    <Composition
      id="EnergyReel"
      component={asComp(EnergyReel)}
      fps={30}
      width={1080}
      height={1920}
      durationInFrames={450}
      defaultProps={{ ...baseProps, style: "energia" } as unknown as AnyProps}
      calculateMetadata={async ({ props }) => ({
        durationInFrames: (props as unknown as VideoConfig).durationInSeconds * 30,
      })}
    />
    <Composition
      id="CarCinematic"
      component={asComp(CarCinematic)}
      fps={30}
      width={1080}
      height={1920}
      durationInFrames={300}
      defaultProps={{ musicPath: staticFile("cinematic_car.aac") } as unknown as AnyProps}
    />
  </>
);
