import bpy 
import json

from ..assets.asset_helpers import get_user_assets, get_generated_assets

from ..assets.ui import draw_assets


def draw_blueprints(layout, name, title, generated_assets):
    nesting_indent = 0.05
    number_of_generated_assets = len(generated_assets)

    header, panel = layout.panel(f"assets{name}", default_closed=True)
    header.label(text=title + f"({number_of_generated_assets})", icon="XRAY")

    if panel:
        for asset in generated_assets:
            row = panel.row()
            split  = row.split(factor=nesting_indent)
            col = split.column()
            col.label(text=" ")
            col = split.column()

            sub_header, sub_panel = col.panel(f"assets_sub{asset.name}", default_closed=False)
            sub_header.label(text=f"{asset.name}        ({asset.path})", icon="XRAY")
            if sub_panel:
                sub_panel.label(text="         some stuff")

class BLENVY_PT_blueprints_panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Blueprints"
    bl_parent_id = "BLENVY_PT_SidePanel"
    bl_options = {'DEFAULT_CLOSED','HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        return context.window_manager.blenvy.mode == 'BLUEPRINTS' if 'blenvy' in context.window_manager else False

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.
        asset_registry = context.window_manager.assets_registry
        blueprint_registry = context.window_manager.blueprints_registry

        blueprint_registry.refresh_blueprints()

        for blueprint in blueprint_registry.blueprints_data.blueprints:

            header, panel = layout.box().panel(f"blueprint_assets{blueprint.name}", default_closed=True)
            if header:
                header.label(text=blueprint.name, icon="XRAY")
                header.prop(blueprint.collection, "always_export")
                
                if blueprint.local:
                    select_blueprint = header.operator(operator="blenvy.blueprint_select", text="", icon="RESTRICT_SELECT_OFF")
                    if blueprint.collection and blueprint.collection.name:
                        select_blueprint.blueprint_collection_name = blueprint.collection.name
                    select_blueprint.blueprint_scene_name = blueprint.scene.name

            if panel:
                split  = panel.split(factor=0.005)
                col = split.column()
                col.label(text=" ")

                col = split.column()

                if blueprint.local:
                    user_assets = get_user_assets(blueprint.collection)
                    generated_assets =  get_generated_assets(blueprint.collection)

                    draw_assets(layout=col, name=blueprint.name, title="Assets", asset_registry=asset_registry, user_assets=user_assets,  generated_assets=generated_assets, target_type="BLUEPRINT", target_name=blueprint.name)

                else:
                    user_assets = get_user_assets(blueprint.collection)
                    generated_assets =  get_generated_assets(blueprint.collection)

                    draw_assets(layout=col, name=blueprint.name, title="Assets", asset_registry=asset_registry, user_assets=user_assets, generated_assets=generated_assets, target_type="BLUEPRINT", target_name=blueprint.name, editable=False)
                    panel.label(text="External blueprint, assets are not editable")
