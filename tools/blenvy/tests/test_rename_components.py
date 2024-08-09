import json
import re
import bpy
import pprint
import pytest

from ..bevy_components.components.metadata import get_bevy_component_value_by_long_name, get_bevy_components, is_bevy_component_in_item, upsert_bevy_component

from .setup_data import setup_data

# small helpers
def get_component_metadata(object, component_name):
    target_components_metadata = object.components_meta.components
    component_meta = next(filter(lambda component: component["long_name"] == component_name, target_components_metadata), None)
    return component_meta

def get_component_propGroup(registry, component_name, component_meta):
    # component_type = registry.short_names_to_long_names[component_name]
    # add_component_operator = bpy.ops.object.add_bevy_component
    property_group_name = registry.get_propertyGroupName_from_longName(component_name)
    propertyGroup = getattr(component_meta, property_group_name, None)
    return propertyGroup


def test_rename_component_single_unit_struct(setup_data):
    registry = bpy.context.window_manager.components_registry
    registry.schema_path = setup_data["components_schemaPath"]
    bpy.ops.object.reload_registry()

    rename_component_operator = bpy.ops.blenvy.component_rename
    object = bpy.context.object


    source_component_name = "bevy_example::test_components::SomeOldUnitStruct"
    target_component_name = "bevy_example::test_components::UnitTest"
    upsert_bevy_component(object, source_component_name, '()')

    rename_component_operator(original_name=source_component_name, new_name=target_component_name, target_objects=json.dumps([object.name]))

    is_old_component_in_object = is_bevy_component_in_item(object, source_component_name)
    is_new_component_in_object = is_bevy_component_in_item(object, target_component_name)
    assert is_old_component_in_object == False
    assert is_new_component_in_object == True
    assert get_bevy_component_value_by_long_name(object, target_component_name) == '()'
    assert get_component_propGroup(registry, target_component_name, get_component_metadata(object, target_component_name)) is not None

    
def test_rename_component_single_complex_struct(setup_data):
    registry = bpy.context.window_manager.components_registry
    registry.schema_path = setup_data["components_schemaPath"]
    bpy.ops.object.reload_registry()

    rename_component_operator = bpy.ops.blenvy.component_rename
    object = bpy.context.object


    source_component_name = "bevy_example::test_components::ProxyCollider"
    target_component_name = "bevy_gltf_worlflow_examples_common_rapier::physics::physics_replace_proxies::Collider"
    upsert_bevy_component(object, source_component_name, 'Capsule(Vec3(x:1.0, y:2.0, z:0.0), Vec3(x:0.0, y:0.0, z:0.0), 3.0)')

    rename_component_operator(original_name=source_component_name, new_name=target_component_name, target_objects=json.dumps([object.name]))

    is_old_component_in_object = is_bevy_component_in_item(object, source_component_name)
    is_new_component_in_object = is_bevy_component_in_item(object, target_component_name)
    assert is_old_component_in_object == False
    assert is_new_component_in_object == True
    assert get_bevy_component_value_by_long_name(object, target_component_name) == 'Capsule(Vec3(x:1.0, y:2.0, z:0.0), Vec3(x:0.0, y:0.0, z:0.0), 3.0)'
    assert get_component_propGroup(registry, target_component_name, get_component_metadata(object, target_component_name)) is not None


def test_rename_component_bulk(setup_data):
    registry = bpy.context.window_manager.components_registry
    registry.schema_path = setup_data["components_schemaPath"]
    bpy.ops.object.reload_registry()

    rename_component_operator = bpy.ops.blenvy.component_rename

    source_component_name = "bevy_example::test_components::SomeOldUnitStruct"
    target_component_name = "bevy_example::test_components::UnitTest"
    objects_names = []
    for object in bpy.data.objects:
        upsert_bevy_component(object, source_component_name, '()')
        objects_names.append(object.name)

    # bulk rename
    rename_component_operator(original_name=source_component_name, new_name=target_component_name, target_objects=json.dumps(objects_names))

    for object in bpy.data.objects:
        is_old_component_in_object = is_bevy_component_in_item(object, source_component_name)
        is_new_component_in_object = is_bevy_component_in_item(object, target_component_name)
        assert is_old_component_in_object == False
        assert is_new_component_in_object == True
        assert get_bevy_component_value_by_long_name(object, target_component_name) == '()'
        assert get_component_propGroup(registry, target_component_name, get_component_metadata(object, target_component_name)) is not None

def test_rename_component_single_error_handling(setup_data):
    registry = bpy.context.window_manager.components_registry
    registry.schema_path = setup_data["components_schemaPath"]
    bpy.ops.object.reload_registry()

    rename_component_operator = bpy.ops.blenvy.component_rename
    object = bpy.context.object


    source_component_name = "bevy_example::test_components::SomeOldUnitStruct"
    target_component_name = "bevy_example::test_components::UnitTest"
    upsert_bevy_component(object, source_component_name, 'Capsule(Vec3(x:1.0, y:2.0, z:0.0), Vec3(x:0.0, y:0.0, z:0.0), 3.0)')

    expected_error = f'Error: Failed to rename component: Errors:["wrong custom property values to generate target component: object: \'{object.name}\', error: input string too big for a unit struct"]\n'
    expected_error = re.escape(expected_error)
    with pytest.raises(Exception, match=expected_error):   
        rename_component_operator(original_name=source_component_name, new_name=target_component_name, target_objects=json.dumps([object.name]))
    
    target_component_metadata = get_component_metadata(object, target_component_name)

    is_old_component_in_object = is_bevy_component_in_item(object, source_component_name)
    is_new_component_in_object = is_bevy_component_in_item(object, target_component_name)
    assert is_old_component_in_object == False
    assert is_new_component_in_object == True
    assert get_bevy_component_value_by_long_name(object, target_component_name) == 'Capsule(Vec3(x:1.0, y:2.0, z:0.0), Vec3(x:0.0, y:0.0, z:0.0), 3.0)'
    assert get_component_propGroup(registry, target_component_name, target_component_metadata) is not None
    assert target_component_metadata.invalid == True
    
    assert target_component_metadata.invalid_details == 'wrong custom property value, overwrite them by changing the values in the ui or change them & regenerate'

def test_rename_component_single_error_handling_clean_errors(setup_data):
    registry = bpy.context.window_manager.components_registry
    registry.schema_path = setup_data["components_schemaPath"]
    bpy.ops.object.reload_registry()

    rename_component_operator = bpy.ops.blenvy.component_rename
    object = bpy.context.object


    source_component_name = "bevy_example::test_components::SomeOldUnitStruct"
    target_component_name = "bevy_example::test_components::UnitTest"
    upsert_bevy_component(object, source_component_name, 'Capsule(Vec3(x:1.0, y:2.0, z:0.0), Vec3(x:0.0, y:0.0, z:0.0), 3.0)')

    expected_error = f'Error: Failed to rename component: Errors:["wrong custom property values to generate target component: object: \'{object.name}\', error: input string too big for a unit struct"]\n'
    expected_error = re.escape(expected_error)
    with pytest.raises(Exception, match=expected_error):   
        rename_component_operator(original_name=source_component_name, new_name=target_component_name, target_objects=json.dumps([object.name]))
    
    target_component_metadata = get_component_metadata(object, target_component_name)

    is_old_component_in_object = is_bevy_component_in_item(object, source_component_name)
    is_new_component_in_object = is_bevy_component_in_item(object, target_component_name)
    assert is_old_component_in_object == False
    assert is_new_component_in_object == True
    assert get_bevy_component_value_by_long_name(object, target_component_name) == 'Capsule(Vec3(x:1.0, y:2.0, z:0.0), Vec3(x:0.0, y:0.0, z:0.0), 3.0)'
    assert get_component_propGroup(registry, target_component_name, target_component_metadata) is not None
    assert target_component_metadata.invalid == True
    
    assert target_component_metadata.invalid_details == 'wrong custom property value, overwrite them by changing the values in the ui or change them & regenerate'

    # if we fix the custom property value & regen the ui, it should be all good
    regen_component_operator = bpy.ops.object.refresh_ui_from_custom_properties_current
    object[target_component_name] = ''
    regen_component_operator()

    assert target_component_metadata.invalid == False
