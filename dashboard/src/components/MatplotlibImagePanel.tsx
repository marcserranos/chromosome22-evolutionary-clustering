export type MatplotlibImagePanelProps = {
  /** Display name for the panel */
  title: string;
  /** Where we expect the image to be copied under public/data */
  expectedPath?: string;
  /** Optional extra hint about generation */
  hint?: string;
};

export function MatplotlibImagePanel({ title, expectedPath, hint }: MatplotlibImagePanelProps) {
  return (
    <div className="mplPanel">
      <div className="mplMetaRow">
        <div className="mplMeta">
          <div className="mplMetaLabel">Dataset</div>
          <div className="mplMetaValue">{expectedPath ?? "—"}</div>
        </div>
        <div className="mplMeta">
          <div className="mplMetaLabel">Points</div>
          <div className="mplMetaValue">—</div>
        </div>
      </div>

      <div className="mplImageFrame" role="img" aria-label={`${title} figure`}>
        <div className="mplEmptyState">
          <div className="mplEmptyTitle">{title}</div>
          <div className="mplEmptyBody">Figure slot ready (matplotlib PNG).</div>
          {hint && <div className="mplEmptyHint">{hint}</div>}
        </div>
      </div>
    </div>
  );
}

export default MatplotlibImagePanel;

