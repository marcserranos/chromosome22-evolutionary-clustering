# Evolutionary clustering (`evo_algorithm`)

Partitions **subjects** (people in the distance matrices) into **K clusters** using a genetic algorithm.

## Vocabulary

| Term | Meaning |
|------|---------|
| **Subject** | One person in the dataset. Row/column `i` in the distance CSVs is subject `i`. |
| **Individual** | One **candidate partition**: length-N chromosome assigning each subject to a cluster `0 .. K-1`. |
| **Population** | The current **set of Individuals** the experiment evolves together (e.g. 80 candidates). |
| **Cluster** | A group label; not the same word as population. |

There is no “geographic population” in the code—only subjects, Individuals, and a Population of candidates.

---

## Problem

Symmetric N×N matrices:

- **Genetic distance** between subjects.
- **Geographic distance** between subjects.

Find an assignment vector:

```text
w[i] = cluster of subject i   (0 <= w[i] < K)
```

---

## Fitness

```text
fitness = alpha * separation - beta * variance - geographic_cost
```

- **Separation**: mean genetic distance for pairs in **different** clusters (want high).
- **Variance**: mean genetic distance for pairs in the **same** cluster (want low).
- **Geographic cost**: mean geographic distance within the same cluster (want low).

If any cluster has fewer than `min_group_size` subjects, fitness = `-1e9`.

---

## Modules

| File | Role |
|------|------|
| `data_loader.py` | Load distance CSVs; returns matrices and `subject_names`. |
| `individual.py` | `Individual`: chromosome, init, mutate, `subjects_per_cluster()`. |
| `population.py` | `Population`: list of Individuals, sort, roulette selection. |
| `fitness.py` | `FitnessEvaluator`: score one Individual. |
| `ea.py` | `EvolutionaryAlgorithm`: generational loop using a Population. |
| `main.py` | Entry point. |
| `visualizations.py` | Six plots after a run (world map, MDS, heatmap, sizes, etc.). |

---

## Algorithm (`ea.py`)

Each generation:

1. Evaluate every Individual in the Population.
2. Sort by fitness.
3. Copy top `elitism_count` unchanged into the next Population.
4. Until full: roulette-select two parents → crossover → mutate → evaluate two children.
5. Replace Population with the new list.

**Roulette selection** (`population.py`): weight = fitness − min(fitness) + ε.

**Crossover**: single-point swap on the chromosome.

**Mutation** (`individual.py`): per subject, with probability `mutation_rate`, move to a different cluster.

---

## Run

```bash
cd evo_algorithm
python main.py
```

Data: `../results/distances/*.csv`.

Tune in `main.py`: `k_groups`, `population_size`, `generations`, `alpha`, `beta`, rates, `min_group_size`.

---

## Output

Per-generation best fitness; final cluster sizes and subject IDs per cluster. Full assignment: `best.chromosome` (same order as CSV labels).

Plots are saved under `results/visualizations/ea/`:

1. **07_fitness_convergence.png** — best, mean, and worst fitness per generation.
2. **08_fitness_best_so_far.png** — running maximum of best fitness.
3. World map — subjects colored by cluster (Cartopy coastlines if installed).
4. MDS — genetic distance embedding colored by cluster.
5. Heatmap — genetic distances with subjects sorted into cluster blocks.
6. Bar chart — cluster sizes.
7. Boxplots — within vs between cluster genetic distance.
8. Histograms — geographic distance within each cluster.

Needs `DATA/processed/samples_metadata_ordered.csv` for lat/lon. Optional: `python -m pip install cartopy`.
