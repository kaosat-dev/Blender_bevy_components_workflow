use std::time::Duration;

use bevy::prelude::*;
use blenvy::{
    AddToGameWorld, BlenvyPlugin, BluePrintBundle, BlueprintAnimationPlayerLink,
    BlueprintAnimations, BlueprintInfo, DynamicBlueprintInstance, GameWorldTag, HideUntilReady,
    SpawnBlueprint,
};
use rand::Rng;

mod component_examples;
use component_examples::*;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// Demo marker component
pub struct Player;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// Demo marker component
pub struct Fox;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// Demo marker component
pub struct Robot;

fn main() {
    App::new()
        .add_plugins((
            DefaultPlugins.set(AssetPlugin::default()),
            // our custom plugins
            ComponentsExamplesPlugin, // Showcases different type of components /structs
            BlenvyPlugin::default(),
        ))
        .register_type::<Player>()
        .register_type::<Fox>()
        .register_type::<Robot>()
        .add_systems(Startup, setup_game)
        .add_systems(Update, (animation_control,))
        .run();
}

// this is how you setup & spawn a level from a blueprint
fn setup_game(mut commands: Commands) {
    // here we actually spawn our game world/level
    commands.spawn((
        BlueprintInfo::from_path("levels/World.glb"), // all we need is a Blueprint info...
        SpawnBlueprint, // and spawnblueprint to tell blenvy to spawn the blueprint now
        HideUntilReady, // only reveal the level once it is ready
        GameWorldTag,
    ));
}

//////////////////////////////////

pub fn animation_control(
    animated_robots: Query<(&BlueprintAnimationPlayerLink, &BlueprintAnimations), With<Robot>>,
    animated_foxes: Query<(&BlueprintAnimationPlayerLink, &BlueprintAnimations), With<Fox>>,

    mut animation_players: Query<(&mut AnimationPlayer, &mut AnimationTransitions)>,

    keycode: Res<ButtonInput<KeyCode>>,
    // mut entities_with_animations : Query<(&mut AnimationPlayer, &mut BlueprintAnimations)>,
) {
    // robots
    if keycode.just_pressed(KeyCode::KeyB) {
        println!("scan animation for robots");
        for (link, animations) in animated_robots.iter() {
            let (mut animation_player, mut animation_transitions) =
                animation_players.get_mut(link.0).unwrap();
            println!("got some animations");
            let anim_name = "Scan";
            animation_transitions
                .play(
                    &mut animation_player,
                    animations
                        .named_indices
                        .get(anim_name)
                        .expect("animation name should be in the list")
                        .clone(),
                    Duration::from_secs(5),
                )
                .repeat();
        }
    }

    // foxes
    if keycode.just_pressed(KeyCode::KeyW) {
        for (link, animations) in animated_foxes.iter() {
            let (mut animation_player, mut animation_transitions) =
                animation_players.get_mut(link.0).unwrap();

            let anim_name = "Walk";
            animation_transitions
                .play(
                    &mut animation_player,
                    animations
                        .named_indices
                        .get(anim_name)
                        .expect("animation name should be in the list")
                        .clone(),
                    Duration::from_secs(5),
                )
                .repeat();
        }
    }

    if keycode.just_pressed(KeyCode::KeyX) {
        for (link, animations) in animated_foxes.iter() {
            let (mut animation_player, mut animation_transitions) =
                animation_players.get_mut(link.0).unwrap();

            let anim_name = "Run";
            animation_transitions
                .play(
                    &mut animation_player,
                    animations
                        .named_indices
                        .get(anim_name)
                        .expect("animation name should be in the list")
                        .clone(),
                    Duration::from_secs(5),
                )
                .repeat();
        }
    }

    if keycode.just_pressed(KeyCode::KeyC) {
        for (link, animations) in animated_foxes.iter() {
            let (mut animation_player, mut animation_transitions) =
                animation_players.get_mut(link.0).unwrap();

            let anim_name = "Survey";
            animation_transitions
                .play(
                    &mut animation_player,
                    animations
                        .named_indices
                        .get(anim_name)
                        .expect("animation name should be in the list")
                        .clone(),
                    Duration::from_secs(5),
                )
                .repeat();
        }
    }

    /* Improveement ideas for the future
    // a bit more ideal API
    if keycode.just_pressed(KeyCode::B) {
        for (animation_player, animations) in  animated_robots.iter() {
            let anim_name = "Scan";
            if animations.named_animations.contains_key(anim_name) {
                let clip = animations.named_animations.get(anim_name).unwrap();
                animation_player.play_with_transition(clip.clone(), Duration::from_secs(5)).repeat();
            }
        }
    }

    // even better API
    if keycode.just_pressed(KeyCode::B) {
        for (animation_player, animations) in  animated_robots.iter() {
            animation_player.play_with_transition("Scan", Duration::from_secs(5)).repeat(); // with a merged animationPlayer + animations storage
            // alternative, perhaps more realistic, and better seperation of concerns
            animation_player.play_with_transition(animations, "Scan", Duration::from_secs(5)).repeat();

        }
    }*/

    /*for (mut anim_player, animations) in entities_with_animations.iter_mut(){

        if keycode.just_pressed(KeyCode::W) {
            let anim_name = "Walk";
            if animations.named_animations.contains_key(anim_name) {
                let clip = animations.named_animations.get(anim_name).unwrap();
                anim_player.play_with_transition(clip.clone(), Duration::from_secs(5)).repeat();
            }
        }
        if keycode.just_pressed(KeyCode::X) {
            let anim_name = "Run";
            if animations.named_animations.contains_key(anim_name) {
                let clip = animations.named_animations.get(anim_name).unwrap();
                anim_player.play_with_transition(clip.clone(), Duration::from_secs(5)).repeat();
            }
        }
        if keycode.just_pressed(KeyCode::C) {
            let anim_name = "Survey";
            if animations.named_animations.contains_key(anim_name) {
                let clip = animations.named_animations.get(anim_name).unwrap();
                anim_player.play_with_transition(clip.clone(), Duration::from_secs(5)).repeat();
            }
        }



        if keycode.just_pressed(KeyCode::S) {
            let anim_name = "Scan";
            if animations.named_animations.contains_key(anim_name) {
                let clip = animations.named_animations.get(anim_name).unwrap();
                anim_player.play_with_transition(clip.clone(), Duration::from_secs(5)).repeat();
            }
        }
        if keycode.just_pressed(KeyCode::I) {
            let anim_name = "Idle";
            if animations.named_animations.contains_key(anim_name) {
                let clip = animations.named_animations.get(anim_name).unwrap();
                anim_player.play_with_transition(clip.clone(), Duration::from_secs(5)).repeat();
            }
        }
    }*/
}
