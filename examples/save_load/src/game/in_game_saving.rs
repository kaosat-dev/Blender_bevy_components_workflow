use bevy::prelude::*;
use bevy_gltf_worlflow_examples_common_rapier::InGameSaving;

pub fn setup_saving_screen(mut commands: Commands) {
    commands.spawn((
        TextBundle::from_section(
            "Saving...",
            TextStyle {
                font_size: 28.0,
                color: Color::WHITE,
                ..Default::default()
            },
        )
        .with_style(Style {
            position_type: PositionType::Relative,
            top: Val::Percent(90.0),
            left: Val::Percent(80.0),
            ..default()
        }),
        InGameSaving,
    ));
}

pub fn teardown_saving_screen(
    in_main_menu: Query<Entity, With<InGameSaving>>,
    mut commands: Commands,
) {
    for entity in in_main_menu.iter() {
        commands.entity(entity).despawn_recursive();
    }
}
