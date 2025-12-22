from __future__ import annotations

import gdsfactory as gf

import functools

default_cell = functools.partial(gf.cell, with_module_name=True, check_instances=False)
