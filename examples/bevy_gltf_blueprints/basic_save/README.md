# Basic physics example/demo

This example showcases various components & blueprints extracted from the gltf files, including physics colliders & rigid bodies

## Notes Workflow with blender / demo information

This example, is actually closer to a boilerplate + tooling showcases how to use a minimalistic [Blender](https://www.blender.org/) (gltf) centric workflow for [Bevy](https://bevyengine.org/), ie defining entites & their components
inside Blender using Blender's objects **custom properties**.
Aka "Blender as editor for Bevy"

It also allows you to setup 'blueprints' in Blender by using collections (the recomended way to go most of the time), or directly on single use objects .


## Running this example

```
cargo run --features bevy/dynamic_linking
```

### Additional notes

* You usually define either the Components directly or use ```Proxy components``` that get replaced in Bevy systems with the actual Components that you want (usually when for some reason, ie external crates with unregistered components etc) you cannot use the components directly.
* this example contains code for future features, not finished yet ! please disregard anything related to saving & loading
