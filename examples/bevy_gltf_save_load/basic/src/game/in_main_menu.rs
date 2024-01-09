use bevy::prelude::*;

use crate::state::{AppState, GameState, InMainMenu};

pub fn setup_main_menu(mut commands: Commands) {
    commands.spawn((Camera2dBundle::default(), InMainMenu));

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
    keycode: Res<Input<KeyCode>>,

    mut next_app_state: ResMut<NextState<AppState>>,
    // mut next_game_state: ResMut<NextState<GameState>>,
    // mut save_requested_events: EventWriter<SaveRequest>,
    // mut load_requested_events: EventWriter<LoadRequest>,
) {
    if keycode.just_pressed(KeyCode::Return) {
        next_app_state.set(AppState::AppLoading);
        // next_game_state.set(GameState::None);
    }

    if keycode.just_pressed(KeyCode::L) {
        next_app_state.set(AppState::AppLoading);
        // load_requested_events.send(LoadRequest { path: "toto".into() })
    }

    if keycode.just_pressed(KeyCode::S) {
        // save_requested_events.send(SaveRequest { path: "toto".into() })
    }
}
