## Dashboard (React)

Interactive demo dashboard that **only reads historical outputs** produced by the Python pipeline / EA runs (no live coupling to the algorithm).

### Quick start

```bash
cd dashboard
npm install
npm run prepare:data
npm run dev
```

### Data loading approach

- Source-of-truth files live in the repo (e.g. `../results/`, `../data/processed/`).
- `npm run prepare:data` copies a curated set of input files into `dashboard/public/data/` using `dashboard/data-manifest.json`.
- The app fetches from `/data/...` so the dev server and production build behave the same.

If you add new experiment outputs, put them in the repo (e.g. `results/experiments/<run_id>/...`) and list them in `data-manifest.json`.

