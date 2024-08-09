import bpy
from bpy.props import (StringProperty, BoolProperty, PointerProperty)
from bpy_types import (PropertyGroup)

from ..propGroups.conversions_from_prop_group import property_group_value_to_custom_property_value
from ..propGroups.conversions_to_prop_group import property_group_value_from_custom_property_value
from ..utils import add_component_to_ui_list

class ComponentMetadata(bpy.types.PropertyGroup):
    short_name : bpy.props.StringProperty(
        name = "name",
        default = ""
    ) # type: ignore

    long_name : bpy.props.StringProperty(
        name = "long name",
        default = ""
    ) # type: ignore

    values: bpy.props.StringProperty(
        name = "Value",
        default = ""
    ) # type: ignore

    enabled: BoolProperty(
        name="enabled",
        description="component enabled",
        default=True
    ) # type: ignore

    invalid: BoolProperty(
        name="invalid",
        description="component is invalid, because of missing registration/ other issues",
        default=False
    ) # type: ignore

    invalid_details: StringProperty(
        name="invalid details",
        description="detailed information about why the component is invalid",
        default=""
    ) # type: ignore

    visible: BoolProperty( # REALLY dislike doing this for UI control, but ok hack for now
        default=True
    ) # type: ignore

   

class ComponentsMeta(PropertyGroup):
    infos_per_component:  StringProperty(
        name="infos per component",
        description="component"
    ) # type: ignore
    components: bpy.props.CollectionProperty(type = ComponentMetadata)  # type: ignore

    # compone
    component_selector: StringProperty(
        search=add_component_to_ui_list
    ) # type: ignore


    @classmethod
    def register(cls):
        # you can add components to both objects , collections , meshes & materials
        bpy.types.Object.components_meta = PointerProperty(type=ComponentsMeta)
        bpy.types.Collection.components_meta = PointerProperty(type=ComponentsMeta)
        bpy.types.Mesh.components_meta = PointerProperty(type=ComponentsMeta)
        bpy.types.Material.components_meta = PointerProperty(type=ComponentsMeta)

    @classmethod
    def unregister(cls):
        del bpy.types.Object.components_meta
        del bpy.types.Collection.components_meta
        del bpy.types.Mesh.components_meta
        del bpy.types.Material.components_meta

# remove no longer valid metadata from item
def cleanup_invalid_metadata(item):
    bevy_components = get_bevy_components(item)
    if len(bevy_components.keys()) == 0: # no components, bail out
        return
    components_metadata = item.components_meta.components
    to_remove = []
    for index, component_meta in enumerate(components_metadata):
        long_name = component_meta.long_name
        if long_name not in bevy_components.keys():
            print("component:", long_name, "present in metadata, but not in item")
            to_remove.append(index)
    for index in to_remove:
        components_metadata.remove(index)


# returns a component definition ( an entry in registry's type_infos) with matching long name or None if nothing has been found
def find_component_definition_from_long_name(long_name):
    registry = bpy.context.window_manager.components_registry
    return registry.type_infos.get(long_name, None)

# FIXME: feels a bit heavy duty, should only be done
# if the components panel is active ?
def ensure_metadata_for_all_items():
    for object in bpy.data.objects:
        add_metadata_to_components_without_metadata(object)
    for collection in bpy.data.collections:
        add_metadata_to_components_without_metadata(collection)


# returns whether an item has custom properties without matching metadata
def do_item_custom_properties_have_missing_metadata(item):
    components_metadata = getattr(item, "components_meta", None)
    if components_metadata == None:
        return True

    components_metadata = components_metadata.components

    missing_metadata = False
    for component_name in get_bevy_components(item) :
        if component_name == "components_meta":
            continue
        component_meta =  next(filter(lambda component: component["long_name"] == component_name, components_metadata), None)
        if component_meta == None: 
            # current component has no metadata but is there even a compatible type in the registry ?
            # if not ignore it
            component_definition = find_component_definition_from_long_name(component_name)
            if component_definition is not None:
                missing_metadata = True
                break

    return missing_metadata


import json

def upsert_bevy_component(item, long_name, value):
    if not 'bevy_components' in item:
        item['bevy_components'] = '{}'
    bevy_components = json.loads(item['bevy_components'])
    bevy_components[long_name] = value
    item['bevy_components'] = json.dumps(bevy_components)
    #item['bevy_components'][long_name] = value # Sigh, this does not work, hits Blender's 63 char length limit

def remove_bevy_component(item, long_name):
    if 'bevy_components' in item:
        bevy_components = json.loads(item['bevy_components'])
        if long_name in bevy_components:
            del bevy_components[long_name]
            item['bevy_components'] = json.dumps(bevy_components)
    if long_name in item:
        del item[long_name]

def get_bevy_components(item):
    if 'bevy_components' in item:
        bevy_components = json.loads(item['bevy_components'])
        return bevy_components
    return {}

def get_bevy_component_value_by_long_name(item, long_name):
    bevy_components = get_bevy_components(item)
    if len(bevy_components.keys()) == 0 :
        return None
    return bevy_components.get(long_name, None)

def is_bevy_component_in_item(item, long_name):
    return get_bevy_component_value_by_long_name(item, long_name) is not None

# adds metadata to item only if it is missing
def add_metadata_to_components_without_metadata(item):
    registry = bpy.context.window_manager.components_registry

    for component_name in get_bevy_components(item) :
        if component_name == "components_meta":
            continue
        upsert_component_in_item(item, component_name, registry)

# adds a component to an item (including metadata) WITHOUT a component definition
def add_component_to_item_without_registry():
    pass

# adds a component to an item (including metadata) using the provided component definition & optional value
def add_component_to_item(item, component_definition, value=None):
    warnings = []
    cleanup_invalid_metadata(item)
    if item is not None:
        # print("add_component_to_item", component_definition)
        long_name = component_definition["long_name"]
        registry = bpy.context.window_manager.components_registry
        if not registry.has_type_infos():
            raise Exception('registry type infos have not been loaded yet or are missing !')
        definition = registry.type_infos[long_name]
        # now we use our pre_generated property groups to set the initial value of our custom property
        (_, propertyGroup) = upsert_component_in_item(item, long_name=long_name, registry=registry)
        if value == None:
            value = property_group_value_to_custom_property_value(propertyGroup, definition, registry, None)
        else: # we have provided a value, that is a raw , custom property value, to set the value of the propertyGroup
            item["__disable__update"] = True # disable update callback while we set the values of the propertyGroup "tree" (as a propertyGroup can contain other propertyGroups) 
            try:
                property_group_value_from_custom_property_value(propertyGroup, definition, registry, value)
            except:
                # if we failed to get the value, we default... to the default
                value = property_group_value_to_custom_property_value(propertyGroup, definition, registry, None)
                warnings.append(f"failed to get the initial value of {item.name}, using default value")
            del item["__disable__update"]
        upsert_bevy_component(item, long_name, value)
    return warnings
       
def upsert_component_in_item(item, long_name, registry):
    # print("upsert_component_in_item", item, "component name", component_name)
    # TODO: upsert this part too ?
    target_components_metadata = item.components_meta.components
    component_definition = registry.type_infos.get(long_name, None)
    if component_definition is not None:
        short_name = component_definition["short_name"]
        long_name = component_definition["long_name"]
        property_group_name = registry.get_propertyGroupName_from_longName(long_name)
        propertyGroup = None

        component_meta = next(filter(lambda component: component["long_name"] == long_name, target_components_metadata), None)
        if not component_meta:
            component_meta = target_components_metadata.add()
            component_meta.short_name = short_name
            component_meta.long_name = long_name
            propertyGroup = getattr(component_meta, property_group_name, None)
        else: # this one has metadata but we check that the relevant property group is present
            propertyGroup = getattr(component_meta, property_group_name, None)

        # try to inject propertyGroup if not present
        if propertyGroup == None:
            #print("propertygroup not found in metadata attempting to inject")
            if property_group_name in registry.component_propertyGroups:
                # we have found a matching property_group, so try to inject it
                # now inject property group
                setattr(ComponentMetadata, property_group_name, registry.component_propertyGroups[property_group_name]) # FIXME: not ideal as ALL instances of ComponentMetadata get the propGroup, but have not found a way to assign it per instance
                propertyGroup = getattr(component_meta, property_group_name, None)
        
        # now deal with property groups details
        if propertyGroup is not None:
            if long_name in registry.invalid_components:
                component_meta.enabled = False
                component_meta.invalid = True
                component_meta.invalid_details = "component contains fields that are not in the schema, disabling"
            else:
                # clear previous invalid state
                if not component_meta.enabled and component_meta.invalid and component_meta.invalid_details == "component contains fields that are not in the schema, disabling":
                    component_meta.enabled = True
                    component_meta.invalid = False
                    component_meta.invalid_details = ""
        else:
            # if we still have not found the property group, mark it as invalid
            component_meta.enabled = False
            component_meta.invalid = True
            component_meta.invalid_details = "component not present in the schema, possibly renamed? Disabling for now"
        # property_group_value_from_custom_property_value(propertyGroup, component_definition, registry, item[component_name])

        return (component_meta, propertyGroup)
    else:
        return(None, None)


def copy_propertyGroup_values_to_another_item(source_item, target_item, component_name, registry):
    if source_item == None or target_item == None or component_name == None:
        raise Exception('missing input data, cannot copy component propertryGroup')
    
    component_definition = find_component_definition_from_long_name(component_name)
    long_name = component_name
    property_group_name = registry.get_propertyGroupName_from_longName(long_name)

    registry = bpy.context.window_manager.components_registry

    source_components_metadata = source_item.components_meta.components
    source_componentMeta = next(filter(lambda component: component["long_name"] == long_name, source_components_metadata), None)
    # matching component means we already have this type of component 
    source_propertyGroup = getattr(source_componentMeta, property_group_name)

    # now deal with the target item
    (_, target_propertyGroup) = upsert_component_in_item(target_item, component_name, registry)
    # add to item
    value = property_group_value_to_custom_property_value(target_propertyGroup, component_definition, registry, None)
    upsert_bevy_component(target_item, long_name, value)

    # copy the values over 
    for field_name in source_propertyGroup.field_names:
        if field_name in source_propertyGroup:
            target_propertyGroup[field_name] = source_propertyGroup[field_name]
    apply_propertyGroup_values_to_item_customProperties(target_item)


# TODO: move to propgroups ?
def apply_propertyGroup_values_to_item_customProperties(item):
    cleanup_invalid_metadata(item)
    registry = bpy.context.window_manager.components_registry
    for component_name in get_bevy_components(item) :
        """if component_name == "components_meta":
            continue"""
        (_, propertyGroup) =  upsert_component_in_item(item, component_name, registry)
        component_definition = find_component_definition_from_long_name(component_name)
        if component_definition is not None:
            value = property_group_value_to_custom_property_value(propertyGroup, component_definition, registry, None)
            upsert_bevy_component(item=item, long_name=component_name, value=value)

# apply component value(s) to custom property of a single component
def apply_propertyGroup_values_to_item_customProperties_for_component(item, component_name):
    registry = bpy.context.window_manager.components_registry
    (_, propertyGroup) =  upsert_component_in_item(item, component_name, registry)
    component_definition = find_component_definition_from_long_name(component_name)
    if component_definition is not None:
        value = property_group_value_to_custom_property_value(propertyGroup, component_definition, registry, None)
        item[component_name] = value
    
    components_metadata = item.components_meta.components
    componentMeta = next(filter(lambda component: component["long_name"] == component_name, components_metadata), None)
    if componentMeta:
        componentMeta.invalid = False
        componentMeta.invalid_details = ""


def apply_customProperty_values_to_item_propertyGroups(item):
    print("apply custom properties to ", item.name)
    registry = bpy.context.window_manager.components_registry
    for component_name in get_bevy_components(item) :
        if component_name == "components_meta":
            continue
        component_definition = find_component_definition_from_long_name(component_name)
        if component_definition is not None:
            property_group_name = registry.get_propertyGroupName_from_longName(component_name)
            components_metadata = item.components_meta.components
            source_componentMeta = next(filter(lambda component: component["long_name"] == component_name, components_metadata), None)
            # matching component means we already have this type of component 
            propertyGroup = getattr(source_componentMeta, property_group_name, None)
            customProperty_value = get_bevy_component_value_by_long_name(item, component_name)
            #value = property_group_value_to_custom_property_value(propertyGroup, component_definition, registry, None)
            
            item["__disable__update"] = True # disable update callback while we set the values of the propertyGroup "tree" (as a propertyGroup can contain other propertyGroups) 
            property_group_value_from_custom_property_value(propertyGroup, component_definition, registry, customProperty_value)
            del item["__disable__update"]
            source_componentMeta.invalid = False
            source_componentMeta.invalid_details = ""

# removes the given component from the item: removes both the custom property and the matching metadata from the item
def remove_component_from_item(item, component_name):
    # remove the component value
    remove_bevy_component(item, component_name)

    # now remove the component's metadata
    components_metadata = getattr(item, "components_meta", None)
    if components_metadata == None:
        return False
    
    components_metadata = components_metadata.components
    to_remove = []
    for index, component_meta in enumerate(components_metadata):
        long_name = component_meta.long_name
        if long_name == component_name:
            to_remove.append(index)
            break
    for index in to_remove:
        components_metadata.remove(index)
    return True

def add_component_from_custom_property(item):
    add_metadata_to_components_without_metadata(item)
    apply_customProperty_values_to_item_propertyGroups(item)

def rename_component(registry, item, original_long_name, new_long_name):
    type_infos = registry.type_infos
    component_definition = type_infos[new_long_name]

    component_ron_value = get_bevy_component_value_by_long_name(item=item, long_name=original_long_name)
    if component_ron_value is None and original_long_name in item:
        component_ron_value = item[original_long_name]
    
    remove_component_from_item(item, original_long_name)
    print("remove & rename")
    return add_component_to_item(item, component_definition, component_ron_value)


def toggle_component(item, component_name):
    components_in_item = item.components_meta.components
    component_meta =  next(filter(lambda component: component["long_name"] == component_name, components_in_item), None)
    if component_meta is not None: 
        component_meta.visible = not component_meta.visible
