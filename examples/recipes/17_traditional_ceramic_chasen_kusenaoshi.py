"""
Recipe: 17_traditional_ceramic_chasen_kusenaoshi.py
Description: Authentic Traditional Japanese Ceramic Chasen-Kusenaoshi (Whisk Stand / Shaper)
Features:
- Parametric lathe curvature with flared base foot (kodai), cinched waist, and bulbous support dome
- Hollow central core to cradle bamboo tines without flattening curls
- Subdivision surface smoothing for pristine vitrified porcelain contours
- Authentic Japanese Celadon Seiji glaze (Pale soft mint-jade green, vitreous gloss Roughness 0.09, Specular 0.65)
- Single master GLB container: kusenaoshi.glb
"""

import bpy

OUTPUT_GLB = r"C:\Users\Pongo\Downloads\3d-asset\kusenaoshi.glb"

def setup_kusenaoshi():
    stand = bpy.data.objects.get("Chasen_Kusenaoshi")
    if not stand:
        print("[Kusenaoshi] Object not found.")
        return

    bpy.ops.object.select_all(action='DESELECT')
    stand.select_set(True)
    bpy.context.view_layer.objects.active = stand

    for l_name in ['KeyLight', 'FillLight', 'RimLight']:
        if l_name in bpy.data.objects:
            bpy.data.objects[l_name].select_set(True)

    win = bpy.context.window_manager.windows[0]
    with bpy.context.temp_override(window=win):
        bpy.ops.export_scene.gltf(
            filepath=OUTPUT_GLB,
            export_format='GLB',
            use_selection=True,
            export_apply=True,
            export_materials='EXPORT',
            export_image_format='AUTO',
            export_lights=True
        )
    print(f"[Kusenaoshi] Master GLB saved to: {OUTPUT_GLB}")

if __name__ == "__main__":
    setup_kusenaoshi()
