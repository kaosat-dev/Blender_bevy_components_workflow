mod lighting_replace_proxies;
use lighting_replace_proxies::*;

use bevy::pbr::{DirectionalLightShadowMap, NotShadowCaster};
use bevy::prelude::*;

pub struct LightingPlugin;
impl Plugin for LightingPlugin {
    fn build(&self, app: &mut App) {
        app
        .insert_resource(DirectionalLightShadowMap { size: 4096 })
         // FIXME: adding these since they are missing
        .register_type::<NotShadowCaster>()

        .add_systems(PreUpdate, lighting_replace_proxies) // FIXME: you should actually run this in a specific state most likely
      ;
    }
}
