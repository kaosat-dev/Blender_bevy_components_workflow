use bevy::prelude::*;
use bevy::utils::HashMap;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// storage for animations for a given entity's BLUEPRINT (ie for example a characters animations), essentially a clone of gltf's `named_animations`
pub struct BlueprintAnimations {
    pub named_animations: HashMap<String, Handle<AnimationClip>>,
}

#[derive(Component, Debug)]
/// Stop gap helper component : this is inserted into a "root" entity (an entity representing a whole gltf file)
/// so that the root entity knows which of its children contains an actualy `AnimationPlayer` component
/// this is for convenience, because currently , Bevy's gltf parsing inserts `AnimationPlayers` "one level down"
/// ie armature/root for animated models, which means more complex queries to trigger animations that we want to avoid
pub struct BlueprintAnimationPlayerLink(pub Entity);

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// storage for animations for a given entity (hierarchy), essentially a clone of gltf's `named_animations`
pub struct InstanceAnimations {
    pub named_animations: HashMap<String, Handle<AnimationClip>>,
}

#[derive(Component, Debug)]
/// Stop gap helper component : this is inserted into a "root" entity (an entity representing a whole gltf file)
/// so that the root entity knows which of its children contains an actualy `AnimationPlayer` component
/// this is for convenience, because currently , Bevy's gltf parsing inserts `AnimationPlayers` "one level down"
/// ie armature/root for animated models, which means more complex queries to trigger animations that we want to avoid
pub struct InstanceAnimationPlayerLink(pub Entity);

/// Stores Animation information: name, frame informations etc
#[derive(Reflect, Default, Debug)]
pub struct AnimationInfo {
    pub name: String,
    pub frame_start: f32,
    pub frame_end: f32,
    pub frames_length: f32,
    pub frame_start_override: f32,
    pub frame_end_override: f32,
}

/// Stores information about animations, to make things a bit easier api wise:
/// these components are automatically inserted by gltf_auto_export on entities that have animations
#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct AnimationInfos {
    pub animations: Vec<AnimationInfo>,
}

pub struct AnimationMarker {
    pub frame: u32,
    pub name: String,
}

/// Stores information about animation markers: practical for adding things like triggering events at specific keyframes etc
/// it is essentiall a hashmap of AnimationName => HashMap<FrameNumber, Vec of marker names>
#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct AnimationMarkers(pub HashMap<String, HashMap<u32, Vec<String>>>);

// FIXME: ugh, ugly, there has to be a better way to do this ?
#[derive(Component, Default, Debug)]
pub struct AnimationMarkerTrackers(pub HashMap<String, HashMap<u32, Vec<AnimationMarkerTracker>>>);

#[derive(Default, Debug)]
pub struct AnimationMarkerTracker {
    // pub frame:u32,
    // pub name: String,
    // pub processed_for_cycle: bool,
    pub prev_frame: u32,
}

/// Event that gets triggered once a specific marker inside an animation has been reached (frame based)
/// Provides some usefull information about which entity , wich animation, wich frame & which marker got triggered
#[derive(Event, Debug)]
pub struct AnimationMarkerReached {
    pub entity: Entity,
    pub animation_name: String,
    pub frame: u32,
    pub marker_name: String,
}
