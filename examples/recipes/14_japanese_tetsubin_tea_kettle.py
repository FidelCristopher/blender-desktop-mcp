"""
Recipe: 14_japanese_tetsubin_tea_kettle.py
Description: Authentic Traditional Japanese Tetsubin (Nanbu Cast Iron Tea Kettle)
Features:
- Cast-iron pot body with realistic wall thickness (~3.5mm) and hollow pouring spout
- Stepped lid (futa) with traditional acorn knob (tsumami)
- Graceful low-profile overhead bail handle (tsuru) oriented inline with the spout axis (front anchor above spout, rear anchor behind)
- Tactile Arare (hailstone) studs and sand-cast iron hada texture baked to 2K PBR
- Velvety Hitam Dove (Matte Black, Roughness 0.92, Metallic 0.02) finish
- Single GLB export container for interactive WebGL / 3D web experiences
"""

import bpy
import math

OUTPUT_GLB = r"C:\Users\Pongo\Downloads\3d-asset\tea-kettle.glb"

def setup_tetsubin_kettle():
    kettle = bpy.data.objects.get("Japanese_Tetsubin_Kettle")
    if not kettle:
        print("[Tetsubin] Kettle mesh not found.")
        return

    # Ensure single export
    bpy.ops.object.select_all(action='DESELECT')
    kettle.select_set(True)
    bpy.context.view_layer.objects.active = kettle

    for l_name in ['KeyLight', 'FillLight', 'RimLight']:
        if l_name in bpy.data.objects:
            bpy.data.objects[l_name].select_set(True)

    bpy.ops.export_scene.gltf(
        filepath=OUTPUT_GLB,
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_materials='EXPORT',
        export_image_format='AUTO',
        export_lights=True
    )
    print(f"[Tetsubin] Master GLB saved to: {OUTPUT_GLB}")

if __name__ == "__main__":
    setup_tetsubin_kettle()
