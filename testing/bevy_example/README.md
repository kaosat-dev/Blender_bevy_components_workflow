# Bevy registry export example/demo

This example showcases 
* the use of the blenvy crate to extract all components & types information into a json file.
* That file is then used by the [Blender addon](https://github.com/kaosat-dev/Blenvy/tree/main/tools/bevy_components) to create Uis for each component,
to be able to add & edit Bevy components easilly in Blender !


## Running this example

```
cargo run --features bevy/dynamic_linking
```

Running the example also regenerates the registry.json file.
