"""
Recipe: 16_traditional_bamboo_chasen_whisk.py
Description: Authentic Traditional Japanese Bamboo Tea Whisk (Chasen / 茶筅)
Features:
- Hand-carved Shiratake (blonde bamboo) cylindrical handle (Jiku) with node ring bulge
- 48 delicate outer tines (Hon-kazu) with natural tulip-dome arch and inward scroll curls
- 16 tightly coiled inner spiral bud tines (Chashin)
- Traditional black braided cord binding rings (Musubi-ito)
- PBR Materials: Warm Golden Bamboo (Roughness 0.44) and Matte Black Cord (Roughness 0.88)
- Single master GLB container: chasen.glb
"""

import bpy

OUTPUT_GLB = r"C:\Users\Pongo\Downloads\3d-asset\chasen.glb"

def setup_chasen():
    chasen = bpy.data.objects.get("Bamboo_Chasen")
    if not chasen:
        print("[Chasen] Bamboo_Chasen object not found.")
        return

    bpy.ops.object.select_all(action='DESELECT')
    chasen.select_set(True)
    bpy.context.view_layer.objects.active = chasen

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
    print(f"[Chasen] Master GLB saved to: {OUTPUT_GLB}")

if __name__ == "__main__":
    setup_chasen()
