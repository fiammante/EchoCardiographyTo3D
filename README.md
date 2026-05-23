# EchoCardiographyTo3D

Convert echocardiography video to a 3D view where **time becomes the depth axis**, using Marching Cubes iso-surface extraction and five optical flow methods for motion analysis.

Interactive 3D rendering is exported to HTML via Plotly. HTML files are not committed to the repo (119 MB+ with the provided mp4 — takes ~10 s to display on a laptop).

---

## Repository Structure

```
EchoCardiographyTo3D/
├── code/        ← Jupyter notebooks (run from here)
├── html/        ← Plotly HTML outputs & benchmark charts (gitignored)
├── images/      ← PNG snapshots from notebooks (gitignored)
├── video/       ← Input mp4 + optical flow mp4 outputs (gitignored)
└── README.md
```

All output paths are resolved relative to the repo root — no hardcoded absolute paths. Place the input video in `video/` before running.

---

## Notebooks

### `EchoGraphy_Time_To_3D_VTK_To_Plotly.ipynb` — VTK version (original)

Uses the **VTK Visualization Toolkit** and its Marching Cubes implementation.
Renders the 3D surface interactively with a VTK window, or exports to Plotly HTML.

![Echo to 3D rendering with Plotly](./screen_shot_echo_to_3D_plotly.png?raw=true "Plotly rendering Echo to 3D")

Python file uses VTK default rendering window:

![Echo to 3D](./echo_to_3D.png?raw=true "Echo to 3D")

---

### `EchoGraphy_Time_To_3D_Skimage_To_Plotly.ipynb` — scikit-image version (main)

Replaces VTK with **scikit-image** `marching_cubes` and adds a full **optical flow benchmark** comparing five methods. No VTK installation required.

**Dependencies:**
```bash
pip install scikit-image opencv-contrib-python plotly numpy pandas matplotlib kaleido
```
> `opencv-contrib-python` is required for Method E (RLOF). It replaces `opencv-python` — uninstall the base package first if already installed.

#### Pipeline

1. Read echocardiography video → grayscale volume `(T, H, W)`
2. Run **Marching Cubes** (iso=127) → triangulated iso-surface mesh
3. Render interactive **Plotly 3D** view → `html/skimage_3d.html`
4. Compute **5 optical flow methods** and compare performance

#### Optical Flow Methods

| | Method | Type | cv2 API |
|---|---|---|---|
| **A** | MC spatio-temporal gradient | 3D sparse (iso-surface) | skimage normals |
| **B** | Farneback | 2D dense | `calcOpticalFlowFarneback` |
| **C** | Lucas-Kanade sparse | 2D sparse (Shi-Tomasi corners) | `calcOpticalFlowPyrLK` |
| **D** | DIS — Dense Inverse Search | 2D dense | `DISOpticalFlow` (PRESET_FAST) |
| **E** | RLOF — Robust Local Optical Flow | 2D sparse (corners) | `calcOpticalFlowSparseRLOF` |

#### Motion Filters (Method A)

The MC gradient view applies a **dual filter** to remove low-signal vertices:
- `|dT| > 0.4` — discards normals nearly perpendicular to the time axis (static spatial edges)
- `mag > 0.4` — discards vertices with negligible flow magnitude

In the test video (76 frames, 576×1024), **79.3% of vertices** (1,104,346 / 1,392,014) pass both filters.

The flow colorscale (Hot) is remapped so the threshold value = 0, eliminating dark colours at the low end.

#### Benchmark Results (Anonymized_EchoCardiography06.mp4)

| Method | Total (ms) | ns/point | Flow mean (px/f) | Flow std |
|---|---|---|---|---|
| A — MC Gradient | **39.47** | 28.35 | 3.35 | 5.60 |
| B — Farneback | 8,702.71 | 196.73 | 0.84 | 0.25 |
| C — LK PyrLK | 623.47 | 20,131 | 3.45 | 1.74 |
| D — DIS | 691.90 | **15.64** | 1.28 | 0.58 |
| E — RLOF | 1,748.95 | 56,465 | 22.78 | 10.33 |

- **Fastest total time:** Method A (iso-surface only)
- **Fastest dense method:** Method D — DIS at 15.64 ns/point (12.6× faster than Farneback)
- **Most stable signal:** Method B — Farneback (std 0.25)
- **RLOF note:** elevated mean due to SR_CROSS mode on greyscale input; use `SR_FIXED` for greyscale echo or provide genuine colour Doppler input

#### Outputs

| File | Location | Description |
|---|---|---|
| `skimage_3d.html` | `html/` | Interactive Plotly 3D iso-surface |
| `flow_mc_gradient.html` | `html/` | MC gradient flow on 3D surface |
| `flow_all_methods.html` | `html/` | Flow magnitude over time (all methods) |
| `flow_benchmark.html` | `html/` | Performance bar charts |
| `*.png` (kaleido) | `images/` | Static PNG snapshots (requires `kaleido`) |
| `snap_method_[A-E].png` | `images/` | Per-method matplotlib snapshots |
| `flow_farneback.mp4` | `video/` | Farneback HSV flow overlay video |
| `flow_lk_pyrlk.mp4` | `video/` | LK PyrLK arrow overlay video |
| `flow_dis.mp4` | `video/` | DIS HSV flow overlay video |

#### Notes

- HTML files are excluded from the repo (too large). Generate them locally by running the notebook.
- Static PNG export via `write_image` requires `pip install kaleido`. Without it the notebook skips image export gracefully.
- The notebook must be placed in the `code/` folder for relative paths to resolve correctly.
- RLOF (`SR_CROSS` mode) requires 3-channel input — the notebook converts greyscale to BGR automatically, but SR_CROSS provides less benefit without genuine colour. For greyscale-only workflows, change `SupportRegionType` to `SR_FIXED`.
