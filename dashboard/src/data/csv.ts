import Papa from "papaparse";

export async function fetchText(path: string): Promise<string> {
  const res = await fetch(path, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch ${path}: ${res.status}`);
  return await res.text();
}

export async function fetchCsvRows(
  path: string,
  opts?: { dynamicTyping?: boolean; skipEmptyLines?: boolean }
): Promise<Record<string, unknown>[]> {
  const text = await fetchText(path);
  const parsed = Papa.parse<Record<string, unknown>>(text, {
    header: true,
    dynamicTyping: opts?.dynamicTyping ?? true,
    skipEmptyLines: opts?.skipEmptyLines ?? true
  });
  if (parsed.errors?.length) {
    const first = parsed.errors[0];
    throw new Error(`CSV parse error in ${path}: ${first.message}`);
  }
  return parsed.data;
}

export async function fetchCsvMatrix(path: string): Promise<number[][]> {
  const text = await fetchText(path);
  const parsed = Papa.parse<string[]>(text.trim(), {
    header: false,
    skipEmptyLines: true
  });
  if (parsed.errors?.length) {
    const first = parsed.errors[0];
    throw new Error(`CSV parse error in ${path}: ${first.message}`);
  }
  const rows = (parsed.data as unknown as string[][]).filter((r) => r.length > 0);
  // Many CSV exports include an empty header cell; we handle both pure numeric and row/col labels.
  // Strategy:
  // - If first cell of first row is non-numeric, treat first row/col as labels and drop them.
  const firstCell = rows[0]?.[0] ?? "";
  const firstCellNum = Number(firstCell);
  const hasLabels = Number.isNaN(firstCellNum);
  const numeric = rows.map((r) => r.map((v) => Number(v)));

  const matrix = hasLabels
    ? numeric.slice(1).map((r) => r.slice(1))
    : numeric.map((r) => r.slice());

  for (let i = 0; i < matrix.length; i++) {
    if (matrix[i].some((x) => !Number.isFinite(x))) {
      throw new Error(`Non-numeric value in matrix CSV: ${path} (row ${i})`);
    }
  }
  return matrix;
}

