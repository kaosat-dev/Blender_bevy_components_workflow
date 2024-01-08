use bevy::{prelude::*, core_pipeline::clear_color::ClearColorConfig};

use crate::state::InGameLoading;

pub fn setup_loading_screen(mut commands: Commands) {
    commands.spawn((
        Camera2dBundle{ 
            camera_2d: Camera2d{
                clear_color: ClearColorConfig::Custom(Color::BLACK)
            },
            camera: Camera {
                // renders after / on top of the main camera
                order: 2,
                ..default()
            },
            ..Default::default()
        }, 
        InGameLoading
    ));

    commands.spawn((
        TextBundle::from_section(
            "Loading...",
            TextStyle {
                //font: asset_server.load("fonts/FiraMono-Medium.ttf"),
                font_size: 28.0,
                color: Color::WHITE,
                ..Default::default()
            },
        )
        .with_style(Style {
            position_type: PositionType::Relative,
            top: Val::Percent(45.0),
            left: Val::Percent(45.0),
            ..default()
        }),
        InGameLoading,
    ));
}

pub fn teardown_loading_screen(in_main_menu: Query<Entity, With<InGameLoading>>, mut commands: Commands) {
    for entity in in_main_menu.iter() {
        commands.entity(entity).despawn_recursive();
    }
}
