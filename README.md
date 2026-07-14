Comparative Analysis Maker
=========================

Quick start
-----------
1. Create a Python 3.11 environment and install dependencies:

```bash
pip install pygame
```

2. Run the demo (uses built-in sample data by default):

```bash
python run_demo.py
```

What the app does
-----------------
- Renders a comparative visual analysis of a base "original" (implicit) and a set of comparands.
- Displays up to 12 feature columns per comparand with three states: perfect (filled rectangle), partial/disputed (underlined filled circle), or none (square with X).
- Draws a legend (auto-wrapping), title, definition text and two columns of comparands.
- Can export the rendered canvas to PNG files (auto-incremented filenames) in `output_images/`.

Files of interest
-----------------
- `comparative_visualizer.py` — main visualization module. Contains:
	- `FeatureStatus` enum
	- `Comparand` dataclass
	- `Visualizer` class with methods: `render_to_surface`, `render_columns`, `export_image`
- `run_demo.py` — demo runner. Loads demo data or reads from `sample_data.csv` / `sample_data.txt` depending on configuration.
- `sample_data.csv`, `sample_data.txt` — example input files.

Quick usage options
-------------------
- Edit `run_demo.py` to change input mode:
	- `USE_DEMO = True` (default) to use built-in demo data.
	- `USE_DEMO = False` then set `SOURCE = 'csv'` or `SOURCE = 'txt'` to load `sample_data.csv` or `sample_data.txt`.

CSV / TXT format
----------------
- First row: comma-separated feature labels (up to 12 recommended).
- Following rows: first column is comparand name; remaining columns are feature states.
- Accepted feature state tokens (case-insensitive): `PERFECT`, `P`, `2` for perfect; `PARTIAL`, `PART`, `1` for partial/disputed; anything else treated as `NONE`.

Examples
--------
A CSV row for a comparand:

```
JUPITER (Roman),PERFECT,PERFECT,PARTIAL,NONE,PERFECT,...
```

Customization
-------------
- Top-level layout constants are defined in `comparative_visualizer.py` (near the top):
	- `DEFAULT_CANVAS_SIZE`, `DEFAULT_LEFT_MARGIN`, `DEFAULT_NAME_COL`, `DEFAULT_ROW_HEIGHT`,
		`DEFAULT_FEATURE_SIZE`, `DEFAULT_SWATCH_SPACING`, `DEFAULT_FONT_SIZE`, `DEFAULT_TITLE_FONT_SIZE`, etc.
- To change visual sizes or spacing, either edit those `DEFAULT_*` variables or pass overrides when creating a `Visualizer` instance:

```python
viz = Visualizer(features, canvas_size=(1080,1350), feature_size=24, name_col=160)
```

Exporting images
----------------
- `export_image(left_list, right_list, title, out_dir='output_images')` saves a PNG with an incremented filename `comparison_###.png`.

Extending the app
-----------------
- To add interactive features (click handlers, hover tooltips), extend `Visualizer.render_columns` to handle events and track hit-testing regions.
- To support other input formats, add a parser in `run_demo.py` and split comparands into left/right lists for `Visualizer`.

Troubleshooting
---------------
- If markers overlap or don't fit, adjust `DEFAULT_FEATURE_SIZE` and `DEFAULT_ROW_HEIGHT` in `comparative_visualizer.py`.
- If fonts don't look right on your OS, change `pygame.font.SysFont(None, size)` calls in the constructor.

License & attribution
---------------------
This repository contains example code and images provided by the user; treat images and art as their own licensed assets outside this code.
