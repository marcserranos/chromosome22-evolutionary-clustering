import { useEffect, useMemo, useRef } from "react";
import Globe, { type GlobeMethods } from "react-globe.gl";
import type { SampleMetaRow } from "../data/types";

type Props = {
  metadata: SampleMetaRow[];
  points: { lat: number; lng: number; id: string; cluster: number; color: string }[] | null;
  k: number;
  selectedCluster: number | null;
  rotationSpeed: number;
  tiltLat: number;
  /** Max vertical wiggle (degrees) from default north-heavy tilt */
  tiltWiggleDeg?: number;
};

// Textured earth (more reliable land/water separation than polygon overlay)
const EARTH_TEXTURE_URL = "https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg";
const EARTH_BUMP_URL = "https://unpkg.com/three-globe/example/img/earth-topology.png";

export function GlobeView({
  metadata,
  points,
  selectedCluster,
  rotationSpeed,
  tiltLat,
  tiltWiggleDeg = 14
}: Props) {
  const globeRef = useRef<GlobeMethods | undefined>(undefined);

  const fallbackPoints = useMemo(() => {
    return metadata
      .map((row, idx) => {
        const lat = typeof row.Latitude === "number" ? row.Latitude : Number(row.Latitude);
        const lon = typeof row.Longitude === "number" ? row.Longitude : Number(row.Longitude);
        if (!Number.isFinite(lat) || !Number.isFinite(lon)) return null;

        const id = String(row.SGDP_ID ?? idx);
        return { lat, lng: lon, id, cluster: 0, color: "rgba(255,255,255,0.8)" };
      })
      .filter((p): p is NonNullable<typeof p> => !!p);
  }, [metadata]);

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
        pointsData={points ?? fallbackPoints}
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
