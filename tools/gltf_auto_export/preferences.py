
from bpy.types import AddonPreferences

from bpy.props import (BoolProperty,
                       IntProperty,
                       StringProperty,
                       EnumProperty,
                       CollectionProperty
                       )

from .internals import (CUSTOM_PG_sceneName)

AutoExportGltfPreferenceNames = [
    'auto_export',
    'export_main_scene_name',
    'export_output_folder',
    'export_library_scene_name',

    'export_blueprints',
    'export_blueprints_path',

    'export_marked_assets',
    'collection_instances_combine_mode',
    'split_out_dynamic_collections',

    'export_materials_library',
    'export_materials_path',

    'export_scene_settings',

    'main_scenes',
    'library_scenes',
    'main_scenes_index',
    'library_scenes_index'
]

class AutoExportGltfAddonPreferences(AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__
    bl_options = {'PRESET'}

    auto_export: BoolProperty(
        name='Auto export',
        description='Automatically export to gltf on save',
        default=True
    )
    export_main_scene_name: StringProperty(
        name='Main scene',
        description='The name of the main scene/level/world to auto export',
        default='Scene'
    )
    export_output_folder: StringProperty(
        name='Export folder (relative)',
        description='The root folder for all exports(relative to current file) Defaults to current folder',
        default=''
    )
    export_library_scene_name: StringProperty(
        name='Library scene',
        description='The name of the library scene to auto export',
        default='Library'
    )
    # scene components
    export_scene_settings: BoolProperty(
        name='Export scene settings',
        description='Export scene settings ie AmbientLighting, Bloom, AO etc',
        default=False
    )

    # blueprint settings
    export_blueprints: BoolProperty(
        name='Export Blueprints',
        description='Replaces collection instances with an Empty with a BlueprintName custom property',
        default=True
    )
    export_blueprints_path: StringProperty(
        name='Blueprints path',
        description='path to export the blueprints to (relative to the Export folder)',
        default='library'
    )

    export_materials_library: BoolProperty(
        name='Export materials library',
        description='remove materials from blueprints and use the material library instead',
        default=False
    )
    export_materials_path: StringProperty(
        name='Materials path',
        description='path to export the materials libraries to (relative to the root folder)',
        default='materials'
    )

    """ combine mode can be 
              - 'Split' (default): replace with an empty, creating links to sub blueprints 
              - 'Embed' : treat it as an embeded object and do not replace it with an empty
              - 'EmbedExternal': embed any instance of a non local collection (ie external assets)

              - 'Inject': inject components from sub collection instances into the curent object => this is now a seperate custom property that you can apply to a collecion instance
            """

    collection_instances_combine_mode : EnumProperty(
        name='Collection instances',
        items=(
           ('Split', 'Split', 'replace collection instances with an empty + blueprint, creating links to sub blueprints (Default, Recomended)'),
           ('Embed', 'Embed', 'treat collection instances as embeded objects and do not replace them with an empty'),
           ('EmbedExternal', 'EmbedExternal', 'treat instances of external (not specifified in the current blend file) collections (aka assets etc) as embeded objects and do not replace them with empties'),
           #('Inject', 'Inject', 'inject components from sub collection instances into the curent object')
        ),
        default='Split'
    )

    export_marked_assets: BoolProperty(
        name='Auto export marked assets',
        description='Collections that have been marked as assets will be systematically exported, even if not in use in another scene',
        default=True
    )

    split_out_dynamic_collections: BoolProperty(
        name='Split out dynamic collections',
        description='For MAIN scenes only (aka levels), toggle this to extract & export any collection or instance marked as dynamic (aka saveable aka mutable)',
        default=True
    )


    main_scenes: CollectionProperty(name="main scenes", type=CUSTOM_PG_sceneName)
    main_scenes_index: IntProperty(name = "Index for main scenes list", default = 0)

    library_scenes: CollectionProperty(name="library scenes", type=CUSTOM_PG_sceneName)
    library_scenes_index: IntProperty(name = "Index for library scenes list", default = 0)

    #####
    export_format: EnumProperty(
        name='Format',
        items=(
            ('GLB', 'glTF Binary (.glb)',
                'Exports a single file, with all data packed in binary form. '
                'Most efficient and portable, but more difficult to edit later'),
               ('GLTF_SEPARATE', 'glTF Separate (.gltf + .bin + textures)',
                'Exports multiple files, with separate JSON, binary and texture data. '
                'Easiest to edit later')
                ),
        description=(
            'Output format and embedding options. Binary is most efficient, '
            'but JSON (embedded or separate) may be easier to edit later'
        ),
        default='GLB'
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
        default=True
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
