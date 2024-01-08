pub mod relationships_insert_dependant_components;
pub use relationships_insert_dependant_components::*;

use bevy::prelude::*;

pub struct EcsRelationshipsPlugin;
impl Plugin for EcsRelationshipsPlugin {
    fn build(&self, app: &mut App) {
        app;
    }
}
