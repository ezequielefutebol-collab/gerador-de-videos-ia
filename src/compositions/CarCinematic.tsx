import React from "react";
import {
  AbsoluteFill,
  Audio,
  Sequence,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

// ─── Night Road (Perspective View) ────────────────────────────────────────────
const NightRoad: React.FC = () => {
  const frame = useCurrentFrame();

  // Animated perspective dashes — 12 lines rushing toward viewer
  const dashes = Array.from({ length: 12 }, (_, i) => {
    const phase = (frame * 4 + i * 160) % 1920;
    const progress = phase / 1920;
    const y = interpolate(progress, [0, 1], [420, 1960]);
    const w = interpolate(progress, [0, 1], [3, 36]);
    const h = interpolate(progress, [0, 1], [14, 90]);
    const op = interpolate(progress, [0, 0.08, 0.92, 1], [0, 1, 1, 0]);
    return { y, w, h, op };
  });

  return (
    <AbsoluteFill>
      {/* Sky gradient */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "linear-gradient(to bottom, #000 0%, #050510 35%, #0a0a14 50%, #111 60%, #0d0d0d 100%)",
        }}
      />
      {/* Road surface */}
      <svg
        style={{ position: "absolute", width: "100%", height: "100%" }}
        viewBox="0 0 1080 1920"
      >
        {/* Road trapezoid */}
        <polygon
          points="400,420  680,420  1080,1920  0,1920"
          fill="#0d0d0d"
        />
        {/* Road edge lines */}
        <line x1="400" y1="420" x2="0" y2="1920" stroke="#222" strokeWidth="3" />
        <line x1="680" y1="420" x2="1080" y2="1920" stroke="#222" strokeWidth="3" />
        {/* Atmospheric fog in mid-distance */}
        <rect x="0" y="380" width="1080" height="120" fill="url(#fogGrad)" />
        {/* Road center dashes */}
        {dashes.map((d, i) => (
          <rect
            key={i}
            x={540 - d.w / 2}
            y={d.y}
            width={d.w}
            height={d.h}
            fill="white"
            opacity={d.op * 0.85}
          />
        ))}
        <defs>
          <linearGradient id="fogGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#050510" stopOpacity="0" />
            <stop offset="50%" stopColor="#0d0d20" stopOpacity="0.5" />
            <stop offset="100%" stopColor="#050510" stopOpacity="0" />
          </linearGradient>
        </defs>
      </svg>
    </AbsoluteFill>
  );
};

// ─── City Bokeh (background city lights, blurred) ─────────────────────────────
const CityBokeh: React.FC = () => (
  <AbsoluteFill style={{ pointerEvents: "none" }}>
    <svg style={{ position: "absolute", width: "100%", height: "100%" }} viewBox="0 0 1080 1920">
      <defs>
        <filter id="bokeh">
          <feGaussianBlur stdDeviation="18" />
        </filter>
      </defs>
      <g filter="url(#bokeh)" opacity={0.35}>
        {[
          [80, 500, 14, "#ff6b35"], [160, 480, 10, "#ffd700"], [260, 510, 8, "#cc44ff"],
          [370, 490, 12, "#ff3366"], [470, 475, 9, "#00ccff"], [600, 500, 11, "#ffaa00"],
          [720, 485, 13, "#ff6b35"], [820, 495, 7, "#00ff88"], [940, 480, 10, "#ff3366"],
          [110, 540, 7, "#ffd700"], [340, 530, 9, "#cc44ff"], [680, 525, 8, "#00ccff"],
          [900, 540, 11, "#ffd700"], [200, 560, 6, "#ff6b35"], [760, 555, 9, "#ff3366"],
        ].map(([cx, cy, r, fill], i) => (
          <circle key={i} cx={cx as number} cy={cy as number} r={r as number} fill={fill as string} />
        ))}
      </g>
    </svg>
  </AbsoluteFill>
);

// ─── Approaching Headlights (front-on car) ────────────────────────────────────
const ApproachingCar: React.FC<{ startFrame: number; endFrame: number }> = ({
  startFrame,
  endFrame,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  if (frame < startFrame) return null;

  const elapsed = frame - startFrame;
  const duration = endFrame - startFrame;

  const progress = spring({
    fps,
    frame: elapsed,
    config: { damping: 120, stiffness: 12, mass: 2.5 },
    durationInFrames: duration,
  });

  const scale = interpolate(progress, [0, 1], [0.04, 3.2]);
  const cy = interpolate(progress, [0, 1], [430, 820]);
  const hSpread = scale * 48;
  const glow = Math.min(scale * 90, 220);

  return (
    <AbsoluteFill>
      <svg
        style={{ position: "absolute", width: "100%", height: "100%", overflow: "visible" }}
        viewBox="0 0 1080 1920"
      >
        <defs>
          <radialGradient id="lhg" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#fffef0" stopOpacity="1" />
            <stop offset="25%" stopColor="#fffde0" stopOpacity="0.85" />
            <stop offset="100%" stopColor="#ffe090" stopOpacity="0" />
          </radialGradient>
          <radialGradient id="rhg" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#fffef0" stopOpacity="1" />
            <stop offset="25%" stopColor="#fffde0" stopOpacity="0.85" />
            <stop offset="100%" stopColor="#ffe090" stopOpacity="0" />
          </radialGradient>
          <linearGradient id="beamFade" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#fff8e0" stopOpacity="0.5" />
            <stop offset="100%" stopColor="#fff8e0" stopOpacity="0" />
          </linearGradient>
        </defs>

        {/* Light beams on road */}
        {scale > 0.1 && (
          <>
            <polygon
              points={`${540 - hSpread * 0.6},${cy}  ${540 - hSpread * 1.1},${cy}  ${120},1920  ${0},1920`}
              fill="url(#beamFade)"
              opacity={Math.min(scale * 0.08, 0.18)}
            />
            <polygon
              points={`${540 + hSpread * 0.6},${cy}  ${540 + hSpread * 1.1},${cy}  ${960},1920  ${1080},1920`}
              fill="url(#beamFade)"
              opacity={Math.min(scale * 0.08, 0.18)}
            />
          </>
        )}

        {/* Car body — front silhouette */}
        <path
          d={`
            M ${540 - hSpread * 3},${cy + hSpread * 1.8}
            L ${540 - hSpread * 3},${cy - hSpread * 0.6}
            C ${540 - hSpread * 2.5},${cy - hSpread * 2.2} ${540 - hSpread * 1.6},${cy - hSpread * 2.8} ${540},${cy - hSpread * 3}
            C ${540 + hSpread * 1.6},${cy - hSpread * 2.8} ${540 + hSpread * 2.5},${cy - hSpread * 2.2} ${540 + hSpread * 3},${cy - hSpread * 0.6}
            L ${540 + hSpread * 3},${cy + hSpread * 1.8}
            Z
          `}
          fill="#080808"
          stroke="#1a1a1a"
          strokeWidth={Math.max(1, scale * 0.4)}
        />

        {/* Grille */}
        <rect
          x={540 - hSpread * 1.1}
          y={cy + hSpread * 0.3}
          width={hSpread * 2.2}
          height={hSpread * 0.75}
          fill="#0f0f0f"
          stroke="#2a2a2a"
          strokeWidth={Math.max(0.5, scale * 0.3)}
          rx={hSpread * 0.1}
        />

        {/* Front splitter */}
        <rect
          x={540 - hSpread * 2.5}
          y={cy + hSpread * 1.5}
          width={hSpread * 5}
          height={hSpread * 0.3}
          fill="#111"
          rx={2}
        />

        {/* Headlight glow — left */}
        <ellipse
          cx={540 - hSpread}
          cy={cy - hSpread * 0.1}
          rx={glow}
          ry={glow * 0.55}
          fill="url(#lhg)"
        />
        {/* Headlight glow — right */}
        <ellipse
          cx={540 + hSpread}
          cy={cy - hSpread * 0.1}
          rx={glow}
          ry={glow * 0.55}
          fill="url(#rhg)"
        />

        {/* DRL strips */}
        {scale > 0.3 && (
          <>
            <line
              x1={540 - hSpread * 1.6}
              y1={cy - hSpread * 0.5}
              x2={540 - hSpread * 0.4}
              y2={cy - hSpread * 0.5}
              stroke="white"
              strokeWidth={Math.max(1.5, scale * 2)}
              strokeLinecap="round"
              opacity={0.9}
            />
            <line
              x1={540 + hSpread * 0.4}
              y1={cy - hSpread * 0.5}
              x2={540 + hSpread * 1.6}
              y2={cy - hSpread * 0.5}
              stroke="white"
              strokeWidth={Math.max(1.5, scale * 2)}
              strokeLinecap="round"
              opacity={0.9}
            />
          </>
        )}
      </svg>
    </AbsoluteFill>
  );
};

// ─── Side-View Car Silhouette (blur past) ─────────────────────────────────────
const CarSideBlur: React.FC<{ startFrame: number }> = ({ startFrame }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const elapsed = frame - startFrame;
  const progress = spring({
    fps,
    frame: elapsed,
    config: { damping: 200, stiffness: 300, mass: 0.3 },
    durationInFrames: 25,
  });

  const x = interpolate(progress, [0, 1], [1400, -400]);
  const opacity = interpolate(progress, [0, 0.05, 0.9, 1], [0, 1, 1, 0]);
  const blur = interpolate(Math.abs(x - 540), [0, 400], [2, 18]);

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div
        style={{
          position: "absolute",
          bottom: "32%",
          left: 0,
          right: 0,
          display: "flex",
          justifyContent: "center",
          opacity,
          filter: `blur(${blur}px)`,
          transform: `translateX(${x - 540}px)`,
        }}
      >
        <svg viewBox="0 0 500 200" width="600" height="240">
          {/* Body */}
          <path
            d="M 10,140 C 10,110 20,96 42,88 L 68,70 C 82,54 108,38 142,32 L 232,28 C 272,27 304,38 328,54 L 374,80 C 392,92 400,108 402,128 L 402,142 Z"
            fill="#0a0a0a"
            stroke="#1e1e1e"
            strokeWidth="2"
          />
          {/* Windshield */}
          <path
            d="M 96,120 C 110,86 130,56 162,43 L 208,36 L 212,80 Z"
            fill="#0d1f30"
            stroke="#112"
            strokeWidth="1.5"
          />
          {/* Rear window */}
          <path
            d="M 258,34 L 314,46 C 338,58 356,76 365,96 L 258,86 Z"
            fill="#0d1f30"
            stroke="#112"
            strokeWidth="1.5"
          />
          {/* Roof scoop */}
          <path
            d="M 202,28 L 220,18 L 248,17 L 256,28 Z"
            fill="#111"
            stroke="#1a1a1a"
            strokeWidth="1"
          />
          {/* Door accent */}
          <path
            d="M 162,118 Q 210,110 258,108"
            stroke="#252525"
            strokeWidth="2"
            fill="none"
          />
          {/* Side sill */}
          <path
            d="M 48,138 L 390,135"
            stroke="#1e1e1e"
            strokeWidth="1.5"
            strokeLinecap="round"
          />
          {/* Rear wheel */}
          <circle cx="316" cy="148" r="36" fill="#0d0d0d" stroke="#1a1a1a" strokeWidth="2" />
          <circle cx="316" cy="148" r="23" fill="#111" stroke="#222" strokeWidth="1.5" />
          <circle cx="316" cy="148" r="9" fill="#1e1e1e" stroke="#2a2a2a" strokeWidth="1" />
          {/* Rear wheel detail spokes */}
          {[0, 60, 120, 180, 240, 300].map((deg) => (
            <line
              key={deg}
              x1={316 + 10 * Math.cos((deg * Math.PI) / 180)}
              y1={148 + 10 * Math.sin((deg * Math.PI) / 180)}
              x2={316 + 22 * Math.cos((deg * Math.PI) / 180)}
              y2={148 + 22 * Math.sin((deg * Math.PI) / 180)}
              stroke="#2a2a2a"
              strokeWidth="2"
            />
          ))}
          {/* Front wheel */}
          <circle cx="90" cy="148" r="36" fill="#0d0d0d" stroke="#1a1a1a" strokeWidth="2" />
          <circle cx="90" cy="148" r="23" fill="#111" stroke="#222" strokeWidth="1.5" />
          <circle cx="90" cy="148" r="9" fill="#1e1e1e" stroke="#2a2a2a" strokeWidth="1" />
          {[0, 60, 120, 180, 240, 300].map((deg) => (
            <line
              key={deg}
              x1={90 + 10 * Math.cos((deg * Math.PI) / 180)}
              y1={148 + 10 * Math.sin((deg * Math.PI) / 180)}
              x2={90 + 22 * Math.cos((deg * Math.PI) / 180)}
              y2={148 + 22 * Math.sin((deg * Math.PI) / 180)}
              stroke="#2a2a2a"
              strokeWidth="2"
            />
          ))}
          {/* Headlight */}
          <path
            d="M 14,96 L 14,116 C 22,120 38,120 48,114 L 44,94 C 32,90 20,90 14,96 Z"
            fill="#fffef0"
          />
          {/* Headlight DRL */}
          <path
            d="M 16,90 Q 32,85 46,88"
            stroke="white"
            strokeWidth="3"
            fill="none"
            strokeLinecap="round"
          />
          {/* Tail light assembly */}
          <rect x="390" y="88" width="12" height="32" fill="#cc0000" rx="1" />
          <rect x="384" y="92" width="8" height="24" fill="#ff2200" rx="1" />
          {/* Low beam line */}
          <path
            d="M 400,104 L 430,100"
            stroke="#ff2200"
            strokeWidth="1.5"
            opacity="0.6"
          />
          {/* Wing/spoiler */}
          <path
            d="M 356,86 L 400,80 L 406,88 L 362,94 Z"
            fill="#0a0a0a"
            stroke="#1a1a1a"
            strokeWidth="1"
          />
        </svg>
      </div>
    </AbsoluteFill>
  );
};

// ─── Tail Lights Receding ──────────────────────────────────────────────────────
const TailLightsReceding: React.FC<{ startFrame: number }> = ({ startFrame }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const elapsed = frame - startFrame;
  const progress = interpolate(elapsed, [0, 70], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Tail lights recede to vanishing point
  const scale = interpolate(progress, [0, 1], [0.5, 0.03]);
  const cy = interpolate(progress, [0, 1], [900, 430]);
  const spread = scale * 60;
  const glow = scale * 100;

  return (
    <AbsoluteFill>
      <svg
        style={{ position: "absolute", width: "100%", height: "100%", overflow: "visible" }}
        viewBox="0 0 1080 1920"
      >
        <defs>
          <radialGradient id="tlg">
            <stop offset="0%" stopColor="#ff0000" stopOpacity="1" />
            <stop offset="40%" stopColor="#cc0000" stopOpacity="0.7" />
            <stop offset="100%" stopColor="#880000" stopOpacity="0" />
          </radialGradient>
        </defs>
        {/* Left tail light glow */}
        <ellipse cx={540 - spread} cy={cy} rx={glow} ry={glow * 0.5} fill="url(#tlg)" />
        {/* Right tail light glow */}
        <ellipse cx={540 + spread} cy={cy} rx={glow} ry={glow * 0.5} fill="url(#tlg)" />
        {/* Car body outline (rear) */}
        <path
          d={`
            M ${540 - spread * 3},${cy + spread * 1.5}
            L ${540 - spread * 2.8},${cy - spread * 2.5}
            L ${540 - spread * 2},${cy - spread * 3}
            L ${540},${cy - spread * 3.2}
            L ${540 + spread * 2},${cy - spread * 3}
            L ${540 + spread * 2.8},${cy - spread * 2.5}
            L ${540 + spread * 3},${cy + spread * 1.5}
            Z
          `}
          fill="#050505"
          stroke="#111"
          strokeWidth={Math.max(0.5, scale * 2)}
        />
      </svg>
    </AbsoluteFill>
  );
};

// ─── Rain/Speed Particles ──────────────────────────────────────────────────────
const RainParticles: React.FC<{ intensity?: number }> = ({ intensity = 1 }) => {
  const frame = useCurrentFrame();
  const count = Math.floor(25 * intensity);

  const drops = Array.from({ length: count }, (_, i) => {
    const seed = i * 137.508 + i * 0.5;
    const x = (seed * 1337) % 1080;
    const speed = 6 + (seed % 10);
    const y = (frame * speed + seed * 80) % 1980 - 30;
    const length = 8 + (seed % 20);
    const op = 0.15 + ((seed % 100) / 100) * 0.3;
    return { x, y, length, op };
  });

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <svg
        style={{ position: "absolute", width: "100%", height: "100%" }}
        viewBox="0 0 1080 1920"
      >
        {drops.map((d, i) => (
          <line
            key={i}
            x1={d.x}
            y1={d.y}
            x2={d.x - 2}
            y2={d.y + d.length}
            stroke="white"
            strokeWidth="1"
            opacity={d.op}
          />
        ))}
      </svg>
    </AbsoluteFill>
  );
};

// ─── Speed Lines (horizontal blur streaks) ────────────────────────────────────
const SpeedLines: React.FC<{ opacity?: number }> = ({ opacity = 0.5 }) => {
  const frame = useCurrentFrame();
  const lines = Array.from({ length: 18 }, (_, i) => {
    const seed = i * 97.3;
    const y = (seed * 2.3 + frame * (2 + (seed % 4))) % 1920;
    const width = 60 + (seed % 320);
    const x = (seed * 7.1) % (1080 - width);
    const op = 0.1 + (seed % 60) / 100;
    return { y, width, x, op };
  });

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <svg
        style={{ position: "absolute", width: "100%", height: "100%" }}
        viewBox="0 0 1080 1920"
      >
        {lines.map((l, i) => (
          <line
            key={i}
            x1={l.x}
            y1={l.y}
            x2={l.x + l.width}
            y2={l.y}
            stroke="white"
            strokeWidth="1"
            opacity={l.op * opacity}
          />
        ))}
      </svg>
    </AbsoluteFill>
  );
};

// ─── Camera Shake ─────────────────────────────────────────────────────────────
const Shake: React.FC<{ intensity?: number; children: React.ReactNode }> = ({
  intensity = 4,
  children,
}) => {
  const frame = useCurrentFrame();
  const sx = Math.sin(frame * 2.5) * intensity + Math.cos(frame * 1.8) * intensity * 0.5;
  const sy = Math.cos(frame * 2.1) * intensity + Math.sin(frame * 2.7) * intensity * 0.3;
  return (
    <div
      style={{
        transform: `translate(${sx}px, ${sy}px)`,
        width: "100%",
        height: "100%",
      }}
    >
      {children}
    </div>
  );
};

// ─── Title Card ───────────────────────────────────────────────────────────────
const TitleCard: React.FC<{
  line1: string;
  line2?: string;
  delay?: number;
  position?: "center" | "bottom-third";
}> = ({ line1, line2, delay = 0, position = "center" }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const prog = spring({
    fps,
    frame: frame - delay,
    config: { damping: 90, stiffness: 60 },
    durationInFrames: 22,
  });
  const y = interpolate(prog, [0, 1], [40, 0]);
  const op = interpolate(prog, [0, 1], [0, 1]);

  const posStyle: React.CSSProperties =
    position === "bottom-third"
      ? { paddingBottom: "30%" }
      : {};

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        flexDirection: "column",
        gap: 16,
        ...posStyle,
      }}
    >
      <div
        style={{
          transform: `translateY(${y}px)`,
          opacity: op,
          textAlign: "center",
          padding: "0 60px",
        }}
      >
        <div
          style={{
            color: "#ffffff",
            fontSize: 88,
            fontFamily: "'Impact', 'Arial Black', sans-serif",
            letterSpacing: 10,
            textTransform: "uppercase",
            textShadow:
              "0 0 40px rgba(255,255,255,0.4), 0 0 80px rgba(180,100,255,0.2)",
            lineHeight: 1.05,
          }}
        >
          {line1}
        </div>
        {line2 && (
          <div
            style={{
              color: "rgba(200,180,255,0.85)",
              fontSize: 32,
              fontFamily: "'Helvetica Neue', Arial, sans-serif",
              letterSpacing: 7,
              marginTop: 14,
              textTransform: "uppercase",
              textShadow: "0 0 20px rgba(180,100,255,0.5)",
            }}
          >
            {line2}
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
};

// ─── Vignette + Letterbox ─────────────────────────────────────────────────────
const Cinematic: React.FC = () => (
  <AbsoluteFill style={{ pointerEvents: "none" }}>
    {/* Vignette */}
    <div
      style={{
        position: "absolute",
        inset: 0,
        background:
          "radial-gradient(ellipse at center, transparent 40%, rgba(0,0,0,0.75) 100%)",
      }}
    />
    {/* Letterbox */}
    <div
      style={{ position: "absolute", top: 0, left: 0, right: 0, height: 80, background: "#000" }}
    />
    <div
      style={{ position: "absolute", bottom: 0, left: 0, right: 0, height: 80, background: "#000" }}
    />
  </AbsoluteFill>
);

// ─── Main Composition ─────────────────────────────────────────────────────────
// 300 frames @ 30fps = 10 seconds
// Scene 1 (0–60):   Dark opener + title
// Scene 2 (60–180):  Night road + approaching headlights
// Scene 3 (175–210): Car rush-by (flash)
// Scene 4 (205–275): Tail lights receding
// Scene 5 (270–300): Outro title + fade out
export const CarCinematic: React.FC<{ musicPath?: string }> = ({ musicPath }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const fadeIn = interpolate(frame, [0, 18], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const fadeOut = interpolate(frame, [durationInFrames - 20, durationInFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Flash when car rushes past
  const flashOp = interpolate(frame, [174, 178, 192, 198], [0, 1, 0.3, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Color tint — shifts to red during rush-by
  const redTint = interpolate(frame, [160, 185, 220], [0, 0.25, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ background: "#000", overflow: "hidden" }}>
      {/* Always: city background bokeh */}
      <CityBokeh />

      {/* Scene 1: Dark title intro */}
      <Sequence from={0} durationInFrames={70}>
        <TitleCard line1="DARKNESS" line2="A Beast Awakens" delay={12} />
      </Sequence>

      {/* Scene 2: Road + approaching headlights */}
      <Sequence from={55} durationInFrames={130}>
        <NightRoad />
        <RainParticles intensity={0.8} />
        <ApproachingCar startFrame={55} endFrame={180} />
      </Sequence>

      {/* Scene 3: Car rushes by — side view blur */}
      <Sequence from={172} durationInFrames={40}>
        <Shake intensity={9}>
          <NightRoad />
          <SpeedLines opacity={0.8} />
          <CarSideBlur startFrame={172} />
        </Shake>
      </Sequence>

      {/* Scene 4: Tail lights receding */}
      <Sequence from={202} durationInFrames={80}>
        <NightRoad />
        <TailLightsReceding startFrame={202} />
        <SpeedLines opacity={0.3} />
        <RainParticles intensity={0.5} />
      </Sequence>

      {/* Scene 5: Outro */}
      <Sequence from={268} durationInFrames={32}>
        <TitleCard line1="POWER" line2="Redefined" delay={5} />
      </Sequence>

      {/* Flash effect */}
      <AbsoluteFill
        style={{ background: "#fff", opacity: flashOp, pointerEvents: "none" }}
      />

      {/* Red tint during rush */}
      <AbsoluteFill
        style={{
          background: "#cc2200",
          opacity: redTint,
          pointerEvents: "none",
          mixBlendMode: "multiply",
        }}
      />

      {/* Cinematic frame overlay (vignette + letterbox) */}
      <Cinematic />

      {/* Fade in/out */}
      <AbsoluteFill
        style={{ background: "#000", opacity: fadeIn, pointerEvents: "none" }}
      />
      <AbsoluteFill
        style={{ background: "#000", opacity: fadeOut, pointerEvents: "none" }}
      />

      {/* Music */}
      {musicPath && <Audio src={musicPath} volume={0.85} startFrom={0} />}
    </AbsoluteFill>
  );
};
