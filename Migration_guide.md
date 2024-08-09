# Blender add-ons

- gltf_auto_export and bevy_components have been replaced with a single Blenvy add-on for simplicity , I recomend reading the [documentation](./tools/blenvy/README.md)
    * settings are **not** transfered from the legacy add-ons !
    * first uninstall the old add-ons
    * install Blenvy
    * configure Blenvy (for these , see the Blenvy add-on docs)
    * [upgrade your components](./tools/blenvy/README-components.md#renamingupgradingfixing-components)


## Components:

- no more need to add your components to an empty called xxx_components, you can now directly add your components to the blueprint's collection itself
- you will need to "upgrade" your components from the previous add-on, as they are stored in a completely different way

## Multiple components with the same short name

 Up until now , it was not possible to have multiple components with the same name (ie foo::bar::componentA & some::other::componentA) as all the logic was based on short names,
 this is not an issue anymore

## Auto export:

- the previous stripped down gltf export settings are not part of the add-on anymore, please configure them like this: 
- you need to reconfigure your auto export settings , as they have changed significantly as has their storage

## All the Bevy crates have been replaced with a single one

- the new crate doesn't even really need configuring, so
- in your cargo.toml file, replace any references to the old crates (bevy_gltf_components, bevy_gltf_blueprints, bevy_registry_export, bevy_gltf_save_load etc)
with:

```toml
# Cargo.toml
[dependencies]
bevy="0.14"
blenvy = { version = "0.1.0"} 
```

and set things up in your code:

```rust no_run
use bevy::prelude::*;
use blenvy::*;

fn main() {
    App::new()
        .add_plugins(DefaultPlugins)
        .add_plugins(BlenvyPlugin)

        .run();
}
```

## Removed almost all setting for the crate

- the ONLY setting is **aabbs** // defaults to true

## Legacy mode has been removed

- less headaches when using the tools!
If you still want to manually specify components using Blender's custom properties you need to


## BlueprintName replaced with BlueprintInfo

- this is a very important change ! to avoid possible path clashes , the ```BlueprintInfo``` component contains
the actual path (with your **assets** folder) to the Blueprint, and a name (for convenience)

## SpawnHere renamed to SpawnBlueprint

changed the naming for more clarity & specificity


## Automatic assets loading

- no more need to preload gltf files, you can spawn a level & all its blueprint like this:

```rust no_run
commands.spawn((
    BlueprintInfo::from_path("levels/World.gltf"),
    HideUntilReady, // Only if you want to keep the level hidden until it is finished spawning
    SpawnBlueprint, // See note above
    GameWorldTag,
    InAppRunning,
));
```

Blenvy will take care of loading all needed blueprints & other assets for you

## Blueprint instance events

- you can now use the ```BlueprintEvent``` to get notified of crucial blueprint instance events

    * ```AssetsLoaded```
    ```rust no run
        /// event fired when a blueprint instance has finished loading all of its assets & before it attempts spawning
        AssetsLoaded {
            entity: Entity,
            blueprint_name: String,
            blueprint_path: String,
            // TODO: add assets list ?
        }
    ```

    * ```InstanceReady```
    ```rust no run
        /// event fired when a blueprint instance has completely finished spawning, ie
        /// - all its assests have been loaded
        /// - all of its child blueprint instances are ready
        /// - all the post processing is finished (aabb calculation, material replacements etc)
        InstanceReady {
            entity: Entity,
            blueprint_name: String,
            blueprint_path: String,
        },

    ```

## BlueprintInstanceDisabled 

you can now query for this component

## Track loading blueprint instances with the BlueprintSpawning component

- other than with events, you can also query for the ```BlueprintSpawning``` component to be sure an entity you are manipulating is finished with its blueprint instance spawning process

## Keep your currently spawning blueprint instances hidden until they are ready with the HideUntilReady component

If you want your blueprint instance to be hidden until it is ready, just add this component to the entity.
This can be particularly usefull in at least two use cases:
- when spawning levels 
- when spawning bluprint instances that contain **lights** at runtime: in previous versions I have noticed some very unpleasant "flashing" effect when spawning blueprints with lights,
this component avoids that issue  

## Hot reload

if you have configured your Bevy project to use hot reload you will automatically get hot reloading of levels & blueprints

## Improved animation handling

- sceneAnimations
- animationTriggers

## Completely restructured blueprint spawning process


Additionally
- you do not really need to worry about SystemSets anymore
