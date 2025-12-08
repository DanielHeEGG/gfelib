import gdsfactory as gf


class LAYER(gf.LayerEnum):
    layout = gf.constant(gf.kcl.layout)

    wafer = (999, 0)

    dummy = (0, 0)
    device = (1, 0)
    device_etch = (2, 0)
    handle = (3, 0)
    handle_etch = (4, 0)
    vias = (5, 0)
    handle_relief = (6, 0)
    reticle = (7, 0)


_layer_views = gf.technology.LayerViews()
_layer_views.add_layer_view(
    "device", gf.technology.LayerView(gds_layer=1, gds_datatype=0, color=(1, 1, 0))
)
_layer_views.add_layer_view("handle", gf.technology.LayerView(color=(0, 0, 1)))
_layer_views.add_layer_view("device_etch", gf.technology.LayerView(color=(0, 1, 0)))


mems_pdk = gf.Pdk(name="MEMS", layers=LAYER, layer_views=_layer_views)
