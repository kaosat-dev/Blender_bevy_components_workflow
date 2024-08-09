[![Crates.io](https://img.shields.io/crates/v/blenvy)](https://crates.io/crates/blenvy)
[![Docs](https://img.shields.io/docsrs/blenvy)](https://docs.rs/blenvy/latest/blenvy/)
[![License](https://img.shields.io/crates/l/blenvy)](https://github.com/kaosat-dev/Blenvy/blob/main/crates/blenvy/License.md)
[![Bevy tracking](https://img.shields.io/badge/Bevy%20tracking-released%20version-lightblue)](https://github.com/bevyengine/bevy/blob/main/docs/plugins_guidelines.md#main-branch-tracking)

# blenvy

This crate allows you to 
- define [Bevy](https://bevyengine.org/) components direclty inside gltf files and instanciate the components on the Bevy side.
- define Blueprints/Prefabs for [Bevy](https://bevyengine.org/) inside gltf files and spawn them in Bevy.
    * Allows you to create lightweight levels, where all assets are different gltf files and loaded after the main level is loaded
    * Allows you to spawn different entities from gtlf files at runtime in a clean manner, including simplified animation support !

    A blueprint is a set of **overrideable** components + a hierarchy: ie 

        * just a Gltf file with Gltf_extras specifying components 
        * a component called BlueprintInfo

    Particularly useful when using [Blender](https://www.blender.org/) as an editor for the [Bevy](https://bevyengine.org/) game engine, combined with the Blender add-on that do a lot of the work for you 
    - [blenvy](https://github.com/kaosat-dev/Blenvy/tree/main/tools/blenvy)
- allows you to create a Json export of all your components/ registered types. 
Its main use case is as a backbone for the [```blenvy``` Blender add-on](https://github.com/kaosat-dev/Blenvy/tree/main/tools/blenvy), that allows you to add & edit components directly in Blender, using the actual type definitions from Bevy 
(and any of your custom types & components that you register in Bevy).
- adds the ability to easilly **save** and **load** your game worlds for [Bevy](https://bevyengine.org/) .

* leverages blueprints & seperation between 
    * **dynamic** entities : entities that can change during the lifetime of your app/game
    * **static** entities : entities that do NOT change (typically, a part of your levels/ environements)
* and allows allow for :
    * a simple save/load workflow thanks to the above
    * ability to specify **which entities** to save or to exclude
    * ability to specify **which components** to save or to exclude
    * ability to specify **which resources** to save or to exclude
    * small(er) save files (only a portion of the entities is saved)

Particularly useful when using [Blender](https://www.blender.org/) as an editor for the [Bevy](https://bevyengine.org/) game engine, combined with the [Blender plugin](https://github.com/kaosat-dev/Blenvy/tree/main/tools/blenvy) that does a lot of the work for you (including spliting generating seperate gltf files for your static vs dynamic assets)

## Usage

Here's a minimal usage example:

```toml
# Cargo.toml
[dependencies]
bevy="0.14"
blenvy = { version = "0.1.0-alpha.1"} 

```

```rust no_run
use bevy::prelude::*;
use blenvy::*;

fn main() {
    App::new()
        .add_plugins(DefaultPlugins)
        .add_plugins(BlenvyPlugin::default())

        .add_systems(Startup, setup_game)
        .add_systems(Update, spawn_blueprint_instance)
        .run();
}


// this is how you setup & spawn a level from a blueprint
fn setup_game(
    mut commands: Commands,
) {

    // here we spawn our game world/level, which is also a blueprint !
    commands.spawn((
        BlueprintInfo::from_path("levels/World.glb"), // all we need is a Blueprint info...
        SpawnBlueprint, // and spawnblueprint to tell blenvy to spawn the blueprint now
        HideUntilReady, // only reveal the level once it is ready
        GameWorldTag,
    ));
}

fn spawn_blueprint_instance(
    mut commands: Commands,
    keycode: Res<ButtonInput<KeyCode>>,
){
    if keycode.just_pressed(KeyCode::KeyS) {
        let new_entity = commands.spawn((
            BlueprintInfo::from_path("spawnable.glb"), // mandatory !!
            SpawnBlueprint, // mandatory !!
            TransformBundle::from_transform(Transform::from_xyz(0.0, 2.0, 0.2)), // VERY important !!
            // any other component you want to insert
        ));
    }
}
```

##  Installation

Add the following to your `[dependencies]` section in `Cargo.toml`:

```toml
blenvy = "0.1.0-alpha.1"
```

Or use `cargo add`:

```toml
cargo add blenvy
```

## Setup

```rust no_run
use bevy::prelude::*;
use blenvy::*;

fn main() {
    App::new()
        .add_plugins(DefaultPlugins)
        .add_plugin(BlenvyPlugin::default())
        .run();
}

```

you may want to configure your settings:

```rust no_run
use bevy::prelude::*;
use blenvy::*;

fn main() {
    App::new()
        .add_plugins((
             BlenvyPlugin{
                aabbs: true, // defaults to false, enable this to automatically calculate aabb for the scene/blueprint
                ..Default::default()
            }
        ))
        .run();
}

```

## Spawning entities from blueprints

You can spawn entities from blueprints like this:
```rust no_run
commands.spawn((
    BlueprintInfo::from_path("Health_Pickup.glb"), // mandatory !!
    // or the alterive: BlueprintInfo{name:"health pickup1".into(), path:"Health_Pickup.glb".into()}
    SpawnBlueprint, // mandatory !!
    
    TransformBundle::from_transform(Transform::from_xyz(x, 2.0, y)), // optional
    // any other component you want to insert
))

``` 

Once spawning of the actual entity is done, the contents (components, children etc) of the Blueprint will have been merged with those of the entity itself.

> Important :
you can **add** or **override** components present inside your Blueprint when spawning the BluePrint itself: ie

### Adding components not specified inside the blueprint

you can just add any additional components you need when spawning :

```rust no_run
commands.spawn((
    BlueprintInfo::from_path("Health_Pickup.glb"),
    SpawnBlueprint,
    TransformBundle::from_transform(Transform::from_xyz(x, 2.0, y)),
    // from Rapier/bevy_xpbd: this means the entity will also have a velocity component when inserted into the world
    Velocity {
        linvel: Vec3::new(vel_x, vel_y, vel_z),
        angvel: Vec3::new(0.0, 0.0, 0.0),
      },
))

``` 
### Overriding components specified inside the blueprint

any component you specify when spawning the Blueprint that is also specified **within** the Blueprint will **override** that component in the final spawned entity

for example 
```rust no_run
commands.spawn((
    BlueprintInfo::from_path("Health_Pickup.glb"),
    SpawnBlueprint,
    TransformBundle::from_transform(Transform::from_xyz(x, 2.0, y)),
    HealthPowerUp(20)// if this is component is also present inside the "Health_Pickup" blueprint, that one will be replaced with this component during spawning
))

``` 

### BluePrintBundle

There is also a ```BluePrintBundle``` for convenience , which just has 
 * a ```BlueprintInfo``` component
 * a ```SpawnBlueprint``` component

## Additional information

- When a blueprint is spawned, an ```FromBlueprint``` component is inserted into all its children entities (and nested children etc)
- this crate also provides a special optional ```GameWorldTag``` component: this is useful when you want to keep all your spawned entities inside a root entity

You can use it in your queries to add your entities as children of this "world"
This way all your levels, your dynamic entities etc, are kept seperated from UI nodes & other entities that are not relevant to the game world

> Note: you should only have a SINGLE entity tagged with that component !

```rust no_run
   commands.spawn((
        BlueprintInfo::from_path("levels/World.glb"), 
        SpawnBlueprint,
        HideUntilReady,
        GameWorldTag, // here it is
    ));
```


## Registry

Blenvy automatically exports a Json file containing of all your registered components/ types, in order to be able to create UIs that allows you to add & edit your components directly in Blender in the [Blenvy](https://github.com/kaosat-dev/Blenvy/tree/main/tools/blenvy) Blender add-on
- The output file will be generated in the ```Startup``` schedule whenever you run your app.
- Every time you compile & run your app, the output json file will be updated.

## Materials

Ff you enable it on the blender side, Blenvy will be using "material libraries" to share common textures/materials between blueprints, in order to avoid asset & memory bloat:
Ie for example without this option, 56 different blueprints using the same material with a large texture would lead to the material/texture being embeded
56 times !!

Generating optimised blueprints and material libraries can be automated using the [Blender plugin](https://github.com/kaosat-dev/Blenvy/tree/main/tools/blenvy)

## Animation

```blenvy``` provides some lightweight helpers to deal with animations stored in gltf files

It has both support for blueprint level animations (shared by all blueprint instance of the same blueprint)

 * an ```BlueprintAnimations``` component that gets inserted into spawned (root) entities that contains a hashmap of all animations contained inside that entity/gltf file .
 * an ```BlueprintAnimationPlayerLink``` component that gets inserted into spawned (root) entities, to make it easier to find Bevy's ```AnimationPlayer``` and ```AnimationTransitions``` components

And instance level animations (specific to one instance)

 * an ```InstanceAnimations``` component that gets inserted into spawned (root) entities that contains a hashmap of all animations **specific to that instance** .
 * an ```InstanceAnimationPlayerLink``` component that gets inserted into spawned (root) entities, to make it easier to find Bevy's ```AnimationPlayer``` and ```AnimationTransitions``` components for the animations above


The workflow for animations is as follows:
* create a gltf file with animations (using Blender & co) as you would normally do
* inside Bevy, use the ```blenvy``` boilerplate (see sections above), no specific setup beyond that is required
* to control the animation of an entity, you need to query for entities that have both ```BlueprintAnimationPlayerLink``` and ```BlueprintAnimations``` components (added by ```blenvy```) AND entities with the ```AnimationPlayer``` component
 
For example (blueprint animations):

```rust no_run
pub fn trigger_blueprint_animations(
    animated_foxes: Query<(&BlueprintAnimationPlayerLink, &BlueprintAnimations), With<Fox>>,
    mut animation_players: Query<(&mut AnimationPlayer, &mut AnimationTransitions)>,
    keycode: Res<ButtonInput<KeyCode>>,
){
    if keycode.just_pressed(KeyCode::KeyW) {
        for (link, animations) in animated_foxes.iter() {
            let (mut animation_player, mut animation_transitions) =
            animation_players.get_mut(link.0).unwrap();

            let anim_name = "Walk";
            animation_transitions
                .play(
                    &mut animation_player,
                    animations
                        .named_indices
                        .get(anim_name)
                        .expect("animation name should be in the list")
                        .clone(),
                    Duration::from_secs(5),
                )
                .repeat();
        }
    }
}
```

see https://github.com/kaosat-dev/Blenvy/tree/main/examples/blenvy/animation for how to set it up correctly


## Additional features

this crate also includes automatic handling of lights in gltf files, to attempt to match Blender's eevee rendering as close as possible:
 * **BlenderLightShadows** (automatically generated by the gltf_auto_export Blender add-on) allows you to toggle light's shadows on/off in Blender and have matching
 behaviour in Bevy
 * **BlenderBackgroundShader** aka background color is also automatically set on the Bevy side
 * **BlenderShadowSettings** sets the cascade_size on the bevy side to match the one configured in Blender



## Examples

https://github.com/kaosat-dev/Blenvy/tree/main/examples/blenvy/components

https://github.com/kaosat-dev/Blenvy/tree/main/examples/blenvy/blueprints

https://github.com/kaosat-dev/Blenvy/tree/main/examples/blenvy/animation

https://github.com/kaosat-dev/Blenvy/tree/main/examples/blenvy/save_load

https://github.com/kaosat-dev/Blenvy/tree/main/examples/blenvy/demo (a full fledged demo)


## Compatible Bevy versions

The main branch is compatible with the latest Bevy release, while the branch `bevy_main` tries to track the `main` branch of Bevy (PRs updating the tracked commit are welcome).

Compatibility of `blenvy` versions:
| `blenvy` | `bevy` |
| :--                 | :--    |
| `0.1`               | `0.14` |
| branch `main`       | `0.14` |
| branch `bevy_main`  | `main` |


## License

This crate, all its code, contents & assets is Dual-licensed under either of

- Apache License, Version 2.0, ([LICENSE-APACHE](./LICENSE_APACHE.md) or https://www.apache.org/licenses/LICENSE-2.0)
- MIT license ([LICENSE-MIT](./LICENSE_MIT.md) or https://opensource.org/licenses/MIT)