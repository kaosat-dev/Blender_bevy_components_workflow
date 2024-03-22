use bevy::prelude::*;
use bevy::utils::HashMap;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// storage for animations for a given entity (hierarchy), essentially a clone of gltf's `named_animations`
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
pub struct Animated{
    pub animations: Vec<String> 
}


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