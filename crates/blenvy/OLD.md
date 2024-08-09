
## SystemSet

the ordering of systems is very important ! 

For example to replace your proxy components (stand-in components when you cannot/ do not want to use real components in the gltf file) with actual ones, which should happen **AFTER** the Blueprint based spawning, 

so ```blenvy``` provides a **SystemSet** for that purpose: ```GltfBlueprintsSet```

Typically , the order of systems should be

***blenvy (GltfComponentsSet::Injection)*** => ***blenvy (GltfBlueprintsSet::Spawn, GltfBlueprintsSet::AfterSpawn)*** => ***replace_proxies***

see https://github.com/kaosat-dev/Blenvy/tree/main/examples/blenvy/basic for how to set it up correctly




