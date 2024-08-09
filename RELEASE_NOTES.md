This new release has a lot of breaking changes in the Blender tooling as well as in the Bevy crates
Here is a rundown + rationale behing the changes:


- Blender add-ons
    - Auto_export: 
        - spliting out of gltf exporter settings
            up until now , the auto export add-on provided a *subset* of gltf settings, causing issues due to lack of features (in particular for animation settings),
            and it required me to play catch up every time there where added / changed settings
            the Ui of Blender's gltf exporter is NOT reusable in any form or way inside another add-on . I tried various solutions such as turning the auto exporter
            into a 'extension' of the standard exporter, but none of them worked in a reliable or 'nice to use' way

            So I decided to split the gltf settings from the auto_export setting, this has multiple advantages:
                * access to ALL gltf settings
                * the gltf UI & settings will always keep up with the official releases
                * less maintenance work

            The only disadvantage is that the standard gltf exporter is a normal exporter, so it generates a 'fake' gltf file that immediatly gets deleted after export, 
            so you will need to use the new side panel to set your gltf settings:
             * this is also done to ensure that the gltf settings settings used for auto export are NOT interfering with the ones you might use when exporting gltf files normally

        - change detection :
        after spending MANY hours analysing the issues with change detection (using some of Blender's built in logic) I came to the conclusion that it was not going to be reliable enough, so I opted for a 'hand made' brute force approach to change detection:
         * every time you save (& thus export), all your scenes are serialized / hashed and that hashed version is compared to the one from the last save to determine what changed and what did not

        - handling of external/ embeded / split etc collections
            while adding tests I also realised that the detection of which main scenes & blueprints that needed to be exported was faulty, so I rewrote all the code in charge of that : this means that in general , based on your settings, the add-on will more accuratly export only those levels/blueprints that really NEED to be exported
        
        - improved handling of multi-blend file projects
            Up until now, all export paths where relative ** to the blend file itself** which could lead to issues when working with multiple blend files
            Also for future improvements regarding assets managment, I changed the export paths to be relative to a new "project root" folder which is your *Bevy project's root folder*
            - the levels/worlds now also got a seperate setting so you can easilly set where to export them too (they are not dumped out into the main export folder anymore), giving you more control over your non blueprint exports

    - bevy_components
        Up until now , it was not possible to have multiple components with the same name (ie ) as all the logic was based on short names
        This required completely changing HOW/WHERE components are stored in objects, and they are now stored inside a 'bevy_components' custom property