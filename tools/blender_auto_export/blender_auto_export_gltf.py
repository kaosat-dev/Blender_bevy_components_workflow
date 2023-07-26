bl_info = {
    "name": "blender_auto_export_gltf",
    "author": "kaosigh",
    "version": (0, 1),
    "blender": (3, 6, 0),
    "location": "File > Import-Export",
    "description": "glTF/glb auto-export",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"
    }

import os
import bpy
from bpy.types import Operator, AddonPreferences
from bpy.app.handlers import persistent
from bpy_extras.io_utils import ExportHelper
from bpy.props import (BoolProperty,
                       IntProperty,
                       StringProperty,
                       EnumProperty,
                       CollectionProperty
                       )

#see here for original gltf exporter infos https://github.com/KhronosGroup/glTF-Blender-IO/blob/main/addons/io_scene_gltf2/__init__.py

@persistent
def deps_update_handler(scene):
    print("-------------")
    print("depsgraph_update_post", scene.name)

    changed = scene.name or ""
    print("changed", changed)
    bpy.context.scene.changedScene = changed
    #set_ChangedScene(changed)
    #auto_export()



#https://docs.blender.org/api/current/bpy.ops.export_scene.html#bpy.ops.export_scene.gltf
def export_gltf (path, export_settings):
    settings = {**export_settings, "filepath": path}
    bpy.ops.export_scene.gltf(**settings)

def get_collection_hierarchy(root_col, levels=1):
    """Read hierarchy of the collections in the scene"""
    level_lookup = {}
    def recurse(root_col, parent, depth):
        if depth > levels: 
            return
        if isinstance(parent,  bpy.types.Collection):
            level_lookup.setdefault(parent, []).append(root_col)
        for child in root_col.children:
            recurse(child, root_col,  depth + 1)
    recurse(root_col, root_col.children, 0)
    return level_lookup

"""
This exports the library's collections into seperate gltf files
"""
def export_library_split(scene, folder_path, gltf_export_preferences):
    # backup current active scene
    old_current_scene = bpy.context.scene
    # set active scene to be the given scene
    bpy.context.window.scene = scene

    export_settings = { **gltf_export_preferences, 'use_active_scene': True}

    root_collection = scene.collection 
    collections_lookup = get_collection_hierarchy(root_collection, 3)

    children_to_parent_collections = {i : k for k, v in collections_lookup.items() for i in v}
    scene_objects = [o for o in root_collection.objects]
    candidates = [x for v in collections_lookup.values() for x in v]
    """
    print("prt_col", children_to_parent_collections)
    print("scene objects", scene_objects) 
    print("candidate", candidates)
    """

    if not candidates:
        # self.report({'INFO'}, "Nothing to export")
        # reset current scene from backup
        bpy.context.window.scene = old_current_scene
        return #{'CANCELLED'}     

    # Unlink all Collections and objects
    for canditate in candidates:
        children_to_parent_collections.get(canditate).children.unlink(canditate)
    for object in scene_objects: 
        scene_objects.objects.unlink(object)   

    # (Re-)link collections of choice to root level and export
    for canditate in candidates:
        root_collection.children.link(canditate)
        collection_name = canditate.name
        gltf_output_path = os.path.join(folder_path, collection_name)
        export_gltf(gltf_output_path, export_settings)
        print("exporting", collection_name, "to", gltf_output_path)
        root_collection.children.unlink(canditate)

    # Reset all back
    for object in scene_objects: 
        scene_objects.objects.link(object)
    for canditate in candidates: 
        children_to_parent_collections.get(canditate).children.link(canditate)

    # reset current scene from backup
    bpy.context.window.scene = old_current_scene


def debug_test(scene):
    root_collection = scene.collection 
    collections_lookup = get_collection_hierarchy(root_collection, 1)

    children_to_parent_collections = {i : k for k, v in collections_lookup.items() for i in v}
    scene_objects = [o for o in root_collection.objects]
    candidates = [x for v in collections_lookup.values() for x in v]
    print("prt_col", children_to_parent_collections)
    print("scene objects", scene_objects) 
    print("candidates", candidates)

"""
export the library into only a few gltf files ie
    scene_collection
        asset_pack1
            asset_a
            asset_b
            asset_c

        asset_pack2
            asset_d
            asset_e

would export 2 gltf files
    asset_pack1.glb
        with three scenes:
           asset_a
           asset_b
           asset_c 

    asset_pack2.glb
        with two scenes:
           asset_d
           asset_f
"""
def export_library_merged(scene, folder_path, gltf_export_preferences):
    # backup current active scene
    old_current_scene = bpy.context.scene
    # set active scene to be the given scene
    bpy.context.window.scene = scene

    export_settings = { 
        **gltf_export_preferences, 
        'use_active_scene': False,
        'use_visible': False,
    }

    root_collection = scene.collection 
    collections_lookup = get_collection_hierarchy(root_collection, 3)

    children_to_parent_collections = {i : k for k, v in collections_lookup.items() for i in v}
    scene_objects = [o for o in root_collection.objects]
    candidates = [x for v in collections_lookup.values() for x in v]
    
    """
    print("prt_col", children_to_parent_collections)
    print("scene objects", scene_objects) 
    print("candidate", candidates)
    """

    virtual_scenes = []
    if not candidates:
        # self.report({'INFO'}, "Nothing to export")
        return #{'CANCELLED'}     

    for canditate in candidates:
        #print("candidate collection", canditate)
        virtual_scene = bpy.data.scenes.new(name=canditate.name)
        virtual_scenes.append(virtual_scene)
        virtual_scene.collection.children.link(canditate)
    try:
        gltf_output_path = os.path.join(folder_path, "library")
        export_gltf(gltf_output_path, export_settings)
    except Exception:
        print("failed to export to gltf")

    for virtual_scene in virtual_scenes:
        bpy.data.scenes.remove(virtual_scene)

    # TODO: we want to exclude the library and the game scene ???
    """
    #backup test 
    backup = bpy.data.scenes["toto"]
    ## add back the scene
    #bpy.data.scenes["toto"] = backup
    collection = ""
    try:
        collection = bpy.data.collections["virtual"]
        bpy.data.collections.remove(collection)
        collection = bpy.data.collections.new("virtual")
    except Exception:
        collection = bpy.data.collections.new("virtual")
        raise

    #bpy.data.scenes["toto"].collection.children.unlink(bpy.data.scenes["toto"].collection)
    #print("copy", collection)

    # nuke the scene
    toto = bpy.data.scenes["toto"]
    print(" toto.collection",  toto.collection.children)
    for child in toto.collection.children:
        print("child ", child)
    for child in toto.collection.objects:
        print("child ", child)

    collection.children.link(toto.collection)

    for child in collection.children:
        print("child 2 ", child)

    for child in toto.collection.objects:
        print("child ", child)
        toto.collection.objects.unlink(child)

    #toto.collection.children.unlink(toto.collection)

    bpy.data.scenes.remove(toto)

    # now recreate it 
    toto = bpy.data.scenes.new(name="toto")
    toto.collection.children.link(collection)
    for child in collection.objects:
        print("adding back child ", child)
        toto.collection.objects.link(child)
    """ 
    # reset current scene from backup
    bpy.context.window.scene = old_current_scene

def export_main(scene, folder_path, gltf_export_preferences, output_name): 
    print("exporting to", folder_path, output_name)
    # backup current active scene
    old_current_scene = bpy.context.scene
    # set active scene to be the given scene
    bpy.context.window.scene = scene

    gltf_output_path = os.path.join(folder_path, output_name)

    export_settings = { **gltf_export_preferences, 'use_active_scene': True}
    export_gltf(gltf_output_path, export_settings)

    # reset current scene from backup
    bpy.context.window.scene = old_current_scene

def auto_export():
    file_path = bpy.data.filepath
    # Get the folder
    folder_path = os.path.dirname(file_path)
    addon_prefs = bpy.context.preferences.addons[__name__].preferences


    library_scene = bpy.data.scenes["library"]

    """
    print("folder", folder_path)
        scn_col = bpy.context.scene.collection

    print("scene", scn_col)
    print("scenes", library_scene, game_scene)

    library_root_collection = library_scene.collection
    library_base_collections_lookup = get_collection_hierarchy(library_root_collection, 3)
    print("lib root collection", library_root_collection)
    print("all collections", library_base_collections_lookup)
    """

    """ 
    lkp_col = get_collection_hierarchy(scn_col, levels=3)
    prt_col = {i : k for k, v in lkp_col.items() for i in v}
    scn_obj = [o for o in scn_col.objects]
    candidates = [x for v in lkp_col.values() for x in v]
    print("scn_col", scn_col)

    print("lkp_col", lkp_col)
    print("prt_col", prt_col)
    print("scene objects", scn_obj) 
    print("candidate", candidates)
    """

    print("-------------")
    
    gltf_export_preferences = dict(
        export_format= 'GLB', #'GLB', 'GLTF_SEPARATE', 'GLTF_EMBEDDED'
        check_existing=False,

        use_selection=False,
        use_visible=True, # Export visible and hidden objects. See Object/Batch Export to skip.
        use_renderable=False,
        use_active_collection= False,
        use_active_collection_with_nested=False,
        use_active_scene = False,

        export_texcoords=True,
        export_normals=True,
        # here add draco settings
        export_draco_mesh_compression_enable = False,

        export_tangents=False,
        #export_materials
        export_colors=True,
        export_attributes=True,
        #use_mesh_edges
        #use_mesh_vertices
        export_cameras=True,
        export_extras=True, # For custom exported properties.
        export_lights=True,
        export_yup=False,
        export_skins=True,
        export_morph=False,
        export_apply=False,
        export_animations=False
    )
        
    for key in addon_prefs.__annotations__.keys():
        if key is not "export_game" and key is not "export_game_scene_name" and key is not "export_game_output_name": #FIXME: ugh, cleanup
            gltf_export_preferences[key] = getattr(addon_prefs,key)
            print("overriding setting", key, "value", getattr(addon_prefs,key))

    # testing (we want an in-memory scene, not one that is visible in the ui)
    #invisible_scene = bpy.types.Scene("foo")


    # export the library 
    #export_library_split(library_scene, folder_path)
    #export_library_merged(library_scene, folder_path, gltf_export_preferences)

    # export the main game world
    # export_main(game_scene, folder_path, gltf_export_preferences)

    export_game = getattr(addon_prefs,"export_game")
    export_game_scene_name = getattr(addon_prefs,"export_game_scene_name")
    export_game_output_name = getattr(addon_prefs,"export_game_output_name")

    print("exporting ??", export_game, export_game_scene_name, export_game_output_name)
    print("last changed", bpy.context.scene.changedScene)
    # optimised variation
    last_changed = bpy.context.scene.changedScene #get_changedScene()
    if last_changed == export_game_scene_name:
         # export the main game world
        if export_game:
            game_scene = bpy.data.scenes[export_game_scene_name]

            print("game world changed, exporting game gltf only")
            export_main(game_scene, folder_path, gltf_export_preferences, export_game_output_name)
    if last_changed == "library": # if the library has changed, so will likely the game world that uses the library assets
        print("library changed, exporting both game & library gltf")
        # export the library 
        # export_library_merged(library_scene, folder_path, gltf_export_preferences)
        # export the main game world
        if export_game:
            game_scene = bpy.data.scenes[export_game_scene_name]
            export_main(game_scene, folder_path, gltf_export_preferences, export_game_output_name)

    return {'FINISHED'}

    

@persistent
def save_handler(dummy): 
    print("-------------")
    print("saved", bpy.data.filepath)
    auto_export()


def get_changedScene(self):
    return self["changedScene"]


def set_ChangedScene(self, value):
    self["changedScene"] = value

class AutoExportGltfAddonPreferences(AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__

    export_format: EnumProperty(
        name='Format',
        items=(('GLB', 'glTF Binary (.glb)',
                'Exports a single file, with all data packed in binary form. '
                'Most efficient and portable, but more difficult to edit later'),
               ('GLTF_EMBEDDED', 'glTF Embedded (.gltf)',
                'Exports a single file, with all data packed in JSON. '
                'Less efficient than binary, but easier to edit later'),
               ('GLTF_SEPARATE', 'glTF Separate (.gltf + .bin + textures)',
                'Exports multiple files, with separate JSON, binary and texture data. '
                'Easiest to edit later')),
        description=(
            'Output format and embedding options. Binary is most efficient, '
            'but JSON (embedded or separate) may be easier to edit later'
        ),
        default='GLB'
    )

    export_game: BoolProperty(
        name='Export world/level',
        description='Export world/level into a seperate gltf file',
        default=False
    )
    export_game_scene_name: StringProperty(
        name='Scene to auto export',
        description='The name of the main scene/level/world to auto export',
        default='world'
    )
    export_game_output_name: StringProperty(
        name='Glb output name',
        description='The glb output name for the main scene to auto export',
        default='world'
    )

    export_copyright: StringProperty(
        name='Copyright',
        description='Legal rights and conditions for the model',
        default=''
    )

    export_image_format: EnumProperty(
        name='Images',
        items=(('AUTO', 'Automatic',
                'Save PNGs as PNGs and JPEGs as JPEGs. '
                'If neither one, use PNG'),
                ('JPEG', 'JPEG Format (.jpg)',
                'Save images as JPEGs. (Images that need alpha are saved as PNGs though.) '
                'Be aware of a possible loss in quality'),
                ('NONE', 'None',
                 'Don\'t export images'),
               ),
        description=(
            'Output format for images. PNG is lossless and generally preferred, but JPEG might be preferable for web '
            'applications due to the smaller file size. Alternatively they can be omitted if they are not needed'
        ),
        default='AUTO'
    )

    export_texture_dir: StringProperty(
        name='Textures',
        description='Folder to place texture files in. Relative to the .gltf file',
        default='',
    )

    """
    export_jpeg_quality: IntProperty(
        name='JPEG quality',
        description='Quality of JPEG export',
        default=75,
        min=0,
        max=100
    )
    """

    export_keep_originals: BoolProperty(
        name='Keep original',
        description=('Keep original textures files if possible. '
                     'WARNING: if you use more than one texture, '
                     'where pbr standard requires only one, only one texture will be used. '
                     'This can lead to unexpected results'
        ),
        default=False,
    )

    export_texcoords: BoolProperty(
        name='UVs',
        description='Export UVs (texture coordinates) with meshes',
        default=True
    )

    export_normals: BoolProperty(
        name='Normals',
        description='Export vertex normals with meshes',
        default=True
    )

    export_draco_mesh_compression_enable: BoolProperty(
        name='Draco mesh compression',
        description='Compress mesh using Draco',
        default=False
    )

    export_draco_mesh_compression_level: IntProperty(
        name='Compression level',
        description='Compression level (0 = most speed, 6 = most compression, higher values currently not supported)',
        default=6,
        min=0,
        max=10
    )

    export_draco_position_quantization: IntProperty(
        name='Position quantization bits',
        description='Quantization bits for position values (0 = no quantization)',
        default=14,
        min=0,
        max=30
    )

    export_draco_normal_quantization: IntProperty(
        name='Normal quantization bits',
        description='Quantization bits for normal values (0 = no quantization)',
        default=10,
        min=0,
        max=30
    )

    export_draco_texcoord_quantization: IntProperty(
        name='Texcoord quantization bits',
        description='Quantization bits for texture coordinate values (0 = no quantization)',
        default=12,
        min=0,
        max=30
    )

    export_draco_color_quantization: IntProperty(
        name='Color quantization bits',
        description='Quantization bits for color values (0 = no quantization)',
        default=10,
        min=0,
        max=30
    )

    export_draco_generic_quantization: IntProperty(
        name='Generic quantization bits',
        description='Quantization bits for generic coordinate values like weights or joints (0 = no quantization)',
        default=12,
        min=0,
        max=30
    )

    export_tangents: BoolProperty(
        name='Tangents',
        description='Export vertex tangents with meshes',
        default=False
    )

    export_materials: EnumProperty(
        name='Materials',
        items=(('EXPORT', 'Export',
        'Export all materials used by included objects'),
        ('PLACEHOLDER', 'Placeholder',
        'Do not export materials, but write multiple primitive groups per mesh, keeping material slot information'),
        ('NONE', 'No export',
        'Do not export materials, and combine mesh primitive groups, losing material slot information')),
        description='Export materials',
        default='EXPORT'
    )

    export_original_specular: BoolProperty(
        name='Export original PBR Specular',
        description=(
            'Export original glTF PBR Specular, instead of Blender Principled Shader Specular'
        ),
        default=False,
    )

    export_colors: BoolProperty(
        name='Vertex Colors',
        description='Export vertex colors with meshes',
        default=True
    )

    export_attributes: BoolProperty(
        name='Attributes',
        description='Export Attributes (when starting with underscore)',
        default=False
    )

    use_mesh_edges: BoolProperty(
        name='Loose Edges',
        description=(
            'Export loose edges as lines, using the material from the first material slot'
        ),
        default=False,
    )

    use_mesh_vertices: BoolProperty(
        name='Loose Points',
        description=(
            'Export loose points as glTF points, using the material from the first material slot'
        ),
        default=False,
    )

    export_cameras: BoolProperty(
        name='Cameras',
        description='Export cameras',
        default=True
    )

    use_selection: BoolProperty(
        name='Selected Objects',
        description='Export selected objects only',
        default=False
    )

    use_visible: BoolProperty(
        name='Visible Objects',
        description='Export visible objects only',
        default=True
    )

    use_renderable: BoolProperty(
        name='Renderable Objects',
        description='Export renderable objects only',
        default=False
    )


    export_apply: BoolProperty(
        name='Export Apply Modifiers',
        description='Apply modifiers (excluding Armatures) to mesh objects -'
                    'WARNING: prevents exporting shape keys',
        default=True
    )

    export_yup: BoolProperty(
        name='+Y Up',
        description='Export using glTF convention, +Y up',
        default=False
    )

    use_visible: BoolProperty(
        name='Visible Objects',
        description='Export visible objects only',
        default=False
    )

    use_renderable: BoolProperty(
        name='Renderable Objects',
        description='Export renderable objects only',
        default=False
    )

    export_extras: BoolProperty(
        name='Custom Properties',
        description='Export custom properties as glTF extras',
        default=True
    )

    export_animations: BoolProperty(
        name='Animations',
        description='Exports active actions and NLA tracks as glTF animations',
        default=False
    )





class TEST_AUTO_OT_gltf(Operator, ExportHelper):
    """test"""
    bl_idname = "export_scenes.auto_gltf"
    bl_label = "Apply settings"
    bl_options = {'PRESET', 'UNDO'}

    # ExportHelper mixin class uses this
    filename_ext = ''

    filter_glob: StringProperty(
            default='*.glb;*.gltf', 
            options={'HIDDEN'}
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator setting before calling.
    
    def draw(self, context):
        layout = self.layout
        preferences = context.preferences
        addon_prefs = preferences.addons[__name__].preferences

        # print("KEYS", dir(addon_prefs))
        #print("BLAS", addon_prefs.__annotations__)
        #print(addon_prefs.__dict__)
        for key in addon_prefs.__annotations__.keys():
            layout.prop(addon_prefs, key)
            #print("key", key)


    #def __init__(self):
    #    print("initializing my magic foo")

    def execute(self, context):     
        preferences = context.preferences

        #print("preferences", preferences.addons, __name__)
        addon_prefs = preferences.addons[__name__].preferences

        #print("addon prefs", addon_prefs)
        #info = ("Path: %s, Number: %d, Boolean %r" %
        #        (addon_prefs.filepath, addon_prefs.number, addon_prefs.boolean))
  
        #self.report({'INFO'}, info)
        #print(info)

        print("CHGANGED color", self)
        return {'FINISHED'}    



# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(TEST_AUTO_OT_gltf.bl_idname, text="glTF auto Export (.glb/gltf)")

classes = [TEST_AUTO_OT_gltf, AutoExportGltfAddonPreferences]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    #bpy.types.Scene.my_tool = bpy.props.PointerProperty(type=My_Settings)  
    #CollectionProperty   

    bpy.types.TOPBAR_MT_file_export.append(menu_func_import)

    bpy.app.handlers.depsgraph_update_post.append(deps_update_handler)
    bpy.app.handlers.save_post.append(save_handler)

    #bpy.types.TOPBAR_MT_file_export.append(menu_func_import)
    bpy.types.Scene.changedScene = bpy.props.StringProperty(get=get_changedScene, set=set_ChangedScene)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.TOPBAR_MT_file_export.remove(menu_func_import)

    bpy.app.handlers.depsgraph_update_post.remove(deps_update_handler)
    bpy.app.handlers.save_post.remove(save_handler)
    #bpy.types.TOPBAR_MT_file_export.remove(menu_func_import)
    del bpy.types.Scene.changedScene
    #del bpy.types.Scene.my_tool

if __name__ == "__main__":
    register()