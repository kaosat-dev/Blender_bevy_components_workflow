use bevy::ecs::system::Command;
use bevy::prelude::*;

// modified version from https://github.com/bevyengine/bevy/issues/1515,
// more specifically https://gist.github.com/nwtnni/85d6b87ae75337a522166c500c9a8418
// to work with Bevy 0.11
pub struct CloneEntity {
    pub source: Entity,
    pub destination: Entity,
}

impl CloneEntity {
    // Copy all components from an entity to another.
    // Using an entity with no components as the destination creates a copy of the source entity.
    // Panics if:
    // - the components are not registered in the type registry,
    // - the world does not have a type registry
    // - the source or destination entity do not exist
    fn clone_entity(self, world: &mut World) {
        let components = {
            let registry = world
                .get_resource::<AppTypeRegistry>()
                .expect("the world should have a type registry")
                .read();

            world
                .get_entity(self.source)
                .expect("source entity should exist")
                .archetype()
                .components()
                .filter_map(|component_id| {
                    let component_info = world
                        .components()
                        .get_info(component_id)
                        .expect("component info should be available");

                    // FIXME: do something cleaner
                    if component_info.name() == "bevy_hierarchy::components::parent::Parent" {
                        return None;
                    }

                    if component_info.name() == "bevy_hierarchy::components::children::Children" {
                        return None;
                    }

                    if component_info.name() == "bevy_transform::components::transform::Transform" {
                        return None;
                    }
                    if component_info.name()
                        == "bevy_transform::components::transform::GlobalTransform"
                    {
                        return None;
                    }
                    // println!("cloning: component: {:?}",component_info.name());

                    let type_id = component_info.type_id().unwrap();

                    return registry.get(type_id);
                    /*if let Some(type_id) = registry.get(type_id) {
                        return type_id.data::<ReflectComponent>().unwrap().clone();
                    }*/
                    /*let type_id = registry.get(type_id).expect(
                        format!(
                            "cannot clone entity: component: {:?} is not registered",
                            component_info.name()
                        )
                        .as_str(),
                    );*/
                    // return type_id.data::<ReflectComponent>().unwrap().clone();
                })
                .map(|type_id| {
                    return type_id.data::<ReflectComponent>().unwrap().clone();
                })
                .collect::<Vec<_>>()
        };

        for component in components {
            let source = component
                .reflect(world.get_entity(self.source).unwrap())
                .unwrap()
                .clone_value();

            // println!("FOO {:?}", source);

            let mut destination = world
                .get_entity_mut(self.destination)
                .expect("destination entity should exist");

            //if destination.contains::comp
            //component.insert(&mut destination, &*source);
            if !destination.contains_type_id(source.type_id()) {
                // println!("copying {:?}", source);
                component.apply_or_insert(&mut destination, &*source);
            }
            // component.apply_or_insert(&mut destination, &*source);
        }
    }
}

// This allows the command to be used in systems
impl Command for CloneEntity {
    fn apply(self, world: &mut World) {
        self.clone_entity(world)
    }
}
