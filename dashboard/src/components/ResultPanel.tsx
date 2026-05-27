import type { TransitionEvent } from "react";

export type PanelId = 4 | 5 | 6 | 7 | 8;

type Props = {
  id: PanelId;
  expanded: boolean;
  onClose: () => void;
  onTransitionEnd?: (e: TransitionEvent) => void;
};

export function ResultPanel({ id, expanded, onClose, onTransitionEnd }: Props) {
  return (
    <div
      className={`resultPanel ${expanded ? "resultPanel--expanded" : ""}`}
      onTransitionEnd={onTransitionEnd}
    >
      <div className="resultPanelHeader">
        <span className="resultPanelTitle">Panel {id}</span>
        <button type="button" className="resultPanelClose" onClick={onClose} aria-label="Close panel">
          ✕
        </button>
      </div>
      <div className="resultPanelBody">
        <p className="resultPanelPlaceholder">Chart / table placeholder</p>
      </div>
    </div>
  );
}
