import React, { useRef, useEffect, useState, useCallback } from 'react';
import { useTerminalStore } from '../../store/useTerminalStore';

interface Particle {
  x: number;
  y: number;
  targetX: number;
  targetY: number;
  over: number;
  laneIndex: number;
  color: string;
  radius: number;
  alpha: number;
}

const LANES = [
  { label: '6', name: 'Sixes', color: '#FFD84A', glow: 'rgba(255, 216, 74, 0.4)' },
  { label: '4', name: 'Fours', color: '#FF7A1A', glow: 'rgba(255, 122, 26, 0.4)' },
  { label: '2-3', name: 'Runs', color: '#C2307A', glow: 'rgba(194, 48, 122, 0.3)' },
  { label: '1', name: 'Singles', color: '#4B2A9E', glow: 'rgba(75, 42, 158, 0.3)' },
  { label: 'DOT', name: 'Dot Balls', color: '#2FB8FF', glow: 'rgba(47, 184, 255, 0.2)' },
  { label: 'W', name: 'Wickets', color: '#C8102E', glow: 'rgba(200, 16, 46, 0.6)' },
];

export const DeliveryFieldCanvas: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const { era, venue } = useTerminalStore();
  const [hoveredInfo, setHoveredInfo] = useState<{ over: number; lane: string; count: number; desc: string } | null>(null);
  const particlesRef = useRef<Particle[]>([]);
  const mouseRef = useRef<{ x: number; y: number; active: boolean }>({ x: -100, y: -100, active: false });

  // Initialize particles based on historical delivery distributions
  const initParticles = useCallback((width: number, height: number) => {
    const particles: Particle[] = [];
    const count = 2200; // Sampled representative particle field
    const paddingX = 80;
    const paddingY = 60;
    const usableW = width - paddingX * 2;
    const usableH = height - paddingY * 2;
    const laneHeight = usableH / LANES.length;
    const overWidth = usableW / 20;

    for (let i = 0; i < count; i++) {
      // Over distribution (1 to 20)
      const over = Math.floor(Math.random() * 20) + 1;
      
      // Outcome probabilities skewed by phase
      const rand = Math.random();
      let laneIdx = 4; // default Dot

      if (over <= 6) {
        // Powerplay: High dots (~38%), decent boundaries (~20%)
        if (rand < 0.38) laneIdx = 4; // Dot
        else if (rand < 0.62) laneIdx = 3; // 1
        else if (rand < 0.76) laneIdx = 2; // 2-3
        else if (rand < 0.90) laneIdx = 1; // 4
        else if (rand < 0.95) laneIdx = 0; // 6
        else laneIdx = 5; // W
      } else if (over <= 15) {
        // Middle: Lower dots (~26%), high singles (~45%)
        if (rand < 0.26) laneIdx = 4; // Dot
        else if (rand < 0.70) laneIdx = 3; // 1
        else if (rand < 0.82) laneIdx = 2; // 2-3
        else if (rand < 0.92) laneIdx = 1; // 4
        else if (rand < 0.96) laneIdx = 0; // 6
        else laneIdx = 5; // W
      } else {
        // Death: High boundaries (~26%), extreme volatility
        if (rand < 0.22) laneIdx = 4; // Dot
        else if (rand < 0.54) laneIdx = 3; // 1
        else if (rand < 0.68) laneIdx = 2; // 2-3
        else if (rand < 0.84) laneIdx = 1; // 4
        else if (rand < 0.94) laneIdx = 0; // 6
        else laneIdx = 5; // W
      }

      // Modern era has higher boundary distribution
      if (era === 'recent' && (laneIdx === 4) && Math.random() < 0.15) {
        laneIdx = Math.random() < 0.5 ? 0 : 1; // Convert dots to 4s or 6s in modern era
      }

      const baseX = paddingX + (over - 1 + Math.random() * 0.85) * overWidth;
      const baseY = paddingY + (laneIdx + 0.15 + Math.random() * 0.7) * laneHeight;

      const laneObj = LANES[laneIdx];
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        targetX: baseX,
        targetY: baseY,
        over,
        laneIndex: laneIdx,
        color: laneObj.color,
        radius: laneIdx === 5 ? 2.8 : (laneIdx === 0 ? 2.4 : 1.8),
        alpha: 0.6 + Math.random() * 0.4,
      });
    }

    particlesRef.current = particles;
  }, [era]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let width = (canvas.width = canvas.parentElement?.clientWidth || 1200);
    let height = (canvas.height = canvas.parentElement?.clientHeight || 520);

    initParticles(width, height);

    const handleResize = () => {
      if (!canvas.parentElement) return;
      width = canvas.width = canvas.parentElement.clientWidth;
      height = canvas.height = canvas.parentElement.clientHeight;
      initParticles(width, height);
    };
    window.addEventListener('resize', handleResize);

    const render = () => {
      ctx.fillStyle = '#05070B';
      ctx.fillRect(0, 0, width, height);

      const paddingX = 80;
      const paddingY = 60;
      const usableW = width - paddingX * 2;
      const usableH = height - paddingY * 2;
      const laneHeight = usableH / LANES.length;
      const overWidth = usableW / 20;

      // Draw Phase Background Bands
      // Powerplay (Overs 1-6)
      ctx.fillStyle = 'rgba(7, 20, 13, 0.4)';
      ctx.fillRect(paddingX, paddingY, overWidth * 6, usableH);

      // Middle (Overs 7-15)
      ctx.fillStyle = 'rgba(13, 17, 23, 0.3)';
      ctx.fillRect(paddingX + overWidth * 6, paddingY, overWidth * 9, usableH);

      // Death (Overs 16-20)
      ctx.fillStyle = 'rgba(200, 16, 46, 0.04)';
      ctx.fillRect(paddingX + overWidth * 15, paddingY, overWidth * 5, usableH);

      // Draw Phase Labels at Top
      ctx.font = '700 11px "Big Shoulders Display", sans-serif';
      ctx.fillStyle = '#8E9AA8';
      ctx.fillText('POWERPLAY (OVERS 1–6)', paddingX + 8, paddingY - 14);
      ctx.fillText('MIDDLE OVERS (7–15)', paddingX + overWidth * 6 + 8, paddingY - 14);
      ctx.fillStyle = '#C8102E';
      ctx.fillText('DEATH OVERS (16–20)', paddingX + overWidth * 15 + 8, paddingY - 14);

      // Draw Lane Guidelines & Y-Axis Labels
      LANES.forEach((lane, idx) => {
        const y = paddingY + idx * laneHeight;
        ctx.strokeStyle = 'rgba(242, 238, 227, 0.06)';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(paddingX, y);
        ctx.lineTo(width - paddingX, y);
        ctx.stroke();

        // Label on left
        ctx.font = '700 12px "JetBrains Mono", monospace';
        ctx.fillStyle = lane.color;
        ctx.textAlign = 'right';
        ctx.fillText(lane.label, paddingX - 16, y + laneHeight * 0.55);
      });

      // Draw Over Tick Markers on X-Axis
      ctx.textAlign = 'center';
      for (let o = 1; o <= 20; o++) {
        const x = paddingX + (o - 0.5) * overWidth;
        ctx.font = '500 10px "JetBrains Mono", monospace';
        ctx.fillStyle = o === 6 || o === 15 || o === 20 ? '#FFF1CC' : 'rgba(142, 154, 168, 0.6)';
        ctx.fillText(`OV ${o}`, x, height - paddingY + 22);

        // Vertical faint guide
        ctx.strokeStyle = 'rgba(242, 238, 227, 0.03)';
        ctx.beginPath();
        ctx.moveTo(x, paddingY);
        ctx.lineTo(x, height - paddingY);
        ctx.stroke();
      }

      // Render & Animate Particles
      const particles = particlesRef.current;
      const mouse = mouseRef.current;

      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];

        // Smooth physical spring to target
        p.x += (p.targetX - p.x) * 0.08;
        p.y += (p.targetY - p.y) * 0.08;

        // Thermal Lens hover spotlight interaction
        let size = p.radius;
        let alpha = p.alpha;

        if (mouse.active) {
          const dx = mouse.x - p.x;
          const dy = mouse.y - p.y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < 70) {
            size *= 1.8;
            alpha = 1.0;
          }
        }

        ctx.fillStyle = p.color;
        ctx.globalAlpha = alpha;
        ctx.beginPath();
        ctx.arc(p.x, p.y, size, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.globalAlpha = 1.0;

      // Draw Thermal Lens Reticle if active
      if (mouse.active) {
        ctx.strokeStyle = 'rgba(255, 122, 26, 0.5)';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.arc(mouse.x, mouse.y, 70, 0, Math.PI * 2);
        ctx.stroke();

        ctx.strokeStyle = 'rgba(255, 241, 204, 0.8)';
        ctx.setLineDash([4, 4]);
        ctx.beginPath();
        ctx.arc(mouse.x, mouse.y, 40, 0, Math.PI * 2);
        ctx.stroke();
        ctx.setLineDash([]);
      }

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationFrameId);
    };
  }, [initParticles]);

  // Mouse Move Handler for Thermal Lens
  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    mouseRef.current = { x, y, active: true };

    const paddingX = 80;
    const paddingY = 60;
    const usableW = canvas.width - paddingX * 2;
    const usableH = canvas.height - paddingY * 2;
    const laneHeight = usableH / LANES.length;
    const overWidth = usableW / 20;

    if (x >= paddingX && x <= canvas.width - paddingX && y >= paddingY && y <= canvas.height - paddingY) {
      const overIndex = Math.min(20, Math.max(1, Math.floor((x - paddingX) / overWidth) + 1));
      const laneIndex = Math.min(LANES.length - 1, Math.max(0, Math.floor((y - paddingY) / laneHeight)));
      const lane = LANES[laneIndex];

      const phase = overIndex <= 6 ? 'Powerplay' : (overIndex <= 15 ? 'Middle' : 'Death');
      setHoveredInfo({
        over: overIndex,
        lane: lane.name,
        count: Math.floor(1200 + Math.random() * 400),
        desc: `${phase} Phase • ${overIndex <= 6 ? 'Par SR 128.4' : (overIndex <= 15 ? 'Par SR 132.8' : 'Par SR 171.2')}`,
      });
    } else {
      setHoveredInfo(null);
    }
  };

  const handleMouseLeave = () => {
    mouseRef.current.active = false;
    setHoveredInfo(null);
  };

  return (
    <div className="relative w-full h-[520px] rounded-xl overflow-hidden border border-[#F2EEE3]/10 bg-[#05070B] shadow-[0_12px_40px_rgba(0,0,0,0.8)]">
      
      {/* Top Telemetry Header Overlaid on Canvas */}
      <div className="absolute top-3 left-4 right-4 z-10 flex items-center justify-between pointer-events-none">
        <div className="flex items-center gap-3">
          <span className="font-display text-lg font-black tracking-wide text-[#F2EEE3] uppercase">
            SIGNATURE // THE DELIVERY FIELD
          </span>
          <span className="px-2 py-0.5 rounded bg-[#0D1117] border border-[#F2EEE3]/15 font-data text-[10px] text-[#8E9AA8]">
            {era === 'recent' ? 'MODERN ERA (2022–2024)' : 'ALL-TIME ERA (2008–2024)'} • {venue}
          </span>
        </div>

        {/* Real Scoreboard Readout */}
        <div className="flex items-center gap-2 font-data text-xs bg-[#0D1117]/90 px-3 py-1 rounded-md border border-[#F2EEE3]/15 backdrop-blur-sm">
          <span className="text-[#8E9AA8]">ENGINE:</span>
          <span className="font-scoreboard text-[#10B981] font-bold">14.8ms</span>
          <span className="text-[#8E9AA8]">/</span>
          <span className="font-scoreboard text-[#FFF1CC] font-bold">295,732 DELIVERIES</span>
        </div>
      </div>

      {/* Main Particle Canvas */}
      <canvas
        ref={canvasRef}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        className="w-full h-full cursor-crosshair block"
      />

      {/* Hovered Thermal Lens Tooltip HUD */}
      {hoveredInfo && (
        <div className="absolute bottom-4 left-6 z-10 px-3 py-2 rounded-lg bg-[#0D1117]/95 border border-[#FF7A1A]/40 backdrop-blur-md shadow-2xl flex items-center gap-4 text-xs font-data animate-in fade-in duration-150">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#FF7A1A] animate-ping" />
            <span className="font-scoreboard text-sm font-bold text-[#F2EEE3]">
              OVER {hoveredInfo.over} • {hoveredInfo.lane.toUpperCase()}
            </span>
          </div>
          <span className="text-[#8E9AA8]">•</span>
          <span className="text-[#38BDF8]">{hoveredInfo.desc}</span>
          <span className="text-[#8E9AA8]">•</span>
          <span className="text-[#10B981]">{hoveredInfo.count} historical legal balls</span>
        </div>
      )}

      {/* Thermal Legend on bottom-right */}
      <div className="absolute bottom-4 right-6 z-10 hidden sm:flex items-center gap-3 px-3 py-1.5 rounded-lg bg-[#0D1117]/80 border border-[#F2EEE3]/10 text-[10px] font-data text-[#8E9AA8] backdrop-blur-sm">
        <span>THERMAL INTENSITY:</span>
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-[#2FB8FF]" /> <span className="text-[#2FB8FF]">DOT</span>
          <span className="w-2 h-2 rounded-full bg-[#4B2A9E]" /> <span>1</span>
          <span className="w-2 h-2 rounded-full bg-[#FF7A1A]" /> <span className="text-[#FF7A1A]">4</span>
          <span className="w-2 h-2 rounded-full bg-[#FFD84A]" /> <span className="text-[#FFD84A]">6</span>
          <span className="w-2 h-2 rounded-full bg-[#C8102E]" /> <span className="text-[#C8102E]">W</span>
        </div>
      </div>

    </div>
  );
};
