use bevy::core_pipeline::tonemapping::Tonemapping;
use bevy::pbr::DirectionalLightShadowMap;
use bevy::prelude::*;
use bevy::render::view::{ColorGrading, ColorGradingGlobal, ColorGradingSection};

use crate::GltfComponentsSet;

pub(crate) fn plugin(app: &mut App) {
    app.register_type::<BlenderBackgroundShader>()
        .register_type::<BlenderShadowSettings>()
        .register_type::<BlenderLightShadows>()
        .register_type::<BlenderToneMapping>()
        .register_type::<BlenderColorGrading>()
        .add_systems(
            Update,
            (
                process_lights,
                process_shadowmap,
                process_background_shader,
                process_tonemapping,
                process_colorgrading,
            )
                .after(GltfComponentsSet::Injection),
        );
}

#[derive(Component, Reflect, Default, Debug, PartialEq, Clone)]
#[reflect(Component)]
#[non_exhaustive]
/// The properties of a light's shadow , to enable controlling per light shadows from Blender
pub struct BlenderLightShadows {
    pub enabled: bool,
    pub buffer_bias: f32,
}

/// The background color as described by Blender's [background shader](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/background.html).
#[derive(Component, Reflect, Default, Debug, PartialEq, Clone)]
#[reflect(Component)]
#[non_exhaustive]
pub struct BlenderBackgroundShader {
    pub color: Color,
    pub strength: f32,
}

/// The settings used by EEVEE's [shadow rendering](https://docs.blender.org/manual/en/latest/render/eevee/render_settings/shadows.html).
#[derive(Component, Reflect, Default, Debug, PartialEq, Clone)]
#[reflect(Component)]
#[non_exhaustive]
pub struct BlenderShadowSettings {
    pub cascade_size: usize,
}

/// Not all possible Blender `ToneMappings` are available in Bevy & vice versa
#[derive(Component, Reflect, Default, Debug, PartialEq, Clone)]
#[reflect(Component)]
#[non_exhaustive]
pub enum BlenderToneMapping {
    #[default]
    None,
    AgX,
    Filmic,
}

#[derive(Component, Reflect, Default, Debug, PartialEq, Clone)]
#[reflect(Component)]
#[non_exhaustive]
pub struct BlenderColorGrading {
    exposure: f32,
    gamma: f32,
}

fn process_lights(
    mut directional_lights: Query<
        (&mut DirectionalLight, Option<&BlenderLightShadows>),
        Added<DirectionalLight>,
    >,
    mut spot_lights: Query<(&mut SpotLight, Option<&BlenderLightShadows>), Added<SpotLight>>,
    mut point_lights: Query<(&mut PointLight, Option<&BlenderLightShadows>), Added<PointLight>>,
) {
    for (mut light, blender_light_shadows) in directional_lights.iter_mut() {
        if let Some(blender_light_shadows) = blender_light_shadows {
            light.shadows_enabled = blender_light_shadows.enabled;
        }
    }
    for (mut light, blender_light_shadows) in spot_lights.iter_mut() {
        if let Some(blender_light_shadows) = blender_light_shadows {
            light.shadows_enabled = blender_light_shadows.enabled;
        }
    }

    for (mut light, blender_light_shadows) in point_lights.iter_mut() {
        if let Some(blender_light_shadows) = blender_light_shadows {
            light.shadows_enabled = blender_light_shadows.enabled;
        }
    }
}

fn process_shadowmap(
    shadowmaps: Query<&BlenderShadowSettings, Added<BlenderShadowSettings>>,
    mut commands: Commands,
) {
    for shadowmap in shadowmaps.iter() {
        commands.insert_resource(DirectionalLightShadowMap {
            size: shadowmap.cascade_size,
        });
    }
}

fn process_background_shader(
    background_shaders: Query<&BlenderBackgroundShader, Added<BlenderBackgroundShader>>,
    mut commands: Commands,
) {
    for background_shader in background_shaders.iter() {
        commands.insert_resource(AmbientLight {
            color: background_shader.color,
            // Just a guess, see <https://github.com/bevyengine/bevy/issues/12280>
            brightness: background_shader.strength * 400.0,
        });
        commands.insert_resource(ClearColor(background_shader.color));
    }
}

// FIXME: this logic should not depend on if toneMapping or Cameras where added first
fn process_tonemapping(
    tonemappings: Query<(Entity, &BlenderToneMapping), Added<BlenderToneMapping>>,
    cameras: Query<Entity, With<Camera>>,
    mut commands: Commands,
) {
    for entity in cameras.iter() {
        for (scene_id, tone_mapping) in tonemappings.iter() {
            match tone_mapping {
                BlenderToneMapping::None => {
                    //println!("TONEMAPPING NONE");
                    commands.entity(entity).remove::<Tonemapping>();
                }
                BlenderToneMapping::AgX => {
                    //println!("TONEMAPPING Agx");
                    commands.entity(entity).insert(Tonemapping::AgX);
                }
                BlenderToneMapping::Filmic => {
                    //println!("TONEMAPPING Filmic");
                    commands.entity(entity).insert(Tonemapping::BlenderFilmic);
                }
            }
            commands.entity(scene_id).remove::<BlenderToneMapping>();
        }
    }
}

// FIXME: this logic should not depend on if toneMapping or Cameras where added first
fn process_colorgrading(
    blender_colorgradings: Query<(Entity, &BlenderColorGrading), Added<BlenderColorGrading>>,
    cameras: Query<Entity, With<Camera>>,
    mut commands: Commands,
) {
    for entity in cameras.iter() {
        for (scene_id, blender_colorgrading) in blender_colorgradings.iter() {
            info!("COLOR GRADING");
            commands.entity(entity).insert(ColorGrading {
                global: ColorGradingGlobal {
                    exposure: blender_colorgrading.exposure,
                    ..Default::default()
                },
                shadows: ColorGradingSection {
                    gamma: blender_colorgrading.gamma,
                    ..Default::default()
                },
                midtones: ColorGradingSection {
                    gamma: blender_colorgrading.gamma,
                    ..Default::default()
                },
                highlights: ColorGradingSection {
                    gamma: blender_colorgrading.gamma,
                    ..Default::default()
                },

                ..Default::default()
            });
            commands.entity(scene_id).remove::<ColorGrading>();
        }
    }
}
