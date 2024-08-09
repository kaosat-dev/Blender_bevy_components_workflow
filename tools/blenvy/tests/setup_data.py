import bpy
import pytest

@pytest.fixture
def setup_data(request):
    print("\nSetting up resources...")

    schema_path = "../../testing/bevy_example/assets/registry.json"

    yield {"schema_path": schema_path}

    def finalizer():
        print("\nPerforming teardown...")
        registry = bpy.context.window_manager.components_registry

        type_infos = registry.type_infos
        object = bpy.context.object
        remove_component_operator = bpy.ops.blenvy.component_remove

        for long_name in type_infos:
            definition = type_infos[long_name]
            component_name = definition["short_name"]
            if component_name in object:
                try:
                    remove_component_operator(component_name=component_name)
                except Exception as error:
                    pass

    request.addfinalizer(finalizer)

    return None