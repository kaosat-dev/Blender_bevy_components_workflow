use bevy::prelude::*;

#[derive(Component, Reflect, Debug, Default)]
#[reflect(Component)]
pub struct Dynamic(pub bool);
