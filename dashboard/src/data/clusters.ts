import { fetchCsvRows } from "./csv";

export type ClusterAssignment = {
  index: number;
  cluster: number;
  sgdpId?: string;
};

export async function loadClusterAssignments(): Promise<ClusterAssignment[] | null> {
  try {
    const rows = await fetchCsvRows("/data/ea/best_chromosome.csv", {
      dynamicTyping: true,
      skipEmptyLines: true
    });

    return rows.map((row, idx) => {
      const anyRow = row as Record<string, unknown>;
      const clusterVal = anyRow.cluster ?? anyRow.Cluster ?? anyRow.CLUSTER;
      const sgdp = (anyRow.SGDP_ID ?? anyRow.sgdp_id ?? anyRow.id) as string | undefined;
      const clusterNum = typeof clusterVal === "number" ? clusterVal : Number(clusterVal);
      return { index: idx, cluster: Number.isFinite(clusterNum) ? clusterNum : 0, sgdpId: sgdp };
    });
  } catch (err) {
    // If file is missing (404) or unreadable, fall back to no assignments.
    return null;
  }
}

