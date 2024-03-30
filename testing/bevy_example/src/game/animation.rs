use std::time::Duration;

use bevy_gltf_blueprints::{
    AnimationInfos, AnimationMarkerReached, AnimationMarkerTrackers, AnimationMarkers,
    BlueprintAnimationPlayerLink, BlueprintAnimations, BlueprintName, BlueprintsList,
    GltfBlueprintsSet, InstanceAnimationPlayerLink, InstanceAnimations,
};

use bevy::{gltf::Gltf, prelude::*};
use bevy_gltf_worlflow_examples_common_rapier::{AppState, GameState};

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

#[derive(Resource)]
pub struct AnimTest(Handle<Gltf>);

pub fn setup_main_scene_animations(asset_server: Res<AssetServer>, mut commands: Commands) {
    commands.insert_resource(AnimTest(asset_server.load("models/World.glb")));
}

pub fn animations(
    added_animation_players: Query<(Entity, &Name, &AnimationPlayer)>,
    added_animation_infos: Query<(Entity, &Name, &AnimationInfos), (Added<AnimationInfos>)>,
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
        println!("");
    }
}

pub fn play_animations(
    animated_marker1: Query<
        (&InstanceAnimationPlayerLink, &InstanceAnimations),
        (With<AnimationInfos>, With<Marker1>),
    >,
    animated_marker2: Query<
        (&InstanceAnimationPlayerLink, &InstanceAnimations),
        (With<AnimationInfos>, With<Marker2>),
    >,
    animated_marker3: Query<
        (
            &InstanceAnimationPlayerLink,
            &InstanceAnimations,
            &BlueprintAnimationPlayerLink,
            &BlueprintAnimations,
        ),
        (With<AnimationInfos>, With<Marker3>),
    >,

    mut animation_players: Query<&mut AnimationPlayer>,
    keycode: Res<ButtonInput<KeyCode>>,
) {
    if keycode.just_pressed(KeyCode::KeyM) {
        for (link, animations) in animated_marker1.iter() {
            println!("animations {:?}", animations.named_animations);
            let mut animation_player = animation_players.get_mut(link.0).unwrap();
            let anim_name = "Blueprint1_move";
            animation_player
                .play_with_transition(
                    animations
                        .named_animations
                        .get(anim_name)
                        .expect("animation name should be in the list")
                        .clone(),
                    Duration::from_secs(5),
                )
                .repeat();
        }
    }
    if keycode.just_pressed(KeyCode::KeyJ) {
        for (link, animations) in animated_marker1.iter() {
            println!("animations {:?}", animations.named_animations);
            let mut animation_player = animation_players.get_mut(link.0).unwrap();
            let anim_name = "Blueprint1_jump";
            animation_player
                .play_with_transition(
                    animations
                        .named_animations
                        .get(anim_name)
                        .expect("animation name should be in the list")
                        .clone(),
                    Duration::from_secs(5),
                )
                .repeat();
        }
    }

    if keycode.just_pressed(KeyCode::KeyA) {
        for (link, animations) in animated_marker2.iter() {
            println!("animations {:?}", animations.named_animations);
            let mut animation_player = animation_players.get_mut(link.0).unwrap();
            let anim_name = "Blueprint1_move";
            animation_player
                .play_with_transition(
                    animations
                        .named_animations
                        .get(anim_name)
                        .expect("animation name should be in the list")
                        .clone(),
                    Duration::from_secs(5),
                )
                .repeat();
        }
    }
    if keycode.just_pressed(KeyCode::KeyB) {
        for (link, animations) in animated_marker2.iter() {
            println!("animations {:?}", animations.named_animations);
            let mut animation_player = animation_players.get_mut(link.0).unwrap();
            let anim_name = "Blueprint1_jump";
            animation_player
                .play_with_transition(
                    animations
                        .named_animations
                        .get(anim_name)
                        .expect("animation name should be in the list")
                        .clone(),
                    Duration::from_secs(5),
                )
                .repeat();
        }
    }

    // play instance animation
    if keycode.just_pressed(KeyCode::KeyW) {
        for (link, animations, _, _) in animated_marker3.iter() {
            println!("animations {:?}", animations.named_animations);
            let mut animation_player = animation_players.get_mut(link.0).unwrap();
            let anim_name = "Blueprint8_move";
            animation_player
                .play_with_transition(
                    animations
                        .named_animations
                        .get(anim_name)
                        .expect("animation name should be in the list")
                        .clone(),
                    Duration::from_secs(5),
                )
                .repeat();
        }
    }
    // play blueprint animation
    if keycode.just_pressed(KeyCode::KeyX) {
        for (_, _, link, animations) in animated_marker3.iter() {
            println!("animations {:?}", animations.named_animations);
            let mut animation_player = animation_players.get_mut(link.0).unwrap();
            let anim_name = "Walk";
            animation_player
                .play_with_transition(
                    animations
                        .named_animations
                        .get(anim_name)
                        .expect("animation name should be in the list")
                        .clone(),
                    Duration::from_secs(5),
                )
                .repeat();
        }
    }
}

pub fn trigger_event_based_on_animation_marker(
    animation_infos: Query<(
        Entity,
        &AnimationMarkers,
        &InstanceAnimationPlayerLink,
        &InstanceAnimations,
        &AnimationInfos,
    )>,
    animation_players: Query<&AnimationPlayer>,
    animation_clips: Res<Assets<AnimationClip>>,
    mut animation_marker_events: EventWriter<AnimationMarkerReached>,
) {
    for (entity, markers, link, animations, animation_infos) in animation_infos.iter() {
        let animation_player = animation_players.get(link.0).unwrap();
        let animation_clip = animation_clips.get(animation_player.animation_clip());

        if animation_clip.is_some() {
            // if marker_trackers.0.contains_key(k)
            // marker_trackers.0
            // println!("Entity {:?} markers {:?}", entity, markers);
            // println!("Player {:?} {}", animation_player.elapsed(), animation_player.completions());

            // FIMXE: yikes ! very inneficient ! perhaps add boilerplate to the "start playing animation" code so we know what is playing
            let animation_name = animations.named_animations.iter().find_map(|(key, value)| {
                if value == animation_player.animation_clip() {
                    Some(key)
                } else {
                    None
                }
            });
            if animation_name.is_some() {
                let animation_name = animation_name.unwrap();

                let animation_length_seconds = animation_clip.unwrap().duration();
                let animation_length_frames = animation_infos
                    .animations
                    .iter()
                    .find(|anim| &anim.name == animation_name)
                    .unwrap()
                    .frames_length;
                // TODO: we also need to take playback speed into account
                let time_in_animation = animation_player.elapsed()
                    - (animation_player.completions() as f32) * animation_length_seconds;
                let frame_seconds =
                    (animation_length_frames as f32 / animation_length_seconds) * time_in_animation;
                let frame = frame_seconds as u32;

                let matching_animation_marker = &markers.0[animation_name];
                if matching_animation_marker.contains_key(&frame) {
                    let matching_markers_per_frame = matching_animation_marker.get(&frame).unwrap();
                    // println!("FOUND A MARKER {:?} at frame {}", matching_markers_per_frame, frame);
                    //emit an event , something like AnimationMarkerReached(entity, animation_name, frame, marker_name)
                    // FIXME: problem, this can fire multiple times in a row, depending on animation length , speed , etc
                    for marker_name in matching_markers_per_frame {
                        animation_marker_events.send(AnimationMarkerReached {
                            entity: entity,
                            animation_name: animation_name.clone(),
                            frame: frame,
                            marker_name: marker_name.clone(),
                        });
                    }
                }
            }
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
