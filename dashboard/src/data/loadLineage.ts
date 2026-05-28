import { fetchCsvRows } from "./csv";

export type LineageRow = {
  generation: number;
  fitness: number;
  chromosome: string;
};

export type LineageData = {
  /** generations[g][i] = cluster id for subject i (metadata order) */
  generations: number[][];
  fitness: number[];
};

function parseChromosome(s: string): number[] {
  // `chromosome` is a CSV cell containing a comma-separated list of ints.
  // Example: "5,1,4,0,5,..."
  const parts = s.split(",");
  const out = new Array<number>(parts.length);
  for (let i = 0; i < parts.length; i++) out[i] = Number(parts[i]);
  return out;
}

export async function loadLineage(experimentKey?: string | null): Promise<LineageData> {
  const path = experimentKey ? `/data/visualizations/${experimentKey}/lineage.csv` : "/data/runs/16_genetic_only_video/lineage.csv";
  const rows = (await fetchCsvRows(path, { dynamicTyping: true })) as unknown as LineageRow[];

  const generations: number[][] = [];
  const fitness: number[] = [];

  for (const r of rows) {
    const g = typeof r.generation === "number" ? r.generation : Number(r.generation);
    if (!Number.isFinite(g)) continue;
    const fit = typeof r.fitness === "number" ? r.fitness : Number(r.fitness);
    const chromo = parseChromosome(String(r.chromosome ?? ""));
    generations.push(chromo);
    fitness.push(Number.isFinite(fit) ? fit : NaN);
  }

  return { generations, fitness };
}

