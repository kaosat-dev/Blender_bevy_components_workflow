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

## Wasm instructions

### Setup

as per the bevy documentation:

```shell
rustup target add wasm32-unknown-unknown
cargo install wasm-bindgen-cli
```


### Building this example

navigate to the current folder , and then

```shell
cargo build --release --target wasm32-unknown-unknown --target-dir ./target
wasm-bindgen --out-name wasm_example \
  --out-dir ./target/wasm \
  --target web target/wasm32-unknown-unknown/release/bevy_gltf_blueprints_basic_wasm_example.wasm

```

### Running this example

run a web server in the current folder, and navigate to the page, you should see the example in your browser


## Additional notes

* You usually define either the Components directly or use ```Proxy components``` that get replaced in Bevy systems with the actual Components that you want (usually when for some reason, ie external crates with unregistered components etc) you cannot use the components directly.
* this example contains code for future features, not finished yet ! please disregard anything related to saving & loading
