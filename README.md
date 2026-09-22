# ODET Wildfire - training materials

Training materials on wildfire-atmosphere interactions for the [ODET](https://www.paucostafoundation.org/en/odet-kicks-off-to-boost-europes-preparedness-for-extreme-wildfire-behaviour/) project, published as a [Jupyter Book](https://jupyterbook.org). They prepare the ground for the online skew-T log-p tool in [`wildfire-meteo-dmt`](https://github.com/wildfire-meteo/wildfire-meteo-dmt).

## Read it

<https://wildfire-meteo.github.io/training-materials/>

It opens in any browser, with nothing to install. The figures are interactive: hover over them, click the legend, move the sliders.

## Development

Each page is a notebook in `notebooks/`, listed in the `toc` of `myst.yml`. The notebooks call `odet_meteo/`, which holds the thermodynamics (the same as `wildfire-meteo-dmt`) and the Plotly skew-T figures. On every push to `main`, `.github/workflows/deploy.yml` executes the notebooks, builds the book and publishes it to GitHub Pages.

To preview the book locally (needs [Node.js](https://nodejs.org)):

```bash
./preview.sh
```

and open <http://localhost:3000>. The first run creates `.venv/` and installs `requirements.txt`. It updates when you save a notebook; after changing `odet_meteo/`, stop it with `Ctrl+C` and run it again.

To write notebooks, install JupyterLab into the same environment and start it:

```bash
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/jupyter lab
```

`odet_meteo` is installed in editable mode, so changes to it apply after restarting the notebook's kernel.
