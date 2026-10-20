"""
Recipe: barista_milk_frothing_pitcher
Category: utensils
Date: 2026-10-21
Notes: Barista Stainless Steel Milk Frothing Pitcher (350ml / 12oz) with precision V-shaped pouring spout and welded flat-ribbon loop handle.
"""

import bpy
import bmesh
import math
import os

def create_barista_milk_pitcher():
    """
    Creates an authentic 350ml Barista Stainless Steel Milk Frothing Pitcher / Steaming Jug.
    Features:
    - Tapered bell cylinder body (Base D = 7.6cm, Top D = 6.8cm, Height = 9.2cm)
    - Sharp V-shaped pouring spout with vertical crease for precision latte art
    - Welded flat-ribbon stainless steel ergonomic loop handle
    - 304 food-grade stainless steel with vertical brushed anisotropic grain
    """
    body_profile = [
        (0.000, 0.0015), (0.032, 0.0015), (0.035, 0.0000), (0.037, 0.0000),
        (0.038, 0.0035), (0.038, 0.0150), (0.0375, 0.030), (0.0368, 0.050),
        (0.0358, 0.070), (0.0346, 0.085), (0.0340, 0.092)
    ]
    segments = 96
    verts_body, faces_body = [], []
    for r, z in body_profile:
        for i in range(segments):
            theta = (2.0 * math.pi * i) / segments
            verts_body.append((r * math.cos(theta), r * math.sin(theta), z))

    for ring in range(len(body_profile) - 1):
        r_start = ring * segments
        next_r_start = (ring + 1) * segments
        for i in range(segments):
            next_i = (i + 1) % segments
            faces_body.append((r_start + i, r_start + next_i, next_r_start + next_i, next_r_start + i))

    c_idx = len(verts_body)
    verts_body.append((0.0, 0.0, 0.0015))
    for i in range(segments):
        faces_body.append((c_idx, (i + 1) % segments, i))

    mesh_body = bpy.data.meshes.new("Pitcher_Body_Mesh")
    mesh_body.from_pydata(verts_body, [], faces_body)
    mesh_body.update()

    pitcher_obj = bpy.data.objects.new("Milk_Frothing_Pitcher", mesh_body)
    bpy.context.collection.objects.link(pitcher_obj)

    # Sharp V-Spout at -X axis
    spout_center = math.pi
    spout_half = math.radians(34)
    for v in pitcher_obj.data.vertices:
        if v.co.z > 0.052:
            theta = math.atan2(v.co.y, v.co.x)
            d_theta = abs(math.atan2(math.sin(theta - spout_center), math.cos(theta - spout_center)))
            if d_theta < spout_half:
                z_factor = ((v.co.z - 0.052) / 0.040)**1.6
                a_weight = math.cos((d_theta / spout_half) * (math.pi / 2))**2.2
                flare = 0.0135 * z_factor * a_weight
                r = math.sqrt(v.co.x**2 + v.co.y**2)
                if r > 0.001:
                    v.co.x += (v.co.x / r) * flare
                    v.co.y += (v.co.y / r) * flare
    pitcher_obj.data.update()

    solid = pitcher_obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    solid.thickness = 0.0011
    solid.offset = -1

    subsurf = pitcher_obj.modifiers.new(name="Subsurf", type='SUBSURF')
    subsurf.levels = 2

    # Handle Ribbon
    path_pts = [
        (0.034, 0.078), (0.039, 0.078), (0.065, 0.078), (0.0675, 0.0755),
        (0.0675, 0.071), (0.061, 0.027), (0.059, 0.024), (0.038, 0.024)
    ]
    bm_h = bmesh.new()
    y_half = 0.0135 / 2.0
    verts_ribbon = []
    for x, z in path_pts:
        v_l = bm_h.verts.new((x, -y_half, z))
        v_r = bm_h.verts.new((x,  y_half, z))
        verts_ribbon.append((v_l, v_r))
    for i in range(len(path_pts) - 1):
        vl1, vr1 = verts_ribbon[i]
        vl2, vr2 = verts_ribbon[i + 1]
        bm_h.faces.new([vl1, vr1, vr2, vl2])

    mesh_handle = bpy.data.meshes.new("Pitcher_Handle_Mesh")
    bm_h.to_mesh(mesh_handle)
    bm_h.free()

    handle_obj = bpy.data.objects.new("Pitcher_Handle", mesh_handle)
    bpy.context.collection.objects.link(handle_obj)

    solid_h = handle_obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    solid_h.thickness = 0.0016
    solid_h.offset = 0

    bevel_h = handle_obj.modifiers.new(name="Bevel", type='BEVEL')
    bevel_h.width = 0.0008
    bevel_h.segments = 2

    handle_obj.parent = pitcher_obj
    return pitcher_obj
