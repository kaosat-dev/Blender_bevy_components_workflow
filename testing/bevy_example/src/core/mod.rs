use std::any::TypeId;

use bevy::{prelude::*, utils::HashSet};
use blenvy::*;

/*use blenvy::*;
use blenvy::*; */

use crate::{ComponentAToFilterOut, ComponentBToFilterOut};

pub struct CorePlugin;
impl Plugin for CorePlugin {
    fn build(&self, app: &mut App) {
        app.add_plugins(
            BlenvyPlugin {
                registry_component_filter: SceneFilter::Denylist(HashSet::from([
                    // this is using Bevy's build in SceneFilter, you can compose what components you want to allow/deny
                    TypeId::of::<ComponentAToFilterOut>(),
                    TypeId::of::<ComponentBToFilterOut>(),
                    // and any other commponent you want to include/exclude
                ])),
                ..Default::default()
            }, /* ExportRegistryPlugin {
                   component_filter: SceneFilter::Denylist(HashSet::from([
                       // this is using Bevy's build in SceneFilter, you can compose what components you want to allow/deny
                       TypeId::of::<ComponentAToFilterOut>(),
                       TypeId::of::<ComponentBToFilterOut>(),
                       // and any other commponent you want to include/exclude
                   ])),
                   ..Default::default()
               },
               BlueprintsPlugin {
                   material_library: true,
                   aabbs: true,
                   ..Default::default()
               }, */
        );
    }
}
