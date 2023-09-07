use bevy::pbr::{Clusters, VisiblePointLights};
use bevy::render::camera::CameraRenderGraph;
use bevy::render::view::VisibleEntities;
use bevy::{prelude::*, gltf::GltfExtras};
use bevy::tasks::IoTaskPool;
use bevy_rapier3d::prelude::RigidBody;
use std::io::Write;
use std::fs::File;

use crate::core::physics::{Collider, RigidBodyProxy};
use crate::game::{Pickable, Player};

use super::Saveable;


const NEW_SCENE_FILE_PATH:&str="save.scn.ron";

pub fn should_save(
    keycode: Res<Input<KeyCode>>,
) -> bool {
    return keycode.just_pressed(KeyCode::S)
}

pub fn save_game(
    world: &mut World,
){
    info!("saving");

    let saveable_entities: Vec<Entity> = world
    .query_filtered::<Entity, With<Saveable>>()
    .iter(world)
    .collect();

    /*let static_entities: Vec<Entity> = world
    .query_filtered::<Entity, Without<Saveable>>()
    .iter(world)
    .collect();*/
    println!("saveable entities {}", saveable_entities.len());

    let mut scene_builder = DynamicSceneBuilder::from_world(world);
    scene_builder
        .deny::<Children>()
        .deny::<Parent>()
        .deny::<ComputedVisibility>()
        .deny::<Visibility>()
        .deny::<GltfExtras>()
        .deny::<GlobalTransform>()

        .deny::<Collider>()
        .deny::<RigidBody>()
        .deny::<RigidBodyProxy>()
        .deny::<Saveable>()

        // camera stuff
        .deny::<Camera>()
        .deny::<CameraRenderGraph>()
        .deny::<Camera3d>()
        .deny::<Clusters>()
        .deny::<VisibleEntities>()
        .deny::<VisiblePointLights>()
        //.deny::<HasGizmoMarker>()


        .extract_entities(saveable_entities.into_iter());

        

   let dyn_scene = scene_builder.build();
   let serialized_scene = dyn_scene.serialize_ron(world.resource::<AppTypeRegistry>()).unwrap();

   #[cfg(not(target_arch = "wasm32"))]
          IoTaskPool::get()
              .spawn(async move {
                  // Write the scene RON data to file
                  File::create(format!("assets/{NEW_SCENE_FILE_PATH}"))
                      .and_then(|mut file| file.write(serialized_scene.as_bytes()))
                      .expect("Error while writing scene to file");
              })
              .detach();
}