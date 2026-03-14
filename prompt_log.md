# Prompt Log — Daylighting Simulation Tracker

## AI Model Used
- Claude (Anthropic) via claude.ai

## Development Process

### Step 1: Choosing a Topic
I asked Claude to help me brainstorm a project that connected to my thesis work on daylighting optimization for O2R conversions in Pittsburgh. We discussed several options:
- Daylighting analysis log
- Building performance case study database
- Glazing/material tracker
- Room daylighting assessment tracker

I shared my thesis progress document so Claude had context on my 512-configuration simulation matrix (unit depth, orientation, light shelf, glazing VT, ceiling reflectance) run through Honeybee-Radiance for Gulf Tower.

**Prompt:** "anything related to building performance especially daylighting? if that fits the assignment well, feel free to brainstorm with me and suggest what in my study area would be appropriate fit for this assignment"

**Prompt:** "can we connect this to my thesis? you have it in your memory that I'm creating a dataset of simulations"

### Step 2: Validating the Idea
I pushed back on whether this was a genuine fit or if Claude was just trying to make it work.

**Prompt:** "do you really think it fits with my assignment? and you're not trying to align it on purpose just to connect it"

Claude gave an honest breakdown of why it works and where it doesn't, and also suggested an alternative (Pittsburgh O2R building database) as a more self-contained option. I chose the simulation tracker.

### Step 3: Discussing Practical Value
I asked whether SQLite would actually help my thesis workflow (data analysis, ML training).

**Prompt:** "so can i use it for better data analysis or model training?"

Claude was honest that for my pandas/scikit-learn pipeline, SQLite doesn't add much, but it could be useful if I build an interactive decision tool later. The main value for this assignment is learning SQL/CRUD fundamentals through a personally relevant project.

### Step 4: Schema Design
We designed the database schema together based on my thesis parameters:
- 5 input parameters (unit_depth_ft, orientation, light_shelf_ft, glazing_vt, ceiling_reflectance)
- 2 output metrics (sda_percent, ase_percent)
- Auto-calculated LEED pass/fail
- Config ID, notes, date

**Prompt:** [I confirmed the schema Claude proposed based on my thesis document]

### Step 5: Building the App
Claude built the full CLI app in one file with:
- Database setup (create_table)
- Create: add simulation with input validation for my specific parameter levels
- Read: view all + 6 filter options
- Update: select by ID, Enter to keep values
- Delete: select by ID with confirmation
- Summary statistics by orientation and depth

<!-- 
TODO: Add any additional prompts you used for debugging, testing, 
or modifying the app after downloading it. Also add prompts for 
any changes you made on your own.
-->

### Step 6: README and Prompt Log
Claude drafted the README and this prompt log template. I reviewed and edited both to make sure they accurately describe the project.

### Step 7: Testing
<!-- TODO: Document your testing process here — 
did you run it locally? any bugs you found and fixed? 
any changes you made? -->

## Time Spent
<!-- TODO: Fill in your actual time estimate -->
- Brainstorming and topic selection: ~XX min
- Schema design and discussion: ~XX min
- Building and testing the app: ~XX min
- README and prompt log: ~XX min
- Total: ~X hours
