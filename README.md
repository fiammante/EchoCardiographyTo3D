# EchoCardiographyTo3D
Convert EchoCardiography to a 3D view with time as depth using Marching Cubes Algorithm.
Notebook renders to HTML using Plotly. I did not add the HTML to github as it is big (119 MB with the provided mp4).
Because of the size of the HTML it takes around 10 seconds to display on my laptop.

## Versions

### VTK version (original)
Uses VTK Visualization Toolkit and Marching Cubes algorithm with VTK default rendering window or Plotly HTML export.

![Echo to 3D rendering with Plotly](./screen_shot_echo_to_3D_plotly.png?raw=true "Plotly rendering Echo to 3D")

Python file uses VTK default rendering window:

![Echo to 3D](./echo_to_3D.png?raw=true "Echo to 3D")

### scikit-image version (alternative)
`EchoGraphy_Time_To_3D_Skimage_To_Plotly.ipynb` replaces the VTK dependency with **scikit-image** `marching_cubes`, keeping the same Plotly HTML output.

Key differences:
- No VTK installation required — `pip install scikit-image opencv-python plotly numpy`
- `skimage.measure.marching_cubes` returns vertices and faces directly as NumPy arrays, eliminating the VTK pipeline boilerplate
- `step_size` parameter allows coarser/faster meshing (e.g. `step_size=2` reduces vertex count ~8×)
- Aspect ratio fixed with `aspectratio=dict(x=1, y=1, z=1)` so the time axis renders at the same visual length as the spatial axes
