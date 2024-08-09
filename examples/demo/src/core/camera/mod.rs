pub mod camera_tracking;
pub use camera_tracking::*;

pub mod camera_replace_proxies;
pub use camera_replace_proxies::*;

use bevy::prelude::*;
use blenvy::GltfBlueprintsSet;

pub struct CameraPlugin;
impl Plugin for CameraPlugin {
    fn build(&self, app: &mut App) {
        app.register_type::<CameraTrackable>()
            .register_type::<CameraTracking>()
            .register_type::<CameraTrackingOffset>()
            .register_type::<SSAOSettings>()
            .add_systems(
                Update,
                (
                    camera_replace_proxies.after(GltfBlueprintsSet::AfterSpawn),
                    camera_track,
                ),
            );
    }
}
