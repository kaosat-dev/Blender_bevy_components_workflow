[![Bevy tracking](https://img.shields.io/badge/Bevy%20tracking-released%20version-lightblue)](https://github.com/bevyengine/bevy/blob/main/docs/plugins_guidelines.md#main-branch-tracking)
[![License](https://img.shields.io/crates/l/blenvy)](https://github.com/kaosat-dev/Blenvy/blob/main/LICENSE.md)
[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/F1F5TO32O)

# BLENVY: a friendly Blender <=> Bevy workflow

![demo](./docs/blender_bevy.png)

Crates & tools for adding components from gltf files in the [Bevy](https://bevyengine.org/) game engine.

It enables a [Blender](https://www.blender.org/) (gltf) centric workflow for Bevy, ie defining entites & their components
inside Blender. Aka "Blender as editor for Bevy"

It also allows you to setup 'blueprints' in Blender by using collections (the recomended way to go most of the time), or directly on single use objects .

## Quickstart

Want to jump right in? See the [quickstart guide](./docs/quickstart/readme.md) for how to setup a basic project as fast as possible.

## Features

* Useful if you want to use Blender as your Editor
* define Bevy components as custom properties in Blender with an UI tool to add & edit Bevy components, automatically export gltf blueprints & more in [Blender](./tools/blenvy/README.md)
* blueprints & levels system : turn your Blender collections into [gltf Blueprints](./crates/blenvy/README.md) for reuse inside levels that are just Blender scenes
* setup & tweak components in Blender Collections & override any of them in your collection instances if you want
* setup & tweak components for objects, meshes and materials as well !
* automatically load all assets for each blueprint (gltf files, manually added assets), with no setup required
* hot reload of your levels & blueprints
* minimal setup & code, you can have something basic running fast
* minimal dependencies: Bevy, Serde & RON only!
* opensource

> If you were previously using the individual bevy_gltf_xxx crates & Blender add-ons please see the [migration guide](./Migration_guide.md)

## Crates

One crate to rule them all !

* [blenvy](./crates/blenvy/) This crate allows you to
  * define components direclty inside gltf files and instanciate/inject the components on the Bevy side.
  * export your project's Bevy registry to json, in order to be able to generate custom component UIs on the Blender side in the Blender [blenvy](./tools/blenvy/README.md) add-on
  * define Blueprints/Prefabs for Bevy inside gltf files and spawn them in Bevy. With the ability to override and add components when spawning, efficient "level" loading etc
  * the ability to save & load your game state in a relatively simple way, by leveraging the blueprint functionality to only save a minimal subset of dynamic data, seperating dynamic & static parts of levels etc.

    OLD videos:
    There is a [video tutorial/explanation](https://youtu.be/-lcScjQCA3c) if you want, or you can read the crate docs.
    There is a [video tutorial/explanation](https://youtu.be/CgyNtwgYwdM) for this one too, or you can read the crate docs

    The examples for the crate are [here](./examples/blenvy/)

## Tools

### Blender: blenvy

* an all in one [Blender addon](./tools/blenvy/README.md) for the Blender side of the workflow:
  * allow easilly adding & editing Bevy components , using automatically generated UIs for each component
  * automatically exports your level/world from Blender to gltf whenever you save your Blend file
  * automatically export your [Gltf blueprints](./crates/blenvy/README.md) & assets

## Examples

you can find all examples, [here](./examples/blenvy)

* [components](./examples/blenvy/components/) use of ```components``` only, to spawn entities with components defined inside gltf files
* [blueprints](./examples/blenvy/blueprints/) use of ```blueprints``` and ```levels``` to spawn a level and then populate it with entities coming from different gltf files, live (at runtime) spawning of entities etc
* [animation](./examples/blenvy/animation/) how to use and trigger animations from gltf files
* [save_load](./examples/blenvy/save_load/) how to save & load levels
* [demo](./examples/demo/) a full demo showcasing all features , including physics, animation

## Workflow

The workflow goes as follows (once you got your Bevy code setup)

* create & register all your components you want to be able to set from the Blender side (this is basic Bevy, no specific work needed)

![component registration](./docs/component_registration.png)

* setup & then use the Blenvy [Bevy crate](./crates/blenvy/README.md)
* setup & then use the Blenvy [Blender add-on](./tools/blenvy/README.md)
* iterate
* have fun !

* then add your components to objects in Blender **with a nice UI** see [here](./README-workflow-ui.md) for more details

See the [quickstart](./docs/quickstart/readme.md) for a full step-by-step guide.

## Third Party Integration

Read about the [Avian Physics Integration](docs/avian/readme.md) to learn how to setup colliders in Blender that will be used by the Avian physics engine in Bevy.

## Limitations / issues

* Some of `avian` or `bevy_rapier` /physics code / ways to define colliders could perhaps be done better/visually within Blender

## Contributors

Thanks to all the contributors helping out with this project ! Big kudos to you, contributions are always appreciated ! :)

* [GitGhillie](https://github.com/GitGhillie)
* [Azorlogh](https://github.com/Azorlogh)
* [BSDGuyShawn](https://github.com/BSDGuyShawn)
* [yukkop](https://github.com/yukkop)
* [killercup](https://github.com/killercup)
* [janhohenheim](https://github.com/janhohenheim)
* [BUGO07](https://github.com/BUGO07)

## License

This repo, all its code, contents & assets is Dual-licensed under either of

* Apache License, Version 2.0, ([LICENSE-APACHE](./LICENSE_APACHE.md) or <https://www.apache.org/licenses/LICENSE-2.0>)
* MIT license ([LICENSE-MIT](./LICENSE_MIT.md) or <https://opensource.org/licenses/MIT>)
