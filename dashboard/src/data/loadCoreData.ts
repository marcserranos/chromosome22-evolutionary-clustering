import { fetchCsvMatrix, fetchCsvRows } from "./csv";
import type { SampleMetaRow } from "./types";
import { loadClusterAssignments, type ClusterAssignment } from "./clusters";

export type CoreData = {
  geneticDistance: number[][];
  geographicDistance: number[][];
  metadata: SampleMetaRow[];
  clusters: ClusterAssignment[] | null;
};

export async function loadCoreData(): Promise<CoreData> {
  const [geneticDistance, geographicDistance, metadata, clusters] = await Promise.all([
    fetchCsvMatrix("/data/distances/genetic_distance.csv"),
    fetchCsvMatrix("/data/distances/geographic_distance.csv"),
    fetchCsvRows("/data/metadata/samples_metadata_ordered.csv", { dynamicTyping: true }),
    loadClusterAssignments()
  ]);

  return {
    geneticDistance,
    geographicDistance,
    metadata: metadata as SampleMetaRow[],
    clusters
  };
}

