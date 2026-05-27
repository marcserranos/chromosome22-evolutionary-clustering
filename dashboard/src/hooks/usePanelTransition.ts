import { useCallback, useRef, useState } from "react";
import type { PanelId } from "../components/ResultPanel";

const TRANSITION_MS = 450;

export function usePanelTransition() {
  const [displayedPanel, setDisplayedPanel] = useState<PanelId | null>(null);
  const [panelExpanded, setPanelExpanded] = useState(false);
  const pendingRef = useRef<PanelId | null>(null);
  const timerRef = useRef<number | null>(null);

  const clearTimer = () => {
    if (timerRef.current != null) {
      window.clearTimeout(timerRef.current);
      timerRef.current = null;
    }
  };

  const expandAfterPaint = useCallback((id: PanelId) => {
    setDisplayedPanel(id);
    requestAnimationFrame(() => {
      requestAnimationFrame(() => setPanelExpanded(true));
    });
  }, []);

  const collapseThen = useCallback((next: () => void) => {
    setPanelExpanded(false);
    clearTimer();
    timerRef.current = window.setTimeout(() => {
      timerRef.current = null;
      next();
    }, TRANSITION_MS);
  }, []);

  const openPanel = useCallback(
    (id: PanelId) => {
      if (displayedPanel === id && panelExpanded) return;

      if (displayedPanel != null) {
        pendingRef.current = id;
        collapseThen(() => {
          const target = pendingRef.current;
          pendingRef.current = null;
          if (target != null) expandAfterPaint(target);
        });
        return;
      }

      expandAfterPaint(id);
    },
    [collapseThen, displayedPanel, expandAfterPaint, panelExpanded]
  );

  const closePanel = useCallback(() => {
    pendingRef.current = null;
    clearTimer();
    if (displayedPanel == null) return;
    collapseThen(() => setDisplayedPanel(null));
  }, [collapseThen, displayedPanel]);

  const isPanelOpen = displayedPanel != null && panelExpanded;

  return {
    displayedPanel,
    panelExpanded,
    isPanelOpen,
    openPanel,
    closePanel
  };
}
