use bevy::{prelude::*, gltf::{GltfPlugin, Gltf}, scene::ScenePlugin, pbr::PbrPlugin, render::{RenderPlugin, pipelined_rendering::PipelinedRenderingPlugin}, core_pipeline::CorePipelinePlugin};
use bevy_gltf_components::{ComponentsFromGltfPlugin, GltfComponentsSet};

#[derive(Resource)]
pub struct MyGltf(pub Handle<Gltf>);


#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// helper marker component
pub struct LoadedMarker;


#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct Pickable;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct Player;


fn setup(
    mut commands: Commands, 
    asset_server: Res<AssetServer>,
) {
    println!("setting up loading");
    commands.insert_resource(MyGltf(asset_server.load("models/level1.glb")));
}

fn foo(
    mut asset_event_reader: EventReader<AssetEvent<Gltf>>,
){
    if let Some(asset_event) = asset_event_reader.read().next() {
        println!("asset event {:?}",asset_event);
        match asset_event {
            AssetEvent::Added { id: _ } => {
                info!("GLTF Added");
            },
            AssetEvent::LoadedWithDependencies { id: _ } => {
                info!("GLTF loaded");
            },
            _ => ()
        }
    }
}


fn spawn_level(
    mut commands: Commands,
    scene_markers: Query<&LoadedMarker>,
    mut asset_event_reader: EventReader<AssetEvent<Gltf>>,
    models: Res<Assets<bevy::gltf::Gltf>>,
) {
    if let Some(asset_event) = asset_event_reader.read().next() {
        match asset_event {
            AssetEvent::LoadedWithDependencies { id } => {
                info!("GLTF loaded/ added {:?}", asset_event);
                let my_gltf = models.get(*id).unwrap();
                if scene_markers.is_empty() {
                    info!("spawning scene");
                    commands.spawn((
                        SceneBundle {
                            scene: my_gltf.scenes[0].clone(),
                            ..default()
                        },
                        LoadedMarker,
                        Name::new("Level1"),
                    ));
                }
            }
            _ => (),
        }
    }
}

fn test(
   players: Query<&Player>,
   pickables: Query<&Pickable>
){
    println!("foo");
    for player in players.iter() {
        println!("found player")
    }

    for pickable in pickables.iter() {
        println!("found pickable")
    }
}


#[test]
fn main() {
    // Setup app
    let mut app = App::new();
    app
        .register_type::<Pickable>()
        .register_type::<Player>()
        .add_plugins((
            MinimalPlugins,

            TransformPlugin::default(),
            HierarchyPlugin::default(),
            AssetPlugin::default(),
            ScenePlugin::default(),


            /*RenderPlugin::default(),
            ImagePlugin::default(),
            WindowPlugin::default(),

            CorePipelinePlugin::default(),
            PipelinedRenderingPlugin::default(),


                */
            PbrPlugin::default(),
            GltfPlugin::default(),

            

        ))
        //.add_plugins(DefaultPlugins)
        //.add_plugins(ComponentsFromGltfPlugin)

        .add_systems(Startup, setup)
        .add_systems(Update, (
            (
                spawn_level,
                test)
            .chain()
            .after(GltfComponentsSet::Injection))
        )

        .run()
        //.run_app_until()
        ;


    /*loop {
        // println!("foo {:?}", app.world.resource::<Added<MyGltf>>().clone());
        app.update();
    }*/

}