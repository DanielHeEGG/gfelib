import gfelib
import gdsfactory as gf
import gfelib.datatypes as gfd
import numpy as np

c = gf.Component()

release = gfd.ReleaseSpec(hole_radius=3, distance=6, layer=1, angle_resolution=1)
bs = gfd.BeamSpec(thick_length=(0, 0.7), thick_offset=(0, 0), thick_width=(20, 0))

circ = gfelib.basic.circle(
    radius=100, geometry_layer=0, angle_resolution=1, release_spec=release
)

rect = gfelib.basic.rectangle(
    (100, 200), geometry_layer=0, centered=False, release_spec=release
)

ring = gfelib.basic.ring(
    radius=80,
    width=150,
    angles=(60, 90),
    geometry_layer=0,
    release_spec=release,
    angle_resolution=1,
)

beam = gfelib.flexure.beam(
    length=200,
    width=4,
    geometry_layer=0,
    release_spec=release,
    beam_spec=bs,
)

beam_cavity = gfelib.flexure.beam_cavity(
    length=100,
    width=10,
    geometry_layer=0,
    etch_layer=3,
    etch_width=50,
    etch_length_offset=10,
)
butt = gfelib.flexure.butterfly(
    radius_inner=100,
    radius_outer=1000,
    angles=(5, 70),
    width_beam=4,
    width_inner=50,
    beam_spec=bs,
    release_inner=False,
    geometry_layer=0,
    angle_resolution=1,
    release_spec=release,
)

# poly = ((0, 0), (200, 200), (0, 800), (-400, 400))
poly = ((-400, 400), (-300, 200), (200, 200), (0, 0))
polygon = gfelib.basic.polygon(points=poly, geometry_layer=0, release_spec=release)

(c << circ).move((500, 500))
(c << rect).move((100, 100))
(c << ring).move((-100, 200))
(c << beam).move((-300, 0))
(c << butt).move((0, 1000))
(c << polygon).move((-1000, -1000))

(c << beam_cavity).move((-300, 200))
c.show()
