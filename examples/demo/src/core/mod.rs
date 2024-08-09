use bevy::prelude::*;
use blenvy::*;

pub struct CorePlugin;
impl Plugin for CorePlugin {
    fn build(&self, app: &mut App) {
        app.add_plugins((BlenvyPlugin {
            ..Default::default()
        },));
    }
}
