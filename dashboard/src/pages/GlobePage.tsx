import { useEffect, useMemo, useRef, useState } from "react";
import { loadMetadata } from "../data/loadMetadata";
import type { SampleMetaRow } from "../data/types";
import GlobeView from "../components/GlobeView";
import { ResultPanel, type PanelId } from "../components/ResultPanel";
import { usePanelTransition } from "../hooks/usePanelTransition";
import { loadLineage, type LineageData } from "../data/loadLineage";

const PANEL_IDS: PanelId[] = [4, 5, 6, 7, 8, 9];
const PANEL_BUTTON_LABELS: Record<PanelId, string> = {
  4: "Genetic PCA",
  5: "Heatmap",
  6: "Fitness evolution",
  7: "Gen/Geo correlation",
  8: "Bridge groups",
  9: "1000G"
};

type LoadState =
  | { status: "idle" | "loading" }
  | { status: "error"; error: string }
  | { status: "ready"; metadata: SampleMetaRow[] };

type KChoice = 2 | 3 | 4 | 5 | 6;

type ClusteredPoint = {
  lat: number;
  lng: number;
  id: string;
  cluster: number; // 0..K-1
  color: string;
};

function clamp(n: number, min: number, max: number) {
  return Math.max(min, Math.min(max, n));
}

/** Cluster 1–6: red, blue, yellow, green, purple, orange */
const CLUSTER_COLORS = [
  "#e63946",
  "#2563eb",
  "#facc15",
  "#22c55e",
  "#a855f7",
  "#f97316"
] as const;

function colorForCluster(clusterIndex: number): string {
  return CLUSTER_COLORS[clusterIndex] ?? CLUSTER_COLORS[0];
}

function colorForAssignment(clusterIndex: number, k: number): string {
  if (clusterIndex < 0 || clusterIndex >= k) return "rgba(255,255,255,0.85)";
  return colorForCluster(clusterIndex);
}

function randomCluster(seed: number, k: number) {
  // deterministic-ish pseudo-random per (seed, index) to keep it stable per run
  const x = Math.sin(seed * 12.9898 + 78.233) * 43758.5453;
  return Math.floor((x - Math.floor(x)) * k);
}

function tintForCluster(clusterIndex: number | null) {
  if (clusterIndex == null) {
    return {
      bg: "rgba(255,255,255,0.16)",
      border: "rgba(255,255,255,0.4)",
      fg: "rgba(255,255,255,0.96)"
    };
  }
  const hex = colorForCluster(clusterIndex);
  const m = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  const r = m ? parseInt(m[1], 16) : 255;
  const g = m ? parseInt(m[2], 16) : 255;
  const b = m ? parseInt(m[3], 16) : 255;
  return {
    bg: `rgba(${r},${g},${b},0.24)`,
    border: `rgba(${r},${g},${b},0.7)`,
    fg: `rgba(${r},${g},${b},0.98)`,
    rgb: `${r}, ${g}, ${b}`
  };
}

export default function GlobePage() {
  const [state, setState] = useState<LoadState>({ status: "idle" });
  const [kChoice, setKChoice] = useState<KChoice>(4);
  const [geoCostEnabled, setGeoCostEnabled] = useState(true);
  const [simSeed, setSimSeed] = useState(1);
  const [spinPulse, setSpinPulse] = useState(0);
  const [clusteredPoints, setClusteredPoints] = useState<ClusteredPoint[] | null>(null);
  const [selectedCluster, setSelectedCluster] = useState<number | null>(null);
  const { displayedPanel, panelExpanded, isPanelOpen, openPanel, closePanel } = usePanelTransition();
  const [lineage, setLineage] = useState<LineageData | null>(null);
  const [lineageKey, setLineageKey] = useState<string | null>(null);
  const [hasSimulated, setHasSimulated] = useState(false);
  const animRef = useRef<number | null>(null);
  const lastGenRef = useRef<number>(-1);
  const [activeExperimentKey, setActiveExperimentKey] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setState({ status: "loading" });
    loadMetadata()
      .then((metadata) => {
        if (cancelled) return;
        setState({ status: "ready", metadata });
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        const msg = err instanceof Error ? err.message : String(err);
        setState({ status: "error", error: msg });
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const kEffective = kChoice;
  const activeTint = tintForCluster(selectedCluster);

  const basePoints = useMemo(() => {
    if (state.status !== "ready") return null;
    return state.metadata
      .map((row, idx) => {
        const lat = typeof row.Latitude === "number" ? row.Latitude : Number(row.Latitude);
        const lon = typeof row.Longitude === "number" ? row.Longitude : Number(row.Longitude);
        if (!Number.isFinite(lat) || !Number.isFinite(lon)) return null;
        const id = String(row.SGDP_ID ?? idx);
        return { lat, lng: lon, id };
      })
      .filter((p): p is NonNullable<typeof p> => !!p);
  }, [state]);

  // If K or cost mode changes, require re-simulation before showing cluster UI.
  useEffect(() => {
    setClusteredPoints(null);
    setSelectedCluster(null);
  }, [kEffective, geoCostEnabled]);

  const stopAnimation = () => {
    if (animRef.current != null) {
      window.cancelAnimationFrame(animRef.current);
      animRef.current = null;
    }
    lastGenRef.current = -1;
  };

  useEffect(() => {
    return () => stopAnimation();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const runSimulation = () => {
    if (state.status !== "ready") return;
    if (!basePoints) return;

    setHasSimulated(true);

    // Kick the 5-second spin pulse, and animate generations during that window.
    setSpinPulse((v) => v + 1);
    stopAnimation();
    setSelectedCluster(null);

    const k = kEffective;
    const expKey = `exp_k${kChoice}_${geoCostEnabled ? "gon" : "goff"}`;
    setActiveExperimentKey(expKey);
    if (lineageKey !== expKey) {
      setLineage(null);
      setLineageKey(expKey);
    }

    const startAnimation = (data: LineageData) => {
      const gens = data.generations;
      const durationMs = 5000;
      const gensPerSecond = 60;
      const maxGen = Math.min(299, gens.length - 1);
      const start = performance.now();

      const renderGen = (gi: number) => {
        const chromo = gens[gi];
        const pts: ClusteredPoint[] = basePoints.map((p, i) => {
          const assigned = chromo?.[i] ?? 0;
          const cluster = Number.isFinite(assigned) ? assigned : 0;
          return {
            ...p,
            cluster,
            color: colorForAssignment(cluster, k)
          };
        });
        setClusteredPoints(pts);
      };

      const tick = (now: number) => {
        const elapsed = now - start;
        const gi = Math.min(maxGen, Math.floor((elapsed / 1000) * gensPerSecond));
        if (gi !== lastGenRef.current) {
          lastGenRef.current = gi;
          renderGen(gi);
        }

        if (elapsed >= durationMs) {
          lastGenRef.current = maxGen;
          renderGen(maxGen);
          animRef.current = null;
          return;
        }

        animRef.current = window.requestAnimationFrame(tick);
      };

      animRef.current = window.requestAnimationFrame(tick);
    };

    if (lineage) {
      startAnimation(lineage);
      return;
    }

    loadLineage(expKey)
      .then((data) => {
        setLineage(data);
        startAnimation(data);
      })
      .catch(() => {
        // Fallback: keep old deterministic simulation behavior if lineage can't be loaded.
        const seed = simSeed + 1;
        const points: ClusteredPoint[] = basePoints.map((p, idx) => {
          const cluster = clamp(randomCluster(seed * 1000 + idx, k), 0, k - 1);
          return { ...p, cluster, color: colorForCluster(cluster) };
        });
        setSimSeed(seed);
        setClusteredPoints(points);
      });
  };

  return (
    <div
      className="globeLayout"
      style={
        {
          ["--tint-bg" as never]: activeTint.bg,
          ["--tint-border" as never]: activeTint.border,
          ["--tint-fg" as never]: activeTint.fg,
          ["--tint-rgb" as never]: activeTint.rgb ?? "255,255,255"
        } as React.CSSProperties
      }
    >
      <header className="globeHeader">
        <div className="group group-left">
          <div className="headerBox headerBox-strong headerBoxControl">
            <div className="controlTitle">K</div>
            <input
              className="kSlider"
              type="range"
              min={0}
              max={4}
              step={1}
              value={kChoice === 2 ? 0 : kChoice === 3 ? 1 : kChoice === 4 ? 2 : kChoice === 5 ? 3 : 4}
              style={
                {
                  ["--k-fill" as never]: `${
                    ((kChoice === 2 ? 0 : kChoice === 3 ? 1 : kChoice === 4 ? 2 : kChoice === 5 ? 3 : 4) / 4) *
                    100
                  }%`
                } as React.CSSProperties
              }
              onChange={(e) => {
                const v = Number(e.target.value);
                const next: KChoice = v === 0 ? 2 : v === 1 ? 3 : v === 2 ? 4 : v === 3 ? 5 : 6;
                setKChoice(next);
              }}
            />
            <div className="controlValue">
              {kChoice}
            </div>
          </div>

          <div className="headerBox headerBoxControl">
            <div className="toggleRow">
              <span className="controlTitle">Geographic cost</span>
              <button
                type="button"
                className={`iosToggle ${geoCostEnabled ? "iosToggle--on" : ""}`}
                onClick={() => setGeoCostEnabled((v) => !v)}
                aria-pressed={geoCostEnabled}
              >
                <span className="iosToggleKnob" />
              </button>
            </div>
          </div>

          <button
            type="button"
            className="headerBox headerBoxButton"
            onClick={runSimulation}
            disabled={state.status !== "ready"}
            style={
              state.status === "ready"
                ? {
                    backgroundColor: activeTint.bg,
                    borderColor: activeTint.border,
                    color: activeTint.fg
                  }
                : undefined
            }
          >
            Simulation
          </button>
        </div>
        <div className="group group-right">
          {PANEL_IDS.map((id) => {
            const isActive = displayedPanel === id && panelExpanded;
            return (
              <button
                key={id}
                type="button"
                className={`headerBox headerBoxPanel ${isActive ? "headerBoxPanel--active" : ""}`}
                onClick={() => openPanel(id)}
                disabled={!hasSimulated}
                aria-disabled={!hasSimulated}
                style={
                  !hasSimulated
                    ? {
                        opacity: 0.5,
                        cursor: "not-allowed"
                      }
                    : isActive
                    ? {
                        backgroundColor: activeTint.bg,
                        borderColor: activeTint.border,
                        color: activeTint.fg
                      }
                    : undefined
                }
              >
                {PANEL_BUTTON_LABELS[id]}
              </button>
            );
          })}
        </div>
      </header>

      <main className={`globeMain workspace ${isPanelOpen || displayedPanel != null ? "workspace--split" : ""}`}>
        {state.status === "error" && (
          <div className="loadError">
            <div>Failed to load subject locations.</div>
            <div className="muted">
              Run <code>npm run prepare:data</code> in <code>dashboard/</code>, then refresh.
            </div>
            <div className="muted" style={{ marginTop: 6 }}>
              {state.error}
            </div>
          </div>
        )}
        {state.status !== "error" && state.status !== "ready" && (
          <div className="loading">loading subjects…</div>
        )}
        {state.status === "ready" && (
          <>
            <div className={`globeStage ${isPanelOpen || displayedPanel != null ? "globeStage--shifted" : ""}`}>
              <div className="globeShell">
                <GlobeView
                  metadata={state.metadata}
                  points={clusteredPoints}
                  k={kEffective}
                  selectedCluster={selectedCluster}
                  rotationSpeed={0.55}
                  spinPulseToken={spinPulse}
                  tiltLat={55}
                />

                {clusteredPoints && (
                  <div className="clusterMenu">
                    {Array.from({ length: kEffective }, (_, i) => {
                      const active = selectedCluster === i;
                      const tint = tintForCluster(i);
                      return (
                        <button
                          key={i}
                          type="button"
                          className={`clusterBtn ${active ? "active" : ""}`}
                          onClick={() => setSelectedCluster((cur) => (cur === i ? null : i))}
                          style={
                            active
                              ? {
                                  backgroundColor: tint.bg,
                                  borderColor: tint.border,
                                  color: "rgba(255,255,255,0.98)"
                                }
                              : undefined
                          }
                        >
                          Cluster {i + 1}
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>

            <aside
              className={`panelAside ${displayedPanel != null ? "panelAside--visible" : ""} ${panelExpanded ? "panelAside--expanded" : ""}`}
              aria-hidden={displayedPanel == null}
            >
              {displayedPanel != null && (
                <ResultPanel
                  id={displayedPanel}
                  expanded={panelExpanded}
                  onClose={closePanel}
                  experimentKey={activeExperimentKey}
                />
              )}
            </aside>
          </>
        )}
      </main>
    </div>
  );
}
