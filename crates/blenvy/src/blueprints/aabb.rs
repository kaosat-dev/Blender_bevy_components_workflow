use bevy::{math::Vec3A, prelude::*, render::primitives::Aabb};

use crate::{BlenvyConfig, BlueprintReadyForFinalizing, BlueprintReadyForPostProcess};

/// helper system that computes the compound aabbs of the scenes/blueprints
pub fn compute_scene_aabbs(
    root_entities: Query<(Entity, &Name), (With<BlueprintReadyForPostProcess>, Without<Aabb>)>,
    other_entities: Query<Entity, (With<BlueprintReadyForPostProcess>, With<Aabb>)>,
    children: Query<&Children>,
    existing_aabbs: Query<&Aabb>,

    mut blenvy_config: ResMut<BlenvyConfig>,
    mut commands: Commands,
) {
    // compute compound aabb
    for (root_entity, name) in root_entities.iter() {
        // info!("generating aabb for {:?}", name);

        // only recompute aabb if it has not already been done before
        if blenvy_config.aabb_cache.contains_key(&name.to_string()) {
            let aabb = blenvy_config
                .aabb_cache
                .get(&name.to_string())
                .expect("we should have the aabb available");
            commands
                .entity(root_entity)
                .insert(*aabb)
                .insert(BlueprintReadyForFinalizing);
        } else {
            let aabb = compute_descendant_aabb(root_entity, &children, &existing_aabbs);
            blenvy_config.aabb_cache.insert(name.to_string(), aabb);
            info!("Step 7: generating aabb for {:?}", name);
            commands
                .entity(root_entity)
                .insert(aabb)
                .insert(BlueprintReadyForFinalizing);
        }
    }
    for entity in other_entities.iter() {
        commands.entity(entity).insert(BlueprintReadyForFinalizing);
    }
}

pub fn compute_descendant_aabb(
    root_entity: Entity,
    children: &Query<&Children>,
    existing_aabbs: &Query<&Aabb>,
) -> Aabb {
    if let Ok(children_list) = children.get(root_entity) {
        let mut chilren_aabbs: Vec<Aabb> = vec![];
        for child in children_list.iter() {
            if let Ok(aabb) = existing_aabbs.get(*child) {
                chilren_aabbs.push(*aabb);
            } else {
                let aabb = compute_descendant_aabb(*child, children, existing_aabbs);
                chilren_aabbs.push(aabb);
            }
        }

        let mut min = Vec3A::splat(f32::MAX);
        let mut max = Vec3A::splat(f32::MIN);
        for aabb in chilren_aabbs.iter() {
            min = min.min(aabb.min());
            max = max.max(aabb.max());
        }
        let aabb = Aabb::from_min_max(Vec3::from(min), Vec3::from(max));

        return aabb;
    }

    Aabb::default()
}
