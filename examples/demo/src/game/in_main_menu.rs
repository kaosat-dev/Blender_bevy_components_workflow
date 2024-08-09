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
    keycode: Res<ButtonInput<KeyCode>>,
    mut next_app_state: ResMut<NextState<AppState>>,
) {
    if keycode.just_pressed(KeyCode::Enter) {
        next_app_state.set(AppState::AppLoading);
    }
}
