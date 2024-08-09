use bevy::core_pipeline::bloom::{BloomCompositeMode, BloomSettings};
use bevy::core_pipeline::experimental::taa::TemporalAntiAliasBundle;
use bevy::core_pipeline::tonemapping::{DebandDither, Tonemapping};
use bevy::pbr::ScreenSpaceAmbientOcclusionBundle;
use bevy::prelude::*;
use bevy::render::camera::Exposure;

use super::CameraTrackingOffset;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct SSAOSettings;

#[allow(clippy::type_complexity)]
pub fn camera_replace_proxies(
    mut commands: Commands,
    mut added_cameras: Query<
        (
            Entity,
            &mut Camera,
            &mut Exposure,
            Option<&BloomSettings>,
            Option<&SSAOSettings>,
        ),
        (Added<Camera>, With<CameraTrackingOffset>),
    >,

    added_bloom_settings: Query<&BloomSettings, Added<BloomSettings>>,
    added_ssao_settings: Query<&SSAOSettings, Added<SSAOSettings>>, // Move to camera
) {
    for (entity, mut camera, mut exposure, bloom_settings, ssao_setting) in added_cameras.iter_mut()
    {
        info!("detected added camera, updating proxy");
        camera.hdr = true;
        exposure.ev100 *= 1.0;
        commands
            .entity(entity)
            .insert(DebandDither::Enabled)
            .insert(Tonemapping::BlenderFilmic);

        // we only inject the scene_level bloom settings if there are no settings already on the Camera
        if bloom_settings.is_none() {
            for bloom_settings in added_bloom_settings.iter() {
                commands.entity(entity).insert(BloomSettings {
                    intensity: bloom_settings.intensity,
                    composite_mode: BloomCompositeMode::Additive,
                    ..default()
                });
            }
        }

        if ssao_setting.is_none() {
            for _ in added_ssao_settings.iter() {
                commands.insert_resource(Msaa::Off); // when using SSAO, you cannot use Msaa

                commands
                    .entity(entity)
                    .insert(ScreenSpaceAmbientOcclusionBundle::default())
                    .insert(TemporalAntiAliasBundle::default());
            }
        }
    }
}
