import { useEffect, useMemo, useState } from "react";
import { ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis } from "recharts";
import type { CoreData } from "../data/loadCoreData";
import { loadCoreData } from "../data/loadCoreData";

type LoadState =
  | { status: "idle" | "loading" }
  | { status: "error"; error: string }
  | { status: "ready"; data: CoreData };

function meanUpperTriangle(m: number[][]): number {
  const n = m.length;
  let sum = 0;
  let count = 0;
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      sum += m[i][j];
      count++;
    }
  }
  return count ? sum / count : NaN;
}

export default function OverviewPage() {
  const [state, setState] = useState<LoadState>({ status: "idle" });

  useEffect(() => {
    let cancelled = false;
    setState({ status: "loading" });
    loadCoreData()
      .then((data) => {
        if (cancelled) return;
        setState({ status: "ready", data });
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

  const derived = useMemo(() => {
    if (state.status !== "ready") return null;
    const n = state.data.geneticDistance.length;
    const meanGen = meanUpperTriangle(state.data.geneticDistance);
    const meanGeo = meanUpperTriangle(state.data.geographicDistance);

    const points = state.data.metadata
      .map((r, i) => ({
        i,
        lat: typeof r.Latitude === "number" ? r.Latitude : Number(r.Latitude),
        lon: typeof r.Longitude === "number" ? r.Longitude : Number(r.Longitude),
        region: String(r.Region ?? ""),
        id: String(r.SGDP_ID ?? i)
      }))
      .filter((p) => Number.isFinite(p.lat) && Number.isFinite(p.lon));

    const regions = new Map<string, number>();
    for (const p of points) regions.set(p.region || "Unknown", (regions.get(p.region || "Unknown") ?? 0) + 1);

    return {
      n,
      meanGen,
      meanGeo,
      points,
      regionCount: regions.size
    };
  }, [state]);

  return (
    <div className="grid">
      <section className="card" style={{ gridColumn: "span 12" }}>
        <div className="cardHeader">
          <div className="cardTitle">Overview</div>
          <div className="pill">static data • smooth UI</div>
        </div>
        <div className="muted">
          This dashboard reads CSV snapshots from <code>public/data/</code> (copied from the repo via{" "}
          <code>npm run prepare:data</code>).
        </div>
      </section>

      <section className="card" style={{ gridColumn: "span 12" }}>
        <div className="cardHeader">
          <div className="cardTitle">Core dataset</div>
          {state.status === "ready" ? <div className="pill">loaded</div> : <div className="pill">{state.status}</div>}
        </div>

        {state.status === "error" ? (
          <div style={{ color: "var(--bad)" }}>
            Failed to load data. Run <code>npm run prepare:data</code> then refresh.
            <div className="muted" style={{ marginTop: 8 }}>
              {state.error}
            </div>
          </div>
        ) : (
          <div className="kpiRow">
            <div className="kpi">
              <div className="kpiLabel">Subjects (N)</div>
              <div className="kpiValue">{derived ? derived.n : "…"}</div>
            </div>
            <div className="kpi">
              <div className="kpiLabel">Mean genetic distance</div>
              <div className="kpiValue">{derived ? derived.meanGen.toFixed(2) : "…"}</div>
            </div>
            <div className="kpi">
              <div className="kpiLabel">Mean geographic distance (km)</div>
              <div className="kpiValue">{derived ? derived.meanGeo.toFixed(0) : "…"}</div>
            </div>
          </div>
        )}
      </section>

      <section className="card" style={{ gridColumn: "span 12" }}>
        <div className="cardHeader">
          <div className="cardTitle">Sample locations (lat/lon)</div>
          <div className="pill">{derived ? `${derived.points.length} points • ${derived.regionCount} regions` : "…"}</div>
        </div>

        <div style={{ height: 420 }}>
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart margin={{ top: 10, right: 18, bottom: 10, left: 10 }}>
              <XAxis type="number" dataKey="lon" name="Longitude" domain={[-180, 180]} tick={{ fill: "rgba(255,255,255,0.65)" }} />
              <YAxis type="number" dataKey="lat" name="Latitude" domain={[-90, 90]} tick={{ fill: "rgba(255,255,255,0.65)" }} />
              <Tooltip
                cursor={{ strokeDasharray: "3 3" }}
                contentStyle={{ background: "rgba(15, 20, 40, 0.95)", border: "1px solid rgba(255,255,255,0.18)" }}
                formatter={(_, __, item) => {
                  const p = item.payload as { id: string; region: string; lat: number; lon: number };
                  return [`${p.lat.toFixed(2)}, ${p.lon.toFixed(2)}`, `${p.id} • ${p.region}`];
                }}
              />
              <Scatter data={derived?.points ?? []} fill="rgba(124, 92, 255, 0.85)" isAnimationActive={false} />
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      </section>
    </div>
  );
}

