use bevy::prelude::*;

use bevy::pbr::{CascadeShadowConfig, CascadeShadowConfigBuilder};

pub fn lighting_replace_proxies(
    mut added_dirights: Query<(Entity, &mut DirectionalLight), Added<DirectionalLight>>,
    mut added_spotlights: Query<&mut SpotLight, Added<SpotLight>>,
    mut added_pointlights: Query<&mut PointLight, Added<PointLight>>,

    mut commands: Commands,
) {
    for (entity, mut light) in added_dirights.iter_mut() {
        light.illuminance *= 5.0;
        light.shadows_enabled = true;
        let shadow_config: CascadeShadowConfig = CascadeShadowConfigBuilder {
            first_cascade_far_bound: 15.0,
            maximum_distance: 135.0,
            ..default()
        }
        .into();
        commands.entity(entity).insert(shadow_config);
    }
    for mut light in added_spotlights.iter_mut() {
        light.shadows_enabled = true;
    }

    for mut light in added_pointlights.iter_mut() {
        light.intensity *= 0.001; // arbitrary/ eyeballed to match the levels of Blender
        light.shadows_enabled = true;
    }
}
