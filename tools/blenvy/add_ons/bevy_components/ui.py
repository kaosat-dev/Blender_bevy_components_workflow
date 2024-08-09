def draw_settings_ui(layout, component_settings):

    row = layout.row()
    col = row.column()
    col.label(text="Registry Schema path")

    col = row.column()
    col.enabled = False
    col.prop(component_settings, "schema_path", text="")

    col = row.column()
    col.operator(operator="blenvy.components_registry_browse_schema", text="", icon="FILE_FOLDER")

    layout.separator()
    layout.operator(operator="blenvy.components_registry_reload", text="reload registry" , icon="FILE_REFRESH")

    layout.separator()
    row = layout.row()

    row.prop(component_settings, "watcher_enabled", text="enable registry file polling")
    row.prop(component_settings, "watcher_poll_frequency", text="registry file poll frequency (s)")

    layout.separator()
    layout.separator()