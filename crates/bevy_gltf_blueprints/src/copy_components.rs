use std::any::TypeId;
use std::error::Error;

use bevy::ecs::component::ComponentId;
use bevy::ecs::system::Command;
use bevy::prelude::*;

// originally based  https://github.com/bevyengine/bevy/issues/1515,
// more specifically https://gist.github.com/nwtnni/85d6b87ae75337a522166c500c9a8418
// to work with Bevy 0.11
// to copy components between entities but NOT overwriting any existing components
// plus some bells & whistles
pub struct CopyComponents {
    pub source: Entity,
    pub destination: Entity,
    pub exclude: Vec<TypeId>,
    pub stringent: bool,
}

impl CopyComponents {
    // Copy all components from an entity to another.
    // Using an entity with no components as the destination creates a copy of the source entity.
    // Panics if:
    // - the components are not registered in the type registry,
    // - the world does not have a type registry
    // - the source or destination entity do not exist
    fn transfer_components(self, world: &mut World) {
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

                    let type_id = component_info.type_id().unwrap();
                    if self.exclude.contains(&type_id) {
                        debug!("excluding component: {:?}", component_info.name());
                        return None;
                    } else {
                        debug!(
                            "cloning: component: {:?} {:?}",
                            component_info.name(),
                            type_id
                        );

                        if let Some(type_registration) = registry.get(type_id) {
                            return Some(type_registration);
                        } else {
                            if self.stringent {
                                return Some(
                                    registry.get(type_id).expect(
                                        format!(
                                        "cannot clone entity: component: {:?} is not registered",
                                        component_info.name()
                                    )
                                        .as_str(),
                                    ),
                                );
                            } else {
                                warn!(
                                    "cannot clone component: component: {:?} is not registered",
                                    component_info.name()
                                );
                                return None;
                            }
                        }
                    }
                })
                .map(|type_id| {
                    return (
                        type_id.data::<ReflectComponent>().unwrap().clone(),
                        type_id.type_info().type_id().clone(), // we need the original type_id down the line
                    );
                })
                .collect::<Vec<_>>()
        };

        for (component, type_id) in components {
            let source = component
                .reflect(world.get_entity(self.source).unwrap())
                .unwrap()
                .clone_value();

            let mut destination = world
                .get_entity_mut(self.destination)
                .expect("destination entity should exist");

            // println!("contains typeid {:?} {}", type_id, destination.contains_type_id(type_id));
            // we only want to copy components that are NOT already in the destination (ie no overwriting existing components)
            if !destination.contains_type_id(type_id) {
                component.insert(&mut destination, &*source);
            }
        }
    }
}

// This allows the command to be used in systems
impl Command for CopyComponents {
    fn apply(self, world: &mut World) {
        self.transfer_components(world)
    }
}
