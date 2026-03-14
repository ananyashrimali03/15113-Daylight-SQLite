"""
Daylighting Simulation Tracker
Tracks parametric daylighting simulation runs for Gulf Tower O2R conversion research.
Uses SQLite to store simulation configurations and results (sDA, ASE, LEED compliance).
"""

import sqlite3
from datetime import date

# --- Database Setup ---

DB_NAME = "daylight_simulations.db"

def get_connection():
    """Connect to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # allows accessing columns by name
    return conn

def create_table():
    """Create the simulations table if it doesn't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS simulations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            config_id TEXT NOT NULL,
            unit_depth_ft INTEGER NOT NULL,
            orientation TEXT NOT NULL,
            light_shelf_ft REAL NOT NULL,
            glazing_vt REAL NOT NULL,
            ceiling_reflectance REAL NOT NULL,
            sda_percent REAL,
            ase_percent REAL,
            leed_pass INTEGER,
            notes TEXT,
            date_run TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("Database ready.")


# --- CRUD: Create ---

def add_simulation():
    """Add a new simulation record to the database."""
    print("\n--- Add New Simulation ---")
    
    # Config ID
    config_id = input("Config ID (e.g., R001): ").strip()
    if not config_id:
        print("Config ID is required. Cancelled.")
        return
    
    # Unit depth - must be one of the valid levels
    valid_depths = [25, 35, 45, 55]
    print(f"Valid unit depths: {valid_depths}")
    try:
        unit_depth = int(input("Unit depth (ft): "))
        if unit_depth not in valid_depths:
            print(f"Warning: {unit_depth} is not a standard depth level, but adding anyway.")
    except ValueError:
        print("Invalid number. Cancelled.")
        return

    # Orientation
    valid_orientations = ['S', 'E', 'W', 'N']
    orientation = input("Orientation (S/E/W/N): ").strip().upper()
    if orientation not in valid_orientations:
        print(f"Invalid orientation. Must be one of {valid_orientations}. Cancelled.")
        return

    # Light shelf depth
    valid_shelves = [0, 1, 2, 3]
    print(f"Valid light shelf depths: {valid_shelves}")
    try:
        light_shelf = float(input("Light shelf depth (ft): "))
    except ValueError:
        print("Invalid number. Cancelled.")
        return

    # Glazing VT
    valid_vt = [0.50, 0.59, 0.64, 0.70]
    print(f"Valid glazing VT values: {valid_vt}")
    try:
        glazing_vt = float(input("Glazing VT: "))
    except ValueError:
        print("Invalid number. Cancelled.")
        return

    # Ceiling reflectance
    valid_refl = [0.70, 0.85]
    print(f"Valid ceiling reflectance values: {valid_refl}")
    try:
        ceiling_refl = float(input("Ceiling reflectance: "))
    except ValueError:
        print("Invalid number. Cancelled.")
        return

    # Results (optional - might not have them yet)
    sda_input = input("sDA % (press Enter to skip): ").strip()
    sda = float(sda_input) if sda_input else None

    ase_input = input("ASE % (press Enter to skip): ").strip()
    ase = float(ase_input) if ase_input else None

    # Auto-calculate LEED pass if both results exist
    leed_pass = None
    if sda is not None and ase is not None:
        leed_pass = 1 if (sda >= 55.0 and ase <= 10.0) else 0

    notes = input("Notes (press Enter to skip): ").strip() or None
    date_run = input(f"Date run (YYYY-MM-DD, Enter for today {date.today()}): ").strip()
    if not date_run:
        date_run = str(date.today())

    # Insert into database
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO simulations 
        (config_id, unit_depth_ft, orientation, light_shelf_ft, glazing_vt, 
         ceiling_reflectance, sda_percent, ase_percent, leed_pass, notes, date_run)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (config_id, unit_depth, orientation, light_shelf, glazing_vt,
          ceiling_refl, sda, ase, leed_pass, notes, date_run))
    conn.commit()
    conn.close()

    leed_str = "PASS" if leed_pass == 1 else ("FAIL" if leed_pass == 0 else "pending")
    print(f"\nSimulation {config_id} added successfully! (LEED: {leed_str})")


# --- CRUD: Read ---

def view_all_simulations():
    """Display all simulation records."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM simulations ORDER BY id")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("\nNo simulations in the database yet.")
        return

    print(f"\n{'='*100}")
    print(f"{'ID':>4} {'Config':>7} {'Depth':>5} {'Dir':>3} {'Shelf':>5} {'VT':>5} {'Ceil':>5} {'sDA%':>6} {'ASE%':>6} {'LEED':>5} {'Date':>12}")
    print(f"{'-'*100}")
    for row in rows:
        sda_str = f"{row['sda_percent']:.1f}" if row['sda_percent'] is not None else "  --"
        ase_str = f"{row['ase_percent']:.1f}" if row['ase_percent'] is not None else "  --"
        leed_str = "PASS" if row['leed_pass'] == 1 else ("FAIL" if row['leed_pass'] == 0 else "  --")
        print(f"{row['id']:>4} {row['config_id']:>7} {row['unit_depth_ft']:>5} {row['orientation']:>3} "
              f"{row['light_shelf_ft']:>5.1f} {row['glazing_vt']:>5.2f} {row['ceiling_reflectance']:>5.2f} "
              f"{sda_str:>6} {ase_str:>6} {leed_str:>5} {row['date_run']:>12}")
    print(f"{'='*100}")
    print(f"Total: {len(rows)} simulations")


def filter_simulations():
    """Filter/sort simulations based on user input."""
    print("\n--- Filter Simulations ---")
    print("1. By orientation (e.g., show all South-facing)")
    print("2. By unit depth")
    print("3. By LEED compliance (pass only)")
    print("4. By minimum sDA threshold")
    print("5. Sort all by sDA (highest first)")
    print("6. By glazing VT")

    choice = input("Choose filter (1-6): ").strip()

    conn = get_connection()
    cursor = conn.cursor()

    if choice == "1":
        ori = input("Orientation (S/E/W/N): ").strip().upper()
        cursor.execute("SELECT * FROM simulations WHERE orientation = ? ORDER BY sda_percent DESC", (ori,))
    elif choice == "2":
        try:
            depth = int(input("Unit depth (25/35/45/55): "))
            cursor.execute("SELECT * FROM simulations WHERE unit_depth_ft = ? ORDER BY sda_percent DESC", (depth,))
        except ValueError:
            print("Invalid number.")
            conn.close()
            return
    elif choice == "3":
        cursor.execute("SELECT * FROM simulations WHERE leed_pass = 1 ORDER BY sda_percent DESC")
    elif choice == "4":
        try:
            threshold = float(input("Minimum sDA %: "))
            cursor.execute("SELECT * FROM simulations WHERE sda_percent >= ? ORDER BY sda_percent DESC", (threshold,))
        except ValueError:
            print("Invalid number.")
            conn.close()
            return
    elif choice == "5":
        cursor.execute("SELECT * FROM simulations WHERE sda_percent IS NOT NULL ORDER BY sda_percent DESC")
    elif choice == "6":
        try:
            vt = float(input("Glazing VT (0.50/0.59/0.64/0.70): "))
            cursor.execute("SELECT * FROM simulations WHERE glazing_vt = ? ORDER BY sda_percent DESC", (vt,))
        except ValueError:
            print("Invalid number.")
            conn.close()
            return
    else:
        print("Invalid choice.")
        conn.close()
        return

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("No matching simulations found.")
        return

    print(f"\n{'='*100}")
    print(f"{'ID':>4} {'Config':>7} {'Depth':>5} {'Dir':>3} {'Shelf':>5} {'VT':>5} {'Ceil':>5} {'sDA%':>6} {'ASE%':>6} {'LEED':>5} {'Date':>12}")
    print(f"{'-'*100}")
    for row in rows:
        sda_str = f"{row['sda_percent']:.1f}" if row['sda_percent'] is not None else "  --"
        ase_str = f"{row['ase_percent']:.1f}" if row['ase_percent'] is not None else "  --"
        leed_str = "PASS" if row['leed_pass'] == 1 else ("FAIL" if row['leed_pass'] == 0 else "  --")
        print(f"{row['id']:>4} {row['config_id']:>7} {row['unit_depth_ft']:>5} {row['orientation']:>3} "
              f"{row['light_shelf_ft']:>5.1f} {row['glazing_vt']:>5.2f} {row['ceiling_reflectance']:>5.2f} "
              f"{sda_str:>6} {ase_str:>6} {leed_str:>5} {row['date_run']:>12}")
    print(f"{'='*100}")
    print(f"Found: {len(rows)} simulations")


# --- CRUD: Update ---

def update_simulation():
    """Update an existing simulation record."""
    print("\n--- Update Simulation ---")
    
    # Show existing records so user can pick one
    view_all_simulations()
    
    try:
        sim_id = int(input("\nEnter the ID of the simulation to update: "))
    except ValueError:
        print("Invalid ID. Cancelled.")
        return

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM simulations WHERE id = ?", (sim_id,))
    row = cursor.fetchone()
    
    if not row:
        print(f"No simulation found with ID {sim_id}.")
        conn.close()
        return

    print(f"\nCurrent values for {row['config_id']}:")
    print(f"  1. Unit depth: {row['unit_depth_ft']} ft")
    print(f"  2. Orientation: {row['orientation']}")
    print(f"  3. Light shelf: {row['light_shelf_ft']} ft")
    print(f"  4. Glazing VT: {row['glazing_vt']}")
    print(f"  5. Ceiling reflectance: {row['ceiling_reflectance']}")
    print(f"  6. sDA %: {row['sda_percent']}")
    print(f"  7. ASE %: {row['ase_percent']}")
    print(f"  8. Notes: {row['notes']}")
    print("(Press Enter to keep current value)")

    # Collect new values, keeping old if user presses Enter
    depth_input = input(f"New unit depth ({row['unit_depth_ft']}): ").strip()
    unit_depth = int(depth_input) if depth_input else row['unit_depth_ft']

    ori_input = input(f"New orientation ({row['orientation']}): ").strip().upper()
    orientation = ori_input if ori_input else row['orientation']

    shelf_input = input(f"New light shelf depth ({row['light_shelf_ft']}): ").strip()
    light_shelf = float(shelf_input) if shelf_input else row['light_shelf_ft']

    vt_input = input(f"New glazing VT ({row['glazing_vt']}): ").strip()
    glazing_vt = float(vt_input) if vt_input else row['glazing_vt']

    ceil_input = input(f"New ceiling reflectance ({row['ceiling_reflectance']}): ").strip()
    ceiling_refl = float(ceil_input) if ceil_input else row['ceiling_reflectance']

    sda_input = input(f"New sDA % ({row['sda_percent']}): ").strip()
    sda = float(sda_input) if sda_input else row['sda_percent']

    ase_input = input(f"New ASE % ({row['ase_percent']}): ").strip()
    ase = float(ase_input) if ase_input else row['ase_percent']

    notes_input = input(f"New notes ({row['notes']}): ").strip()
    notes = notes_input if notes_input else row['notes']

    # Recalculate LEED pass
    leed_pass = None
    if sda is not None and ase is not None:
        leed_pass = 1 if (sda >= 55.0 and ase <= 10.0) else 0

    cursor.execute("""
        UPDATE simulations 
        SET unit_depth_ft = ?, orientation = ?, light_shelf_ft = ?, glazing_vt = ?,
            ceiling_reflectance = ?, sda_percent = ?, ase_percent = ?, leed_pass = ?, notes = ?
        WHERE id = ?
    """, (unit_depth, orientation, light_shelf, glazing_vt, ceiling_refl,
          sda, ase, leed_pass, notes, sim_id))
    conn.commit()
    conn.close()

    leed_str = "PASS" if leed_pass == 1 else ("FAIL" if leed_pass == 0 else "pending")
    print(f"\nSimulation ID {sim_id} updated! (LEED: {leed_str})")


# --- CRUD: Delete ---

def delete_simulation():
    """Delete a simulation record."""
    print("\n--- Delete Simulation ---")
    
    view_all_simulations()
    
    try:
        sim_id = int(input("\nEnter the ID of the simulation to delete: "))
    except ValueError:
        print("Invalid ID. Cancelled.")
        return

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT config_id FROM simulations WHERE id = ?", (sim_id,))
    row = cursor.fetchone()
    
    if not row:
        print(f"No simulation found with ID {sim_id}.")
        conn.close()
        return

    confirm = input(f"Are you sure you want to delete {row['config_id']}? (y/n): ").strip().lower()
    if confirm == 'y':
        cursor.execute("DELETE FROM simulations WHERE id = ?", (sim_id,))
        conn.commit()
        print(f"Simulation {row['config_id']} deleted.")
    else:
        print("Cancelled.")
    
    conn.close()


# --- Summary Stats ---

def show_summary():
    """Show summary statistics of all simulations."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as total FROM simulations")
    total = cursor.fetchone()['total']
    
    if total == 0:
        print("\nNo simulations in the database yet.")
        conn.close()
        return

    cursor.execute("SELECT COUNT(*) as count FROM simulations WHERE leed_pass = 1")
    passing = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM simulations WHERE leed_pass = 0")
    failing = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM simulations WHERE sda_percent IS NULL")
    pending = cursor.fetchone()['count']

    cursor.execute("""
        SELECT orientation, COUNT(*) as count, 
               AVG(sda_percent) as avg_sda, AVG(ase_percent) as avg_ase
        FROM simulations 
        WHERE sda_percent IS NOT NULL
        GROUP BY orientation
    """)
    ori_stats = cursor.fetchall()

    cursor.execute("""
        SELECT unit_depth_ft, COUNT(*) as count,
               AVG(sda_percent) as avg_sda,
               SUM(CASE WHEN leed_pass = 1 THEN 1 ELSE 0 END) as pass_count
        FROM simulations
        WHERE sda_percent IS NOT NULL
        GROUP BY unit_depth_ft
    """)
    depth_stats = cursor.fetchall()

    conn.close()

    print(f"\n{'='*50}")
    print(f"  SIMULATION SUMMARY")
    print(f"{'='*50}")
    print(f"  Total simulations:  {total}")
    print(f"  LEED passing:       {passing}")
    print(f"  LEED failing:       {failing}")
    print(f"  Results pending:    {pending}")
    
    if ori_stats:
        print(f"\n  By Orientation:")
        for row in ori_stats:
            print(f"    {row['orientation']}: {row['count']} sims, avg sDA={row['avg_sda']:.1f}%, avg ASE={row['avg_ase']:.1f}%")
    
    if depth_stats:
        print(f"\n  By Unit Depth:")
        for row in depth_stats:
            pass_rate = (row['pass_count'] / row['count'] * 100) if row['count'] > 0 else 0
            print(f"    {row['unit_depth_ft']}ft: {row['count']} sims, avg sDA={row['avg_sda']:.1f}%, LEED pass rate={pass_rate:.0f}%")

    print(f"{'='*50}")


# --- Main Menu ---

def main():
    """Main application loop."""
    create_table()
    
    print("\n" + "="*50)
    print("  DAYLIGHTING SIMULATION TRACKER")
    print("  Gulf Tower O2R Conversion Research")
    print("="*50)

    while True:
        print("\n--- Main Menu ---")
        print("1. Add a simulation")
        print("2. View all simulations")
        print("3. Filter/search simulations")
        print("4. Update a simulation")
        print("5. Delete a simulation")
        print("6. Summary statistics")
        print("7. Quit")

        choice = input("\nChoose an option (1-7): ").strip()

        if choice == "1":
            add_simulation()
        elif choice == "2":
            view_all_simulations()
        elif choice == "3":
            filter_simulations()
        elif choice == "4":
            update_simulation()
        elif choice == "5":
            delete_simulation()
        elif choice == "6":
            show_summary()
        elif choice == "7":
            print("\nGoodbye! Keep optimizing that daylight.")
            break
        else:
            print("Invalid choice. Please enter 1-7.")


if __name__ == "__main__":
    main()
