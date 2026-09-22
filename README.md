# ODET Wildfire - training materials

Training materials on wildfire-atmosphere interactions, published as a [Jupyter Book](https://jupyterbook.org). For now they are intended to prepare learners for working with the online skew-T log-p tool in [`wildfire-meteo-dmt`](https://github.com/wildfire-meteo/wildfire-meteo-dmt).

## How to read it

The book for now contains a single notebook, and is deployed to <https://wildfire-meteo.github.io/training-materials/>.

## Development

One can add notebooks to the book by adding an `*.ipynb` to the `notebooks/` directory, then it in the `toc` of `myst.yml`. The notebooks import `odet_meteo/`, which contains the thermodynamics (following `wildfire-meteo-dmt`) and Plotly skew-T figures (now organised per notebook). On every push to `main`, `.github/workflows/deploy.yml` executes the notebooks, builds the book and publishes it to GitHub Pages.

To preview the book locally (needs [Node.js](https://nodejs.org)):

```bash
./preview.sh
```

The first run creates `.venv/` and installs `requirements.txt`. It updates when you save a notebook; after changing `odet_meteo/`, stop the local server and run it again.

To write notebooks, install JupyterLab into the same environment and start it:

```bash
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/jupyter lab
```

`odet_meteo` is installed in editable mode, so changes to it apply after restarting the notebook's kernel.