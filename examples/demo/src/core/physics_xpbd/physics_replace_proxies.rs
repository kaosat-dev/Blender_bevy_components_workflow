use bevy::prelude::*;
use bevy_xpbd_3d::prelude::Collider as XpbdCollider;
use bevy_xpbd_3d::prelude::*;

use super::utils::*;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub enum Collider {
    Ball(f32),
    Cuboid(Vec3),
    Capsule(Vec3, Vec3, f32),
    #[default]
    Mesh,
}

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub enum AutoAABBCollider {
    #[default]
    Cuboid,
    Ball,
    Capsule,
}

// replaces all physics stand-ins with the actual xpbd types
#[allow(clippy::type_complexity)]
pub(crate) fn physics_replace_proxies(
    meshes: Res<Assets<Mesh>>,
    mesh_handles: Query<&Handle<Mesh>>,
    mut proxy_colliders: Query<
        (Entity, &Collider, &Name, &mut Visibility),
        (Without<XpbdCollider>, Added<Collider>),
    >,
    // needed for tri meshes
    children: Query<&Children>,

    mut commands: Commands,
) {
    for proxy_colider in proxy_colliders.iter_mut() {
        let (entity, collider_proxy, name, mut visibility) = proxy_colider;
        // we hide the collider meshes: perhaps they should be removed altogether once processed ?
        if name.ends_with("_collider") || name.ends_with("_sensor") {
            *visibility = Visibility::Hidden;
        }

        let mut xpbd_collider: XpbdCollider;
        match collider_proxy {
            Collider::Ball(radius) => {
                info!("generating collider from proxy: ball");
                xpbd_collider = XpbdCollider::sphere(*radius);
                commands.entity(entity)
                    .insert(xpbd_collider)
                    //.insert(ActiveEvents::COLLISION_EVENTS)  // FIXME: this is just for demo purposes (also is there something like that in xpbd ?) !!!
                    ;
            }
            Collider::Cuboid(size) => {
                info!("generating collider from proxy: cuboid");
                xpbd_collider = XpbdCollider::cuboid(size.x, size.y, size.z);
                commands.entity(entity)
                    .insert(xpbd_collider)
                    //.insert(ActiveEvents::COLLISION_EVENTS)  // FIXME: this is just for demo purposes (also is there something like that in xpbd ?) !!!
                    ;
            }
            Collider::Capsule(a, b, radius) => {
                info!("generating collider from proxy: capsule");
                // FIXME: temp
                let height = Vec3::distance(*a, *b);
                xpbd_collider = XpbdCollider::capsule(height, *radius);
                info!("CAPSULE {} {}", height, radius);
                commands.entity(entity)
                    .insert(xpbd_collider)
                    .insert(    Mass(5.0)                )
                    //.insert(ActiveEvents::COLLISION_EVENTS)  // FIXME: this is just for demo purposes (also is there something like that in xpbd ?) !!!
                    ;
            }
            Collider::Mesh => {
                info!("generating collider from proxy: mesh");
                for (_, collider_mesh) in
                    Mesh::search_in_children(entity, &children, &meshes, &mesh_handles)
                {
                    xpbd_collider = XpbdCollider::trimesh_from_mesh(collider_mesh).unwrap(); // convex_hull_from_mesh?
                    commands.entity(entity).insert(xpbd_collider);
                }
            }
        }
    }
}
