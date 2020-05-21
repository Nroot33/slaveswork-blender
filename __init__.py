bl_info = {
    "name" : "test2",
    "author" : "alencion",
    "description" : "Simple test addon",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "warning" : "",
    "category" : "Render"
}

import bpy, settings_panel

def register():
    bpy.utils.register_class(settings_panel.SlavesWorkPanel)
    bpy.utils.register_class(settings_panel.RenderSlavesWorkOperator)
    bpy.utils.register_class(settings_panel.StopSlavesWorkOperator)

def unregister():
    bpy.utils.unregister_class(settings_panel.Slaves_Work_Panel)
    bpy.utils.unregister_class(settings_panel.RenderSlavesWorkOperator)
    bpy.utils.unregister_class(settings_panel.StopSlavesWorkOperator)