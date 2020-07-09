# ##### BEGIN GPL LICENSE BLOCK #####
#
#  BitWrk - A Bitcoin-friendly, anonymous marketplace for computing power
#  Copyright (C) 2013-2016  Jonas Eschenburg <jonas@bitwrk.net>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import math


def render_resolution(scene):
    percentage = max(1, min(10000, scene.render.resolution_percentage))
    print("percentage : ", percentage)
    resx = int(scene.render.resolution_x * percentage / 100)
    print("resx : ", resx)
    resy = int(scene.render.resolution_y * percentage / 100)
    print("resy : ", resy)

    scale = scene.render.resolution_percentage / 100.0
    print("scale : ", scale)
    size_x = int(scene.render.resolution_x * scale)
    print("size_x : ", size_x)
    size_y = int(scene.render.resolution_y * scale)
    print("size_y : ", size_y)
    return (resx, resy)


def max_tilesize(scene):
    def f(x): return x * x if scene.cycles.use_square_samples else x

    if scene.cycles.progressive == 'PATH':
        cost_per_bounce = f(scene.cycles.samples)
    elif scene.cycles.progressive == 'BRANCHED_PATH':
        cost_per_bounce = f(scene.cycles.aa_samples) * (
            f(scene.cycles.diffuse_samples) +
            f(scene.cycles.glossy_samples) +
            f(scene.cycles.transmission_samples) +
            f(scene.cycles.ao_samples) +
            f(scene.cycles.mesh_light_samples) +
            f(scene.cycles.subsurface_samples))
    else:
        raise RuntimeError("Unknows sampling type: %s" %
                           (scene.cycles.progressive))

    settings = scene.slaves_work_settings

    cost_per_pixel = 1 * scene.cycles.max_bounces * cost_per_bounce
    return int(math.floor(512*1024*1024 / cost_per_pixel / settings.boost_factor))
