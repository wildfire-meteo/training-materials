#
# Copyright 2026 Wageningen University & Research (WUR)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Skew-T log-p diagrams in Plotly, drawn as ../wildfire-meteo-dmt/web/skewt.js
draws them: same skew, axes, background lines, colours and line styles. Plotly
figures stay interactive in a static web page (hover, zoom, legend toggles,
precomputed sliders), without Python running.
"""

import numpy as np
import plotly.graph_objects as go

from . import thermo as thrm

# Slant of the "Temperature (skew)" x-axis in the web tool.
SKEW_FACTOR = 35

X_LIMITS = (-40, 50)
P_BOTTOM_HPA = 1050
P_TICKS_HPA = [1000, 900, 800, 700, 600, 500, 400, 300, 200, 100]

FONT_SIZE = 14
COLOR_T  = "#EB0056"
COLOR_TD = "#0056EB"
BG_OPACITY = 0.5
BG_COLORS = {
    "isobars":        (179, 179, 179),
    "isotherms":      (148, 103, 189),
    "isohumes":       ( 31, 119, 180),
    "dry_adiabats":   (214,  39,  40),
    "moist_adiabats": ( 13, 145,  70),
}
BG_DASHED = {"isobars", "isotherms"}
BG_LABELS = {
    "isobars":        "Isobars",
    "isotherms":      "Isotherms",
    "isohumes":       "Isohumes",
    "dry_adiabats":   "Dry adiabats",
    "moist_adiabats": "Moist adiabats",
}
LW_BG = 1
LW_PROFILE = 2.5
DASH = "4px,3px"


def skew_transform(T, p):
    """
    Map temperature and pressure to the skewed x-coordinate of the diagram.

    Parameters:
    ----------
    T : float or np.ndarray
        Temperature in K.
    p : float or np.ndarray
        Pressure in Pa.

    Returns:
    -------
    float or np.ndarray
        Skewed x-coordinate in degC; equal to the temperature at 1000 hPa.
    """
    return (T - thrm.T0) + SKEW_FACTOR * (np.log(1000) - np.log(p / 100))


def inv_skew_transform(x, p):
    """
    Map a skewed x-coordinate back to temperature.

    Parameters:
    ----------
    x : float or np.ndarray
        Skewed x-coordinate in degC.
    p : float or np.ndarray
        Pressure in Pa.

    Returns:
    -------
    float or np.ndarray
        Temperature in K.
    """
    return x - SKEW_FACTOR * (np.log(1000) - np.log(p / 100)) + thrm.T0


def get_static_lines(ktot=64):
    """
    Calculate static background lines of a skew-T diagram.

    Parameters:
    ----------
    ktot : int
        Number of vertical levels in curved lines.

    Returns:
    -------
    dict with pressure arrays (Pa) and temperature arrays (K), shape (ktot, n_lines).
    """
    p_moist     = np.geomspace(105_000, 10_000, ktot)
    p_dry       = np.geomspace(105_000, 50_000, ktot)
    p_isotherms = p_moist
    p_isohumes  = p_dry

    # Start points (temperature in Celsius at 1000 hPa) of static lines.
    x0_isotherms      = np.arange(-120, 40.01, 10)
    x0_dry_adiabats   = np.arange( -40, 80.01, 10)
    x0_moist_adiabats = np.arange(-15, 55.01, 5)
    r_isohumes        = np.array([0.5, 1, 2, 4, 8, 15, 30])  # g/kg

    x = x0_isotherms + thrm.T0
    isotherms = np.broadcast_to(x[np.newaxis, :], (p_isotherms.size, len(x)))

    x = x0_dry_adiabats + thrm.T0
    dry_adiabats = x[np.newaxis, :] * thrm.exner(p_dry[:, np.newaxis])

    x = x0_moist_adiabats + thrm.T0
    moist_adiabats = thrm.calc_moist_adiabat(x, p_moist)

    q_isohumes = r_isohumes / (1000 + r_isohumes)
    isohumes = thrm.dewpoint(q_isohumes[np.newaxis, :], p_isohumes[:, np.newaxis])
    isohume_mixing_ratios = r_isohumes.astype(float)

    return {
        "p_isotherms":            p_isotherms,
        "p_dry":                  p_dry,
        "p_moist":                p_moist,
        "p_isohumes":             p_isohumes,
        "isotherms":              isotherms,
        "dry_adiabats":           dry_adiabats,
        "moist_adiabats":         moist_adiabats,
        "isohumes":               isohumes,
        "isohume_mixing_ratios":  isohume_mixing_ratios,
    }


def _bg_color(family, opacity=BG_OPACITY):
    r, g, b = BG_COLORS[family]
    return f"rgba({r},{g},{b},{opacity})"


def _joined(x, y):
    """
    Lines as columns of x and y, joined into one trace separated by gaps.
    """
    n = x.shape[1]
    gap = np.full((1, n), np.nan)
    return np.vstack([x, gap]).T.ravel(), np.vstack([y, gap]).T.ravel()


def _family_trace(family, T, p):
    x, y = _joined(skew_transform(T, p[:, np.newaxis]), np.broadcast_to(p[:, np.newaxis] / 100, T.shape))
    return go.Scatter(
        x=x, y=y, mode="lines", name=BG_LABELS[family], legendgroup=family,
        line=dict(color=_bg_color(family), width=LW_BG, dash=DASH if family in BG_DASHED else "solid"),
        hoverinfo="skip", connectgaps=False)


def _profile_trace(name, color, T, p):
    return go.Scatter(
        x=skew_transform(T, p), y=p / 100, mode="lines", name=name,
        line=dict(color=color, width=LW_PROFILE), customdata=T - thrm.T0,
        hovertemplate=f"{name}: %{{customdata:.1f}} °C<br>Pressure: %{{y:.0f}} hPa<extra></extra>")


def skewt_figure(sounding=None, p_top=10_000):
    """
    Draw a skew-T log-p diagram, optionally with a sounding on it.

    Clicking a legend entry shows or hides that line family; hovering over the
    temperature or dew point shows its value.

    Parameters:
    ----------
    sounding : dict, optional
        Sounding with arrays "p" (Pa), "T" (K) and "Td" (K), as returned by
        `odet_meteo.soundings.load_sounding`.
    p_top : float
        Pressure at the top of the diagram in Pa.

    Returns:
    -------
    plotly.graph_objects.Figure
    """
    bg = get_static_lines()
    fig = go.Figure()

    p_isobars = np.array(P_TICKS_HPA, dtype=float) * 100
    x_isobars = np.array(X_LIMITS, dtype=float)[:, np.newaxis] * np.ones((1, p_isobars.size))
    x, y = _joined(x_isobars, np.broadcast_to(p_isobars / 100, x_isobars.shape))
    fig.add_trace(go.Scatter(
        x=x, y=y, mode="lines", name=BG_LABELS["isobars"], legendgroup="isobars",
        line=dict(color=_bg_color("isobars"), width=LW_BG, dash=DASH), hoverinfo="skip"))

    fig.add_trace(_family_trace("isotherms", bg["isotherms"], bg["p_isotherms"]))
    fig.add_trace(_family_trace("isohumes", bg["isohumes"], bg["p_isohumes"]))
    p_label = bg["p_isohumes"][-1]
    fig.add_trace(go.Scatter(
        x=skew_transform(bg["isohumes"][-1], p_label), y=np.full(bg["isohumes"].shape[1], p_label / 100),
        mode="text", text=[f"{r:.1f}" for r in bg["isohume_mixing_ratios"]], textposition="top center",
        textfont=dict(size=12, color=_bg_color("isohumes")), legendgroup="isohumes",
        showlegend=False, hoverinfo="skip"))
    fig.add_trace(_family_trace("dry_adiabats", bg["dry_adiabats"], bg["p_dry"]))
    fig.add_trace(_family_trace("moist_adiabats", bg["moist_adiabats"], bg["p_moist"]))

    if sounding is not None:
        fig.add_trace(_profile_trace("Temperature", COLOR_T, sounding["T"], sounding["p"]))
        fig.add_trace(_profile_trace("Dew point", COLOR_TD, sounding["Td"], sounding["p"]))

    fig.update_xaxes(
        range=X_LIMITS, tickvals=np.arange(X_LIMITS[0], X_LIMITS[1] + 1, 10),
        ticktext=[f"{x}°" for x in range(X_LIMITS[0], X_LIMITS[1] + 1, 10)],
        title="Temperature (°C)", showgrid=False, zeroline=False,
        showline=True, mirror=True, linecolor="#ccc")
    fig.update_yaxes(
        type="log", range=[np.log10(P_BOTTOM_HPA), np.log10(p_top / 100)],
        tickvals=[p for p in P_TICKS_HPA if p >= p_top / 100], title="Pressure (hPa)",
        showgrid=False, showline=True, mirror=True, linecolor="#ccc")
    fig.update_layout(
        height=650, margin=dict(l=70, r=20, t=30, b=60), font=dict(size=FONT_SIZE),
        plot_bgcolor="white", paper_bgcolor="white", hovermode="closest",
        legend=dict(title="Click to show or hide", font=dict(size=12)))
    return fig


def add_dry_adiabat_slider(fig, theta_C=np.arange(0, 60.1, 2)):
    """
    Add a highlighted dry adiabat to a skew-T figure, with a slider that
    moves it from one potential temperature to the next.

    Parameters:
    ----------
    fig : plotly.graph_objects.Figure
        Figure returned by `skewt_figure`.
    theta_C : array-like
        Potential temperatures in degC the slider steps through; the dry
        adiabat of potential temperature theta crosses 1000 hPa at T = theta.

    Returns:
    -------
    plotly.graph_objects.Figure
        The same figure, with the slider.
    """
    p = np.geomspace(105_000, 10_000, 64)
    n_before = len(fig.data)
    for i, theta in enumerate(theta_C):
        T = (theta + thrm.T0) * thrm.exner(p)
        fig.add_trace(go.Scatter(
            x=skew_transform(T, p), y=p / 100, mode="lines", visible=(i == 0),
            name="Dry adiabat through slider", showlegend=False, hoverinfo="skip",
            line=dict(color=_bg_color("dry_adiabats", 1), width=LW_PROFILE)))

    steps = []
    for i, theta in enumerate(theta_C):
        visible = [True] * n_before + [j == i for j in range(len(theta_C))]
        steps.append(dict(method="restyle", args=[{"visible": visible}], label=f"{theta:.0f}"))
    fig.update_layout(sliders=[dict(
        steps=steps, active=0, currentvalue=dict(prefix="Dry adiabat through 1000 hPa at (°C): "),
        pad=dict(t=50))])
    fig.update_layout(height=750)
    return fig
