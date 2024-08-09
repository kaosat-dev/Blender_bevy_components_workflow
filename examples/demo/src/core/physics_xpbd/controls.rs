use bevy::ecs::system::Res;
use bevy::gizmos::config::GizmoConfigStore;
use bevy::input::keyboard::KeyCode;
use bevy::input::ButtonInput;
use bevy::log::info;
use bevy::{prelude::ResMut, time::Time};

use bevy_xpbd_3d::prelude::Physics;
use bevy_xpbd_3d::prelude::*;

pub(crate) fn pause_physics(mut time: ResMut<Time<Physics>>) {
    info!("pausing physics");
    time.pause();
}

pub(crate) fn resume_physics(mut time: ResMut<Time<Physics>>) {
    info!("unpausing physics");
    time.unpause();
}

pub(crate) fn toggle_physics_debug(
    mut config_store: ResMut<GizmoConfigStore>,
    keycode: Res<ButtonInput<KeyCode>>,
) {
    if keycode.just_pressed(KeyCode::KeyD) {
        let config = config_store.config_mut::<PhysicsGizmos>().0;
        config.enabled = !config.enabled;
        // config.aabb_color = Some(Color::WHITE);
    }
}
