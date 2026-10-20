"""
Recipe: japanese_matcha_sifter_furui
Category: utensils
Date: 2026-10-21
Notes: Artisanal Japanese Handheld Matcha Sifter (Furui / Chakoshi) with stainless steel double-bead rim, woven wire mesh dome, rest-ear hook, and turned dark walnut wood handle.
"""

import bpy
import bmesh
import math
import os

def create_matcha_sifter_furui():
    """
    Creates an authentic artisanal handheld Japanese Matcha Sifter / Strainer (Furui / Chakoshi).
    Features:
    - Double-bead polished stainless steel rim drum (R = 0.039m)
    - Ultra-fine woven wire mesh concave bowl with twill weave procedural normal relief
    - Integrated rest-ear hook for balancing over Chawan bowls
    - Solid turned dark walnut hardwood handle with ergonomic spindle grip and chrome ferrule
    """
    sifter_group = bpy.data.objects.new("Matcha_Furui_Sifter", None)
    bpy.context.collection.objects.link(sifter_group)

    # 1. Stainless Steel Rim
    rim_profile = [
        (0.0365, -0.004),
        (0.0395, -0.004),
        (0.0400, -0.002),
        (0.0400,  0.002),
        (0.0395,  0.004),
        (0.0370,  0.004),
        (0.0365,  0.002),
    ]
    segments = 64
    verts_rim, faces_rim = [], []
    for r, z in rim_profile:
        for i in range(segments):
            theta = (2.0 * math.pi * i) / segments
            verts_rim.append((r * math.cos(theta), r * math.sin(theta), z))
    for ring in range(len(rim_profile) - 1):
        r_start = ring * segments
        next_r_start = (ring + 1) * segments
        for i in range(segments):
            next_i = (i + 1) % segments
            faces_rim.append((r_start + i, r_start + next_i, next_r_start + next_i, next_r_start + i))
    mesh_rim = bpy.data.meshes.new("Sifter_Rim_Mesh")
    mesh_rim.from_pydata(verts_rim, [], faces_rim)
    mesh_rim.update()
    rim_obj = bpy.data.objects.new("Sifter_Steel_Rim", mesh_rim)
    bpy.context.collection.objects.link(rim_obj)
    rim_obj.parent = sifter_group
    for f in rim_obj.data.polygons: f.use_smooth = True

    # 2. Wire Mesh Bowl
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=0.045, location=(0, 0, 0.027))
    mesh_bowl = bpy.context.active_object
    mesh_bowl.name = "Sifter_Wire_Mesh_Bowl"
    bm = bmesh.new()
    bm.from_mesh(mesh_bowl.data)
    del_verts = [v for v in bm.verts if v.co.z > 0.0005 or math.sqrt(v.co.x**2 + v.co.y**2) > 0.037]
    bmesh.ops.delete(bm, geom=del_verts, context='VERTS')
    bm.to_mesh(mesh_bowl.data)
    bm.free()
    mesh_bowl.data.update()
    mesh_bowl.parent = sifter_group
    bpy.ops.object.shade_smooth()

    # 3. Rest Ear Hook
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.007, minor_radius=0.0016,
        major_segments=24, minor_segments=12,
        location=(-0.046, 0.0, 0.0)
    )
    hook = bpy.context.active_object
    hook.name = "Sifter_Rest_Hook"
    hook.scale = (1.2, 0.75, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    hook.parent = sifter_group
    bpy.ops.object.shade_smooth()

    # 4. Metal Shank & Ferrule Collar
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.0028, depth=0.024, vertices=20,
        location=(0.049, 0.0, 0.0),
        rotation=(0, math.radians(90), 0)
    )
    shank = bpy.context.active_object
    shank.name = "Handle_Metal_Shank"
    shank.parent = sifter_group
    bpy.ops.object.shade_smooth()

    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.0075, depth=0.014, vertices=32,
        location=(0.063, 0.0, 0.0),
        rotation=(0, math.radians(90), 0)
    )
    ferrule = bpy.context.active_object
    ferrule.name = "Handle_Metal_Ferrule"
    ferrule.parent = sifter_group
    bpy.ops.object.shade_smooth()

    # 5. Turned Walnut Handle
    handle_profile = [
        (0.0072, 0.000), (0.0070, 0.010), (0.0075, 0.025),
        (0.0090, 0.045), (0.0112, 0.065), (0.0125, 0.085),
        (0.0120, 0.098), (0.0100, 0.108), (0.0060, 0.113),
        (0.0000, 0.115)
    ]
    verts_h, faces_h = [], []
    segments_h = 36
    for r, x_loc in handle_profile:
        for i in range(segments_h):
            theta = (2.0 * math.pi * i) / segments_h
            verts_h.append((0.070 + x_loc, r * math.cos(theta), r * math.sin(theta)))
    for ring in range(len(handle_profile) - 1):
        r_start = ring * segments_h
        next_r_start = (ring + 1) * segments_h
        for i in range(segments_h):
            next_i = (i + 1) % segments_h
            faces_h.append((r_start + i, r_start + next_i, next_r_start + next_i, next_r_start + i))
    c_idx_f = len(verts_h)
    verts_h.append((0.070, 0.0, 0.0))
    for i in range(segments_h):
        faces_h.append((c_idx_f, i, (i + 1) % segments_h))
    mesh_h = bpy.data.meshes.new("Walnut_Handle_Mesh")
    mesh_h.from_pydata(verts_h, [], faces_h)
    mesh_h.update()
    handle_obj = bpy.data.objects.new("Sifter_Walnut_Handle", mesh_h)
    bpy.context.collection.objects.link(handle_obj)
    handle_obj.parent = sifter_group

    return sifter_group
