import { useEffect, useState } from "react";
import { loadMetadata } from "../data/loadMetadata";
import type { SampleMetaRow } from "../data/types";
import GlobeView from "../components/GlobeView";
import { ResultPanel, type PanelId } from "../components/ResultPanel";
import { usePanelTransition } from "../hooks/usePanelTransition";

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

type KChoice = 2 | 3 | 4 | 5 | "explored";

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

  const kEffective = kChoice === "explored" ? 5 : kChoice;
  const activeTint = tintForCluster(selectedCluster);

  // If K changes, require re-simulation before showing cluster UI.
  useEffect(() => {
    setClusteredPoints(null);
    setSelectedCluster(null);
  }, [kEffective]);

  const runSimulation = () => {
    if (state.status !== "ready") return;

    const k = kEffective;
    const seed = simSeed + 1;

    const points: ClusteredPoint[] = state.metadata
      .map((row, idx) => {
        const lat = typeof row.Latitude === "number" ? row.Latitude : Number(row.Latitude);
        const lon = typeof row.Longitude === "number" ? row.Longitude : Number(row.Longitude);
        if (!Number.isFinite(lat) || !Number.isFinite(lon)) return null;

        const cluster = clamp(randomCluster(seed * 1000 + idx, k), 0, k - 1);
        const id = String(row.SGDP_ID ?? idx);
        return { lat, lng: lon, id, cluster, color: colorForCluster(cluster) };
      })
      .filter((p): p is ClusteredPoint => !!p);

    setSimSeed(seed);
    setSpinPulse((v) => v + 1);
    setSelectedCluster(null);
    setClusteredPoints(points);
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
                const next: KChoice = v === 0 ? 2 : v === 1 ? 3 : v === 2 ? 4 : v === 3 ? 5 : "explored";
                setKChoice(next);
              }}
            />
            <div className="controlValue">
              {kChoice === "explored" ? "Explored" : kChoice}
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
                style={
                  isActive
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
                <ResultPanel id={displayedPanel} expanded={panelExpanded} onClose={closePanel} />
              )}
            </aside>
          </>
        )}
      </main>
    </div>
  );
}
