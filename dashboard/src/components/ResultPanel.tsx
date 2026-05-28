import type { TransitionEvent } from "react";
import MatplotlibImagePanel from "./MatplotlibImagePanel";

export type PanelId = 4 | 5 | 6 | 7 | 8 | 9;

const PANEL_LABELS: Record<PanelId, string> = {
  4: "Genetic PCA",
  5: "Heatmap",
  6: "Fitness evolution",
  7: "Gen/Geo correlation",
  8: "Bridge groups",
  9: "1000G"
};

type Props = {
  id: PanelId;
  expanded: boolean;
  onClose: () => void;
  experimentKey?: string | null;
  onTransitionEnd?: (e: TransitionEvent) => void;
};

function PanelBody({ id, experimentKey }: { id: PanelId; experimentKey?: string | null }) {
  const title = PANEL_LABELS[id];
  const prefix = experimentKey ? `/data/visualizations/${experimentKey}` : "/data/visualizations";
  const expectedPath =
    id === 4
      ? `${prefix}/genetic_pca.png`
      : id === 5
        ? `${prefix}/heatmap.png`
        : id === 6
          ? `${prefix}/fitness_evolution.png`
          : id === 7
            ? `${prefix}/gen_geo_correlation.png`
            : id === 8
              ? `${prefix}/bridge_groups.png`
              : `${prefix}/1000g.png`;

  if (id === 9) {
    return (
      <div style={{ color: "rgba(255,255,255,0.92)", fontSize: 13, lineHeight: 1.38 }}>
        <div style={{ fontWeight: 650, fontSize: 15, marginBottom: 10 }}>1000 Genomes superpopulations</div>

        <div style={{ color: "rgba(255,255,255,0.78)" }}>
          <div style={{ marginBottom: 10 }}>
            <div style={{ fontWeight: 650 }}>
              AFR — African
            </div>
            <div>Examples: Yoruba (Nigeria), Luhya (Kenya), Gambian, Mende (Sierra Leone)</div>
          </div>

          <div style={{ marginBottom: 10 }}>
            <div style={{ fontWeight: 650 }}>
              AMR — Admixed American
            </div>
            <div>Examples: Mexican ancestry (Los Angeles), Puerto Rican, Colombian, Peruvian</div>
          </div>

          <div style={{ marginBottom: 10 }}>
            <div style={{ fontWeight: 650 }}>
              EAS — East Asian
            </div>
            <div>Examples: Han Chinese (Beijing / Southern China), Japanese, Kinh (Vietnam), Dai (China)</div>
          </div>

          <div style={{ marginBottom: 10 }}>
            <div style={{ fontWeight: 650 }}>
              EUR — European
            </div>
            <div>Examples: British (England & Scotland), Finnish, Iberian (Spain), Toscani (Italy)</div>
          </div>

          <div>
            <div style={{ fontWeight: 650 }}>
              SAS — South Asian
            </div>
            <div>Examples: Punjabi (Lahore), Gujarati (Houston), Bengali (Bangladesh), Sri Lankan Tamil</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <MatplotlibImagePanel
      title={title}
      expectedPath={expectedPath}
      hint={
        "Put the PNG into results/, add it to dashboard/data-manifest.json, then run `npm run prepare:data` to copy into public/data."
      }
    />
  );
}

export function ResultPanel({ id, expanded, onClose, experimentKey, onTransitionEnd }: Props) {
  return (
    <div
      className={`resultPanel ${expanded ? "resultPanel--expanded" : ""}`}
      onTransitionEnd={onTransitionEnd}
    >
      <div className="resultPanelHeader">
        <span className="resultPanelTitle">{PANEL_LABELS[id]}</span>
        <button type="button" className="resultPanelClose" onClick={onClose} aria-label="Close panel">
          ✕
        </button>
      </div>
      <div className="resultPanelBody">
        <PanelBody id={id} experimentKey={experimentKey} />
      </div>
    </div>
  );
}
