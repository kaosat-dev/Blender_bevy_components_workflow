use bevy::prelude::*;
use bevy_gltf_worlflow_examples_common_rapier::{AppState, InMainMenu};

pub fn setup_main_menu(mut commands: Commands) {
    commands.spawn((
        Camera2dBundle {
            camera: Camera {
                order: 102, // needed because of this: https://github.com/jakobhellermann/bevy_editor_pls/blob/crates/bevy_editor_pls_default_windows/src/cameras/mod.rs#L213C9-L213C28
                ..default()
            },
            ..Default::default()
        },
        InMainMenu,
    ));

    commands.spawn((
        TextBundle::from_section(
            "SOME GAME TITLE !!",
            TextStyle {
                font_size: 18.0,
                color: Color::WHITE,
                ..Default::default()
            },
        )
        .with_style(Style {
            position_type: PositionType::Absolute,
            top: Val::Px(100.0),
            left: Val::Px(200.0),
            ..default()
        }),
        InMainMenu,
    ));

    commands.spawn((
        TextBundle::from_section(
            "New Game (press Enter to start)
                - press N to restart (once the game is started)
                - press S to save (once the game is started)
                - press L to load (once the game is started)
                - press T for demo spawning (once the game is started)
                - press U to spawn entities with unregistered components (once the game is started)
                - press P to spawn entities attached to the player (once the game is started)
            ",
            TextStyle {
                font_size: 18.0,
                color: Color::WHITE,
                ..Default::default()
            },
        )
        .with_style(Style {
            position_type: PositionType::Absolute,
            top: Val::Px(200.0),
            left: Val::Px(200.0),
            ..default()
        }),
        InMainMenu,
    ));

    /*
    commands.spawn((
        TextBundle::from_section(
            "Load Game",
            TextStyle {
                font_size: 18.0,
                color: Color::WHITE,
                ..Default::default()
            },
        )
        .with_style(Style {
            position_type: PositionType::Absolute,
            top: Val::Px(250.0),
            left: Val::Px(200.0),
            ..default()
        }),
        InMainMenu
    ));

    commands.spawn((
        TextBundle::from_section(
            "Exit Game",
            TextStyle {
                font_size: 18.0,
                color: Color::WHITE,
                ..Default::default()
            },
        )
        .with_style(Style {
            position_type: PositionType::Absolute,
            top: Val::Px(300.0),
            left: Val::Px(200.0),
            ..default()
        }),
        InMainMenu
    ));*/
}

pub fn teardown_main_menu(in_main_menu: Query<Entity, With<InMainMenu>>, mut commands: Commands) {
    for entity in in_main_menu.iter() {
        commands.entity(entity).despawn_recursive();
    }
}

pub fn main_menu(
    keycode: Res<ButtonInput<KeyCode>>,
    mut next_app_state: ResMut<NextState<AppState>>,
) {
    if keycode.just_pressed(KeyCode::Enter) {
        next_app_state.set(AppState::AppLoading);
    }

    if keycode.just_pressed(KeyCode::KeyL) {
        next_app_state.set(AppState::AppLoading);
    }
}
