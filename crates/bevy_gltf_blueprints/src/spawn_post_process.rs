use std::any::TypeId;

use bevy::prelude::*;
use bevy::scene::SceneInstance;
// use bevy::utils::hashbrown::HashSet;

use super::{AnimationPlayerLink, Animations};
use super::{SpawnHere, Spawned};
use crate::{CopyComponents, InBlueprint, OriginalChildren};

/// this system is in charge of doing any necessary post processing after a blueprint scene has been spawned
/// - it removes one level of useless nesting
/// - it copies the blueprint's root components to the entity it was spawned on (original entity)
/// - it copies the children of the blueprint scene into the original entity
/// - it add AnimationLink components so that animations can be controlled from the original entity
/// - it cleans up/ removes a few , by then uneeded components
pub(crate) fn spawned_blueprint_post_process(
    unprocessed_entities: Query<
        (
            Entity,
            &Children,
            Option<&Name>,
            &OriginalChildren,
            &Animations,
        ),
        (With<SpawnHere>, With<SceneInstance>, With<Spawned>),
    >,
    added_animation_players: Query<(Entity, &Parent), Added<AnimationPlayer>>,
    all_children: Query<&Children>,

    mut commands: Commands,
) {
    for (original, children, name, original_children, animations) in unprocessed_entities.iter() {
        info!("post processing blueprint for entity {:?}", name);

        if children.len() == 0 {
            warn!("timing issue ! no children found, please restart your bevy app (bug being investigated)");
            continue;
        }
        // the root node is the first & normally only child inside a scene, it is the one that has all relevant components
        let mut root_entity = Entity::PLACEHOLDER; //FIXME: and what about childless ones ?? => should not be possible normally
                                                   // let diff = HashSet::from_iter(original_children.0).difference(HashSet::from_iter(children));
                                                   // we find the first child that was not in the entity before (aka added during the scene spawning)
        for c in children.iter() {
            if !original_children.0.contains(c) {
                root_entity = *c;
                break;
            }
        }

        // we flag all children of the blueprint instance with 'InBlueprint'
        // can be usefull to filter out anything that came from blueprints vs normal children
        for child in all_children.iter_descendants(root_entity) {
            commands.entity(child).insert(InBlueprint);
        }

        // copy components into from blueprint instance's root_entity to original entity
        commands.add(CopyComponents {
            source: root_entity,
            destination: original,
            exclude: vec![TypeId::of::<Parent>(), TypeId::of::<Children>()],
            stringent: false,
        });

        // we move all of children of the blueprint instance one level to the original entity
        if let Ok(root_entity_children) = all_children.get(root_entity) {
            for child in root_entity_children.iter() {
                // info!("copying child {:?} upward from {:?} to {:?}", names.get(*child), root_entity, original);
                commands.entity(original).add_child(*child);
            }
        }

        if animations.named_animations.keys().len() > 0 {
            for (added, parent) in added_animation_players.iter() {
                if parent.get() == root_entity {
                    // FIXME: stopgap solution: since we cannot use an AnimationPlayer at the root entity level
                    // and we cannot update animation clips so that the EntityPaths point to one level deeper,
                    // BUT we still want to have some marker/control at the root entity level, we add this
                    commands.entity(original).insert(AnimationPlayerLink(added));
                }
            }
        }

        commands.entity(original).remove::<SpawnHere>();
        commands.entity(original).remove::<Spawned>();
        commands.entity(original).remove::<Handle<Scene>>();
        commands.entity(root_entity).despawn_recursive();
    }
}
