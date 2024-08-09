use bevy::prelude::*;

use crate::GameState;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// Demo marker component
pub struct Player;

fn player_move_demo(
    keycode: Res<ButtonInput<KeyCode>>,
    mut players: Query<&mut Transform, With<Player>>,
) {
    let speed = 0.2;
    if let Ok(mut player) = players.get_single_mut() {
        if keycode.pressed(KeyCode::ArrowLeft) {
            player.translation.x += speed;
        }
        if keycode.pressed(KeyCode::ArrowRight) {
            player.translation.x -= speed;
        }

        if keycode.pressed(KeyCode::ArrowUp) {
            player.translation.z += speed;
        }
        if keycode.pressed(KeyCode::ArrowDown) {
            player.translation.z -= speed;
        }
    }
}

pub struct PlayerPlugin;
impl Plugin for PlayerPlugin {
    fn build(&self, app: &mut App) {
        app.register_type::<Player>().add_systems(
            Update,
            (player_move_demo,).run_if(in_state(GameState::InGame)),
        );
    }
}
