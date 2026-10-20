"""
Recipe: japanese_obon_tea_tray
Category: tableware
Date: 2026-10-21
Notes: Authentic Japanese Round Lacquered Tea Tray (Obon / Maru-bon) with tactile center Uzumaki spiral and vermilion red rim crest.
"""

import bpy
import math
import os

def create_obon_tray():
    profile = [
        (0.000, 0.0025),
        (0.125, 0.0025),
        (0.130, 0.0000),
        (0.138, 0.0000),
        (0.142, 0.0035),
        (0.146, 0.0100),
        (0.149, 0.0180),
        (0.150, 0.0255),
        (0.148, 0.0275),
        (0.144, 0.0275),
        (0.142, 0.0250),
        (0.140, 0.0180),
        (0.138, 0.0120),
        (0.136, 0.0080),
        (0.110, 0.0080),
        (0.080, 0.0080),
        (0.050, 0.0080),
        (0.025, 0.0080),
        (0.000, 0.0080),
    ]

    segments = 96
    verts = []
    faces = []
    num_rings = len(profile)

    for r, z in profile:
        for i in range(segments):
            theta = (2.0 * math.pi * i) / segments
            verts.append((r * math.cos(theta), r * math.sin(theta), z))

    for ring in range(num_rings - 1):
        r_start = ring * segments
        next_r_start = (ring + 1) * segments
        for i in range(segments):
            next_i = (i + 1) % segments
            faces.append((r_start + i, r_start + next_i, next_r_start + next_i, next_r_start + i))

    mesh = bpy.data.meshes.new("Japanese_Obon_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obon_obj = bpy.data.objects.new("Japanese_Obon_Tray", mesh)
    bpy.context.collection.objects.link(obon_obj)

    # Tactile Archimedean spiral ripple in center floor
    for v in obon_obj.data.vertices:
        if v.co.z > 0.006 and v.co.z < 0.010:
            r = math.sqrt(v.co.x**2 + v.co.y**2)
            if r < 0.052:
                theta = math.atan2(v.co.y, v.co.x)
                spiral_phase = (r * 320.0) - theta
                falloff = 0.5 * (1.0 + math.cos(math.pi * min(1.0, r / 0.052)))
                v.co.z += math.sin(spiral_phase) * 0.00035 * falloff

    obon_obj.data.update()

    subsurf = obon_obj.modifiers.new(name="Subsurf", type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 2

    for f in obon_obj.data.polygons:
        f.use_smooth = True

    return obon_obj
