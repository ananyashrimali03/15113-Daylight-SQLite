# Daylighting Simulation Tracker

A CLI app that tracks parametric daylighting simulation runs for my thesis research on office-to-residential (O2R) conversions in Pittsburgh. I'm running 512 Honeybee-Radiance simulations on Gulf Tower to find which design parameter combinations achieve LEED v4 daylighting compliance (sDA ≥55%, ASE ≤10%) in deep floor plate buildings.

I chose this topic because I needed a way to manage and query my simulation configurations and results as they come in from batch runs. Each record represents one simulation with its input parameters and performance outputs.

## Database Schema

**Table: `simulations`**

| Column              | Type    | Description                                      |
|---------------------|---------|--------------------------------------------------|
| id                  | INTEGER | Primary key, auto-increment                      |
| config_id           | TEXT    | Unique config label (e.g., "R001")               |
| unit_depth_ft       | INTEGER | Unit depth from facade: 25, 35, 45, or 55 ft     |
| orientation         | TEXT    | Facade orientation: S, E, W, or N                |
| light_shelf_ft      | REAL    | Interior light shelf projection: 0, 1, 2, or 3 ft|
| glazing_vt          | REAL    | Glazing visible transmittance: 0.50–0.70         |
| ceiling_reflectance | REAL    | Ceiling reflectance: 0.70 or 0.85                |
| sda_percent         | REAL    | Spatial Daylight Autonomy result (nullable)       |
| ase_percent         | REAL    | Annual Sunlight Exposure result (nullable)        |
| leed_pass           | INTEGER | 1 if sDA≥55 AND ASE≤10, 0 if not, NULL if pending|
| notes               | TEXT    | Optional notes about the run                     |
| date_run            | TEXT    | Date the simulation was run                      |

## How to Run

**Requirements:** Python 3 (no external packages needed — uses only `sqlite3` and `datetime` from the standard library).

```
python daylight_tracker.py
```

The database file (`daylight_simulations.db`) is created automatically on first run. It is excluded from version control via `.gitignore` since it contains local test data.

## CRUD Operations

**Create (option 1):** Add a new simulation by entering the config ID, unit depth, orientation, light shelf depth, glazing VT, ceiling reflectance, and optionally sDA/ASE results. LEED pass/fail is auto-calculated when both results are provided. Results can be left blank if the simulation hasn't finished yet.

**Read (option 2 and 3):** Option 2 shows all simulations in a formatted table. Option 3 lets you filter by orientation, unit depth, LEED compliance, minimum sDA threshold, sort by sDA descending, or filter by glazing VT.

**Update (option 4):** Select a simulation by its ID number, then update any field. Press Enter to keep the current value for any field you don't want to change. LEED pass is recalculated automatically.

**Delete (option 5):** Select a simulation by ID and confirm deletion.

**Bonus — Summary (option 6):** Shows aggregate stats including total count, LEED pass/fail breakdown, and average sDA by orientation and unit depth.
