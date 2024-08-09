import bpy
from .setup_data import setup_data

def test_blend(setup_data):
    registry = bpy.context.window_manager.components_registry
    registry.schema_path = setup_data["components_schemaPath"]
    bpy.ops.object.reload_registry()

    long_name = "bevy_example::test_components::BasicTest"

    add_component_operator = bpy.ops.object.add_bevy_component
    add_component_operator(component_type=long_name)

    property_group_name = registry.get_propertyGroupName_from_longName(long_name)
    object = bpy.context.object

    target_components_metadata = object.components_meta.components
    component_meta = next(filter(lambda component: component["long_name"] == long_name, target_components_metadata), None)
    propertyGroup = getattr(component_meta, property_group_name, None)


    assert propertyGroup.field_names == ['a', 'b', 'c']