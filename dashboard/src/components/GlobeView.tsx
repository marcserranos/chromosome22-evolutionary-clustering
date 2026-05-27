import { useEffect, useMemo, useRef } from "react";
import Globe, { type GlobeMethods } from "react-globe.gl";
import type { SampleMetaRow } from "../data/types";

type GeoPoint = { lat: number; lng: number; id: string };

type Props = {
  metadata: SampleMetaRow[];
  points: { lat: number; lng: number; id: string; cluster: number; color: string }[] | null;
  k: number;
  selectedCluster: number | null;
  rotationSpeed: number;
  /** Increment to trigger a temporary spin-up/spin-down pulse */
  spinPulseToken?: number;
  tiltLat: number;
  /** Max vertical wiggle (degrees) from default north-heavy tilt */
  tiltWiggleDeg?: number;
};

// Textured earth (more reliable land/water separation than polygon overlay)
const EARTH_TEXTURE_URL = "https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg";
const EARTH_BUMP_URL = "https://unpkg.com/three-globe/example/img/earth-topology.png";

function clamp(n: number, min: number, max: number) {
  return Math.max(min, Math.min(max, n));
}

function geoKey(lat: number, lng: number) {
  // We intentionally treat ONLY exact matches as overlaps.
  return `${lat}|${lng}`;
}

function spreadOverlappingLocations<T extends GeoPoint>(pts: T[]): T[] {
  const groups = new Map<string, T[]>();
  for (const p of pts) {
    const key = geoKey(p.lat, p.lng);
    const arr = groups.get(key);
    if (arr) arr.push(p);
    else groups.set(key, [p]);
  }

  let any = false;
  const out: T[] = [];
  for (const arr of groups.values()) {
    if (arr.length <= 1) {
      out.push(arr[0]);
      continue;
    }
    any = true;

    // Stable ordering so the offsets don't "shuffle" between renders.
    const sorted = [...arr].sort((a, b) => a.id.localeCompare(b.id));
    const baseLat = sorted[0].lat;
    const baseLng = sorted[0].lng;

    // Degrees. Small but visible at the scale of our point radius.
    const baseR = 1.14;
    const lonScale = Math.max(0.35, Math.cos((baseLat * Math.PI) / 180));

    for (let i = 0; i < sorted.length; i++) {
      const p = sorted[i];
      const ring = Math.floor(i / 8);
      const slot = i % 8;
      const angle = (slot / 8) * Math.PI * 2;
      const r = baseR * (1 + ring * 0.7);
      const dLat = Math.sin(angle) * r;
      const dLng = (Math.cos(angle) * r) / lonScale;

      out.push({
        ...p,
        lat: clamp(baseLat + dLat, -89.9, 89.9),
        lng: ((baseLng + dLng + 540) % 360) - 180
      });
    }
  }

  return any ? out : pts;
}

export function GlobeView({
  metadata,
  points,
  selectedCluster,
  rotationSpeed,
  spinPulseToken,
  tiltLat,
  tiltWiggleDeg = 14
}: Props) {
  const globeRef = useRef<GlobeMethods | undefined>(undefined);
  const spinAnimRef = useRef<number | null>(null);

  const fallbackPoints = useMemo(() => {
    const raw = metadata
      .map((row, idx) => {
        const lat = typeof row.Latitude === "number" ? row.Latitude : Number(row.Latitude);
        const lon = typeof row.Longitude === "number" ? row.Longitude : Number(row.Longitude);
        if (!Number.isFinite(lat) || !Number.isFinite(lon)) return null;

        const id = String(row.SGDP_ID ?? idx);
        return { lat, lng: lon, id, cluster: 0, color: "rgba(255,255,255,0.8)" };
      })
      .filter((p): p is NonNullable<typeof p> => !!p);
    return spreadOverlappingLocations(raw);
  }, [metadata]);

  const pointsToRender = useMemo(() => {
    if (!points) return fallbackPoints;
    return spreadOverlappingLocations(points);
  }, [fallbackPoints, points]);

  useEffect(() => {
    const globe = globeRef.current;
    if (!globe) return;
    globe.pointOfView({ lat: tiltLat, lng: 10, altitude: 2.2 }, 0);
    const controls = globe.controls();
    controls.autoRotate = true;
    controls.autoRotateSpeed = rotationSpeed;

    // Limited vertical wiggle around the default tilt (no full vertical spin).
    const wiggleRad = (tiltWiggleDeg * Math.PI) / 180;
    queueMicrotask(() => {
      const center = controls.getPolarAngle();
      controls.minPolarAngle = Math.max(0.05, center - wiggleRad);
      controls.maxPolarAngle = Math.min(Math.PI - 0.05, center + wiggleRad);
    });
    controls.enablePan = false;
  }, [rotationSpeed, tiltLat, tiltWiggleDeg]);

  useEffect(() => {
    const globe = globeRef.current;
    if (!globe) return;
    const controls = globe.controls();

    if (spinAnimRef.current != null) {
      window.cancelAnimationFrame(spinAnimRef.current);
      spinAnimRef.current = null;
    }

    if (spinPulseToken == null) return;

    const base = rotationSpeed;
    const peak = base * 50;
    const durationMs = 5000;
    const start = performance.now();

    const tick = (now: number) => {
      const t = (now - start) / durationMs;
      const clamped = Math.max(0, Math.min(1, t));
      // Smooth 1 -> 5 -> 1 over 5s (peak at midpoint).
      const shape = Math.sin(Math.PI * clamped); // 0..1..0
      const speed = base + (peak - base) * shape;
      controls.autoRotateSpeed = speed;

      if (clamped >= 1) {
        controls.autoRotateSpeed = base;
        spinAnimRef.current = null;
        return;
      }
      spinAnimRef.current = window.requestAnimationFrame(tick);
    };

    spinAnimRef.current = window.requestAnimationFrame(tick);

    return () => {
      if (spinAnimRef.current != null) {
        window.cancelAnimationFrame(spinAnimRef.current);
        spinAnimRef.current = null;
      }
      controls.autoRotateSpeed = base;
    };
  }, [rotationSpeed, spinPulseToken]);

  return (
    <div className="globeCanvasHost">
      <Globe
        ref={globeRef}
        animateIn={true}
        backgroundColor="rgba(0,0,0,0)"
        globeImageUrl={EARTH_TEXTURE_URL}
        bumpImageUrl={EARTH_BUMP_URL}
        showAtmosphere={false}
        showGraticules={false}
        rendererConfig={{ antialias: false, alpha: true }}
        pointsData={pointsToRender}
        pointAltitude={(p) => {
          const gp = p as { cluster: number };
          const base = 0.025;
          if (selectedCluster == null) return base;
          return gp.cluster === selectedCluster ? base * 6 : base;
        }}
        pointRadius={0.28}
        pointColor="color"
        pointsMerge={false}
      />
    </div>
  );
}

export default GlobeView;
