use bevy::prelude::*;

#[derive(Component, Reflect, Debug)]
#[reflect(Component)]
/// Component for cameras, with an offset from the Trackable target  
///
pub struct CameraTracking {
    pub offset: Vec3,
}
impl Default for CameraTracking {
    fn default() -> Self {
        CameraTracking {
            offset: Vec3::new(0.0, 6.0, 8.0),
        }
    }
}

#[derive(Component, Reflect, Debug, Deref, DerefMut)]
#[reflect(Component)]
/// Component for cameras, with an offset from the Trackable target  
pub struct CameraTrackingOffset(Vec3);
impl Default for CameraTrackingOffset {
    fn default() -> Self {
        CameraTrackingOffset(Vec3::new(0.0, 6.0, 8.0))
    }
}

impl CameraTrackingOffset {
    fn new(input: Vec3) -> Self {
        CameraTrackingOffset(input)
    }
}

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// Add this component to an entity if you want it to be tracked by a Camera
pub struct CameraTrackable;

pub fn camera_track(
    mut tracking_cameras: Query<
        (&mut Transform, &CameraTrackingOffset),
        (
            With<Camera>,
            With<CameraTrackingOffset>,
            Without<CameraTrackable>,
        ),
    >,
    camera_tracked: Query<&Transform, With<CameraTrackable>>,
) {
    for (mut camera_transform, tracking_offset) in tracking_cameras.iter_mut() {
        for tracked_transform in camera_tracked.iter() {
            let target_position = tracked_transform.translation + tracking_offset.0;
            let eased_position = camera_transform.translation.lerp(target_position, 0.1);
            camera_transform.translation = eased_position; // + tracking.offset;// tracked_transform.translation + tracking.offset;
            *camera_transform = camera_transform.looking_at(tracked_transform.translation, Vec3::Y);
        }
    }
}
