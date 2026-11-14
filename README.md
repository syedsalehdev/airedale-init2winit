# Airedale Applied Intelligence Challenge

Engineering-track analysis by team init2winit.

We joined five Airedale datasets across 3,000 serial numbers, reconciled
manufacturing and field-failure labels, analyzed failure patterns by supplier,
facility, controls revision and shift, and evaluated 178 investment portfolios
under a $750,000 budget.

## Recommended portfolio

- Automated Leak Detection — $350,000
- Supplier Quality Improvement Program — $175,000
- Smart Torque Tool Deployment — $100,000
- Braze Process Training — $50,000

Total investment: $675,000

## Repository contents

- `analysis/` contains the Python analysis and portfolio-selection code.
- `outputs/` contains the resulting statistics and portfolio calculations.
- `charts/` contains the nine figures used in the presentation.
- `data/` documents the fields and label-reconciliation process.

## Reproducing the analysis

Run the scripts from the repository root in this order:

1. `analysis/data.py`
2. `analysis/analysis.py`
3. `analysis/robust.py`
4. `analysis/robust2.py`
5. `analysis/final_numbers.py`
6. `analysis/charts.py`

The analysis uses the Airedale competition datasets supplied through the
Virginia Tech competition materials.
