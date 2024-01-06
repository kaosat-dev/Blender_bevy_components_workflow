use bevy::gltf::Gltf;
use bevy::utils::HashSet;
use bevy::{asset::LoadState, prelude::*};

use crate::gltf_extras_to_components;

#[derive(Resource)]
/// component to keep track of gltfs' loading state
pub struct GltfLoadingTracker {
    pub loading_gltfs: HashSet<Handle<Gltf>>,
    pub loaded_gltfs: HashSet<Handle<Gltf>>,
}

impl GltfLoadingTracker {
    pub fn new() -> GltfLoadingTracker {
        GltfLoadingTracker {
            loaded_gltfs: HashSet::new(),
            loading_gltfs: HashSet::new(),
        }
    }
    pub fn add_gltf(&mut self, handle: Handle<Gltf>) {
        self.loading_gltfs.insert(handle);
    }
}

pub fn track_new_gltf(
    mut tracker: ResMut<GltfLoadingTracker>,
    mut events: EventReader<AssetEvent<Gltf>>,
    asset_server: Res<AssetServer>,
) {
    println!("tracking");
    for event in events.read() {
        if let AssetEvent::LoadedWithDependencies { id } = event {
            let handle = asset_server
                .get_id_handle(*id)
                .expect("this gltf should have been loaded");
            tracker.add_gltf(handle.clone());
            debug!("gltf created {:?}", handle.clone());
        }
    }
    events.clear();
}

pub fn process_loaded_scenes(
    mut gltfs: ResMut<Assets<Gltf>>,
    mut tracker: ResMut<GltfLoadingTracker>,
    mut scenes: ResMut<Assets<Scene>>,
    app_type_registry: Res<AppTypeRegistry>,
    asset_server: Res<AssetServer>,
) {
    let mut loaded_gltfs = Vec::new();
    for gltf in &tracker.loading_gltfs {
        debug!(
            "checking for loaded gltfs {:?}",
            asset_server.get_load_state(gltf)
        );

        if let Some(load_state) = asset_server.get_load_state(gltf.clone()) {
            if load_state == LoadState::Loaded {
                debug!("Adding scene to processing list");
                loaded_gltfs.push(gltf.clone());
            }
        }
    }

    let type_registry = app_type_registry.read();

    for gltf_handle in &loaded_gltfs {
        if let Some(gltf) = gltfs.get_mut(gltf_handle) {
            gltf_extras_to_components(gltf, &mut scenes, &*type_registry);
        }
        tracker.loading_gltfs.remove(gltf_handle);
        tracker.loaded_gltfs.insert(gltf_handle.clone());
        debug!("Done loading scene");
    }
}
