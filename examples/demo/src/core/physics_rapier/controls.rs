use bevy::{
    ecs::system::Res,
    input::{keyboard::KeyCode, ButtonInput},
    log::info,
    prelude::ResMut,
};
use bevy_rapier3d::{prelude::RapierConfiguration, render::DebugRenderContext};

pub(crate) fn pause_physics(mut physics_config: ResMut<RapierConfiguration>) {
    info!("pausing physics");
    physics_config.physics_pipeline_active = false;
}

pub(crate) fn resume_physics(mut physics_config: ResMut<RapierConfiguration>) {
    info!("unpausing physics");
    physics_config.physics_pipeline_active = true;
}

pub(crate) fn toggle_physics_debug(
    mut debug_config: ResMut<DebugRenderContext>,
    keycode: Res<ButtonInput<KeyCode>>,
) {
    if keycode.just_pressed(KeyCode::KeyD) {
        debug_config.enabled = !debug_config.enabled;
    }
}
