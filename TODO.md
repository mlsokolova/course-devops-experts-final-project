# TODO

Potential improvements to the historical analytics layer (`quakestats.py`, `graph_dashboard.html`), from a seismology-oriented perspective. The Kaggle dataset (1990–2023) supports time, location, magnitude, and likely depth — enough for meaningful regional statistics beyond the current median / inter-event gap / max event cards.

## High priority — largest scientific value

- [ ] **Magnitude-frequency distribution** — event counts by magnitude bins (e.g. M 3–4, 4–5, 5–6); optional **b-value** estimate from log-frequency vs magnitude
- [ ] **Annual seismicity rate** — events per year (or month), with configurable magnitude cutoff (e.g. M≥4 only)
- [ ] **Depth distribution** — median depth, histogram, share of shallow (&lt;20 km) vs intermediate/deep events
- [ ] **Largest event per decade** and **years since last significant event** (e.g. M≥5) in the selected area
- [ ] **Cumulative event counts** above explicit completeness thresholds — always state the minimum magnitude used

## Medium priority — spatial and temporal patterns

- [ ] **Epicenter density map** or heatmap for the selected radius (extend existing spatial filters in DuckDB)
- [ ] **Aftershock / swarm indicator** — elevated activity within N days and km of a mainshock (simple rules before full declustering)
- [ ] **Cumulative energy proxy** — sum of \(10^{1.5M}\) over time to show dominance of rare large events
- [ ] **Regional comparison** — same metrics for the selected area vs country/continent baseline
- [ ] **Replace or supplement inter-event time** with catalog-wide rate; raw mean gap is misleading during aftershock sequences

## Lower priority — advanced or dataset-dependent

- [ ] **Tsunamigenic events** — if the parquet includes tsunami flags, surface offshore high-impact events (relevant for Japan, Chile, Indonesia, Eastern Med)
- [ ] **Event declustering** — separate background seismicity from aftershock swarms for rigorous rate estimates
- [ ] **Fault / tectonic context** — distance to known fault lines or plate boundaries (needs additional geospatial layers)
- [ ] **b-value temporal trends** — compare magnitude distribution across decades (sensitive to catalog completeness)

## Presentation and data quality

- [ ] **Document catalog limitations** in the UI — completeness varies by year and region; small events are under-reported before ~2000 in many areas
- [ ] **Label metrics clearly** — distinguish historical DuckDB stats (1990–2023) from live USGS graphs on the same page
- [ ] **Region-specific defaults** — tailor magnitude cutoffs and helper text for Israel, California, Japan, Chile, Indonesia
- [ ] **Visualize new metrics** — bar charts for magnitude bins, line charts for annual rate, depth histogram alongside existing cards

## Implementation notes

- New queries belong in `quakestats.py` (remote `quack_query` over the existing `earthquakes` table).
- Reuse the spatial filter pattern already used for `ST_Distance_Spheroid` around the selected lat/lon/radius.
- Prefer DuckDB window functions and `GROUP BY` for time-series aggregations before adding new Python dependencies.

