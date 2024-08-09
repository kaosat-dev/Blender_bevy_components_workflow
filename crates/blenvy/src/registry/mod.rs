use std::path::PathBuf;

pub mod export_types;
pub use export_types::*;

use bevy::{
    app::Startup,
    asset::AssetPlugin,
    prelude::{App, IntoSystemConfigs, Plugin, Res, Resource},
    scene::SceneFilter,
};

use crate::BlenvyConfig;

pub struct ExportRegistryPlugin {
    pub component_filter: SceneFilter,
    pub resource_filter: SceneFilter,
    pub save_path: PathBuf,
}

impl Default for ExportRegistryPlugin {
    fn default() -> Self {
        Self {
            component_filter: SceneFilter::default(),
            resource_filter: SceneFilter::default(),
            save_path: PathBuf::from("registry.json"), // relative to assets folder
        }
    }
}

fn export_registry(blenvy_config: Res<BlenvyConfig>) -> bool {
    // TODO: add detection of Release builds, wasm, and android in order to avoid exporting registry in those cases
    blenvy_config.export_registry
}

impl Plugin for ExportRegistryPlugin {
    fn build(&self, app: &mut App) {
        app.register_asset_root().add_systems(Startup, export_types.run_if(export_registry));
    }
}

trait RegistryExportApp {
    fn register_asset_root(&mut self) -> &mut Self;
}
impl RegistryExportApp for App {
    fn register_asset_root(&mut self) -> &mut Self {
        let asset_plugin = get_asset_plugin(self);
        let path_str = asset_plugin.file_path.clone();
        let path = PathBuf::from(path_str);
        self.insert_resource(AssetRoot(path))
    }
}

fn get_asset_plugin(app: &App) -> &AssetPlugin {
    let asset_plugins: Vec<&AssetPlugin> = app.get_added_plugins();
    asset_plugins.into_iter().next().expect(ASSET_ERROR)
}

const ASSET_ERROR: &str = "Bevy_registry_export requires access to the Bevy asset plugin. \
    Please add `ExportRegistryPlugin` after `AssetPlugin`, which is commonly added as part of the `DefaultPlugins`";

#[derive(Debug, Clone, PartialEq, Eq, Hash, Resource)]
pub(crate) struct AssetRoot(pub(crate) PathBuf);
