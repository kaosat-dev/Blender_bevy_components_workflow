use bevy::prelude::*;

mod lighting;
pub use lighting::*;

pub(crate) fn plugin(app: &mut App) {
    app.add_plugins(lighting::plugin);
}
