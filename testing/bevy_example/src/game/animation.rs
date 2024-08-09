use std::time::Duration;

/*use blenvy::{
    AnimationInfos, AnimationMarkerReached, BlueprintAnimationPlayerLink, BlueprintAnimations,
    InstanceAnimationPlayerLink, InstanceAnimations,
};*/

use bevy::{animation::RepeatAnimation, gltf::Gltf, prelude::*};

use blenvy::{
    AnimationInfos, AnimationMarkerReached, BlueprintAnimationPlayerLink, BlueprintAnimations,
    BlueprintInstanceDisabled, InstanceAnimationPlayerLink, InstanceAnimations,
};

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// flag component for testing
pub struct Marker1;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// flag component for testing
pub struct Marker2;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// flag component for testing
pub struct Marker3;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// flag component for testing; this is at the BLUEPRINT level
pub struct MarkerAllFoxes;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// flag component for testing; this is at the INSTANCE level
pub struct MarkerSpecificFox;

/*
#[allow(clippy::type_complexity)]
pub fn animations(
    added_animation_players: Query<(Entity, &Name, &AnimationPlayer)>,
    added_animation_infos: Query<(Entity, &Name, &AnimationInfos), Added<AnimationInfos>>,
    animtest: Res<AnimTest>,
    mut commands: Commands,
    assets_gltf: Res<Assets<Gltf>>,
    parents: Query<&Parent>,
) {
    for (entity, name, animation_infos) in added_animation_infos.iter() {
        //println!("animated stuf {:?} on entity {}", animation_infos, name);
        let gltf = assets_gltf.get(&animtest.0).unwrap();
        let mut matching_data = true;
        for animation_info in &animation_infos.animations {
            if !gltf.named_animations.contains_key(&animation_info.name) {
                matching_data = false;
                break;
            }
        }
        if matching_data {
            println!(
                "inserting Animations components into {} ({:?})",
                name, entity
            );
            println!("Found match {:?}", gltf.named_animations);
            commands.entity(entity).insert(InstanceAnimations {
                named_animations: gltf.named_animations.clone(),
            });
            for ancestor in parents.iter_ancestors(entity) {
                if added_animation_players.contains(ancestor) {
                    // println!("found match with animationPlayer !! {:?}",names.get(ancestor));
                    commands
                        .entity(entity)
                        .insert(InstanceAnimationPlayerLink(ancestor));
                }
                // info!("{:?} is an ancestor of {:?}", ancestor, player);
            }
        }
    }
}*/

pub fn check_animations(
    // (&BlueprintAnimationPlayerLink, &BlueprintAnimations)
    foxes: Query<
        (
            Entity,
            Option<&BlueprintAnimationPlayerLink>,
            Option<&InstanceAnimationPlayerLink>,
        ),
        (With<MarkerAllFoxes>, Without<BlueprintInstanceDisabled>),
    >,

    foo: Query<
        (
            Entity,
            Option<&BlueprintAnimationPlayerLink>,
            Option<&InstanceAnimationPlayerLink>,
        ),
        (With<Marker1>, Without<BlueprintInstanceDisabled>),
    >,
    bar: Query<
        (
            Entity,
            Option<&BlueprintAnimationPlayerLink>,
            Option<&InstanceAnimationPlayerLink>,
        ),
        (With<Marker2>, Without<BlueprintInstanceDisabled>),
    >,
    baz: Query<
        (
            Entity,
            Option<&BlueprintAnimationPlayerLink>,
            Option<&InstanceAnimationPlayerLink>,
        ),
        (With<Marker3>, Without<BlueprintInstanceDisabled>),
    >,

    bli: Query<(Entity, &AnimationInfos)>,
    anim_players: Query<(Entity, &AnimationPlayer)>,
    all_names: Query<&Name>,
) {
    /*for bla in foxes.iter() {
        println!("MarkerAllFoxes {:?} {:?} {:?}", all_names.get(bla.0), bla.1, bla.2)
    }
    for bla in foo.iter() {
        println!("Marker1 {:?} {:?} {:?}", all_names.get(bla.0), bla.1, bla.2)
    }

    for bla in bar.iter() {
        println!("Marker2 {:?} {:?} {:?}", all_names.get(bla.0), bla.1, bla.2)
    }
    for bla in baz.iter() {
        println!("Marker3 {:?} {:?} {:?}", all_names.get(bla.0), bla.1, bla.2)
    }
    println!(""); */
    /*for blo in bli.iter() {
        println!("YOOOOO {:?}", all_names.get(blo.0))
    }
    for anim in anim_players.iter() {
        println!("Players {:?}", all_names.get(anim.0))
    }*/
}

#[allow(clippy::type_complexity)]
pub fn play_animations(
    animated_foxes: Query<
        (&BlueprintAnimationPlayerLink, &BlueprintAnimations),
        With<MarkerAllFoxes>,
    >,
    animated_fox: Query<
        (&BlueprintAnimationPlayerLink, &BlueprintAnimations),
        With<MarkerSpecificFox>,
    >,

    animated_marker1: Query<
        (&InstanceAnimationPlayerLink, &InstanceAnimations),
        (With<AnimationInfos>, With<Marker1>),
    >,

    animated_marker2: Query<
        (&InstanceAnimationPlayerLink, &InstanceAnimations),
        (With<AnimationInfos>, With<Marker2>),
    >,

    with_blueprint_and_scene_animations: Query<
        (
            &InstanceAnimationPlayerLink,
            &InstanceAnimations,
            &BlueprintAnimationPlayerLink,
            &BlueprintAnimations,
        ),
        (With<AnimationInfos>, With<Marker3>),
    >,
    mut animation_players: Query<(&mut AnimationPlayer, &mut AnimationTransitions)>,
    keycode: Res<ButtonInput<KeyCode>>,
) {
    if keycode.just_pressed(KeyCode::KeyQ) {
        println!("playing fox blueprint animation requested");
        for (link, animations) in animated_fox.iter() {
            println!("BAR");

            // println!("animations {:?}", animations.named_animations);
            let (mut animation_player, mut animation_transitions) =
                animation_players.get_mut(link.0).unwrap();
            let anim_name = "Survey";
            let animation_index = animations
                .named_indices
                .get(anim_name)
                .expect("animation name should be in the list")
                .clone();

            animation_transitions
                .play(
                    &mut animation_player,
                    animation_index,
                    Duration::from_secs(5),
                )
                .repeat();

            /*let Some((&playing_animation_index, _)) = animation_player.playing_animations().next() else {
                continue;
            };
            let playing_animation = animation_player.animation_mut(playing_animation_index).unwrap();
            println!("Playing animation {:?}", playing_animation);
            playing_animation.set_repeat(RepeatAnimation::Forever);*/
        }
        println!("");
    }

    if keycode.just_pressed(KeyCode::KeyP) {
        println!("playing fox blueprint animation requested");
        for (link, animations) in animated_foxes.iter() {
            println!("FOO");

            // println!("animations {:?}", animations.named_animations);
            let (mut animation_player, mut animation_transitions) =
                animation_players.get_mut(link.0).unwrap();
            let anim_name = "Run";
            let animation_index = animations
                .named_indices
                .get(anim_name)
                .expect("animation name should be in the list")
                .clone();

            animation_transitions
                .play(
                    &mut animation_player,
                    animation_index,
                    Duration::from_secs(5),
                )
                .repeat();

            /*let Some((&playing_animation_index, _)) = animation_player.playing_animations().next() else {
                continue;
            };
            let playing_animation = animation_player.animation_mut(playing_animation_index).unwrap();
            println!("Playing animation {:?}", playing_animation);
            playing_animation.set_repeat(RepeatAnimation::Forever);*/
        }
        println!("");
    }

    if keycode.just_pressed(KeyCode::KeyO) {
        println!("playing marker 3 blueprint animation requested");
        for (_, _, link, animations) in with_blueprint_and_scene_animations.iter() {
            // This only works for entities that are spawned as part of the level, as scene animations are only there in that case
            // println!("animations {:?}", animations.named_animations.keys());
            let (mut animation_player, mut animation_transitions) =
                animation_players.get_mut(link.0).unwrap();
            let anim_name = "Walk";
            let animation_index = animations
                .named_indices
                .get(anim_name)
                .expect("animation name should be in the list")
                .clone();

            animation_transitions
                .play(
                    &mut animation_player,
                    animation_index,
                    Duration::from_secs(5),
                )
                .repeat();
        }
    }

    if keycode.just_pressed(KeyCode::KeyI) {
        println!("playing marker 3 scene animation requested");
        for (link, animations, _, _) in with_blueprint_and_scene_animations.iter() {
            //println!("animations {:?}", animations.named_animations.keys());
            let (mut animation_player, mut animation_transitions) =
                animation_players.get_mut(link.0).unwrap();
            let anim_name = "Blueprint8_move";
            let animation_index = animations
                .named_indices
                .get(anim_name)
                .expect("animation name should be in the list")
                .clone();

            animation_transitions
                .play(
                    &mut animation_player,
                    animation_index,
                    Duration::from_secs(5),
                )
                .repeat();
        }
    }

    if keycode.just_pressed(KeyCode::KeyU) {
        for (link, animations) in animated_marker1.iter() {
            println!("animations {:?}", animations.named_animations);
            let (mut animation_player, mut animation_transitions) =
                animation_players.get_mut(link.0).unwrap();

            let anim_name = "Blueprint1_move";
            let animation_index = animations
                .named_indices
                .get(anim_name)
                .expect("animation name should be in the list")
                .clone();

            animation_transitions
                .play(
                    &mut animation_player,
                    animation_index,
                    Duration::from_secs(5),
                )
                .repeat();
        }
    }
    if keycode.just_pressed(KeyCode::KeyY) {
        for (link, animations) in animated_marker1.iter() {
            println!("animations {:?}", animations.named_animations);
            let (mut animation_player, mut animation_transitions) =
                animation_players.get_mut(link.0).unwrap();

            let anim_name = "Blueprint1_jump";
            let animation_index = animations
                .named_indices
                .get(anim_name)
                .expect("animation name should be in the list")
                .clone();

            animation_transitions
                .play(
                    &mut animation_player,
                    animation_index,
                    Duration::from_secs(5),
                )
                .repeat();
        }
    }
    if keycode.just_pressed(KeyCode::KeyT) {
        for (link, animations) in animated_marker2.iter() {
            println!("animations {:?}", animations.named_animations);
            let (mut animation_player, mut animation_transitions) =
                animation_players.get_mut(link.0).unwrap();

            let anim_name = "Blueprint1_move";
            let animation_index = animations
                .named_indices
                .get(anim_name)
                .expect("animation name should be in the list")
                .clone();

            animation_transitions
                .play(
                    &mut animation_player,
                    animation_index,
                    Duration::from_secs(5),
                )
                .repeat();
        }
    }
}

pub fn react_to_animation_markers(
    mut animation_marker_events: EventReader<AnimationMarkerReached>,
) {
    for event in animation_marker_events.read() {
        println!("animation marker event {:?}", event)
    }
}
