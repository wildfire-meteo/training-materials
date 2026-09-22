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
Figures of notebooks/1_introduction_skewt.ipynb, one function per figure. Each
takes a sounding as returned by `odet_meteo.soundings.load_model_sounding`.
"""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from . import parcel as prcl
from . import skewt
from . import thermo as thrm

# Parcels as in the web tool: black, long dashes; their levels thin and light.
COLOR_PARCEL = "#000000"
COLOR_PARCEL_ALT = "#9e9e9e"
DASH_PARCEL = "12px,5px"
LW_PARCEL = 2.6

ANNOTATION_BOX = dict(
    xref="paper", yref="paper", x=0.98, y=0.98, xanchor="right", yanchor="top",
    align="left", showarrow=False, bgcolor="rgba(255,255,255,0.9)",
    bordercolor="#ccc", borderwidth=1, borderpad=6, font=dict(size=13))


def _hover(T, z):
    return np.column_stack([np.atleast_1d(T) - thrm.T0, np.atleast_1d(z)])


def _p_at_height(sounding, z):
    return np.exp(np.interp(z, sounding["z"], np.log(sounding["p"])))


def _box(text):
    return dict(ANNOTATION_BOX, text=text)


def _level_line(p, text, color=COLOR_PARCEL, visible=True):
    """
    A labelled horizontal line at pressure p (Pa), as the web tool marks
    cloud base and plume top.
    """
    return go.Scatter(
        x=list(skewt.X_LIMITS), y=[p / 100, p / 100], mode="lines+text",
        line=dict(color=color, width=1, dash=skewt.DASH), opacity=0.6,
        text=["", text], textposition="top left", textfont=dict(size=12, color=color),
        showlegend=False, hoverinfo="skip", visible=visible)


def _add_step_slider(fig, steps, labels, prefix, annotations=None, active=0):
    """
    Add a slider that shows one group of traces at a time.

    Parameters:
    ----------
    fig : plotly.graph_objects.Figure
        Figure holding the traces that are always shown.
    steps : list of lists of traces
        Traces to show at each step of the slider.
    labels : list of str
        Label of each step.
    prefix : str
        Text before the label of the current step.
    annotations : list of str, optional
        Text box shown at each step.
    active : int
        Step shown initially.
    """
    n_fixed = len(fig.data)
    owner = []
    for i, group in enumerate(steps):
        for trace in group:
            trace.visible = (i == active)
            fig.add_trace(trace)
            owner.append(i)

    slider_steps = []
    for i, label in enumerate(labels):
        visible = [True] * n_fixed + [o == i for o in owner]
        layout = {"annotations": [_box(annotations[i])]} if annotations else {}
        slider_steps.append(dict(method="update", args=[{"visible": visible}, layout], label=label))

    fig.update_layout(
        sliders=[dict(steps=slider_steps, active=active, currentvalue=dict(prefix=prefix),
                      pad=dict(t=60))],
        height=fig.layout.height + 90)
    if annotations:
        fig.update_layout(annotations=[_box(annotations[active])])


def temperature_and_pressure_figure(sounding):
    """
    Temperature and pressure against height, side by side.
    """
    z, T, p = sounding["z"], sounding["T"] - thrm.T0, sounding["p"] / 100
    fig = make_subplots(rows=1, cols=2, shared_yaxes=True, horizontal_spacing=0.08)
    fig.add_trace(go.Scatter(
        x=T, y=z, mode="lines+markers", name="Temperature",
        line=dict(color=skewt.COLOR_T, width=skewt.LW_PROFILE), marker=dict(size=5),
        hovertemplate="Temperature: %{x:.1f} °C<br>Height: %{y:.0f} m<extra></extra>"), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=p, y=z, mode="lines+markers", name="Pressure",
        line=dict(color="#333333", width=skewt.LW_PROFILE), marker=dict(size=5),
        hovertemplate="Pressure: %{x:.0f} hPa<br>Height: %{y:.0f} m<extra></extra>"), row=1, col=2)
    axis = dict(showgrid=True, gridcolor="#eee", zeroline=False, showline=True, mirror=True, linecolor="#ccc")
    fig.update_xaxes(title="Temperature (°C)", **axis, row=1, col=1)
    fig.update_xaxes(title="Pressure (hPa)", **axis, row=1, col=2)
    fig.update_yaxes(**axis, range=[0, 16_500], tickformat="d")
    fig.update_yaxes(title="Height above the ground (m)", row=1, col=1)
    fig.update_layout(
        height=500, margin=dict(l=70, r=20, t=30, b=60), font=dict(size=skewt.FONT_SIZE),
        plot_bgcolor="white", paper_bgcolor="white", showlegend=False)
    return fig


def height_or_pressure_figure(sounding):
    """
    The temperature profile, with buttons that switch the vertical axis
    between height and (log-)pressure.
    """
    z, T, p = sounding["z"], sounding["T"], sounding["p"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=T - thrm.T0, y=z, mode="lines+markers", name="Temperature",
        line=dict(color=skewt.COLOR_T, width=skewt.LW_PROFILE), marker=dict(size=5),
        customdata=np.column_stack([z, p / 100]),
        hovertemplate="Temperature: %{x:.1f} °C<br>Height: %{customdata[0]:.0f} m"
                      "<br>Pressure: %{customdata[1]:.0f} hPa<extra></extra>"))
    p_isobars = np.array(skewt.P_TICKS_HPA, dtype=float)
    x_iso = np.tile([-70.0, 40.0, np.nan], p_isobars.size)
    y_iso = np.repeat(p_isobars, 3)
    fig.add_trace(go.Scatter(
        x=x_iso, y=y_iso, mode="lines", name="Isobars", visible=False, hoverinfo="skip",
        line=dict(color=skewt._bg_color("isobars", 1), width=1, dash=skewt.DASH)))

    height_axis = {"yaxis.type": "linear", "yaxis.range": [0, 16_500], "yaxis.tickvals": None, "yaxis.tickformat": "d",
                   "yaxis.title.text": "Height above the ground (m)"}
    pressure_axis = {"yaxis.type": "log", "yaxis.range": [np.log10(skewt.P_BOTTOM_HPA), 2],
                     "yaxis.tickvals": skewt.P_TICKS_HPA, "yaxis.tickformat": "", "yaxis.title.text": "Pressure (hPa)"}
    fig.update_layout(updatemenus=[dict(
        type="buttons", direction="right", x=0, xanchor="left", y=1.12, yanchor="bottom",
        showactive=True, buttons=[
            dict(label="Height on the vertical axis", method="update",
                 args=[{"y": [z, y_iso], "visible": [True, False]}, height_axis]),
            dict(label="Pressure on the vertical axis", method="update",
                 args=[{"y": [p / 100, y_iso], "visible": [True, True]}, pressure_axis]),
        ])])
    axis = dict(showgrid=False, zeroline=False, showline=True, mirror=True, linecolor="#ccc")
    fig.update_xaxes(title="Temperature (°C)", range=[-70, 40], **axis)
    fig.update_yaxes(title="Height above the ground (m)", range=[0, 16_500], tickformat="d", **axis)
    fig.update_layout(
        height=560, margin=dict(l=70, r=20, t=80, b=60), font=dict(size=skewt.FONT_SIZE),
        plot_bgcolor="white", paper_bgcolor="white", showlegend=False)
    return fig


def skew_slider_figure(sounding, skew_factors=np.linspace(0, skewt.SKEW_FACTOR, 6)):
    """
    Temperature against log-pressure, with isotherms, and a slider that skews
    the diagram from not at all to as much as in the web tool.
    """
    p, T = sounding["p"], sounding["T"]
    bg = skewt.get_static_lines()
    p_iso = bg["p_isotherms"][:, np.newaxis]

    def skewed(T_k, p_pa, factor):
        return (T_k - thrm.T0) + factor * (np.log(1000) - np.log(p_pa / 100))

    def isotherm_xy(factor):
        return skewt._joined(skewed(bg["isotherms"], p_iso, factor),
                             np.broadcast_to(p_iso / 100, bg["isotherms"].shape))

    x_range = (-70, 50)
    fig = skewt.skewt_figure(lines=("isobars",), height=700)
    fig.data[0].x = np.where(np.isnan(fig.data[0].x), np.nan, np.where(fig.data[0].x < 0, x_range[0], x_range[1]))
    x_iso, y_iso = isotherm_xy(skew_factors[0])
    fig.add_trace(go.Scatter(
        x=x_iso, y=y_iso, mode="lines", name="Isotherms", hoverinfo="skip",
        line=dict(color=skewt._bg_color("isotherms"), width=skewt.LW_BG, dash=skewt.DASH)))
    fig.add_trace(go.Scatter(
        x=skewed(T, p, skew_factors[0]), y=p / 100, mode="lines", name="Temperature",
        line=dict(color=skewt.COLOR_T, width=skewt.LW_PROFILE),
        customdata=_hover(T, sounding["z"]), hovertemplate=skewt.hover_template("Temperature", True)))

    n = len(skew_factors)
    steps = []
    for i, factor in enumerate(skew_factors):
        x_iso, _ = isotherm_xy(factor)
        label = "none" if i == 0 else ("as in the web tool" if i == n - 1 else f"{100 * factor / skew_factors[-1]:.0f}%")
        steps.append(dict(method="restyle", label=label,
                          args=[{"x": [x_iso, skewed(T, p, factor)]}, [1, 2]]))
    ticks = np.arange(-60, x_range[1] + 1, 20)
    fig.update_xaxes(range=x_range, tickvals=ticks, ticktext=[f"{t}°" for t in ticks])
    fig.update_layout(
        sliders=[dict(steps=steps, active=0, currentvalue=dict(prefix="Skew: "), pad=dict(t=60))],
        height=790)
    return fig


# Parcels of the buoyancy quiz: (name, pressure in Pa, temperature minus surroundings in K).
QUIZ_PARCELS = [("A", 92_500, 3), ("B", 85_000, -3), ("C", 70_000, 0), ("D", 50_000, 2), ("E", 30_000, -4)]


def buoyancy_quiz_figure(sounding, parcels=QUIZ_PARCELS):
    """
    The sounding with a few parcels next to it; hovering a parcel explains
    whether it rises or sinks.
    """
    fig = skewt.skewt_figure(sounding, lines=("isobars", "isotherms"), dewpoint=False, height=700)
    for name, p, dT in parcels:
        T_env = prcl.interp_log_p(p, sounding["p"], sounding["T"])
        if dT > 0:
            verdict = "warmer → lighter → <b>positively buoyant</b>: it rises"
        elif dT < 0:
            verdict = "colder → heavier → <b>negatively buoyant</b>: it sinks"
        else:
            verdict = "the same temperature → equally heavy → <b>neutrally buoyant</b>: it stays"
        text = (f"Parcel {name}: {T_env + dT - thrm.T0:.1f} °C<br>"
                f"Surroundings: {T_env - thrm.T0:.1f} °C<br>{verdict}")
        fig.add_trace(go.Scatter(
            x=[skewt.skew_transform(T_env + dT, p)], y=[p / 100], mode="markers+text",
            marker=dict(size=16, color="white", line=dict(color=COLOR_PARCEL, width=2)),
            text=[name], textposition="middle right", textfont=dict(size=15),
            name=f"Parcel {name}", showlegend=False, hovertemplate=text + "<extra></extra>"))
    return fig


def dry_ascent_figure(sounding, heights=np.arange(0, 2_801, 200)):
    """
    The surface parcel lifted along its dry adiabat, with a slider over height.
    """
    T0, p0 = sounding["T"][0], sounding["p"][0]
    fig = skewt.skewt_figure(sounding, lines=("isobars", "isotherms", "dry_adiabats"),
                             dewpoint=False, height=700)
    steps, annotations = [], []
    for z in heights:
        p_path = np.geomspace(p0, _p_at_height(sounding, z), 30)
        T_path = prcl.dry_adiabat(T0, p0, p_path)
        z_path = prcl.interp_log_p(p_path, sounding["p"], sounding["z"])
        T_env = prcl.interp_log_p(p_path[-1], sounding["p"], sounding["T"])
        steps.append([
            skewt.profile_trace("Rising parcel", COLOR_PARCEL, T_path, p_path, z_path,
                                dash=DASH_PARCEL, width=LW_PARCEL),
            skewt.profile_trace("Rising parcel", COLOR_PARCEL, T_path[-1:], p_path[-1:], z_path[-1:],
                                mode="markers", marker=dict(size=14, color=COLOR_PARCEL), showlegend=False)])
        dT = T_path[-1] - T_env
        if z == 0:
            verdict = "The parcel starts at the surface,<br>as warm as the air around it."
        elif abs(dT) < 0.1:
            verdict = "About as warm as its surroundings:<br><b>this is about as high as it gets</b>."
        elif dT > 0:
            verdict = f"{dT:.1f} °C warmer than its surroundings:<br><b>it keeps rising</b>."
        else:
            verdict = f"{-dT:.1f} °C colder than its surroundings:<br><b>it cannot rise this far</b>."
        annotations.append(
            f"Parcel at {z:.0f} m: {T_path[-1] - thrm.T0:.1f} °C<br>"
            f"Surroundings: {T_env - thrm.T0:.1f} °C<br>{verdict}")
    _add_step_slider(fig, steps, [f"{z:.0f}" for z in heights],
                     "Height of the parcel above the ground (m): ", annotations)
    return fig


def dewpoint_figure(sounding):
    """
    The sounding with its dew point.
    """
    return skewt.skewt_figure(sounding, lines=("isobars", "isotherms", "dry_adiabats"), height=700)


def isohumes_figure(sounding):
    """
    The sounding with its dew point and the isohumes.
    """
    return skewt.skewt_figure(sounding, lines=("isobars", "isotherms", "isohumes", "dry_adiabats"),
                              height=700)


def lcl_construction_figure(sounding):
    """
    Step-by-step construction of the lifting condensation level of the
    surface parcel.
    """
    T0, Td0, p0 = sounding["T"][0], sounding["Td"][0], sounding["p"][0]
    p_lcl, T_lcl = prcl.find_lcl(T0, Td0, p0)
    z_lcl = prcl.interp_log_p(p_lcl, sounding["p"], sounding["z"])
    p_path = np.geomspace(p0, 70_000, 60)
    z_path = prcl.interp_log_p(p_path, sounding["p"], sounding["z"])

    fig = skewt.skewt_figure(sounding, lines=("isobars", "isotherms", "isohumes", "dry_adiabats"), height=700)
    start = [
        skewt.profile_trace("Surface temperature", skewt.COLOR_T, np.array([T0]), np.array([p0]), np.array([0.0]),
                            mode="markers", marker=dict(size=14, color=skewt.COLOR_T), showlegend=False),
        skewt.profile_trace("Surface dew point", skewt.COLOR_TD, np.array([Td0]), np.array([p0]), np.array([0.0]),
                            mode="markers", marker=dict(size=14, color=skewt.COLOR_TD), showlegend=False)]
    dry = skewt.profile_trace("Parcel temperature (dry adiabat)", COLOR_PARCEL,
                              prcl.dry_adiabat(T0, p0, p_path), p_path, z_path, dash=DASH_PARCEL, width=LW_PARCEL)
    humid = skewt.profile_trace("Parcel dew point (isohume)", COLOR_PARCEL_ALT,
                                prcl.isohume(Td0, p0, p_path), p_path, z_path, dash=DASH_PARCEL, width=LW_PARCEL)
    lcl = [skewt.profile_trace("Lifting condensation level", COLOR_PARCEL, np.array([T_lcl]), np.array([p_lcl]),
                               np.array([z_lcl]), mode="markers", showlegend=False,
                               marker=dict(size=16, color="white", line=dict(color=COLOR_PARCEL, width=3))),
           _level_line(p_lcl, f"cloud base: {z_lcl:.0f} m")]

    steps = [start, start + [dry], start + [dry, humid], start + [dry, humid] + lcl]
    steps = [[go.Scatter(trace) for trace in group] for group in steps]
    annotations = [
        f"<b>Step 1.</b> Start at the surface, with the<br>temperature ({T0 - thrm.T0:.1f} °C, red dot) and<br>"
        f"the dew point ({Td0 - thrm.T0:.1f} °C, blue dot).",
        "<b>Step 2.</b> From the temperature, go up<br>along the dry adiabat (black dashes):<br>"
        "the temperature of the rising parcel.",
        "<b>Step 3.</b> From the dew point, go up<br>along the isohume (grey dashes):<br>"
        "the dew point of the rising parcel.",
        f"<b>Step 4.</b> Where the two lines meet, the parcel<br>is cool enough for its water vapour to<br>"
        f"condense: the lifting condensation level,<br>at {z_lcl:.0f} m and {T_lcl - thrm.T0:.1f} °C.",
    ]
    _add_step_slider(fig, steps, ["1", "2", "3", "4"], "Step ", annotations)
    return fig


def moist_ascent_figure(sounding):
    """
    The surface parcel lifted dry to its LCL and moist above, compared with
    staying on the dry adiabat.
    """
    rise = prcl.lift_surface_parcel(sounding)
    T0, p0 = sounding["T"][0], sounding["p"][0]
    fig = skewt.skewt_figure(sounding, height=730)
    p_dry = np.geomspace(rise["p_lcl"], 40_000, 40)
    fig.add_trace(skewt.profile_trace(
        "Without condensation (dry adiabat)", COLOR_PARCEL_ALT, prcl.dry_adiabat(T0, p0, p_dry), p_dry,
        prcl.interp_log_p(p_dry, sounding["p"], sounding["z"]), dash=DASH_PARCEL, width=LW_PARCEL))
    above = rise["p"] >= 40_000
    fig.add_trace(skewt.profile_trace(
        "Surface parcel", COLOR_PARCEL, rise["T"][above], rise["p"][above], rise["z"][above],
        dash=DASH_PARCEL, width=LW_PARCEL))
    fig.add_trace(_level_line(rise["p_lcl"], f"cloud base: {rise['z_lcl']:.0f} m"))
    return fig


def pyrocloud_figure(sounding, heating=np.arange(0, 4.01, 0.5)):
    """
    The surface parcel heated by the fire, with a slider over the heating.
    """
    fig = skewt.skewt_figure(sounding, height=730)
    steps, annotations = [], []
    for dT in heating:
        rise = prcl.lift_surface_parcel(sounding, dT=dT)
        shown = rise["p"] >= 20_000
        group = [
            skewt.profile_trace("Heated surface parcel", COLOR_PARCEL, rise["T"][shown], rise["p"][shown],
                                rise["z"][shown], dash=DASH_PARCEL, width=LW_PARCEL),
            _level_line(rise["p_lcl"], f"cloud base: {rise['z_lcl']:.0f} m")]
        reaches_lcl = rise["p_lcl"] >= rise["p_top"]
        pyrocloud = reaches_lcl and rise["dT_lcl"] >= 0.5
        if pyrocloud:
            group.append(_level_line(rise["p_top"], f"plume top: {rise['z_top']:.0f} m"))
        steps.append(group)

        text = (f"The fire heats the surface air by {dT:.1f} °C.<br>"
                f"Cloud base: {rise['z_lcl']:.0f} m, {rise['T_lcl'] - thrm.T0:.1f} °C.<br>")
        if not reaches_lcl:
            text += (f"The plume stops at {rise['z_top']:.0f} m, below<br>"
                     "its cloud base: <b>no pyrocloud</b>.")
        elif not pyrocloud:
            text += (f"At cloud base the plume is only {rise['dT_lcl']:.1f} °C<br>"
                     "warmer than its surroundings: <b>on the edge</b>.<br>"
                     "A little more heat decides whether<br>a pyrocloud forms.")
        else:
            text += (f"At cloud base the plume is {rise['dT_lcl']:.1f} °C warmer<br>"
                     f"than its surroundings: <b>a pyrocloud</b>,<br>up to about {rise['z_top']:.0f} m.")
        annotations.append(text)
    _add_step_slider(fig, steps, [f"+{dT:.1f}" for dT in heating],
                     "Extra heating of the surface air by the fire (°C): ", annotations)
    return fig
