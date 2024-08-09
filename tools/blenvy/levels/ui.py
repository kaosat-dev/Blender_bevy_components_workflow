from types import SimpleNamespace
import bpy
from ..assets.asset_helpers import get_generated_assets, get_user_assets
from ..assets.ui import draw_assets
from ..blueprints.ui import draw_blueprints

class BLENVY_PT_levels_panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = ""
    bl_parent_id = "BLENVY_PT_SidePanel"
    bl_options = {'DEFAULT_CLOSED','HIDE_HEADER'}
    
    @classmethod
    def poll(cls, context):
        return context.window_manager.blenvy.mode == 'LEVELS'
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.
        blenvy = context.window_manager.blenvy
        layout.operator(operator="blenvy.assets_generate_files", text="Generate")

        asset_registry = context.window_manager.assets_registry
        blueprints_registry = context.window_manager.blueprints_registry
        #blueprints_registry.refresh_blueprints()
        blueprints_data = blueprints_registry.blueprints_data

        for scene in blenvy.level_scenes:
            header, panel = layout.box().panel(f"level_assets{scene.name}", default_closed=False)
            if header:
                header.label(text=scene.name)#, icon="HIDE_OFF")
                header.prop(scene, "always_export")
                select_level = header.operator(operator="blenvy.level_select", text="", icon="RESTRICT_SELECT_OFF")
                select_level.level_name = scene.name

            if panel:
                user_assets = get_user_assets(scene)
                generated_assets =  get_generated_assets(scene)
                row = panel.row()
                #row.label(text="row")
                """col = row.column()
                col.label(text=" ")

                col = row.column()
                col.label(text="col in row 2")

                column = panel.column()
                column.label(text="col")"""

                split  = panel.split(factor=0.005)
                col = split.column()
                col.label(text=" ")
                col = split.column()

                scene_assets_panel = draw_assets(layout=col, name=f"{scene.name}_assets", title=f"Assets", asset_registry=asset_registry, user_assets=user_assets, generated_assets=generated_assets, target_type="SCENE", target_name=scene.name)
                scene_blueprints_panel = draw_blueprints(layout=col, name=f"{scene.name}_blueprints", title=f"Blueprints", generated_assets=generated_assets, )
    
        settings = {"blueprints_path": "blueprints", "export_gltf_extension": ".glb"}
        settings = SimpleNamespace(**settings)
