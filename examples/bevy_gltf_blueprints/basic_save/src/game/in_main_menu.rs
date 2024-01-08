use bevy::prelude::*;

use crate::state::{AppState, GameState, InMainMenu};

pub fn setup_main_menu(mut commands: Commands) {
    commands.spawn((Camera2dBundle::default(), InMainMenu));

    commands.spawn((
        TextBundle::from_section(
            "SOME GAME TITLE !!",
            TextStyle {
                //font: asset_server.load("fonts/FiraMono-Medium.ttf"),
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
            "New Game (press Enter to start, press T once the game is started for demo spawning)",
            TextStyle {
                //font: asset_server.load("fonts/FiraMono-Medium.ttf"),
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
                //font: asset_server.load("fonts/FiraMono-Medium.ttf"),
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
                //font: asset_server.load("fonts/FiraMono-Medium.ttf"),
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

pub fn teardown_main_menu(bla: Query<Entity, With<InMainMenu>>, mut commands: Commands) {
    for bli in bla.iter() {
        commands.entity(bli).despawn_recursive();
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
