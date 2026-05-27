import { useEffect, useRef } from "react";

export type StarfieldBackgroundProps = {
  className?: string;
  children?: React.ReactNode;
  /** Number of stars */
  count?: number;
  /** Travel speed */
  speed?: number;
  /** Star color */
  starColor?: string;
  /** Enable twinkling */
  twinkle?: boolean;
};

type Star = {
  x: number;
  y: number;
  z: number;
  twinkleSpeed: number;
  twinkleOffset: number;
};

function cx(...parts: Array<string | undefined | false>) {
  return parts.filter(Boolean).join(" ");
}

export function StarfieldBackground({
  className,
  children,
  count = 280,
  speed = 0.35,
  starColor = "#ffffff",
  twinkle = true
}: StarfieldBackgroundProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let width = 0;
    let height = 0;
    const maxDepth = 1500;
    let animationId = 0;
    let tick = 0;

    const resizeToContainer = () => {
      const rect = container.getBoundingClientRect();
      width = Math.max(1, Math.floor(rect.width));
      height = Math.max(1, Math.floor(rect.height));
      const dpr = Math.max(1, Math.min(2, window.devicePixelRatio || 1));
      canvas.width = Math.floor(width * dpr);
      canvas.height = Math.floor(height * dpr);
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };

    // Create stars
    const createStar = (initialZ?: number): Star => ({
      x: (Math.random() - 0.5) * width * 2,
      y: (Math.random() - 0.5) * height * 2,
      z: initialZ ?? Math.random() * maxDepth,
      twinkleSpeed: Math.random() * 0.02 + 0.01,
      twinkleOffset: Math.random() * Math.PI * 2
    });

    resizeToContainer();
    const stars: Star[] = Array.from({ length: count }, () => createStar());

    const ro = new ResizeObserver(() => resizeToContainer());
    ro.observe(container);

    // Initial clear
    ctx.fillStyle = "#0a0a0f";
    ctx.fillRect(0, 0, width, height);

    const animate = () => {
      tick++;

      // Fade effect for trails
      ctx.fillStyle = "rgba(10, 10, 15, 0.18)";
      ctx.fillRect(0, 0, width, height);

      const cx0 = width / 2;
      const cy0 = height / 2;

      for (const star of stars) {
        // Move star toward camera
        star.z -= speed * 2;

        // Reset if passed camera
        if (star.z <= 0) {
          star.x = (Math.random() - 0.5) * width * 2;
          star.y = (Math.random() - 0.5) * height * 2;
          star.z = maxDepth;
        }

        // Project to 2D
        const scale = 400 / star.z;
        const x = cx0 + star.x * scale;
        const y = cy0 + star.y * scale;

        // Skip if off screen
        if (x < -10 || x > width + 10 || y < -10 || y > height + 10) continue;

        // Size based on depth (closer = bigger)
        const size = Math.max(0.5, (1 - star.z / maxDepth) * 3);

        // Opacity based on depth (closer = brighter)
        let opacity = (1 - star.z / maxDepth) * 0.9 + 0.1;

        // Twinkle effect
        if (twinkle && star.twinkleSpeed > 0.015) {
          opacity *= 0.7 + 0.3 * Math.sin(tick * star.twinkleSpeed + star.twinkleOffset);
        }

        // Draw star
        ctx.beginPath();
        ctx.arc(x, y, size, 0, Math.PI * 2);
        ctx.fillStyle = starColor;
        ctx.globalAlpha = opacity;
        ctx.fill();

        // Draw subtle streak for fast/close stars
        if (star.z < maxDepth * 0.3 && speed > 0.3) {
          const streakLength = (1 - star.z / maxDepth) * speed * 8;
          const angle = Math.atan2(star.y, star.x);
          ctx.beginPath();
          ctx.moveTo(x, y);
          ctx.lineTo(x - Math.cos(angle) * streakLength, y - Math.sin(angle) * streakLength);
          ctx.strokeStyle = starColor;
          ctx.globalAlpha = opacity * 0.3;
          ctx.lineWidth = size * 0.5;
          ctx.stroke();
        }
      }

      ctx.globalAlpha = 1;
      animationId = window.requestAnimationFrame(animate);
    };

    animationId = window.requestAnimationFrame(animate);

    return () => {
      window.cancelAnimationFrame(animationId);
      ro.disconnect();
    };
  }, [count, speed, starColor, twinkle]);

  return (
    <div ref={containerRef} className={cx("starfieldRoot", className)}>
      <canvas ref={canvasRef} className="starfieldCanvas" />

      <div className="starfieldNebula" aria-hidden="true" />
      <div className="starfieldVignette" aria-hidden="true" />

      {children && <div className="starfieldContent">{children}</div>}
    </div>
  );
}

export default StarfieldBackground;

