use bevy::{gltf::Gltf, prelude::*};
use bevy_gltf_worlflow_examples_common_rapier::{
    assets::GameAssets, GameState, InAppRunning, Player,
};
use bevy_rapier3d::prelude::*;
use blenvy::GameWorldTag;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct LevelTransition {
    pub target: String,
}

// very barebones example of triggering level transitions
#[allow(clippy::too_many_arguments)]
pub fn trigger_level_transition(
    mut collision_events: EventReader<CollisionEvent>,
    level_transition_triggers: Query<&LevelTransition>,
    parents: Query<&Parent>,
    players: Query<&Player>,

    mut commands: Commands,

    game_assets: Res<GameAssets>,
    models: Res<Assets<bevy::gltf::Gltf>>,
    game_world: Query<(Entity, &GameWorldTag)>,
) {
    for collision_event in collision_events.read() {
        match collision_event {
            CollisionEvent::Started(entity1, entity2, _) => {
                // we need to accomodate for the fact that the collider may be a child of the level transition (FIXME: is this a missunderstanding on my part about rapier child colliders ?)
                let entity1_parent = parents.get(*entity1).unwrap();
                let entity2_parent = parents.get(*entity2).unwrap();

                if level_transition_triggers.get(*entity1).is_ok()
                    || level_transition_triggers.get(*entity2).is_ok()
                    || level_transition_triggers.get(entity1_parent.get()).is_ok()
                    || level_transition_triggers.get(entity2_parent.get()).is_ok()
                {
                    println!("collision started, we can transition to level");
                    let transition_trigger;
                    if level_transition_triggers.get(*entity1).is_ok() {
                        transition_trigger = level_transition_triggers.get(*entity1).unwrap();
                    } else if level_transition_triggers.get(*entity2).is_ok() {
                        transition_trigger = level_transition_triggers.get(*entity2).unwrap();
                    } else if level_transition_triggers.get(entity1_parent.get()).is_ok() {
                        transition_trigger =
                            level_transition_triggers.get(entity1_parent.get()).unwrap();
                    } else {
                        transition_trigger =
                            level_transition_triggers.get(entity2_parent.get()).unwrap();
                    }

                    if players.get(*entity1).is_ok()
                        || players.get(entity1_parent.get()).is_ok()
                        || players.get(*entity2).is_ok()
                        || players.get(entity2_parent.get()).is_ok()
                    {
                        println!("one entity is the player, we can enter")
                    } else {
                        // if none of our entities is a player, bail out, as only entities with player components should trigger a transition
                        return;
                    }

                    let current_game_world = game_world.single();

                    // remove current level/world
                    info!("despawning current level");
                    commands.entity(current_game_world.0).despawn_recursive();

                    let target_level = &transition_trigger.target;
                    let level: Handle<Gltf>;
                    println!("target level {}", target_level);
                    if target_level == "Level1" {
                        level = game_assets.level1.clone().unwrap();
                    } else if target_level == "Level2" {
                        level = game_assets.level2.clone().unwrap();
                    } else {
                        level = game_assets.world.clone().unwrap();
                    }
                    info!("spawning new level");
                    commands.spawn((
                        SceneBundle {
                            // note: because of this issue https://github.com/bevyengine/bevy/issues/10436, "world" is now a gltf file instead of a scene
                            scene: models
                                .get(level.id())
                                .expect("main level should have been loaded")
                                .scenes[0]
                                .clone(),
                            ..default()
                        },
                        bevy::prelude::Name::from("world"),
                        GameWorldTag,
                        InAppRunning,
                    ));
                }
            }
            CollisionEvent::Stopped(_entity1, _entity2, _) => {
                // println!("collision ended")
            }
        }
    }
}

pub struct LevelsPlugin;
impl Plugin for LevelsPlugin {
    fn build(&self, app: &mut App) {
        app.register_type::<LevelTransition>().add_systems(
            Update,
            (trigger_level_transition,).run_if(in_state(GameState::InGame)),
        );
    }
}
