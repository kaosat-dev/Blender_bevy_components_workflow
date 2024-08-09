use bevy::prelude::*;
use bevy_gltf_worlflow_examples_common_rapier::InGameLoading;

pub fn setup_loading_screen(mut commands: Commands) {
    commands.spawn((
        Camera2dBundle {
            camera: Camera {
                clear_color: ClearColorConfig::Custom(Color::BLACK),
                // renders after / on top of the main camera
                order: 2,
                ..default()
            },
            ..Default::default()
        },
        InGameLoading,
    ));

    commands.spawn((
        TextBundle::from_section(
            "Loading...",
            TextStyle {
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

pub fn teardown_loading_screen(
    in_main_menu: Query<Entity, With<InGameLoading>>,
    mut commands: Commands,
) {
    for entity in in_main_menu.iter() {
        commands.entity(entity).despawn_recursive();
    }
}
