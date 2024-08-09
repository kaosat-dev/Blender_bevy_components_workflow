use bevy::prelude::*;

pub fn insert_dependant_component<
    Dependant: Component,
    Dependency: Component + std::default::Default,
>(
    mut commands: Commands,
    entities_without_depency: Query<(Entity, &Name), (With<Dependant>, Without<Dependency>)>,
) {
    for (entity, name) in entities_without_depency.iter() {
        let name = name.clone().to_string();
        commands.entity(entity).insert(Dependency::default());
        warn!("found an entity called {} with a {} component but without an {}, please check your assets", name.clone(), std::any::type_name::<Dependant>(), std::any::type_name::<Dependency>());
    }
}
