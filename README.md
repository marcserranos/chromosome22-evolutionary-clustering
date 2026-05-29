# Chromosome 22 Evolutionary Clustering

Evolutionary algorithm implementation to uncover genetic structure and barriers in SGDP chromosome 22 data using individual-level analysis across 278 samples from 7 geographic regions.

**Status:** Data preparation complete ✓ | EA implementation & results ready ✓ | Dashboard deployed on Vercel

---

## Quick Start

### 1. Setup

```bash
# Clone repository
git clone https://github.com/marcserranos/chromosome22-evolutionary-clustering.git
cd chromosome22-evolutionary-clustering

# Install Python dependencies
pip install -r evo_algorithm/requirements.txt

# Install dashboard dependencies
cd dashboard && npm install && cd ..
```

### 2. Data

Data files must be acquired separately:
- Raw genotypes: `data/raw/chr.sgdp.pub.22.bcf` (1GB, from Harvard servers)
- Processed data will be placed in `data/processed/`

### 3. Run Evolutionary Algorithm

```bash
cd evo_algorithm
python main.py  # Run single experiment
# or
python multi_run.py  # Run multiple K values
# or
python run_parameter_sweep.py  # Sweep parameters
```

### 4. View Dashboard

```bash
cd dashboard
npm run dev  # Local development at http://localhost:5173
npm run build  # Build for production
```

**Deployed:** [View on Vercel](https://chromosome22-dashboard.vercel.app)

---

## Project Structure

```
chromosome22-evolutionary-clustering/
│
├── 📊 dashboard/                    React + Vite dashboard (deployed to Vercel)
│   ├── src/                         React components & pages
│   ├── public/                      Static assets
│   ├── package.json                 Node dependencies
│   └── vite.config.ts               Vite configuration
│
├── 🎨 dashboard_plot_maker/         Visualization generator (Python)
│   ├── generate_dashboard_plots.py  Main visualization pipeline
│   └── visualizations/              Generated PNG outputs
│
├── 🧬 evo_algorithm/                Evolutionary algorithm implementation
│   ├── main.py                      Single run
│   ├── multi_run.py                 Multiple K experiments
│   ├── run_parameter_sweep.py       Parameter optimization
│   ├── ea.py                        EA engine
│   ├── fitness.py                   Fitness functions
│   ├── individual.py                Individual representation
│   ├── population.py                Population management
│   ├── data_loader.py               Data loading utilities
│   ├── consistency_analyzer.py      Results analysis
│   ├── consistency_visualizations.py Result plots
│   └── requirements.txt              Python dependencies
│
├── 📁 data/                         Data directory (excluded from git)
│   ├── raw/                         Raw BCF genotypes
│   └── processed/                   Filtered & processed genotypes
│
├── 📊 results/                      Results & outputs (excluded from git)
│   ├── distances/                   Distance matrices
│   ├── visualizations/              Diagnostic plots
│   ├── runs/                        EA run outputs
│   └── consistency/                 Consistency analysis
│
├── 📚 docs/                         Documentation
│   ├── EXECUTIVE_SUMMARY.md         Status & key findings
│   ├── PROJECT_OVERVIEW.md          Quick reference
│   ├── PIPELINE_SUMMARY.md          Full methodology
│   ├── METHODS.md                   Mathematical details
│   ├── DATA_ANALYSIS_REPORT.md      Statistical results
│   └── FILE_MANIFEST.md             Complete file inventory
│
└── .development/                    Development & internal docs (not published)
    ├── legacy_scripts/              Old data processing scripts
    ├── claude_context/              AI assistant context
    └── handovers/                   Handover documentation
```

---

## Key Results

| Metric | Value |
|--------|-------|
| Samples | 278 individuals |
| Variants | 104,573 SNPs (chromosome 22) |
| Regions | 7 geographic continents |
| Genetic-geographic correlation | r = 0.503 |

---

## Architecture

### Data Pipeline
1. **Parse**: BCF → Genotypes (278 × 1.1M variants)
2. **Filter**: MAF > 0.05, non-monomorphic → 104k SNPs
3. **Distance**: Genetic (IBS) & geographic (haversine)
4. **Validate**: Correlation analysis, visualization

### Evolutionary Algorithm
- **Representation**: K cluster assignments for 278 individuals
- **Fitness**: Combines genetic homogeneity + geographic coherence
- **Selection**: Tournament selection
- **Variation**: Crossover + mutation operators
- **Termination**: Convergence or max generations

### Dashboard
- **Frontend**: React + TypeScript with Vite
- **Visualization**: Interactive 3D globe (react-globe.gl), heatmaps, scatter plots
- **Data**: Generated from `dashboard_plot_maker/` pipeline

---

## Documentation

Start with these in order:
1. **[EXECUTIVE_SUMMARY.md](docs/EXECUTIVE_SUMMARY.md)** — Project status & findings (5 min)
2. **[PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md)** — Quick reference guide (10 min)
3. **[PIPELINE_SUMMARY.md](docs/PIPELINE_SUMMARY.md)** — Complete methodology (15 min)
4. **[METHODS.md](docs/METHODS.md)** — Mathematical procedures (30 min)

---

## Deployment

### Vercel (Dashboard)
```bash
# Automatic deployment from main branch
git push origin main
# Dashboard redeploys automatically
```

**Configuration:**
- Root Directory: `dashboard`
- Build Command: `npm run build`
- Environment: Node.js (v25)

### Local Testing
```bash
cd dashboard
npm run dev      # Development server
npm run build    # Production build
npm run preview  # Preview build
```

---

## Contributing

This repository is a research project. For modifications:

1. Create a feature branch
2. Test locally (data pipeline & dashboard)
3. Run EA validation if algorithm changes
4. Commit with clear messages
5. Create pull request

---

## License

See [LICENSE](LICENSE) file.

---

## Citation

If you use this work, please cite:

```bibtex
@software{chromosome22clustering2024,
  title={Chromosome 22 Evolutionary Clustering},
  author={Serrano, Marc},
  year={2024},
  url={https://github.com/marcserranos/chromosome22-evolutionary-clustering}
}
```

---

## Resources

- [SGDP Project](https://www.simonsfoundation.org/simons-genome-diversity-project/)
- [Haversine Distance](https://en.wikipedia.org/wiki/Haversine_formula)
- [Identity-by-State (IBS)](https://en.wikipedia.org/wiki/Identity_by_descent)
- [Evolutionary Algorithms](https://en.wikipedia.org/wiki/Evolutionary_algorithm)
