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
Non-entraining parcels, lifted as on a skew-T: along a dry adiabat (constant
potential temperature) up to the lifting condensation level, and along a moist
adiabat above it. Buoyancy is judged from temperature alone.
"""

import numpy as np

from . import thermo as thrm


def interp_log_p(p_new, p, values):
    """
    Interpolate a profile linearly in log-pressure.

    Parameters:
    ----------
    p_new : float or np.ndarray
        Pressures to interpolate to in Pa.
    p : np.ndarray
        Pressures of the profile in Pa, decreasing.
    values : np.ndarray
        Profile values at `p`.

    Returns:
    -------
    float or np.ndarray
        Values at `p_new`.
    """
    return np.interp(-np.log(p_new), -np.log(p), values)


def find_lcl(T_sfc, Td_sfc, p_sfc, tol=5):
    """
    Find the lifting condensation level of a surface parcel, where its dry
    adiabat meets its isohume. Port of `find_lcl` in ../wildfire-meteo-dmt/web/parcel.js.

    Parameters:
    ----------
    T_sfc : float
        Parcel temperature at the start in K.
    Td_sfc : float
        Parcel dew-point temperature at the start in K.
    p_sfc : float
        Pressure at the start in Pa.
    tol : float
        Tolerance of the bisection in Pa.

    Returns:
    -------
    p_lcl : float
        Pressure of the LCL in Pa.
    T_lcl : float
        Temperature at the LCL in K.
    """
    theta_sfc = T_sfc / thrm.exner(p_sfc)
    q_sfc = thrm.qsat(Td_sfc, p_sfc)

    def residual(p):
        return theta_sfc * thrm.exner(p) - thrm.dewpoint(q_sfc, p)

    p_lo = 500e2
    p_hi = p_sfc
    while (p_hi - p_lo) > tol:
        p_mid = 0.5 * (p_lo + p_hi)
        if residual(p_mid) > 0:
            p_hi = p_mid
        else:
            p_lo = p_mid

    p_lcl = 0.5 * (p_lo + p_hi)
    return p_lcl, theta_sfc * thrm.exner(p_lcl)


def dry_adiabat(T_start, p_start, p):
    """
    Temperature along the dry adiabat through (T_start, p_start).

    Parameters:
    ----------
    T_start : float
        Temperature in K.
    p_start : float
        Pressure in Pa.
    p : float or np.ndarray
        Pressures in Pa.

    Returns:
    -------
    float or np.ndarray
        Temperature in K.
    """
    return T_start / thrm.exner(p_start) * thrm.exner(p)


def isohume(Td_start, p_start, p):
    """
    Dew-point temperature along the isohume through (Td_start, p_start): the
    dew point of a parcel that keeps its water vapour as it rises.

    Parameters:
    ----------
    Td_start : float
        Dew-point temperature in K.
    p_start : float
        Pressure in Pa.
    p : float or np.ndarray
        Pressures in Pa.

    Returns:
    -------
    float or np.ndarray
        Dew-point temperature in K.
    """
    return thrm.dewpoint(thrm.qsat(Td_start, p_start), p)


def moist_adiabat(T_start, p_start, p_top=10_000, n=64):
    """
    Temperature along the moist adiabat through (T_start, p_start), upward.

    Parameters:
    ----------
    T_start : float
        Temperature in K.
    p_start : float
        Pressure in Pa.
    p_top : float
        Pressure in Pa where the adiabat ends.
    n : int
        Number of levels.

    Returns:
    -------
    p : np.ndarray
        Pressures in Pa, decreasing.
    T : np.ndarray
        Temperature in K.
    """
    p = np.geomspace(p_start, p_top, n)
    return p, thrm.calc_moist_adiabat(np.array([T_start]), p)[:, 0]


def lift_surface_parcel(sounding, dT=0.0, n=200):
    """
    Lift the surface parcel of a sounding: dry up to its LCL, moist above.

    Parameters:
    ----------
    sounding : dict
        Arrays "p" (Pa), "T" (K), "Td" (K), "z" (m), the surface first.
    dT : float
        Extra heating of the parcel at the surface in K; its moisture is kept.
    n : int
        Number of levels of the dry and of the moist part.

    Returns:
    -------
    dict with:
        p, T, z   : the parcel's path, from the surface up to the top of the sounding
        p_lcl, T_lcl, z_lcl : its lifting condensation level
        p_top, z_top : the first level above the surface where it is colder than
                       its surroundings, where it stops rising
        dT_lcl    : parcel minus environment temperature at the LCL in K
    """
    p_sfc = sounding["p"][0]
    T_sfc = sounding["T"][0] + dT
    p_lcl, T_lcl = find_lcl(T_sfc, sounding["Td"][0], p_sfc)

    p_dry = np.geomspace(p_sfc, p_lcl, n)
    p_moist, T_moist = moist_adiabat(T_lcl, p_lcl, p_top=sounding["p"][-1], n=n)
    p = np.r_[p_dry, p_moist[1:]]
    T = np.r_[dry_adiabat(T_sfc, p_sfc, p_dry), T_moist[1:]]

    T_env = interp_log_p(p, sounding["p"], sounding["T"])
    z = interp_log_p(p, sounding["p"], sounding["z"])
    colder = np.nonzero(T[1:] < T_env[1:])[0]
    k_top = colder[0] + 1 if colder.size else p.size - 1

    return {
        "p": p, "T": T, "z": z,
        "p_lcl": p_lcl, "T_lcl": T_lcl,
        "z_lcl": interp_log_p(p_lcl, sounding["p"], sounding["z"]),
        "p_top": p[k_top], "z_top": z[k_top],
        "dT_lcl": T_lcl - interp_log_p(p_lcl, sounding["p"], sounding["T"]),
    }
