# EchoCardiographyTo3D

Convert video to a 3D view where **time becomes the depth axis**, using Marching Cubes iso-surface extraction and optical flow analysis. Originally designed for echocardiography, the pipeline generalises to any 2D video — traffic, industrial inspection, crowd monitoring, sports biomechanics.

Interactive 3D rendering is exported to HTML via Plotly. HTML files are not committed to the repo (119 MB+ with the provided mp4 — takes ~10 s to display on a laptop).

---

## Repository Structure

```
EchoCardiographyTo3D/
├── code/        ← Jupyter notebooks (run from here)
├── html/        ← Plotly HTML outputs & benchmark charts (gitignored)
├── images/      ← PNG snapshots from notebooks (gitignored)
├── video/       ← Input mp4/avi + optical flow mp4 outputs (gitignored)
└── README.md
```

All output paths are resolved relative to the repo root — no hardcoded absolute paths. Place input videos in `video/` before running.

---

## Notebooks

### `EchoGraphy_Time_To_3D_VTK_To_Plotly.ipynb` — VTK version (original)

Uses the **VTK Visualization Toolkit** and its Marching Cubes implementation.
Renders the 3D surface interactively with a VTK window, or exports to Plotly HTML.

![Echo to 3D rendering with Plotly](./screen_shot_echo_to_3D_plotly.png?raw=true "Plotly rendering Echo to 3D")

---

### `EchoGraphy_Time_To_3D_Skimage_To_Plotly.ipynb` — Echocardiography benchmark (main)

Replaces VTK with **scikit-image** `marching_cubes` and adds a full **optical flow benchmark** comparing five methods on anonymised echocardiography video.

**Dependencies:**
```bash
pip install scikit-image opencv-contrib-python plotly numpy pandas matplotlib kaleido
```

#### Optical Flow Methods

| | Method | Type | API |
|---|---|---|---|
| **A** | MC spatio-temporal gradient | 3D sparse (iso-surface) | skimage normals |
| **B** | Farneback | 2D dense | `calcOpticalFlowFarneback` |
| **C** | Lucas-Kanade PyrLK | 2D sparse (corners) | `calcOpticalFlowPyrLK` |
| **D** | DIS — Dense Inverse Search | 2D dense | `DISOpticalFlow` |
| **E** | RLOF — Robust Local Optical Flow | 2D sparse | `calcOpticalFlowSparseRLOF` |

#### Motion Filters (Method A)

Dual filter on the MC gradient view: `|dT| > 0.4` (directional) AND `mag > 0.4` (magnitude).
**79.3% of vertices** (1,104,346 / 1,392,014) pass both filters. Hot colorscale remapped so the threshold = 0.

#### Benchmark Results (Anonymized_EchoCardiography06.mp4 · 76 frames · 576×1024)

| Method | Total (ms) | ns/point | Flow mean (px/f) | Flow std |
|---|---|---|---|---|
| A — MC Gradient | **39.47** | 28.35 | 3.35 | 5.60 |
| B — Farneback | 8,702.71 | 196.73 | 0.84 | 0.25 |
| C — LK PyrLK | 623.47 | 20,131 | 3.45 | 1.74 |
| D — DIS | 691.90 | **15.64** | 1.28 | 0.58 |
| E — RLOF | 1,748.95 | 56,465 | 22.78 | 10.33 |

- **Fastest total:** Method A · **Fastest dense:** Method D (12.6× faster than Farneback per pixel)
- **Most stable:** Method B · **RLOF note:** use `SR_FIXED` for greyscale echo

#### Outputs

| File | Location | Description |
|---|---|---|
| `skimage_3d.html` | `html/` | Interactive Plotly 3D iso-surface |
| `flow_mc_gradient.html` | `html/` | MC gradient flow on 3D surface |
| `flow_all_methods.html` | `html/` | Flow magnitude over time (all methods) |
| `flow_benchmark.html` | `html/` | Performance bar charts |
| `*.png` | `images/` | Static snapshots (requires `kaleido`) |
| `flow_farneback.mp4` | `video/` | Farneback HSV overlay video |
| `flow_lk_pyrlk.mp4` | `video/` | LK PyrLK arrow overlay video |
| `flow_dis.mp4` | `video/` | DIS HSV overlay video |

---

### `BackgroundFlow_Skimage_To_Plotly.ipynb` — Background suppression + optical flow

Applies **MOG2/KNN background subtraction** in-memory (no intermediate video file), then runs the same five optical flow methods on the foreground masks. Demonstrated on the OpenCV sample `vtest.avi` (pedestrian surveillance footage), but works on any 2D video.

**Dependencies:** same as above. `vtest.avi` is downloaded automatically from the OpenCV GitHub if not found locally.

#### Key differences from the echocardiography notebook

| | Echocardiography | Background suppression |
|---|---|---|
| Input | Raw grayscale frames | MOG2/KNN foreground masks |
| Video | Medical echo (anonymised) | Any 2D video (default: vtest.avi) |
| Intermediate file | None | None (in-memory pipeline) |
| MC iso level | 127 | 192 |
| Combined snapshot | ✗ | ✓ (original \| mask \| 3D) |

#### Benchmark Results (vtest.avi · MOG2 · 80 frames · 576×768)

| Method | Total (ms) | ns/point | Flow mean (px/f) | Flow std |
|---|---|---|---|---|
| A — MC Gradient | **5.16** | **13.91** | 9.29 | 3.98 |
| B — Farneback | 6,983.38 | 199.83 | 0.41 | 0.24 |
| C — LK PyrLK | 433.38 | 19,008 | 6.74 | 15.01 |
| D — DIS | 544.08 | 15.57 | 3.06 | 2.98 |
| E — RLOF | 1,854.14 | 80,611 | — | — |

- MC gradient is **1,353× faster** than Farneback on the background mask (5 ms vs 6,983 ms)
- DIS remains the fastest dense method at 15.57 ns/pixel
- Working on the foreground mask rather than raw video reduces Farneback's mean flow from 0.84 → 0.41 px/frame, confirming cleaner motion isolation

#### Outputs

| File | Location | Description |
|---|---|---|
| `background_3d.html` | `html/` | Interactive Plotly 3D foreground iso-surface |
| `background_3d.png` | `images/` | Static 3D snapshot |
| `background_combined.png` | `images/` | Three-panel: original \| mask \| 3D scatter |
| `bg_flow_all_methods.html` | `html/` | Flow magnitude over time (all methods) |
| `bg_flow_benchmark.html` | `html/` | Performance bar charts |
| `bg_flow_snapshots.png` | `images/` | Per-method flow overlay snapshots |

---

### `backgound_suppression_mask_save_to_video.py` — Utility script

Saves the MOG2/KNN foreground mask to a separate `fgMask.mp4` file. Adapted from the OpenCV background subtraction example. The notebook version does the same in-memory without writing a file.

---

## Notes

- All notebooks must be placed in the `code/` folder for relative paths to resolve correctly.
- Static PNG export requires `pip install kaleido`. Without it the notebooks skip image export gracefully.
- RLOF (`SR_CROSS` mode) requires 3-channel input — converted automatically from greyscale, but `SR_FIXED` mode is recommended for greyscale-only workflows.
- HTML files are excluded from the repo (too large). Generate them locally by running the notebooks.
