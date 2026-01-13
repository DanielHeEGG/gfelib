from __future__ import annotations

import gdsfactory as gf

default_cell = gf._cell.override_defaults(
    gf.cell, with_module_name=True, check_instances=False
)
