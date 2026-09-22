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

DATA_DIR = Path(__file__).parent / "data"


def available_soundings():
    """
    List the soundings shipped with the package.

    Returns:
    -------
    list of str
        Names accepted by `load_sounding`.
    """
    return sorted(p.stem for p in DATA_DIR.glob("*.csv"))


def load_sounding(name):
    """
    Load a sounding shipped with the package.

    The data lives inside the package, so it loads without file access from
    the notebook, which some browsers block in JupyterLite.

    Parameters:
    ----------
    name : str
        Sounding name, e.g. "madrid_1998062412" (see `available_soundings`).

    Returns:
    -------
    dict of np.ndarray, ordered from the surface upward:
        p  : pressure in Pa
        z  : height above sea level in m
        T  : temperature in K
        Td : dew-point temperature in K
        u  : eastward wind in m/s
        v  : northward wind in m/s
    """
    data = np.genfromtxt(DATA_DIR / f"{name}.csv", delimiter=",", names=True)
    return {key: data[key] for key in data.dtype.names}
