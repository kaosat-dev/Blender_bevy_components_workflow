use bevy::core_pipeline::bloom::{BloomCompositeMode, BloomSettings};
use bevy::core_pipeline::tonemapping::{DebandDither, Tonemapping};
use bevy::prelude::*;

use super::CameraTrackingOffset;

pub fn camera_replace_proxies(
    mut commands: Commands,
    mut added_cameras: Query<(Entity, &mut Camera), (Added<Camera>, With<CameraTrackingOffset>)>,
) {
    for (entity, mut camera) in added_cameras.iter_mut() {
        info!("detected added camera, updating proxy");
        camera.hdr = true;
        commands
            .entity(entity)
            .insert(DebandDither::Enabled)
            .insert(Tonemapping::BlenderFilmic)
            .insert(BloomSettings {
                intensity: 0.01,
                composite_mode: BloomCompositeMode::Additive,
                ..default()
            });
    }
}
