"""
Cluster consistency analysis: canonical labeling and stability metrics across multiple runs.
"""

import numpy as np
from scipy.optimize import linear_sum_assignment
from sklearn.metrics import adjusted_rand_score


class ConsistencyAnalyzer:
    """Handles relabeling, stability computation, and consistency metrics across multiple EA runs."""

    @staticmethod
    def relabel_partition_hungarian(reference_chromosome, target_chromosome):
        """
        Relabel target_chromosome to match reference_chromosome using optimal bipartite matching.

        Creates overlap matrix M[i,j] = # subjects in cluster i (reference) AND cluster j (target),
        then uses Hungarian algorithm to find matching that maximizes overlap.

        Args:
            reference_chromosome: list/array of cluster assignments for reference run
            target_chromosome: list/array of cluster assignments to relabel

        Returns:
            relabeled_chromosome: target_chromosome with clusters relabeled
            permutation: dict mapping {old_label: new_label}
            overlap_matrix: the overlap matrix used (useful for visualization)
        """
        k_groups = max(reference_chromosome) + 1
        ref_array = np.array(reference_chromosome)
        tgt_array = np.array(target_chromosome)

        # Build overlap matrix: rows=reference clusters, cols=target clusters
        overlap = np.zeros((k_groups, k_groups))
        for i in range(k_groups):
            for j in range(k_groups):
                overlap[i, j] = np.sum((ref_array == i) & (tgt_array == j))

        # Hungarian algorithm: maximize overlap (negate for minimization)
        ref_indices, tgt_indices = linear_sum_assignment(-overlap)

        # Create permutation: old_label (in target) -> new_label (to match reference)
        permutation = {tgt_indices[i]: ref_indices[i] for i in range(len(ref_indices))}

        # Apply relabeling
        relabeled = np.array([permutation[label] for label in target_chromosome])

        return relabeled, permutation, overlap

    @staticmethod
    def canonicalize_all_partitions(list_of_chromosomes):
        """
        Relabel all partitions to match the first one (reference run).

        Args:
            list_of_chromosomes: list of chromosome arrays from different runs

        Returns:
            canonicalized: list of relabeled chromosome arrays (first is unchanged)
            permutations: list of permutation dicts used for relabeling
            overlap_matrices: list of overlap matrices for each relabeling
        """
        reference = np.array(list_of_chromosomes[0])
        canonicalized = [reference]
        permutations = [{}]  # Reference run has identity permutation
        overlap_matrices = [None]

        for target in list_of_chromosomes[1:]:
            relabeled, perm, overlap = ConsistencyAnalyzer.relabel_partition_hungarian(reference, target)
            canonicalized.append(relabeled)
            permutations.append(perm)
            overlap_matrices.append(overlap)

        return canonicalized, permutations, overlap_matrices

    @staticmethod
    def compute_subject_stability(list_of_chromosomes):
        """
        Compute stability metrics for each subject across all runs.

        For each subject, determines:
        - Most frequent cluster assignment (after canonicalization)
        - Consistency fraction: % of runs in most frequent cluster
        - Raw assignments across runs (for detailed inspection)

        Args:
            list_of_chromosomes: list of canonicalized chromosome arrays

        Returns:
            stability_scores: dict {subject_idx: {'consistent_cluster': int, 'consistency_fraction': float}}
            cluster_assignments: dict {subject_idx: list of cluster assignments across runs}
        """
        num_subjects = len(list_of_chromosomes[0])
        num_runs = len(list_of_chromosomes)

        cluster_assignments = {i: [] for i in range(num_subjects)}
        stability_scores = {}

        # Collect assignments for each subject across all runs
        for chromosome in list_of_chromosomes:
            for subject_idx, cluster in enumerate(chromosome):
                cluster_assignments[subject_idx].append(int(cluster))

        # Compute stability metrics
        for subject_idx in range(num_subjects):
            assignments = np.array(cluster_assignments[subject_idx])
            unique_clusters, counts = np.unique(assignments, return_counts=True)

            most_common_idx = np.argmax(counts)
            most_common_cluster = int(unique_clusters[most_common_idx])
            consistency = float(counts[most_common_idx] / num_runs)

            stability_scores[subject_idx] = {
                'consistent_cluster': most_common_cluster,
                'consistency_fraction': consistency,
                'num_runs': num_runs,
                'num_unique_clusters': len(unique_clusters)
            }

        return stability_scores, cluster_assignments

    @staticmethod
    def compute_ari_matrix(list_of_chromosomes):
        """
        Compute Adjusted Rand Index (ARI) between all pairs of partitions.

        ARI is a standard metric for partition similarity: 1.0 = identical, 0.0 = random, <0 = worse than random

        Args:
            list_of_chromosomes: list of chromosome arrays

        Returns:
            ari_matrix: symmetric matrix of pairwise ARI values (n x n, where n = len(list_of_chromosomes))
        """
        n = len(list_of_chromosomes)
        ari_matrix = np.zeros((n, n))

        for i in range(n):
            ari_matrix[i, i] = 1.0  # Perfect match with self
            for j in range(i + 1, n):
                ari = adjusted_rand_score(list_of_chromosomes[i], list_of_chromosomes[j])
                ari_matrix[i, j] = ari
                ari_matrix[j, i] = ari

        return ari_matrix

    @staticmethod
    def compute_stability_summary(stability_scores):
        """
        Compute summary statistics from stability scores.

        Returns:
            summary: dict with keys like 'mean_consistency', 'std_consistency', 'num_stable_subjects', etc.
        """
        consistencies = np.array([s['consistency_fraction'] for s in stability_scores.values()])

        return {
            'mean_consistency': float(np.mean(consistencies)),
            'std_consistency': float(np.std(consistencies)),
            'min_consistency': float(np.min(consistencies)),
            'max_consistency': float(np.max(consistencies)),
            'num_stable_subjects': int(np.sum(consistencies == 1.0)),  # Always in same cluster
            'num_variable_subjects': int(np.sum(consistencies < 1.0)),  # At least one switch
            'num_frontier_subjects': int(np.sum(consistencies < 0.5))  # Less than half the time in primary cluster
        }
