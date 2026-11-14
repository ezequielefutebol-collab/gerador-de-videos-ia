import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  interpolate,
  spring,
  Sequence,
} from "remotion";

const W = 1080;
const H = 1920;
const FPS = 30;
const tf = (s: number) => Math.round(s * FPS);

/* ── Colors ─────────────────────────────────────────────────── */
const C = {
  sky: "#7BC4E0",
  skyNight: "#0A1628",
  horizon: "#B8DFF0",
  ground: "#6B4E2A",
  grass: "#4A7C3F",
  concrete: "#C8BBAB",
  concreteLight: "#E0D8CC",
  steel: "#7A8FA6",
  orange: "#FF6B1A",
  yellow: "#FFD700",
  red: "#E53E3E",
  green: "#38A169",
  blue: "#1B3A5C",
  blueLight: "#2B6CB0",
  white: "#FFFFFF",
  black: "#0A0A0A",
  bg: "#0D1117",
};

/* ── Spring helper ───────────────────────────────────────────── */
const sp = (frame: number, damping = 14, stiffness = 120) =>
  spring({ fps: FPS, frame, config: { damping, stiffness, mass: 1 } });

/* ── Subtitle ────────────────────────────────────────────────── */
const Sub: React.FC<{
  text: string;
  color?: string;
  size?: number;
}> = ({ text, color = C.white, size = 54 }) => {
  const f = useCurrentFrame();
  const op = interpolate(f, [0, 8, 70, 85], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <div
      style={{
        position: "absolute",
        bottom: 200,
        left: 50,
        right: 50,
        textAlign: "center",
        opacity: op,
        zIndex: 60,
      }}
    >
      <span
        style={{
          fontFamily: "Impact, 'Arial Black', sans-serif",
          fontSize: size,
          color,
          textShadow:
            "3px 3px 0 #000,-3px -3px 0 #000,3px -3px 0 #000,-3px 3px 0 #000",
          lineHeight: 1.25,
          display: "block",
          wordBreak: "break-word",
        }}
      >
        {text}
      </span>
    </div>
  );
};

/* ── BigText ─────────────────────────────────────────────────── */
const BigText: React.FC<{
  text: string;
  color?: string;
  size?: number;
  y?: string;
  delay?: number;
}> = ({ text, color = C.white, size = 90, y = "42%", delay = 0 }) => {
  const f = useCurrentFrame() - delay;
  const scale = f >= 0 ? 0.6 + 0.4 * sp(f) : 0;
  const op = interpolate(f, [0, 6], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <div
      style={{
        position: "absolute",
        top: y,
        left: 60,
        right: 60,
        transform: `translateY(-50%) scale(${scale})`,
        textAlign: "center",
        opacity: op,
        zIndex: 20,
      }}
    >
      <span
        style={{
          fontFamily: "Impact, 'Arial Black', sans-serif",
          fontSize: size,
          color,
          textShadow:
            "4px 4px 0 #000,-4px -4px 0 #000,4px -4px 0 #000,-4px 4px 0 #000",
          lineHeight: 1.2,
          display: "block",
        }}
      >
        {text}
      </span>
    </div>
  );
};

/* ── Sky background ──────────────────────────────────────────── */
const SkyBg: React.FC<{ night?: boolean }> = ({ night = false }) => (
  <div
    style={{
      position: "absolute",
      inset: 0,
      background: night
        ? `linear-gradient(180deg, ${C.skyNight} 0%, #1A2F4A 100%)`
        : `linear-gradient(180deg, ${C.sky} 0%, ${C.horizon} 70%, #A8C8A0 100%)`,
    }}
  />
);

/* ── Worker character (flat 2D) ──────────────────────────────── */
const Worker: React.FC<{
  x: number;
  y: number;
  scale?: number;
  flip?: boolean;
  hatColor?: string;
}> = ({ x, y, scale = 1, flip = false, hatColor = C.yellow }) => {
  const sx = flip ? -scale : scale;
  return (
    <g transform={`translate(${x},${y}) scale(${sx},${scale})`}>
      {/* body */}
      <rect x={-22} y={0} width={44} height={60} fill={C.blueLight} rx={6} />
      {/* legs */}
      <rect x={-20} y={56} width={16} height={32} fill="#1A3A5A" rx={4} />
      <rect x={6} y={56} width={16} height={32} fill="#1A3A5A" rx={4} />
      {/* arms */}
      <rect x={-38} y={4} width={18} height={10} fill={C.blueLight} rx={5} />
      <rect x={22} y={4} width={18} height={10} fill={C.blueLight} rx={5} />
      {/* head */}
      <circle cx={0} cy={-24} r={28} fill="#D4A574" />
      {/* hard hat */}
      <ellipse cx={0} cy={-46} rx={34} ry={8} fill={hatColor} />
      <rect x={-26} y={-56} width={52} height={16} fill={hatColor} rx={8} />
      {/* eyes */}
      <circle cx={-10} cy={-24} r={5} fill={C.black} />
      <circle cx={10} cy={-24} r={5} fill={C.black} />
      {/* smile */}
      <path d="M -10 -10 Q 0 -2 10 -10" stroke={C.black} strokeWidth={3} fill="none" />
    </g>
  );
};

/* ── Building SVG ────────────────────────────────────────────── */
const Building: React.FC<{
  floors: number;
  night?: boolean;
  showCrane?: boolean;
}> = ({ floors, night = false, showCrane = false }) => {
  const totalFloors = 20;
  const floorH = 44;
  const bW = 340;
  const baseX = (W - bW) / 2;
  const baseY = H * 0.72;

  // Window lit pattern per floor (deterministic)
  const windowLit = (floor: number, win: number) => {
    if (!night) return C.sky;
    const seed = (floor * 7 + win * 3) % 10;
    return seed > 3 ? C.yellow : "#1A2A3A";
  };

  return (
    <g>
      {/* Ground */}
      <rect x={0} y={baseY} width={W} height={H - baseY} fill={night ? "#120E08" : C.ground} />
      <rect x={0} y={baseY - 18} width={W} height={18} fill={night ? "#1A180A" : C.grass} />

      {/* Road markings at base */}
      <rect x={0} y={baseY - 2} width={W} height={4} fill={night ? "#2A2010" : "#8B7355"} />

      {/* Building floors */}
      {Array.from({ length: Math.min(floors, totalFloors) }, (_, i) => {
        const y = baseY - (i + 1) * floorH;
        return (
          <g key={i}>
            <rect
              x={baseX}
              y={y}
              width={bW}
              height={floorH - 2}
              fill={night ? "#2A3844" : C.concrete}
              stroke={night ? "#3A4A5A" : "#A09585"}
              strokeWidth={1.5}
            />
            {[0, 1, 2].map((w) => (
              <rect
                key={w}
                x={baseX + 24 + w * 102}
                y={y + 8}
                width={68}
                height={floorH - 18}
                fill={windowLit(i, w)}
                rx={3}
              />
            ))}
          </g>
        );
      })}

      {/* Roof cap */}
      {floors > 0 && (
        <rect
          x={baseX - 12}
          y={baseY - Math.min(floors, totalFloors) * floorH - 10}
          width={bW + 24}
          height={14}
          fill={C.steel}
          rx={3}
        />
      )}

      {/* Floor counter badge */}
      {floors > 0 && floors < totalFloors && (
        <g>
          <rect
            x={baseX + bW + 16}
            y={baseY - Math.min(floors, totalFloors) * floorH - 8}
            width={110}
            height={48}
            fill={C.orange}
            rx={8}
          />
          <text
            x={baseX + bW + 71}
            y={baseY - Math.min(floors, totalFloors) * floorH + 26}
            fill={C.white}
            fontFamily="Impact, Arial Black, sans-serif"
            fontSize={30}
            fontWeight="bold"
            textAnchor="middle"
          >
            {`${floors}° AND`}
          </text>
        </g>
      )}

      {/* Crane */}
      {showCrane && floors > 0 && floors < totalFloors && (
        <g>
          <line
            x1={baseX + bW / 2}
            y1={baseY - floors * floorH - 10}
            x2={baseX + bW / 2}
            y2={baseY - floors * floorH - 160}
            stroke={C.steel}
            strokeWidth={8}
          />
          <line
            x1={baseX + bW / 2 - 20}
            y1={baseY - floors * floorH - 160}
            x2={baseX + bW / 2 + 180}
            y2={baseY - floors * floorH - 160}
            stroke={C.steel}
            strokeWidth={8}
          />
          <line
            x1={baseX + bW / 2 + 180}
            y1={baseY - floors * floorH - 160}
            x2={baseX + bW / 2 + 180}
            y2={baseY - floors * floorH - 60}
            stroke="#8A8A8A"
            strokeWidth={3}
            strokeDasharray="6,4"
          />
        </g>
      )}
    </g>
  );
};

/* ── SCENE 1: Hook ───────────────────────────────────────────── */
const SceneHook: React.FC = () => {
  const f = useCurrentFrame();
  const questionScale = 0.5 + 0.5 * sp(Math.max(0, f - 20));
  const arrowOp = interpolate(f, [25, 35], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill>
      <SkyBg />
      <svg width={W} height={H} style={{ position: "absolute" }}>
        {/* Empty terrain */}
        <rect x={0} y={H * 0.72} width={W} height={H * 0.28} fill={C.ground} />
        <rect x={0} y={H * 0.72 - 18} width={W} height={18} fill={C.grass} />
        {/* Arrow pointing down */}
        <g opacity={arrowOp}>
          <line
            x1={W / 2}
            y1={H * 0.6}
            x2={W / 2}
            y2={H * 0.68}
            stroke={C.orange}
            strokeWidth={8}
          />
          <polygon
            points={`${W / 2},${H * 0.70} ${W / 2 - 24},${H * 0.68} ${W / 2 + 24},${H * 0.68}`}
            fill={C.orange}
          />
        </g>
        {/* Question mark */}
        <text
          x={W / 2}
          y={H * 0.5}
          textAnchor="middle"
          dominantBaseline="middle"
          fontFamily="Impact, Arial Black, sans-serif"
          fontSize={280}
          fill={C.orange}
          style={{
            transform: `scale(${questionScale})`,
            transformOrigin: `${W / 2}px ${H * 0.5}px`,
          }}
        >
          ?
        </text>
      </svg>
      <div
        style={{
          position: "absolute",
          top: "14%",
          left: 60,
          right: 60,
          textAlign: "center",
          opacity: interpolate(f, [0, 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
        }}
      >
        <span
          style={{
            fontFamily: "Impact, 'Arial Black', sans-serif",
            fontSize: 68,
            color: C.white,
            textShadow: "3px 3px 0 #000,-3px -3px 0 #000",
            lineHeight: 1.2,
            display: "block",
          }}
        >
          E SE VOCÊ PUDESSE VER
        </span>
        <span
          style={{
            fontFamily: "Impact, 'Arial Black', sans-serif",
            fontSize: 68,
            color: C.yellow,
            textShadow: "3px 3px 0 #000,-3px -3px 0 #000",
            lineHeight: 1.2,
            display: "block",
          }}
        >
          TUDO ISSO ACONTECER?
        </span>
      </div>
      <Sub text="Você está prestes a ver um prédio de 20 andares ser construído do zero." size={44} />
    </AbsoluteFill>
  );
};

/* ── SCENE 2: Character Card ─────────────────────────────────── */
const SceneCard: React.FC = () => {
  const f = useCurrentFrame();
  const cardScale = 0.7 + 0.3 * sp(f, 12, 100);
  const op = interpolate(f, [0, 8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", inset: 0, background: C.blue }} />
      <svg width={W} height={H} style={{ position: "absolute" }}>
        {/* Background grid lines */}
        {Array.from({ length: 12 }, (_, i) => (
          <line
            key={i}
            x1={0}
            y1={(i + 1) * (H / 12)}
            x2={W}
            y2={(i + 1) * (H / 12)}
            stroke="rgba(255,255,255,0.05)"
            strokeWidth={1}
          />
        ))}
        <Worker x={W / 2} y={H * 0.32} scale={3.5} />
      </svg>
      <div
        style={{
          position: "absolute",
          top: "52%",
          left: 80,
          right: 80,
          transform: `scale(${cardScale})`,
          transformOrigin: "center",
          opacity: op,
          background: "rgba(0,0,0,0.75)",
          border: `4px solid ${C.orange}`,
          borderRadius: 20,
          padding: "32px 40px",
          textAlign: "center",
        }}
      >
        <div
          style={{
            fontFamily: "Impact, 'Arial Black', sans-serif",
            fontSize: 90,
            color: C.white,
            lineHeight: 1,
            marginBottom: 8,
          }}
        >
          MARCOS
        </div>
        <div
          style={{
            fontFamily: "Impact, 'Arial Black', sans-serif",
            fontSize: 52,
            color: C.yellow,
            letterSpacing: 4,
          }}
        >
          32 ANOS
        </div>
        <div
          style={{
            fontFamily: "'Arial Black', sans-serif",
            fontSize: 38,
            color: C.orange,
            marginTop: 8,
            letterSpacing: 2,
          }}
        >
          ENGENHEIRO CIVIL
        </div>
        <div
          style={{
            marginTop: 20,
            height: 4,
            background: C.orange,
            borderRadius: 2,
          }}
        />
        <div
          style={{
            fontFamily: "Arial, sans-serif",
            fontSize: 32,
            color: "rgba(255,255,255,0.7)",
            marginTop: 12,
          }}
        >
          MAIOR PROJETO DA SUA VIDA
        </div>
      </div>
      <Sub text="Marcos tinha acabado de ganhar o maior projeto da sua vida." size={44} />
    </AbsoluteFill>
  );
};

/* ── SCENE 3: Problem ────────────────────────────────────────── */
const SceneProblem: React.FC = () => {
  const f = useCurrentFrame();
  const item1 = interpolate(f, [0, 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const item2 = interpolate(f, [15, 25], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const item3 = interpolate(f, [30, 40], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", inset: 0, background: "#0F1A0F" }} />
      <div
        style={{
          position: "absolute",
          top: "12%",
          left: 60,
          right: 60,
          textAlign: "center",
          opacity: interpolate(f, [0, 8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
        }}
      >
        <div
          style={{
            fontFamily: "Impact, 'Arial Black', sans-serif",
            fontSize: 72,
            color: C.red,
            textShadow: "3px 3px 0 #000",
            lineHeight: 1,
          }}
        >
          O PROBLEMA?
        </div>
      </div>

      {/* Stat cards */}
      {[
        { label: "ORÇAMENTO", value: "R$ 12 MILHÕES", op: item1, y: "30%" },
        { label: "PRAZO", value: "24 MESES", op: item2, y: "50%" },
        { label: "TRABALHADORES", value: "300 PESSOAS", op: item3, y: "70%" },
      ].map(({ label, value, op, y }) => (
        <div
          key={label}
          style={{
            position: "absolute",
            top: y,
            left: 80,
            right: 80,
            transform: `translateY(-50%) translateX(${(1 - op) * -60}px)`,
            opacity: op,
            display: "flex",
            alignItems: "center",
            gap: 20,
            background: "rgba(255,255,255,0.08)",
            border: `2px solid ${C.orange}`,
            borderRadius: 14,
            padding: "20px 28px",
          }}
        >
          <div style={{ flex: 1 }}>
            <div style={{ fontFamily: "Arial, sans-serif", fontSize: 28, color: "rgba(255,255,255,0.6)", letterSpacing: 2 }}>
              {label}
            </div>
            <div style={{ fontFamily: "Impact, 'Arial Black', sans-serif", fontSize: 62, color: C.yellow, lineHeight: 1 }}>
              {value}
            </div>
          </div>
          <div style={{ width: 8, height: 70, background: C.orange, borderRadius: 4 }} />
        </div>
      ))}
      <Sub text="Qualquer erro destruiria tudo." color={C.red} size={56} />
    </AbsoluteFill>
  );
};

/* ── SCENE 4+5: Foundation ───────────────────────────────────── */
const SceneFoundation: React.FC = () => {
  const f = useCurrentFrame();
  const drillY = interpolate(f, [0, 50], [H * 0.3, H * 0.65], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill>
      <SkyBg />
      <svg width={W} height={H} style={{ position: "absolute" }}>
        {/* Ground layers */}
        <rect x={0} y={H * 0.72} width={W} height={H * 0.1} fill={C.ground} />
        <rect x={0} y={H * 0.82} width={W} height={H * 0.06} fill="#8B7355" />
        <rect x={0} y={H * 0.88} width={W} height={H * 0.06} fill="#6B5533" />
        <rect x={0} y={H * 0.94} width={W} height={H * 0.06} fill="#4A3822" />
        {/* Grass */}
        <rect x={0} y={H * 0.72 - 18} width={W} height={18} fill={C.grass} />

        {/* Drill hole */}
        <rect
          x={W / 2 - 18}
          y={H * 0.72}
          width={36}
          height={H * 0.22 - 10}
          fill="#2A1A0A"
          rx={4}
        />

        {/* Drill machine */}
        <rect x={W / 2 - 60} y={drillY - 80} width={120} height={80} fill={C.steel} rx={8} />
        <rect x={W / 2 - 10} y={drillY - 80} width={20} height={H * 0.72 - drillY + 80} fill="#5A6A7A" />
        {/* drill tip */}
        <polygon
          points={`${W / 2 - 14},${drillY} ${W / 2 + 14},${drillY} ${W / 2},${drillY + 30}`}
          fill={C.orange}
        />

        {/* Depth label */}
        <text
          x={W / 2 + 70}
          y={H * 0.88}
          fill={C.orange}
          fontFamily="Impact, Arial Black, sans-serif"
          fontSize={40}
        >
          18m
        </text>
        <text
          x={W / 2 + 68}
          y={H * 0.93}
          fill="rgba(255,255,255,0.7)"
          fontFamily="Arial, sans-serif"
          fontSize={26}
        >
          ROCHA FIRME
        </text>
      </svg>
      <Sub text="Primeiro: entender o que tem 18m abaixo dos seus pés." size={46} />
    </AbsoluteFill>
  );
};

/* ── SCENE 6+7: Building Growing ─────────────────────────────── */
const SceneBuilding: React.FC<{ targetFloors: number; night?: boolean }> = ({
  targetFloors,
  night = false,
}) => {
  const f = useCurrentFrame();
  const dur = 90;
  const floors = Math.ceil(interpolate(f, [0, dur], [0, targetFloors], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  }));

  return (
    <AbsoluteFill>
      <SkyBg night={night} />
      <svg width={W} height={H} style={{ position: "absolute" }}>
        <Building floors={floors} night={night} showCrane={floors < targetFloors} />
        {!night && floors < targetFloors && (
          <Worker x={W / 2 - 200} y={H * 0.72 - 90} scale={1.6} hatColor={C.yellow} />
        )}
        {!night && floors < targetFloors && (
          <Worker x={W / 2 + 220} y={H * 0.72 - 90} scale={1.6} hatColor={C.orange} flip />
        )}
      </svg>
      <Sub
        text={`Cada andar: 15 dias · 80 toneladas de concreto`}
        size={42}
      />
    </AbsoluteFill>
  );
};

/* ── SCENE 8: Crack Alert ────────────────────────────────────── */
const SceneCrack: React.FC = () => {
  const f = useCurrentFrame();
  const flash = interpolate(
    (f % 20) < 10 ? (f % 20) : 20 - (f % 20),
    [0, 10],
    [0, 0.6],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const alertScale = 0.5 + 0.5 * sp(f, 10, 150);

  return (
    <AbsoluteFill>
      <SkyBg night />
      <svg width={W} height={H} style={{ position: "absolute" }}>
        <Building floors={10} night />
        {/* Crack on building */}
        <path
          d={`M ${W / 2 + 60},${H * 0.72 - 10 * 44 + 20} L ${W / 2 + 40},${H * 0.72 - 10 * 44 + 50} L ${W / 2 + 55},${H * 0.72 - 10 * 44 + 65} L ${W / 2 + 35},${H * 0.72 - 10 * 44 + 90}`}
          stroke={C.red}
          strokeWidth={5}
          fill="none"
          strokeLinecap="round"
        />
        {/* Red flash overlay */}
        <rect x={0} y={0} width={W} height={H} fill={C.red} opacity={flash} />
      </svg>
      <div
        style={{
          position: "absolute",
          top: "18%",
          left: 70,
          right: 70,
          transform: `scale(${alertScale})`,
          transformOrigin: "center",
          background: C.red,
          border: `6px solid ${C.yellow}`,
          borderRadius: 20,
          padding: "28px 32px",
          textAlign: "center",
        }}
      >
        <div style={{ fontFamily: "Impact, 'Arial Black', sans-serif", fontSize: 56, color: C.white, lineHeight: 1 }}>
          ⚠️ ALERTA
        </div>
        <div style={{ fontFamily: "Impact, 'Arial Black', sans-serif", fontSize: 46, color: C.yellow, marginTop: 8 }}>
          RACHADURA DETECTADA
        </div>
        <div style={{ fontFamily: "Arial, sans-serif", fontSize: 32, color: C.white, marginTop: 8 }}>
          10° ANDAR · PILAR CENTRAL
        </div>
      </div>
      <Sub text="No 10° andar, Marcos encontrou algo que ninguém esperava." size={42} />
    </AbsoluteFill>
  );
};

/* ── SCENE 9: Decision ───────────────────────────────────────── */
const SceneDecision: React.FC = () => {
  const f = useCurrentFrame();
  const opt1 = interpolate(f, [0, 15], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const opt2 = interpolate(f, [20, 35], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", inset: 0, background: "#1A0A0A" }} />
      <BigText text="DECISÃO CRÍTICA" color={C.red} size={88} y="14%" />
      <div
        style={{
          position: "absolute",
          top: "26%",
          left: 70,
          right: 70,
          opacity: opt1,
          transform: `translateY(${(1 - opt1) * -30}px)`,
        }}
      >
        <div
          style={{
            border: `4px solid ${C.red}`,
            borderRadius: 16,
            padding: "24px 28px",
            background: "rgba(229,62,62,0.15)",
            textAlign: "center",
          }}
        >
          <div style={{ fontFamily: "Impact, 'Arial Black', sans-serif", fontSize: 56, color: C.red }}>
            DEMOLIR O ANDAR
          </div>
          <div style={{ fontFamily: "Arial, sans-serif", fontSize: 32, color: "rgba(255,255,255,0.6)", marginTop: 6 }}>
            -45 dias · R$ 800 mil
          </div>
        </div>
      </div>
      <div
        style={{
          position: "absolute",
          top: "50%",
          left: 70,
          right: 70,
          opacity: opt2,
          transform: `translateY(${(1 - opt2) * 30}px)`,
        }}
      >
        <div
          style={{
            border: `4px solid ${C.green}`,
            borderRadius: 16,
            padding: "24px 28px",
            background: "rgba(56,161,105,0.15)",
            textAlign: "center",
          }}
        >
          <div style={{ fontFamily: "Impact, 'Arial Black', sans-serif", fontSize: 56, color: C.green }}>
            REFORÇAR PILARES
          </div>
          <div style={{ fontFamily: "Arial, sans-serif", fontSize: 32, color: "rgba(255,255,255,0.6)", marginTop: 6 }}>
            -20 dias · R$ 300 mil
          </div>
        </div>
      </div>
      <div
        style={{
          position: "absolute",
          top: "72%",
          left: 0,
          right: 0,
          textAlign: "center",
          opacity: interpolate(f, [40, 55], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
        }}
      >
        <span style={{ fontFamily: "Impact, 'Arial Black', sans-serif", fontSize: 72, color: C.yellow }}>
          24H PARA DECIDIR
        </span>
      </div>
      <Sub text="R$ 800 mil em jogo. 24 horas para decidir." color={C.yellow} size={48} />
    </AbsoluteFill>
  );
};

/* ── SCENE 10-14: Technical scenes (compact) ─────────────────── */
const SceneTech: React.FC<{
  title: string;
  stat: string;
  detail: string;
  icon: "pipe" | "wire" | "brick" | "elevator" | "facade";
  bgColor?: string;
}> = ({ title, stat, detail, icon, bgColor = "#0A1A2A" }) => {
  const f = useCurrentFrame();
  const op = interpolate(f, [0, 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  const icons: Record<string, React.ReactNode> = {
    pipe: (
      <g>
        {[0, 1, 2, 3].map((i) => (
          <g key={i}>
            <line
              x1={W / 2 - 200 + i * 120}
              y1={H * 0.42}
              x2={W / 2 - 200 + i * 120}
              y2={H * 0.60}
              stroke="#4A90D9"
              strokeWidth={22}
              strokeLinecap="round"
            />
            <line
              x1={W / 2 - 200 + i * 120}
              y1={H * 0.60}
              x2={W / 2 - 160 + i * 120}
              y2={H * 0.60}
              stroke="#4A90D9"
              strokeWidth={22}
              strokeLinecap="round"
            />
          </g>
        ))}
      </g>
    ),
    wire: (
      <g>
        {[0, 1, 2].map((i) => (
          <line
            key={i}
            x1={W / 2 - 200}
            y1={H * 0.44 + i * 60}
            x2={W / 2 + 200}
            y2={H * 0.44 + i * 60}
            stroke={i === 1 ? C.yellow : "#2D7DD2"}
            strokeWidth={16}
            strokeLinecap="round"
          />
        ))}
      </g>
    ),
    brick: (
      <g>
        {[0, 1, 2, 3, 4].map((row) =>
          [0, 1, 2].map((col) => (
            <rect
              key={`${row}-${col}`}
              x={W / 2 - 200 + col * 140 + (row % 2) * 70}
              y={H * 0.42 + row * 44}
              width={120}
              height={36}
              fill="#C0603A"
              stroke="#8B3020"
              strokeWidth={2}
              rx={2}
            />
          ))
        )}
      </g>
    ),
    elevator: (
      <g>
        <rect x={W / 2 - 90} y={H * 0.38} width={180} height={240} fill="#3A4A5A" rx={6} stroke={C.steel} strokeWidth={4} />
        <rect x={W / 2 - 70} y={H * 0.42} width={60} height={120} fill="#2A3A4A" rx={3} />
        <rect x={W / 2 + 10} y={H * 0.42} width={60} height={120} fill="#2A3A4A" rx={3} />
        <circle cx={W / 2} cy={H * 0.36} r={28} fill={C.steel} />
        <line x1={W / 2 - 90} y1={H * 0.38} x2={W / 2} y2={H * 0.33} stroke="#8A8A8A" strokeWidth={6} />
        <line x1={W / 2 + 90} y1={H * 0.38} x2={W / 2} y2={H * 0.33} stroke="#8A8A8A" strokeWidth={6} />
        {/* Counterweight */}
        <rect x={W / 2 + 110} y={H * 0.44} width={60} height={80} fill="#5A6A7A" rx={4} />
        <line x1={W / 2 + 140} y1={H * 0.44} x2={W / 2} y2={H * 0.33} stroke="#8A8A8A" strokeWidth={4} strokeDasharray="8,4" />
      </g>
    ),
    facade: (
      <g>
        <Building floors={16} />
        {/* Glass panels on facade */}
        {[0, 1, 2, 3].map((i) => (
          <rect
            key={i}
            x={W / 2 - 160 + i * 85}
            y={H * 0.72 - 16 * 44 - 10}
            width={70}
            height={16 * 44}
            fill="rgba(135,206,235,0.3)"
            stroke="rgba(255,255,255,0.4)"
            strokeWidth={1}
          />
        ))}
      </g>
    ),
  };

  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", inset: 0, background: bgColor }} />
      <svg width={W} height={H} style={{ position: "absolute", opacity: op }}>
        {icons[icon]}
      </svg>
      <div
        style={{
          position: "absolute",
          top: "14%",
          left: 60,
          right: 60,
          textAlign: "center",
          opacity: op,
        }}
      >
        <div style={{ fontFamily: "Impact, 'Arial Black', sans-serif", fontSize: 72, color: C.white, lineHeight: 1, textShadow: "3px 3px 0 #000" }}>
          {title}
        </div>
      </div>
      <div
        style={{
          position: "absolute",
          bottom: "28%",
          left: 70,
          right: 70,
          background: "rgba(0,0,0,0.7)",
          border: `3px solid ${C.orange}`,
          borderRadius: 14,
          padding: "18px 22px",
          textAlign: "center",
          opacity: interpolate(f, [15, 28], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
        }}
      >
        <div style={{ fontFamily: "Impact, 'Arial Black', sans-serif", fontSize: 70, color: C.yellow, lineHeight: 1 }}>
          {stat}
        </div>
        <div style={{ fontFamily: "Arial, sans-serif", fontSize: 32, color: "rgba(255,255,255,0.75)", marginTop: 6 }}>
          {detail}
        </div>
      </div>
      <Sub text={detail} size={40} />
    </AbsoluteFill>
  );
};

/* ── SCENE 16: Inspection Failed ─────────────────────────────── */
const SceneInspectionFail: React.FC = () => {
  const f = useCurrentFrame();
  const stampScale = f > 25 ? 0.5 + 0.5 * sp(f - 25, 8, 200) : 0;
  const stampOp = interpolate(f - 25, [0, 5], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill>
      <SkyBg />
      <svg width={W} height={H} style={{ position: "absolute" }}>
        <Building floors={20} />
        {/* Inspector with clipboard */}
        <Worker x={W * 0.25} y={H * 0.72 - 90} scale={1.8} hatColor={C.red} />
        {/* Clipboard */}
        <rect x={W * 0.25 + 30} y={H * 0.72 - 160} width={90} height={110} fill={C.white} rx={4} stroke="#8A8A8A" strokeWidth={3} />
        {[0, 1, 2, 3].map((l) => (
          <line
            key={l}
            x1={W * 0.25 + 40}
            y1={H * 0.72 - 148 + l * 24}
            x2={W * 0.25 + 108}
            y2={H * 0.72 - 148 + l * 24}
            stroke="#8A8A8A"
            strokeWidth={3}
          />
        ))}
      </svg>

      {/* REPROVADO stamp */}
      <div
        style={{
          position: "absolute",
          top: "22%",
          left: 90,
          right: 90,
          transform: `scale(${stampScale}) rotate(-8deg)`,
          transformOrigin: "center",
          opacity: stampOp,
          border: `10px solid ${C.red}`,
          borderRadius: 16,
          padding: "24px",
          textAlign: "center",
          background: "rgba(229,62,62,0.12)",
        }}
      >
        <div style={{ fontFamily: "Impact, 'Arial Black', sans-serif", fontSize: 100, color: C.red, lineHeight: 1 }}>
          REPROVADO
        </div>
        <div style={{ fontFamily: "Arial, sans-serif", fontSize: 36, color: C.white, marginTop: 6 }}>
          VISTORIA DA PREFEITURA
        </div>
      </div>
      <Sub text="3 dias antes da entrega: vistoria reprovada." color={C.red} size={50} />
    </AbsoluteFill>
  );
};

/* ── SCENE 17: Race ──────────────────────────────────────────── */
const SceneRace: React.FC = () => {
  const f = useCurrentFrame();
  const count = Math.max(0, 72 - Math.floor(f * 0.9));

  return (
    <AbsoluteFill>
      <SkyBg night />
      <svg width={W} height={H} style={{ position: "absolute" }}>
        <Building floors={20} night />
        {/* Spotlights */}
        <ellipse cx={W / 2 - 160} cy={H * 0.72 - 10} rx={80} ry={240} fill="rgba(255,255,180,0.08)" />
        <ellipse cx={W / 2 + 160} cy={H * 0.72 - 10} rx={80} ry={240} fill="rgba(255,255,180,0.08)" />
        {/* Workers at night */}
        {[-3, -1, 1, 3].map((i) => (
          <Worker
            key={i}
            x={W / 2 + i * 130}
            y={H * 0.72 - 90}
            scale={1.5}
            hatColor={i < 0 ? C.yellow : C.orange}
          />
        ))}
      </svg>
      <div
        style={{
          position: "absolute",
          top: "16%",
          left: 0,
          right: 0,
          textAlign: "center",
        }}
      >
        <div style={{ fontFamily: "Impact, 'Arial Black', sans-serif", fontSize: 56, color: "rgba(255,255,255,0.7)", letterSpacing: 4 }}>
          CONTAGEM REGRESSIVA
        </div>
        <div
          style={{
            fontFamily: "Impact, 'Arial Black', sans-serif",
            fontSize: 160,
            color: count <= 24 ? C.red : C.yellow,
            lineHeight: 1,
            textShadow: "0 0 30px rgba(255,100,0,0.5)",
          }}
        >
          {count}H
        </div>
      </div>
      <Sub text="72 horas. 5 equipes. Sem dormir." color={C.yellow} size={56} />
    </AbsoluteFill>
  );
};

/* ── SCENE 18: Approval ──────────────────────────────────────── */
const SceneApproval: React.FC = () => {
  const f = useCurrentFrame();
  const stampScale = f > 15 ? 0.3 + 0.7 * sp(f - 15, 8, 200) : 0;
  const stampOp = f > 15 ? 1 : 0;
  const bgFlash = interpolate(f, [15, 22], [0, 0.3], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill>
      <SkyBg />
      <svg width={W} height={H} style={{ position: "absolute" }}>
        <Building floors={20} />
        <Worker x={W / 2} y={H * 0.72 - 90} scale={2} hatColor={C.yellow} />
        <rect x={0} y={0} width={W} height={H} fill={C.green} opacity={bgFlash} />
      </svg>
      <div
        style={{
          position: "absolute",
          top: "18%",
          left: 90,
          right: 90,
          transform: `scale(${stampScale}) rotate(-5deg)`,
          transformOrigin: "center",
          opacity: stampOp,
          border: `10px solid ${C.green}`,
          borderRadius: 16,
          padding: "24px",
          textAlign: "center",
          background: "rgba(56,161,105,0.15)",
        }}
      >
        <div style={{ fontFamily: "Impact, 'Arial Black', sans-serif", fontSize: 100, color: C.green, lineHeight: 1 }}>
          APROVADO
        </div>
        <div style={{ fontFamily: "Arial, sans-serif", fontSize: 36, color: C.white, marginTop: 6 }}>
          HABITE-SE EMITIDO
        </div>
        <div style={{ fontFamily: "Impact, 'Arial Black', sans-serif", fontSize: 48, color: C.yellow, marginTop: 8 }}>
          17:58 — ÚLTIMO DIA
        </div>
      </div>
      <Sub text="No último dia, às 17h58… aprovado." color={C.green} size={54} />
    </AbsoluteFill>
  );
};

/* ── SCENE 20: Viral Number ──────────────────────────────────── */
const SceneViralNumber: React.FC = () => {
  const f = useCurrentFrame();
  const count = Math.floor(interpolate(f, [0, 100], [0, 9600], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  }));
  const bigScale = 0.6 + 0.4 * sp(f, 10, 60);

  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", inset: 0, background: "#050810" }} />
      <div
        style={{
          position: "absolute",
          top: "20%",
          left: 0,
          right: 0,
          textAlign: "center",
          opacity: interpolate(f, [0, 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
        }}
      >
        <div style={{ fontFamily: "'Arial Black', sans-serif", fontSize: 36, color: "rgba(255,255,255,0.5)", letterSpacing: 6, textTransform: "uppercase" }}>
          Para construir esse prédio foram usados
        </div>
      </div>
      <div
        style={{
          position: "absolute",
          top: "36%",
          left: 0,
          right: 0,
          textAlign: "center",
          transform: `scale(${bigScale})`,
          transformOrigin: "center",
        }}
      >
        <div
          style={{
            fontFamily: "Impact, 'Arial Black', sans-serif",
            fontSize: 160,
            color: C.orange,
            lineHeight: 1,
            textShadow: `0 0 60px ${C.orange}`,
            fontVariantNumeric: "tabular-nums",
          }}
        >
          {count.toLocaleString("pt-BR")}
        </div>
        <div
          style={{
            fontFamily: "Impact, 'Arial Black', sans-serif",
            fontSize: 68,
            color: C.yellow,
            lineHeight: 1,
            marginTop: 8,
          }}
        >
          CAMINHONADAS
        </div>
        <div
          style={{
            fontFamily: "Arial, sans-serif",
            fontSize: 38,
            color: "rgba(255,255,255,0.65)",
            marginTop: 10,
          }}
        >
          de material de construção
        </div>
      </div>
      <Sub text="9.600 caminhões. É o que custa um prédio de 20 andares." size={42} />
    </AbsoluteFill>
  );
};

/* ── SCENE 21: Scale Data ────────────────────────────────────── */
const SceneScaleData: React.FC = () => {
  const f = useCurrentFrame();
  const items = [
    { label: "TIJOLOS", value: "1.440.000", delay: 0 },
    { label: "AÇO", value: "2.400 toneladas", delay: 15 },
    { label: "CONCRETO", value: "8.600 m³", detail: "= 3 piscinas olímpicas", delay: 30 },
  ];

  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", inset: 0, background: "#0A100A" }} />
      <div
        style={{
          position: "absolute",
          top: "10%",
          left: 0,
          right: 0,
          textAlign: "center",
          opacity: interpolate(f, [0, 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
        }}
      >
        <span style={{ fontFamily: "Impact, 'Arial Black', sans-serif", fontSize: 72, color: C.white, textShadow: "3px 3px 0 #000" }}>
          A ESCALA DA OBRA
        </span>
      </div>
      <div style={{ position: "absolute", top: "24%", left: 60, right: 60, display: "flex", flexDirection: "column", gap: 28 }}>
        {items.map(({ label, value, detail, delay }) => {
          const op = interpolate(f - delay, [0, 15], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          return (
            <div
              key={label}
              style={{
                opacity: op,
                transform: `translateX(${(1 - op) * -50}px)`,
                background: "rgba(255,255,255,0.06)",
                border: `2px solid ${C.green}`,
                borderRadius: 14,
                padding: "22px 28px",
                display: "flex",
                alignItems: "center",
                gap: 24,
              }}
            >
              <div style={{ width: 6, height: 70, background: C.green, borderRadius: 3 }} />
              <div style={{ flex: 1 }}>
                <div style={{ fontFamily: "Arial, sans-serif", fontSize: 26, color: "rgba(255,255,255,0.5)", letterSpacing: 3, textTransform: "uppercase" }}>
                  {label}
                </div>
                <div style={{ fontFamily: "Impact, 'Arial Black', sans-serif", fontSize: 58, color: C.yellow, lineHeight: 1 }}>
                  {value}
                </div>
                {detail && (
                  <div style={{ fontFamily: "Arial, sans-serif", fontSize: 28, color: C.green, marginTop: 4 }}>
                    {detail}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
      <Sub text="8.600m³ de concreto — isso encheria 3 piscinas olímpicas." size={40} />
    </AbsoluteFill>
  );
};

/* ── SCENE 22: Cliffhanger ───────────────────────────────────── */
const SceneCliffhanger: React.FC = () => {
  const f = useCurrentFrame();
  const envelopeSlide = interpolate(f, [0, 30], [H, H * 0.4], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const textOp = interpolate(f, [80, 100], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", inset: 0, background: C.blue }} />
      <svg width={W} height={H} style={{ position: "absolute" }}>
        {/* Background city silhouette */}
        {[0, 1, 2, 3, 4, 5, 6].map((i) => (
          <rect
            key={i}
            x={i * 180 - 60}
            y={H * 0.5 - i % 3 * 120 - 80}
            width={140}
            height={H * 0.5 + i % 3 * 120 + 80}
            fill="#0D2040"
          />
        ))}
        {/* Marcos at desk */}
        <Worker x={W / 2} y={H * 0.65} scale={2.2} hatColor={C.orange} />
        {/* Desk */}
        <rect x={W / 2 - 200} y={H * 0.65 + 68} width={400} height={20} fill="#6B4E2A" rx={4} />

        {/* Envelope sliding in */}
        <g transform={`translate(${W / 2 - 160}, ${envelopeSlide})`}>
          <rect x={0} y={0} width={320} height={200} fill={C.concreteLight} rx={8} stroke="#A09585" strokeWidth={3} />
          <line x1={0} y1={0} x2={160} y2={100} stroke="#A09585" strokeWidth={3} />
          <line x1={320} y1={0} x2={160} y2={100} stroke="#A09585" strokeWidth={3} />
          <text x={160} y={140} textAnchor="middle" fontFamily="Impact, Arial Black, sans-serif" fontSize={28} fill={C.red} fontWeight="bold">
            PROJETO 2
          </text>
          <text x={160} y={168} textAnchor="middle" fontFamily="Arial, sans-serif" fontSize={22} fill="#6B5533">
            TORRE — 40 ANDARES
          </text>
        </g>
      </svg>
      <div
        style={{
          position: "absolute",
          top: "14%",
          left: 0,
          right: 0,
          textAlign: "center",
          opacity: textOp,
        }}
      >
        <div style={{ fontFamily: "Impact, 'Arial Black', sans-serif", fontSize: 90, color: C.yellow, textShadow: "4px 4px 0 #000", lineHeight: 1 }}>
          E DESSA VEZ...
        </div>
        <div style={{ fontFamily: "Impact, 'Arial Black', sans-serif", fontSize: 72, color: C.white, textShadow: "3px 3px 0 #000", marginTop: 8 }}>
          ELE ACEITOU?
        </div>
      </div>
      <Sub text="Novo projeto: Torre de 40 andares. Dobro do tamanho." size={44} />
    </AbsoluteFill>
  );
};

/* ── SCENE 23: CTA ───────────────────────────────────────────── */
const SceneCTA: React.FC = () => {
  const f = useCurrentFrame();
  const pulse = 0.95 + 0.05 * Math.sin(f * 0.2);

  return (
    <AbsoluteFill>
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `linear-gradient(160deg, ${C.blue} 0%, #0A1628 100%)`,
        }}
      />
      <svg width={W} height={H} style={{ position: "absolute" }}>
        {/* City silhouette with completed building */}
        {[0, 1, 2, 3, 4, 5].map((i) => (
          <rect
            key={i}
            x={i * 190 - 50}
            y={H * 0.65 - i % 3 * 100 - 60}
            width={130}
            height={H * 0.35 + i % 3 * 100 + 60}
            fill="#0D2040"
          />
        ))}
        <Building floors={20} night />
      </svg>

      <div
        style={{
          position: "absolute",
          top: "18%",
          left: 0,
          right: 0,
          textAlign: "center",
          opacity: interpolate(f, [0, 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
        }}
      >
        <div style={{ fontFamily: "Impact, 'Arial Black', sans-serif", fontSize: 56, color: "rgba(255,255,255,0.65)", letterSpacing: 6 }}>
          PARTE 2 EM BREVE
        </div>
      </div>

      <div
        style={{
          position: "absolute",
          top: "50%",
          left: 70,
          right: 70,
          transform: `translateY(-50%) scale(${pulse})`,
          background: C.orange,
          borderRadius: 24,
          padding: "32px 20px",
          textAlign: "center",
          boxShadow: `0 0 40px rgba(255,107,26,0.5)`,
          opacity: interpolate(f, [15, 28], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
        }}
      >
        <div style={{ fontFamily: "Impact, 'Arial Black', sans-serif", fontSize: 90, color: C.white, lineHeight: 1, textShadow: "3px 3px 0 rgba(0,0,0,0.3)" }}>
          SEGUE O PERFIL
        </div>
        <div style={{ fontFamily: "Impact, 'Arial Black', sans-serif", fontSize: 52, color: C.yellow, marginTop: 10, lineHeight: 1 }}>
          PARA VER A PARTE 2
        </div>
      </div>
    </AbsoluteFill>
  );
};

/* ── MAIN COMPOSITION ────────────────────────────────────────── */
export const PredioAnimation: React.FC = () => {
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      {/* Scene 1: Hook — 0–60f (2s) */}
      <Sequence from={tf(0)} durationInFrames={tf(2)}>
        <SceneHook />
      </Sequence>

      {/* Scene 2: Character card — 2–5s */}
      <Sequence from={tf(2)} durationInFrames={tf(3)}>
        <SceneCard />
      </Sequence>

      {/* Scene 3: Problem — 5–8s */}
      <Sequence from={tf(5)} durationInFrames={tf(3)}>
        <SceneProblem />
      </Sequence>

      {/* Scene 4+5: Foundation / Soil — 8–13s */}
      <Sequence from={tf(8)} durationInFrames={tf(5)}>
        <SceneFoundation />
      </Sequence>

      {/* Scene 6: Building growing (0→8 floors) — 13–18s */}
      <Sequence from={tf(13)} durationInFrames={tf(5)}>
        <SceneBuilding targetFloors={8} />
      </Sequence>

      {/* Scene 7: Building 8→15 floors — 18–21s (before crack) */}
      <Sequence from={tf(18)} durationInFrames={tf(3)}>
        <SceneBuilding targetFloors={15} />
      </Sequence>

      {/* Scene 8: Crack Alert — 21–24s */}
      <Sequence from={tf(21)} durationInFrames={tf(3)}>
        <SceneCrack />
      </Sequence>

      {/* Scene 9: Decision — 24–27s */}
      <Sequence from={tf(24)} durationInFrames={tf(3)}>
        <SceneDecision />
      </Sequence>

      {/* Scene 10: Hydraulic pipes — 27–30s */}
      <Sequence from={tf(27)} durationInFrames={tf(3)}>
        <SceneTech title="HIDRÁULICA" stat="12 KM" detail="de tubulação instalada por dentro das paredes" icon="pipe" bgColor="#0A1522" />
      </Sequence>

      {/* Scene 11: Electrical — 30–33s */}
      <Sequence from={tf(30)} durationInFrames={tf(3)}>
        <SceneTech title="ELÉTRICA" stat="480 TOMADAS" detail="240 lâmpadas · 1 subestação própria" icon="wire" bgColor="#15100A" />
      </Sequence>

      {/* Scene 12: Masonry — 33–36s */}
      <Sequence from={tf(33)} durationInFrames={tf(3)}>
        <SceneTech title="ALVENARIA" stat="MÊS 14" detail="As paredes fecham. O prédio começa a parecer real." icon="brick" bgColor="#1A0A0A" />
      </Sequence>

      {/* Scene 13: Elevator — 36–39s */}
      <Sequence from={tf(36)} durationInFrames={tf(3)}>
        <SceneTech title="ELEVADOR" stat="630 KG" detail="8 pessoas · funciona por contrapesos" icon="elevator" bgColor="#0A0A1A" />
      </Sequence>

      {/* Scene 14: Facade — 39–42s */}
      <Sequence from={tf(39)} durationInFrames={tf(3)}>
        <SceneTech title="FACHADA" stat="ANDAR 20" detail="Mês 18. O prédio finalmente tem um rosto." icon="facade" bgColor="#07121A" />
      </Sequence>

      {/* Scene 15: Fast cuts — building night 15→20 — 42–45s */}
      <Sequence from={tf(42)} durationInFrames={tf(3)}>
        <SceneBuilding targetFloors={20} night />
      </Sequence>

      {/* Scene 16: Inspection fail — 45–48s */}
      <Sequence from={tf(45)} durationInFrames={tf(3)}>
        <SceneInspectionFail />
      </Sequence>

      {/* Scene 17: Race against time — 48–51s */}
      <Sequence from={tf(48)} durationInFrames={tf(3)}>
        <SceneRace />
      </Sequence>

      {/* Scene 18: Approval — 51–54s */}
      <Sequence from={tf(51)} durationInFrames={tf(3)}>
        <SceneApproval />
      </Sequence>

      {/* Scene 19: Keys — 54–58s (reuse building with workers) */}
      <Sequence from={tf(54)} durationInFrames={tf(4)}>
        <AbsoluteFill>
          <SkyBg />
          <svg width={W} height={H} style={{ position: "absolute" }}>
            <Building floors={20} />
            {[-2, -1, 0, 1, 2].map((i) => (
              <Worker key={i} x={W / 2 + i * 160} y={H * 0.72 - 90} scale={1.4} hatColor={i % 2 === 0 ? C.yellow : C.orange} />
            ))}
          </svg>
          <BigText text="80 FAMÍLIAS" color={C.yellow} size={120} y="18%" />
          <BigText text="RECEBERAM AS CHAVES" color={C.white} size={68} y="30%" delay={15} />
          <Sub text="80 famílias receberam as chaves no mesmo dia." size={48} />
        </AbsoluteFill>
      </Sequence>

      {/* Scene 20: Viral number — 58–62s */}
      <Sequence from={tf(58)} durationInFrames={tf(4)}>
        <SceneViralNumber />
      </Sequence>

      {/* Scene 21: Scale data — 62–66s */}
      <Sequence from={tf(62)} durationInFrames={tf(4)}>
        <SceneScaleData />
      </Sequence>

      {/* Scene 22: Cliffhanger — 66–71s */}
      <Sequence from={tf(66)} durationInFrames={tf(5)}>
        <SceneCliffhanger />
      </Sequence>

      {/* Scene 23: CTA — 71–75s */}
      <Sequence from={tf(71)} durationInFrames={tf(4)}>
        <SceneCTA />
      </Sequence>
    </AbsoluteFill>
  );
};
