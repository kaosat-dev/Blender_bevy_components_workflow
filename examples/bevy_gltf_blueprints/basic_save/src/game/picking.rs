use super::Player;
use bevy::prelude::*;
use bevy_gltf_blueprints::GltfBlueprintsSet;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct Pickable;

// very simple, crude picking (as in picking up objects) implementation

pub fn picking(
    players: Query<&GlobalTransform, With<Player>>,
    pickables: Query<(Entity, &GlobalTransform), With<Pickable>>,
    mut commands: Commands,
) {
    for player_transforms in players.iter() {
        for (pickable, pickable_transforms) in pickables.iter() {
            let distance = player_transforms
                .translation()
                .distance(pickable_transforms.translation());
            if distance < 2.5 {
                commands.entity(pickable).despawn_recursive();
            }
        }
    }
}

pub struct PickingPlugin;
impl Plugin for PickingPlugin {
    fn build(&self, app: &mut App) {
        app.register_type::<Pickable>()
            .add_systems(Update, (picking.after(GltfBlueprintsSet::AfterSpawn),));
    }
}
