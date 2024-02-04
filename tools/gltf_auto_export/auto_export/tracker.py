import bpy
from bpy.types import (PropertyGroup)
from bpy.props import (PointerProperty)

from .internals import CollectionsToExport

class AutoExportTracker(PropertyGroup):

    changed_objects_per_scene = {}
    change_detection_enabled = True
    export_params_changed = False

    @classmethod
    def register(cls):
        bpy.types.WindowManager.auto_export_tracker = PointerProperty(type=AutoExportTracker)
        # register list of exportable collections
        bpy.types.WindowManager.exportedCollections = bpy.props.CollectionProperty(type=CollectionsToExport)

        # setup handlers for updates & saving
        #bpy.app.handlers.save_post.append(cls.save_handler)
        #bpy.app.handlers.depsgraph_update_post.append(cls.deps_update_handler)

    @classmethod
    def unregister(cls):
        # remove handlers & co
        """try:
            bpy.app.handlers.depsgraph_update_post.remove(cls.deps_update_handler)
        except:pass
        try:
            bpy.app.handlers.save_post.remove(cls.save_handler)
        except:pass"""
        del bpy.types.WindowManager.auto_export_tracker
        del bpy.types.WindowManager.exportedCollections

    @classmethod
    def save_handler(cls, scene, depsgraph):
        print("-------------")
        print("saved", bpy.data.filepath)
        # auto_export(changes_per_scene, export_parameters_changed)
        bpy.ops.export_scenes.auto_gltf(direct_mode= True)

        # (re)set a few things after exporting
        # reset wether the gltf export paramters were changed since the last save 
        cls.export_params_changed = False
        # reset whether there have been changed objects since the last save 
        cls.changed_objects_per_scene.clear()
        # all our logic is done, mark this as done
        print("EXPORT DONE")

    @classmethod
    def deps_update_handler(cls, scene, depsgraph):
        # print("change detection enabled", cls.change_detection_enabled)
        if scene.name != "temp_scene":
            #print("depsgraph_update_post", scene.name)
            changed_scene = scene.name or ""

            # only deal with changes if we are no in the mids of saving/exporting
            if cls.change_detection_enabled:
                #print("-------------")
                if not changed_scene in cls.changed_objects_per_scene:
                    cls.changed_objects_per_scene[changed_scene] = {}

                # depsgraph = bpy.context.evaluated_depsgraph_get()
                for obj in depsgraph.updates:
                    if isinstance(obj.id, bpy.types.Object):
                        # get the actual object
                        object = bpy.data.objects[obj.id.name]
                        # print("changed object", obj.id.name)
                        cls.changed_objects_per_scene[scene.name][obj.id.name] = object
                    elif isinstance(obj.id, bpy.types.Material): # or isinstance(obj.id, bpy.types.ShaderNodeTree):
                        # print("changed material", obj.id, "scene", scene.name,)
                        material = bpy.data.materials[obj.id.name]
                        #now find which objects are using the material
                        for obj in bpy.data.objects:
                            for slot in obj.material_slots:
                                if slot.material == material:
                                    cls.changed_objects_per_scene[scene.name][obj.name] = obj

                items = 0
                for scene_name in cls.changed_objects_per_scene:
                    items += len(cls.changed_objects_per_scene[scene_name].keys())
                if items == 0:
                    cls.changed_objects_per_scene.clear()
                #print("changed_objects_per_scene", cls.changed_objects_per_scene)
            else:
                cls.changed_objects_per_scene.clear()

    def disable_change_detection(self,):
        self.change_detection_enabled = False
        self.__class__.change_detection_enabled = False
    def enable_change_detection(self):
        self.change_detection_enabled = True
        self.__class__.change_detection_enabled = True

