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

from pathlib import Path

import numpy as np
import xarray as xr

DATA_DIR = Path(__file__).parent / "data"


def load_model_sounding(name, time, p_top=10_000):
    """
    Load one time of a model sounding exported from the web tool, starting at
    the surface as the web tool does: the 2 m temperature and dew point at
    surface pressure, followed by the model levels above the surface.

    Parameters:
    ----------
    name : str
        Name of a netCDF file in the package data, e.g. "progtemps_martorell-example".
    time : str
        Time to select, e.g. "2021-07-13T15:00".
    p_top : float
        Levels above this pressure (Pa) are dropped.

    Returns:
    -------
    dict of np.ndarray, ordered from the surface upward:
        p  : pressure in Pa
        z  : height above ground in m
        T  : temperature in K
        Td : dew-point temperature in K
    and "time" : the selected time, as a string.
    """
    ds = xr.open_dataset(DATA_DIR / f"{name}.nc").sel(time=time)
    p_sfc = float(ds["surface_pressure"])
    above = (ds["p"].values < p_sfc) & (ds["p"].values >= p_top)
    return {
        "p":    np.r_[p_sfc, ds["p"].values[above]],
        "z":    np.r_[0.0, ds["z_agl"].values[above]],
        "T":    np.r_[float(ds["T_2m"]), ds["T"].values[above]],
        "Td":   np.r_[float(ds["Td_2m"]), ds["Td"].values[above]],
        "time": str(ds["time"].values)[:16],
    }
