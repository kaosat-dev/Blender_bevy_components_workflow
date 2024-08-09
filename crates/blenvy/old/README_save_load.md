[![Crates.io](https://img.shields.io/crates/v/bevy_gltf_save_load)](https://crates.io/crates/bevy_gltf_save_load)
[![Docs](https://img.shields.io/docsrs/bevy_gltf_save_load)](https://docs.rs/bevy_gltf_save_load/latest/bevy_gltf_save_load/)
[![License](https://img.shields.io/crates/l/bevy_gltf_save_load)](https://github.com/kaosat-dev/Blenvy/blob/main/crates/bevy_gltf_save_load/License.md)
[![Bevy tracking](https://img.shields.io/badge/Bevy%20tracking-released%20version-lightblue)](https://github.com/bevyengine/bevy/blob/main/docs/plugins_guidelines.md#main-branch-tracking)

# bevy_gltf_save_load (deprecated in favor of Blenvy)

> bevy_gltf_save_load has been deprecated in favor of its successor [Blenvy](https://crates.io/crates/blenvy), part of the [Blenvy project](https://github.com/kaosat-dev/Blenvy). No further development or maintenance will be done for Bevy bevy_gltf_save_load. See [#194](https://github.com/kaosat-dev/Blenvy/issues/194) for background.

Built upon [bevy_gltf_blueprints](https://crates.io/crates/bevy_gltf_blueprints) this crate adds the ability to easilly **save** and **load** your game worlds for [Bevy](https://bevyengine.org/) .

* leverages blueprints & seperation between 
    * **dynamic** entities : entities that can change during the lifetime of your app/game
    * **static** entities : entities that do NOT change (typically, a part of your levels/ environements)
* and allows allow for :
    * a simple save/load workflow thanks to the above
    * ability to specify **which entities** to save or to exclude
    * ability to specify **which components** to save or to exclude
    * ability to specify **which resources** to save or to exclude
    * small(er) save files (only a portion of the entities is saved)

Particularly useful when using [Blender](https://www.blender.org/) as an editor for the [Bevy](https://bevyengine.org/) game engine, combined with the [Blender plugin](https://github.com/kaosat-dev/Blenvy/tree/main/tools/gltf_auto_export) that does a lot of the work for you (including spliting generating seperate gltf files for your static vs dynamic assets)


A bit of heads up:

* very opinionated !
* still in the early stages & not 100% feature complete
* fun fact: as the static level structure is stored seperatly, you can change your level layout & **still** reload an existing save file


## Usage

Here's a minimal usage example:

```toml
# Cargo.toml
[dependencies]
bevy="0.14"
bevy_gltf_save_load = "0.5"
bevy_gltf_blueprints = "0.11" // also needed
```

```rust no_run
use bevy::prelude::*;
use bevy_gltf_save_load::*;

fn main() {
    App::new()
        .add_plugins((
            DefaultPlugins,
            SaveLoadPlugin::default()
        ))
        .run();
}



// add a system to trigger saving
pub fn request_save(
    mut save_requests: EventWriter<SavingRequest>,
    keycode: Res<Input<KeyCode>>,
)
{
    if keycode.just_pressed(KeyCode::S) {
        save_requests.send(SavingRequest {
            path: "save.scn.ron".into(),
        })
    }
}

// add a system to trigger loading
pub fn request_load(
    mut load_requests: EventWriter<LoadRequest>,
    keycode: Res<Input<KeyCode>>,
)
{
    if keycode.just_pressed(KeyCode::L) {
        save_requests.send(LoadRequest {
            path: "save.scn.ron".into(),
        })
    }
}

// setting up your world
// on initial setup, the static entities & the dynamic entities are kept seperate for clarity & loaded as blueprints from 2 seperate files
pub fn setup_game(
    mut commands: Commands,
    mut next_game_state: ResMut<NextState<GameState>>,
) {
    info!("setting up game world");
    // here we actually spawn our game world/level
    let world_root = commands
        .spawn((
            Name::from("world"),
            GameWorldTag,
            InAppRunning,
            TransformBundle::default(),
            InheritedVisibility::default(),
        ))
        .id();

    // and we fill it with static entities
    let static_data = commands
        .spawn((
            Name::from("static"),
            BluePrintBundle {
                blueprint: BlueprintName("World".to_string()),
                ..Default::default()
            },
            StaticEntitiesRoot,
            Library("models".into())
        ))
        .id();

    // and we fill it with dynamic entities
    let dynamic_data = commands
        .spawn((
            Name::from("dynamic"),
            BluePrintBundle {
                blueprint: BlueprintName("World_dynamic".to_string()),
                ..Default::default()
            },
            DynamicEntitiesRoot,
            NoInBlueprint,
            Library("models".into())
        ))
        .id();
    commands.entity(world_root).add_child(static_data);
    commands.entity(world_root).add_child(dynamic_data);

    next_game_state.set(GameState::InGame)
}


```

take a look at the [example](https://github.com/kaosat-dev/Blenvy/blob/main/examples/bevy_gltf_save_load/basic/src/game/mod.rs) for more clarity


##  Installation

Add the following to your `[dependencies]` section in `Cargo.toml`:

```toml
bevy_gltf_save_load = "0.3"
bevy_gltf_blueprints = "0.10" // also needed, as bevy_gltf_save_load does not re-export it at this time
```

Or use `cargo add`:

```toml
cargo add bevy_gltf_save_load
```

## Setup

```rust no_run
use bevy::prelude::*;
use bevy_gltf_save_load::*;

fn main() {
    App::new()
        .add_plugins((
            DefaultPlugins
            SaveLoadPlugin::default()
        ))
        .run();
}

```

you likely need to configure your settings (otherwise, not much will be saved)

```rust no_run
use bevy::prelude::*;
use bevy_gltf_save_load::*;

fn main() {
    App::new()
        .add_plugins((
            DefaultPlugins,
            SaveLoadPlugin {
                save_path: "scenes".into(), // where do we save files to (under assets for now) defaults to "scenes"
                component_filter: SceneFilter::Allowlist(HashSet::from([ // this is using Bevy's build in SceneFilter, you can compose what components you want to allow/deny
                    TypeId::of::<Name>(),
                    TypeId::of::<Transform>(),
                    TypeId::of::<Velocity>(),
                    // and any other commponent you want to include/exclude
                ])),
                resource_filter: SceneFilter::deny_all(), // same logic as above, but for resources : also be careful & remember to register your resources !
                ..Default::default()
            },
            // you need to configure the blueprints plugin as well (might be pre_configured in the future, but for now you need to do it manually)
            BlueprintsPlugin {
                library_folder: "models/library".into(),
                format: GltfFormat::GLB,
                aabbs: true,
                ..Default::default()
            },
        ))
        .run();
}

```
### How to make sure your entites will be saved

- only entites that have a **Dynamic** component will be saved ! (the component is provided as part of the crate)
- you can either add that component at runtime or have it baked-in in the Blueprint

### Component Filter:
 
- by default only the following components are going to be saved 
    - **Parent**
    - **Children**
    - **BlueprintName** : part of bevy_gltf_blueprints, used under the hood
    - **SpawnHere** :part of bevy_gltf_blueprints, used under the hood
    - **Dynamic** : included in this crate, allows you to tag components as dynamic aka saveable ! Use this to make sure your entities are saved !

- you **CANNOT** remove these as they are part of the boilerplate
- you **CAN** add however many other components you want, allow them all etc as you see fit
- you can find more information about the SceneFilter object [here](https://bevyengine.org/news/bevy-0-11/#scene-filtering) and [here](https://docs.rs/bevy/latest/bevy/scene/enum.SceneFilter.html)


## Events


- to trigger **saving** use the ```SavingRequest``` event 
```rust no_run
// add a system to trigger saving
pub fn request_save(
    mut save_requests: EventWriter<SavingRequest>,
    keycode: Res<Input<KeyCode>>,
)
{
    if keycode.just_pressed(KeyCode::S) {
        save_requests.send(SavingRequest {
            path: "save.scn.ron".into(),
        })
    }
}

```


- to trigger **loading** use the ```LoadRequest``` event 

```rust no_run
// add a system to trigger saving
pub fn request_load(
    mut load_requests: EventWriter<LoadRequest>,
    keycode: Res<Input<KeyCode>>,
)
{
    if keycode.just_pressed(KeyCode::L) {
        save_requests.send(LoadRequest {
            path: "save.scn.ron".into(),
        })
    }
}
```

- you also notified when saving / loading is done 
    - ```SavingFinished``` for saving
    - ```LoadingFinished``` for loading

> Note: I **highly** recomend you change states when you start/finish saving & loading, otherwise things **will** get unpredictable
Please see [the example](https://github.com/kaosat-dev/Blenvy/tree/main/examples/bevy_gltf_save_load/basic/src/game/mod.rs) for this.

## Additional notes

- the name + path of the **static** level blueprint/gltf file will be saved as part of the save file, and reused to dynamically
load the correct static assets, which is necessary when you have multiple levels, and thus all required information to reload a save is contained within the save

## SystemSet

For convenience ```bevy_gltf_save_load``` provides two **SystemSets** 
 - [```LoadingSet```](./src/lib.rs#19)
 - [```SavingSet```](./src/lib.rs#24)


## Examples

Highly advised to get a better understanding of how things work !
To get started I recomend looking at 

- [world setup](https://github.com/kaosat-dev/Blenvy/tree/main/examples/bevy_gltf_save_load/basic/src/game/in_game.rs)
- [various events & co](https://github.com/kaosat-dev/Blenvy/tree/main/examples/bevy_gltf_save_load/basic/src/game/mod.rs)


All examples are here:

- https://github.com/kaosat-dev/Blenvy/tree/main/examples/bevy_gltf_save_load/basic


## Compatible Bevy versions

The main branch is compatible with the latest Bevy release, while the branch `bevy_main` tries to track the `main` branch of Bevy (PRs updating the tracked commit are welcome).

Compatibility of `bevy_gltf_save_load` versions:
| `bevy_gltf_save_load` | `bevy` |
| :--                 | :--    |
| `0.5 `              | `0.14` |
| `0.4 `              | `0.13` |
| `0.1 -0.3`          | `0.12` |
| branch `main`       | `0.12` |
| branch `bevy_main`  | `main` |


## License

This crate, all its code, contents & assets is Dual-licensed under either of

- Apache License, Version 2.0, ([LICENSE-APACHE](./LICENSE_APACHE.md) or https://www.apache.org/licenses/LICENSE-2.0)
- MIT license ([LICENSE-MIT](./LICENSE_MIT.md) or https://opensource.org/licenses/MIT)