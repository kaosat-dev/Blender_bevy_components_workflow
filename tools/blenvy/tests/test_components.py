import bpy
import pprint

from ..bevy_components.propGroups.conversions_to_prop_group import property_group_value_from_custom_property_value
from ..bevy_components.propGroups.conversions_from_prop_group import property_group_value_to_custom_property_value
from .component_values_shuffler import component_values_shuffler
from .expected_component_values import (expected_custom_property_values, expected_custom_property_values_randomized)
from ..bevy_components.components.metadata import get_bevy_component_value_by_long_name, get_bevy_components, upsert_bevy_component

from .setup_data import setup_data

def test_components_should_generate_correct_custom_properties(setup_data):
    registry = bpy.context.window_manager.components_registry
    registry.schema_path = setup_data["components_schemaPath"]
    bpy.ops.object.reload_registry()

    type_infos = registry.type_infos
    object = bpy.context.object

    add_component_operator = bpy.ops.object.add_bevy_component
    errors = []
    addable_components = []
    added_components = []

    custom_property_values = {}
    
    for long_name in type_infos:
        definition = type_infos[long_name]
        long_name = definition["long_name"]
        is_component = definition['isComponent']  if "isComponent" in definition else False
        if not is_component:
            continue

        addable_components.append(long_name)

        try:
            add_component_operator(component_type=long_name)

            property_group_name = registry.get_propertyGroupName_from_longName(long_name)

            target_components_metadata = object.components_meta.components
            component_meta = next(filter(lambda component: component["long_name"] == long_name, target_components_metadata), None)
            propertyGroup = getattr(component_meta, property_group_name, None)
            added_components.append(long_name)
            custom_property_values[long_name] = get_bevy_component_value_by_long_name(object, long_name)
            assert get_bevy_component_value_by_long_name(object, long_name) == expected_custom_property_values[long_name]

        except Exception as error:
            errors.append(error)

    pp = pprint.PrettyPrinter(depth=14, width=120)
    print("CUSTOM PROPERTY VALUES")
    pp.pprint(custom_property_values)

    assert len(errors) == 0
    assert len(added_components) == 173

    
def test_components_should_generate_correct_custom_properties_with_randomized_values(setup_data):
    registry = bpy.context.window_manager.components_registry
    registry.schema_path = setup_data["components_schemaPath"]
    bpy.ops.object.reload_registry()

    type_infos = registry.type_infos
    object = bpy.context.object

    add_component_operator = bpy.ops.object.add_bevy_component
    errors = []
    error_components = []
    addable_components = []
    added_components = []

    custom_property_values = {}
    
    for long_name in type_infos:
        definition = type_infos[long_name]
        long_name = definition["long_name"]
        is_component = definition['isComponent']  if "isComponent" in definition else False
        if not is_component:
            continue

        addable_components.append(long_name)

        try:
            add_component_operator(component_type=long_name)
            property_group_name = registry.get_propertyGroupName_from_longName(long_name)

            target_components_metadata = object.components_meta.components
            component_meta = next(filter(lambda component: component["long_name"] == long_name, target_components_metadata), None)
            propertyGroup = getattr(component_meta, property_group_name, None)
            component_values_shuffler(seed= 10, property_group=propertyGroup, definition=definition, registry=registry)

            added_components.append(long_name)
            custom_property_values[long_name] = get_bevy_component_value_by_long_name(object, long_name)
            assert get_bevy_component_value_by_long_name(object, long_name) == expected_custom_property_values_randomized[long_name]

        except Exception as error:
            errors.append(error)
            error_components.append(long_name)

    pp = pprint.PrettyPrinter(depth=14, width=120)
    print("CUSTOM PROPERTY VALUES")
    pp.pprint(custom_property_values)

    print("error_components", error_components)
    assert len(errors) == 0
    assert len(added_components) == 173

def test_components_should_generate_correct_propertyGroup_values_from_custom_properties(setup_data):
    registry = bpy.context.window_manager.components_registry
    registry.schema_path = setup_data["components_schemaPath"]
    bpy.ops.object.reload_registry()

    type_infos = registry.type_infos
    object = bpy.context.object

    add_component_operator = bpy.ops.object.add_bevy_component
    errors = []
    addable_components = []
    added_components = []
    failing_components = []

    for long_name in type_infos:
        definition = type_infos[long_name]
        long_name = definition["long_name"]
        is_component = definition['isComponent']  if "isComponent" in definition else False
        if not is_component:
            continue

        addable_components.append(long_name)

        try:
            add_component_operator(component_type=long_name)
            property_group_name = registry.get_propertyGroupName_from_longName(long_name)

            target_components_metadata = object.components_meta.components
            component_meta = next(filter(lambda component: component["long_name"] == long_name, target_components_metadata), None)
            propertyGroup = getattr(component_meta, property_group_name, None)
            added_components.append(long_name)
            # randomise values
            component_values_shuffler(seed= 10, property_group=propertyGroup, definition=definition, registry=registry)
            custom_property_value = get_bevy_component_value_by_long_name(object, long_name)

            # first check if custom property value matches what we expect
            assert custom_property_value == expected_custom_property_values_randomized[long_name]

            # we update propgroup values from custom property values
            property_group_value_from_custom_property_value(propertyGroup, definition, registry, custom_property_value, nesting = [])
            # and then generate it back
            custom_property_value_regen = property_group_value_to_custom_property_value(propertyGroup, definition, registry, None)
            assert custom_property_value_regen == expected_custom_property_values_randomized[long_name]

            # custom_property_values[long_name] = object[long_name]
            #assert object[long_name] == expected_custom_property_values[long_name]
            #print("CUSTOM PROPERTY ", object[long_name])

        except Exception as error:
            errors.append(error)
            failing_components.append(long_name)

    for index, error in enumerate(errors):
        print("ERROR", error, failing_components[index])
    assert len(errors) == 0
    assert len(added_components) == 173


def test_remove_components(setup_data):
    registry = bpy.context.window_manager.components_registry
    registry.schema_path = setup_data["components_schemaPath"]
    bpy.ops.object.reload_registry()

    type_infos = registry.type_infos

    add_component_operator = bpy.ops.object.add_bevy_component
    errors = []
    addable_components = []
    added_components = []

    for long_name in type_infos:
        definition = type_infos[long_name]
        long_name = definition["long_name"]
        is_component = definition['isComponent']  if "isComponent" in definition else False
        if not is_component:
            continue

        addable_components.append(long_name)

        try:
            add_component_operator(component_type=long_name)
            object = bpy.context.object
            # print("propertyGroup", propertyGroup, propertyGroup.field_names)
            added_components.append(long_name)
        except Exception as error:
            errors.append(error)
    assert len(errors) == 0

    # now test component removal
    errors.clear()
    remove_component_operator = bpy.ops.blenvy.component_remove
    for long_name in added_components:
        try:
            remove_component_operator(component_name=long_name)
        except Exception as error:
            errors.append(error)
    assert len(errors) == 0
    
def test_copy_paste_components(setup_data):
    context = bpy.context
    registry = context.window_manager.components_registry
    registry.schema_path = setup_data["components_schemaPath"]
    bpy.ops.object.reload_registry()

    long_name = "bevy_example::test_components::BasicTest"

    # SOURCE object setup
    add_component_operator = bpy.ops.object.add_bevy_component
    add_component_operator(component_type=long_name)

    property_group_name = registry.get_propertyGroupName_from_longName(long_name)
    object = context.object

    target_components_metadata = object.components_meta.components
    component_meta = next(filter(lambda component: component["long_name"] == long_name, target_components_metadata), None)
    propertyGroup = getattr(component_meta, property_group_name, None)

    setattr(propertyGroup, propertyGroup.field_names[0], 25.0)

    copy_component_operator = bpy.ops.blenvy.component_copy
    copy_component_operator(source_component_name=long_name, source_item_name=object.name)

    # ---------------------------------------
    # TARGET object 
    bpy.ops.mesh.primitive_cube_add()
    new_cube = bpy.context.selected_objects[0]
    # change name
    new_cube.name = "TargetCube"
    target_components_metadata = new_cube.components_meta.components
    component_meta = next(filter(lambda component: component["long_name"] == long_name, target_components_metadata), None)

    # first check that there is no component currently
    assert component_meta == None

    paste_component_operator = bpy.ops.blenvy.component_paste
    paste_component_operator()

    target_components_metadata = new_cube.components_meta.components
    component_meta = next(filter(lambda component: component["long_name"] == long_name, target_components_metadata), None)

    # now after pasting to the new object, it should have component meta
    assert component_meta is not None

    # and then check if the propertyGroup of the target object is correct
    propertyGroup = getattr(component_meta, property_group_name, None)
    assert propertyGroup.field_names == ['a', 'b', 'c']

    a_fieldValue = getattr(propertyGroup, propertyGroup.field_names[0])
    assert a_fieldValue == 25.0
