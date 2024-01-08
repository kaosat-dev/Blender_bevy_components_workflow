use bevy::{math::Vec3A, prelude::*, render::primitives::Aabb};

use crate::{BluePrintsConfig, BlueprintName, Spawned};

/// helper system that computes the compound aabbs of the scenes/blueprints
pub fn compute_scene_aabbs(
    root_entities: Query<(Entity, &Name, &Children), (With<Spawned>, Without<Aabb>)>,
    children: Query<&Children>,
    existing_aabbs: Query<&Aabb>,

    mut blueprints_config: ResMut<BluePrintsConfig>,
    mut commands: Commands,
) {
    // compute compound aabb
    for (root_entity, name, instance_children) in root_entities.iter() {
        // info!("generating aabb for {:?}", name);
        // let root_entity = instance_children.first().unwrap();

        // only recompute aabb if it has not already been done before
        if blueprints_config.aabb_cache.contains_key(&name.to_string()) {
            let aabb = blueprints_config
                .aabb_cache
                .get(&name.to_string())
                .expect("we should have the aabb available");
            commands.entity(root_entity).insert(*aabb);
        } else {
            let aabb = compute_descendant_aabb(root_entity, &children, &existing_aabbs);
            commands.entity(root_entity).insert(aabb);
            blueprints_config.aabb_cache.insert(name.to_string(), aabb);
        }
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
                let aabb = compute_descendant_aabb(*child, children, &existing_aabbs);
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

    return Aabb::default();
}
