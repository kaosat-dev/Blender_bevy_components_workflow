use bevy::{prelude::*, gltf::{GltfPlugin, Gltf}, scene::ScenePlugin};
use bevy_gltf_components::*;


#[derive(Component, Reflect, Default, Debug, )]
#[reflect(Component)]
struct BasicTest{
    a: f32,
    b: u64,
    c: String
}

#[derive(Component, Reflect, Default, Debug, )]
#[reflect(Component)]
struct UnitTest;


#[derive(Resource)]
struct AssetLoadHelper(Handle<Scene>);

#[derive(Resource)]
struct Loaded(u32);

fn setup(
    mut commands: Commands,
    asset_server: Res<AssetServer>,
) {

    let tmp: Handle<Scene>  = asset_server.load("level1.glb#Scene0");
    println!("setting up loading");
    // commands.insert_resource(AssetLoadHelper(tmp));
}



fn spawn_level(
    mut asset_event_reader: EventReader<AssetEvent<Gltf>>,
    mut loaded: ResMut<Loaded>,
  ){

    //println!("loading");
    if let Some(asset_event) = asset_event_reader.iter().next() {
        println!("asset event");
        match asset_event {
            AssetEvent::Added { id: _ } => {
                info!("GLTF loaded");
                loaded.0 += 1;
                /*if scene_markers.is_empty() {
                    info!("spawning scene");
                    commands.spawn(
                        (
                            SceneBundle {
                                scene: preloaded_scene.0.clone(),
                                ..default()
                            },
                            LoadedMarker,
                            Name::new("Level1")
                        )
                    );
                    next_state.set(AppState::Running);
                }*/
            }
            _ => ()
        }
    }

 }

// #[test]
fn components_injected() {
    // Setup app
    let mut app = App::new();
    app
        .register_type::<BasicTest>()
        .register_type::<UnitTest>()
        .add_plugins((
            MinimalPlugins,
            AssetPlugin::default(),
            GltfPlugin::default(),
            ScenePlugin::default()
        ))

        //.add_plugins(ComponentsFromGltfPlugin)
        .add_systems(Startup, setup);
        // .add_systems(Update, spawn_level);

        app.insert_resource(Loaded(0));

    // Run systems
    app.run();
    /*app.update();
    app.update();
    app.update();
    app.update();
    app.update();
    app.update();
    app.update();
    app.update();
    app.update();
    app.update();
    app.update();

    loop {
        app.update();
        println!("foo {}", app.world.resource::<Loaded>().0);
        if app.world.resource::<Loaded>().0 > 0 {
            break;
        }
    }*/

    // Check resulting changes
    let mut query = app.world.query::<(Entity, &Name, &UnitTest)>();
    println!("AAAAHHH {:?}", query);
    let mut results = 0;
    for res in query.iter(&app.world) {
        results +=1;
    }
    assert_eq!(results, 1);
}