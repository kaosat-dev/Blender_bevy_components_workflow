Auto export
 - [x] the original blueprints & levels path are now left as is, and there is an auto injection of xxxpath_full for absolute paths
    - [x] replace all uses of the paths with the correct ones above
        - [x] levels
        - [x] blueprints
        - [x] materials
 - [x] move out the UI for "assets" folder out of "blueprints condition"
 - [x] fix asset path calculations
     - root path => relative to blend file path
     - asset path => relative to root path
     - blueprints/levels/blueprints path => relative to assets path
 - [ ] add error handling for de/serialization of project, so that in case of error, the previous saved serialized project is thrown away

- move out some parameters from auto export to a higher level (as they are now used in multiple places)
    - [x] main/ library scene names
    - [x] paths

- [x] Data storage for custom properties:
    - for scenes (main scenes)
        - at scene level
    - for blueprints 
        - at collection level
        - Note: these should be COPIED to the scene level when exporting, into the temp_scene's properties

    > NOTE: UP until we manage to create a PR for Bevy to directly support the scene level gltf_extras, the auto exporter should automatically create (& remove)
        any additional object with scene_<scene_name>_components to copy that data to

Assets:
    - blueprint assets should be auto_generated & inserted into the list of assets : these assets are NOT removable by the user
    - should not change the list of manually added assets
 - [x] store assets 
   - [x] per main scene for level/world assets
   - [x] per blueprint for blueprint in lib scene
 - [x] UI:
    - [x] we need to display all direct assets (stored in the scene)
    - [ ] indirect assets: 
        - QUESTION : do we want to include them in the list of assets per level ? 
            -  this would enable pre-loading ALL the assets, but is not ideal in most other cases
            - so add an option ?
        - [x] the assets of local blueprints 

Blueprints:
    - [x] on save: write IN THE COLLECTION PROPERTIES
        - list of assets
        - export path
    - [x] blueprint selection for nested blueprints is broken

    - [ ] scan & inject on load
    - [ ] scan & inject on save
    - [ ] decide where & when to do & store blueprints data

Components:
    - [x] add support for adding components to collections
    - [x] upgrade all operators:
        - [x] add 
        - [x] remove
        - [x] copy & paste
        - [x] BLENVY_OT_component_rename_component
        - [x] BLENVY_OT_component_fix
    - [x] add handling for core::ops::Range<f32> & other ranges
    - [x] fix is_component_valid that is used in blenvy 
    - [x] Hashmap Support
        - [x] fix parsing of keys's type either on Bevy side (prefered) or on the Blender side 
        - [x] fix weird issue with missing "0" property when adding new entry in empty hashmap => happens only if the values for the "setter" have never been set
        - [x] handle missing types in registry for keys & values
        - [x] adding a hashmap nukes every existing component ??
    - [x] Add correct upgrade handling from individual component to bevy_components
    - [x] Settings handling:
        - [x] move saveable settings out to a settings file
        - [x] update save & load
        - [x] add handling of polling frequency & enabling
    - [x] move advanced tools to components tab
    - [x] remove most of the (bulk) advanced tools, too complex, too unclear (even for me !) and of limited use
        - component renaming should be kept, but perhaps simplified: 
            - if a renaming fails because the parameters are incompatible, nuke the old parameters
        - perhaps just add a display list of all NON component custom properties, so the user can find them easilly ?
        - [x] status "unregistered" is often false and misleading
            -> see in registry ui "for custom_property in object.keys():"
    - [x] overhaul / improve the component selector (with built in searching, etc)
    - [x] remove select_component_name_to_replace
    - [x] display of invalid components is not working ?
    - [x] weird items are present in the components list that do not seem to be components
    - [x] remove :
        - BLENVY_OT_component_list_add_item
        - BLENVY_OT_component_list_remove_item
        - BLENVY_OT_component_list_select_item: merge it into the rest of the actions 
    - [x] clearing invalid flag after a registry change does not work correctly (ie the ui still says the component is invalid)
        - [x] should reset ALL "invalid" flags IF they have the matching data
    - [x] registry auto reload not working ?
    - [x] changing the registry breaks all the values of existing components !!!!!!
        -> VERY likely due to the int-offset computation for hashes of components
        - now switched to tiger_hash
        - [x] add warning about hash colision (not much we can/ could do if it is the case ?)
        - [x] double check weird collisions AND/OR reuse existing if applicable
    - [x] annoying default path for registry, should be relative to the assets path


General things to solve:
 - [x] save settings
 - [x] load settings
    - [x] add blueprints data

- [x] rename all path stuff using the old naming convention : "blueprints_path_full"
- [x] generate the full paths directly when setting them in the UI  
    - [x] problem : how to deal with defaults: do it on start/load ?
- [x] filter out scenes that have already been used in scenes list

General issues:
 - there is no safeguard for naming collisions for naming across blender files
 - this can cause an issue for assets list "parent" 
 - "parents" can only be blueprints
    - they normally need/have unique export paths (otherwise, user error, perhaps show it ?)
    - perhaps a simple hashing of the parent's path would be enought 

 - [x] addon-prefs => settings
 - [x] generate_gltf_export_settings => should not use add-on prefs at all ? since we are not overriding gltf settings that way anymore ?
 - [x] remove hard coded path for standard gltf settings
 - [x] load settings on file load
    - [x] auto_export
    - [x] components
    - [x] add handling of errors when trying to load settings

- [x] fix auto export workflow
- [x] add hashing of modifiers/ geometry nodes in serialize scene
- [x] add ability to FORCE export specific blueprints & levels
- [x] change scene selector to work on actual scenes aka to deal with renamed scenes
    - [x] remove get_main_and_library_scenes as it should not be needed anymore
- [x] fix asset file selection
- [x] change "assets" tab to "levels"/worlds tab & modify UI accordingly
- [x] remove local assets, useless
- [x] remove 'export_marked_assets' it should be a default setting
- [x] disable/ hide asset editing ui for external assets
- [x] fix level asets UI 
- [x] remove BlueprintsList & replace is with assets list
- [x] switch to bevy 0.14 rc2
- [x] trigger events when assets are loaded, blueprints are spawned & co
- [x] overall cleanup
    - [x] object.add_bevy_component => blenvy.component_add

Blender side:
- [x] force overwrite of settings files instead of partial updates ?
- [x] prevent loop when loading/setting/saving settings
- [x] fix asset changes not being detected as a scene change
- [x] fix scene setting changes not being detected as a scene change
- [x] add back lighting_components
- [x] check if scene components are being deleted through our scene re-orgs in the spawn post process
- [x] fix unreliable project hashing between sessions: (note, it is due to the use of hash() : https://stackoverflow.com/questions/27522626/hash-function-in-python-3-3-returns-different-results-between-sessions)
- [x] figure out why there are still changes per session (it is due to object pointer being present in the generated "hash")
    - materials & modifiers, both using the same underlying logic
        - [x] filter out components_meta
        - [x] filter out xxx_ui propgroups
- [x] fix missing main/lib scene names in blenvy_common_settings
- [x] fix incorect updating of main/lib scenes list in settings
- [ ] add handling of scene renames
    - [x] store (on load) a mapping of scene objects to scene names
    - [x] on save, calculate another mapping of scene objects to scene names
        - if there is a mismatch between the stored version & the new version for a given scene, it has been renamed !
    - [x] pass this information to scene diffing to remap old/new scene names
    - [ ] move the rename detection to AFTER scene serialization, otherwise we could have a naming mistmatch
        - weird behaviour, perhaps find another way , ie for example replace scene name in saved previous data
        - is post save causing the issue ? review
- [x] investigate weird issue of changes detected to all after a reload 

- [x] should we write the previous _xxx data only AFTER a sucessfull export only ?
- [x] finer grained control of setting changes to trigger a re-export:
    - [x] common: any of them should trigger
    - [x] components: none
    - [x] auto_export:
        - auto_export: yes
        - gltf settings: yes
        - change detection: no ?
        - export blueprints: YES
            - export split dynamic/static: YES
            - export merge mode : YES
            - materials: YES
- [x] blenvy tooling not appearing in library scenes ?? (edit: was actually , it was not appearing in anything but object mode)
- [x] find a solution for the new color handling 
    - [x] in theory, srgba, linearrgba , and hsva should be able to be represented visually
    - [x] bevy_render::color::Color => bevy_color::color::Color
- [x] fix weird issue with hashmaps with enums as values
- [x] prevent attempting to add unexisting components to targets (ie when using the component search)
    - [x] also for the bulk fix actions
- [x] selection of nested objects in collections IS NOT WORKING !!! AHH
- [x] fix/ overhaul upgreadable components
    - [x] add listing of upgradeable components for
        - [x] meshes
        - [x] materials
    - [x] fix display of upgradeaeble components & co
    - [x] add clear visual distinction between internal (selectable) & non selectable ones
    - [x] do not make selection button available for external blueprints/collections 
        - [x] perhaps do not show the other buttons & inputs either ? we cannot change the values of an external library file anyway

- [x] BLENVY_OT_item_select is missing handling for the other types (outside of object & collection)
    - [x] fix selection logic 
- [x] update testing blend files
- [x] disable 'export_hierarchy_full_collections' for all cases: not reliable and redudant
- [x] fix systematic material exports despite no changes
- [x] investigate lack of detection of changes of adding/changing components
    - [x] change scene serialization to account for collections ...sigh
    - [x] also add one NOT PER scene for materials, to fix the above issue with materials
    - [x] move material caching into hash material
- [x] also remove ____dummy____.bin when export format is gltf

- [ ] fix/cleanup asset information injection (also needed for hot reload)
    - [ ] add back per blueprint assets
    - [ ] reuse the already existing asset_scan + export thing
    - thoughts: 
       - the "list of all assets" is actually the "fake"/generated one: nobody would write a list of assets for sub assets,
    you would just add the assets to your blueprint
       - in Bevy at spawning we have
               blueprint => assets
            for hot reload we need
               asset => blueprint instances so we can despawn/respawn etc blueprint instances when one of their assets has changed 

               problem of untyped vs typed
               perhaps have a mapping of untyped => typed id
               map asset id => [entity ids]

- [ ] add option to 'split out' meshes from blueprints ? 
    - [ ] ie considering meshletts etc , it would make sense to keep blueprints seperate from purely mesh gltfs

- [ ] materials fixes & upgrades
    - [x] materials do not get exported again if the files are missing, until you change a material
    - [x] materials do not get exported when a material is added ?
    - [x] add_material_info_to_objects is now called AFTER the blueprint export, making it useless, needs change !
    - [ ] materials_path custom property should be ignored both in the list of fixable component AND on export
    - [ ] if we want to add material_infos & others as normal components they should not be editable, so we need another attribute, and adapt the UI for that

    - [x] injection of materials_infos should be done outside of export_materials as it should run even if materials do not need exporting

    - [x] if material library is toggled, then changes to materials should not change the blueprints that are using them => not really: as the name & co might change
    - [ ] material assets seem to be added to list regardless of whether material exports are enabled or not
    - [x] review & upgrade overall logic of material libraries, their names & output path
    - [x] change materials logic to work with multiple materials per mesh
        - [x] the index of the generated gltf files is reliable, and can be used both in Blender & Bevy
        - [x] change MaterialInfo to MaterialInfos & turn it into a vec/list & updated logic both on Blender & Bevy side
    - [ ] persist exported materials paths in blueprints so that it can be read from library file users
        - [ ] just like "export_path" write it into each blueprint's collection
        - [ ] scan for used materials per blueprint !
        - [ ] for scenes, scan for used materials of all non instance objects (TODO: what about overrides ?)

- [ ] add a way of visualizing per blueprint instances ?
- [ ] display export path of blueprints (mostly external) ?
- [ ] hidden objects/collections only semi respected at export
    - this is because blueprints are external ?
    - [ ] verify based on gltf settings
    - [ ] add "Visibility::Hidden" component otherwise 
        https://devtalk.blender.org/t/how-to-get-render-visibility-for-object/23717

- [ ] inject_export_path_into_internal_blueprints should be called on every asset/blueprint scan !! Not just on export
- [ ] undo after a save removes any saved "serialized scene" data ? DIG into this
- [ ] add tests for
    - [ ] disabled components 
    - [ ] blueprint instances as children of blueprint instances
    - [ ] blueprint instances as children of empties

- [x] check/ fix behaviour of blender plugin if all folders are the same (ie, all in assets for example)
- [x] rename all "main scene xx" to "level scene"
- [x] make sure the "add scene" button is not available unless you have actually selected one
- [x] make auto export be on by default, however bail out early by detecting if there are any level/blueprint scenes
- [x] remove custom components to filter out correctly from exported blueprints list 
- [ ] for built in Component types that need to be injected to be used by blueprints, 
      namely: 
    - BlueprintInfos (not 100% sure for this one)
    - MaterialInfos
    - the various scene Components 
    - BlueprintAssets (although not really needed anymore with the meta files)

    - [ ] Inject real components instead of just custom properties
    - [ ] add boilerplate to generate real component values from type definitions instead of hacking pseudo ron strings
    - [ ] fall back to bevy_components if that fails (missing registry) or just basic custom properties
    - [ ] If that fails as well ?
- [ ] auto reload registry if absent/possible
    - cannot be done from UI possibly polling with increasing timeout
    - bpy.ops.blenvy.components_registry_reload()
    - double check bpy.context.components_registry

- [x] filter out MaterialInfos from list of "fixable components"


Bevy Side:
- [x] deprecate BlueprintName & BlueprintPath & use BlueprintInfo instead
- [x] make blueprint instances invisible until spawning is done to avoid "spawn flash"?
    - [x] make this controlable via an additional "HideUntilReady" component
    - [x] register "HideUntilReady" so users can set this on their blueprints in Blender directly
- [x] restructure blueprint spawning 
    - [x] "blueprint ready" only be triggered after all its sub blueprints are ready 
    - [x] "blueprintInstance ready"/finished
        BlueprintAssetsLoaded
        BlueprintSceneSpawned
        BlueprintChildrenReady
        BlueprintReadyForPostProcess
    - [x] fix issues with deeply nested blueprints
        - perhaps reverse logic by using iter_ascendants
    - [x] fix materials handling
    - [ ] fix animations handling
        - [x] fix/upgrade blueprint level animations
        - [x] fix/upgrade scene level animations
        - [x] rename SceneAnimations to InstanceAnimations (more coherent with the rest)
        - [ ] add back & cleanup animation frame triggers
    - [x] move sub blueprint handling to blueprints_finalize_instances
- [x] look into component overriding , it seems broken:
    - [x] blueprint level/ collection level components are now visible in instances in Blender
    - [x] they do not seem to be transfered to the (instance) entity above:
        could they be on the "empty node" ? 

- [ ] simplify testing example:
    - [x] remove use of rapier physics (or even the whole common boilerplate ?)
    - [ ] remove/replace bevy editor pls with some native ui to display hierarchies
    - [ ] a full fledged demo (including physics & co)
    - [ ] other examples without interactions or physics 

- [ ] add hot reloading
    - [x] basics
    - [x] make it enabled/disabled based on general flag
    - [x] account for changes impact both parent & children (ie "world" and "blueprint3") for example, which leads to a crash as there is double despawn /respawn so we need to filter things out 
    - [x] if there are many assets/blueprints that have changed at the same time, it causes issues similar to the above, so apply a similar fix
        - [x] also ignore any entities currently spawning (better to loose some information, than cause a crash)
    - [x] for sub blueprint tracking: do not propagate/ deal with parent blueprints if they are not themselves Spawning (ie filter out by "BlueprintSpawning")
    - [x] cleanup internals
    - [ ] analyse what is off with blueprint level components 
    - [x] add the root blueprint itself to the assets either on the blender side or on the bevy side programatically
    - [ ] invalidate despawned entity & parent entities AABB 
    - [ ] add unloading/cache removal of materials

- [ ] add back and upgrade save-load

- [x] review & change general component insertion & spawning ordering & logic
    - GltfComponentsSet::Injection => GltfBlueprintsSet::Spawn => GltfBlueprintsSet::AfterSpawn
        Injection => inject lights & co => spawn => afterSpawn
                                                 => Injection => inject lights & co 

- [ ] add a way of overriding assets for collection instances => how can we make this possible
- [ ] cleanup all the spurious debug messages
- [x] fix animation handling
    - [x] how to deal with animation graphs ?


- [x] remove "Library" component & co
- [x] make "InBlueprint" non optional, 
- [x] and perhaps rename it to "FromBlueprint"
- [ ] perhaps change it to FromBlueprint(BlueprintInfo)
    - [ ] in order for this to work correctly, stop iterating descendants as soon as there is one with an Existing FromBlueprint component

- [x] BlueprintInstanceDisabled => BlueprintInstanceDisabled
- [x] fix "remove component" operator from the rename/fix/update components panel
- [ ] replace string in BlueprintInfo path with PathBuf ?

- [x] update main docs
    - [x] rename project to Blenvy
    - [x] replace all references to the old 2 add-ons with those to Blenvy
- [x] rename repo to "Blenvy"
- [x] do a deprecation release of all bevy_gltf_xxx crates to point at the new Blenvy crate
- [ ] consider finding a way of having unique ids for all objects & collections in Blender (not trivial, if not impossible)
    this would allow things such as 
        - [ ] mapping uuids to blueprint paths
        - [ ] solving problems with scene renames
        - [ ] the ability to map external TEXT files to data in BLender (git-able, hand editable)
- [x] make aabbs calculation non configurable, getting rid of the last setting (for now)
- [ ] add information & screenshots about adding assets to the Blender add-on docs
- [x] finally deal cleanly with gltf export failures & make sure to always reset the state of the blend file

clear && pytest -svv --blender-template ../../testing/bevy_example/art/testing_library.blend --blender-executable /home/ckaos/tools/blender/blender-4.1.0-linux-x64/blender tests/test_bevy_integration_prepare.py  && pytest -svv --blender-executable /home/ckaos/tools/blender/blender-4.1.0-linux-x64/blender tests/test_bevy_integration.py