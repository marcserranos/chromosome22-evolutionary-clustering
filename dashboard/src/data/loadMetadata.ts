import { fetchCsvRows } from "./csv";
import type { SampleMetaRow } from "./types";

export async function loadMetadata(): Promise<SampleMetaRow[]> {
  const rows = await fetchCsvRows("/data/metadata/samples_metadata_ordered.csv", {
    dynamicTyping: true
  });
  return rows as SampleMetaRow[];
}
