def upsert_scene_components(level_scenes):
    for scene in level_scenes:
        if scene.world is not None:
            scene['BlenderBackgroundShader'] = ambient_color_to_component(scene.world)
        scene['BlenderShadowSettings'] = scene_shadows_to_component(scene)

        if scene.eevee.use_bloom:
            scene['BloomSettings'] = scene_bloom_to_component(scene)
        elif 'BloomSettings' in scene:
            del scene['BloomSettings']

        if scene.eevee.use_gtao: 
            scene['SSAOSettings'] = scene_ao_to_component(scene)
        elif 'SSAOSettings' in scene:
            del scene['SSAOSettings']

        scene['BlenderToneMapping'] = scene_tonemapping_to_component(scene)
        scene['BlenderColorGrading'] = scene_colorgrading_to_component(scene)

def remove_scene_components(level_scenes):
    pass

def scene_tonemapping_to_component(scene):
    tone_mapping =  scene.view_settings.view_transform
    blender_to_bevy = {
        'NONE': 'None',
        'AgX': 'AgX',
        'Filmic': 'Filmic',
    }
    bevy_tone_mapping = blender_to_bevy[tone_mapping] if tone_mapping in blender_to_bevy else 'None'
    return bevy_tone_mapping

def scene_colorgrading_to_component(scene):
    return f"(exposure: {scene.view_settings.exposure}, gamma: {scene.view_settings.gamma})"


def ambient_color_to_component(world):
    color = None
    strength = None
    try:
        color = world.node_tree.nodes['Background'].inputs[0].default_value
        strength = world.node_tree.nodes['Background'].inputs[1].default_value
    except Exception as ex:
        print("failed to parse ambient color: Only background is supported")
   
    if color is not None and strength is not None:
        colorRgba = f"LinearRgba((red: {color[0]}, green: {color[1]}, blue: {color[2]}, alpha: {color[3]}))"
        component = f"( color: {colorRgba}, strength: {strength})"
        return component
    return None

def scene_shadows_to_component(scene):
    cascade_size = scene.eevee.shadow_cascade_size
    component = f"(cascade_size: {cascade_size})"
    return component

def scene_bloom_to_component(scene):
    component = f"BloomSettings(intensity: {scene.eevee.bloom_intensity})"
    return component

def scene_ao_to_component(scene):
    ssao = scene.eevee.use_gtao
    component= "SSAOSettings()"
    return component
