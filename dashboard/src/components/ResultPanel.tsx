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
            ? "/data/visualizations/gen_geo_correlation.png"
            : id === 8
              ? `${prefix}/bridge_groups.png`
              : `${prefix}/1000g.png`;

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
