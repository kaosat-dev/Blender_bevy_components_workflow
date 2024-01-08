use bevy::prelude::{info, ResMut};
use bevy_rapier3d::prelude::RapierConfiguration;

pub fn pause_physics(mut physics_config: ResMut<RapierConfiguration>) {
    info!("pausing physics");
    physics_config.physics_pipeline_active = false;
}

pub fn resume_physics(mut physics_config: ResMut<RapierConfiguration>) {
    info!("unpausing physics");
    physics_config.physics_pipeline_active = true;
}
