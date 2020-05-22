bl_info = {
    "name" : "test2",
    "author" : "alencion",
    "description" : "Simple test addon",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "warning" : "",
    "category" : "Render"
}

# from . settings import SlavesWorkSettings
# from . settings_panel import SlavesWork_PT_Panel, RenderSlavesWorkOperator, StopSlavesWorkOperator, SlavesWorkChecker
# from . render import SlavesWorkRenderEngine
from . import settings, settings_panel, render, slaveswork

if "bpy" in locals():
    import importlib
    importlib.reload(slaveswork)
    importlib.reload(settings)
    importlib.reload(settings_panel)
    importlib.reload(render)
import bpy

def register():
    bpy.utils.register_class(settings.SlavesWorkSettings)
    bpy.utils.register_class(settings_panel.SlavesWork_PT_Panel)
    bpy.utils.register_class(settings_panel.RenderSlavesWorkOperator)
    bpy.utils.register_class(settings_panel.StopSlavesWorkOperator)
    bpy.utils.register_class(settings_panel.SlavesWorkChecker)
    bpy.utils.register_class(render.SlavesWorkRenderEngine)

    for name in dir(bpy.types):
        klass = getattr(bpy.types, name)
        if 'COMPAT_ENGINES' not in dir(klass):
            continue
        if 'CYCLES' not in klass.COMPAT_ENGINES:
            continue
        if 'SLAVES_WORK_RENDER' not in klass.COMPAT_ENGINES:
            klass.COMPAT_ENGINES.add('SLAVES_WORK_RENDER')

def unregister():
    bpy.utils.unregister_class(settings_panel.SlavesWorkChecker)
    bpy.utils.unregister_class(render.SlavesWorkRenderEngine)
    bpy.utils.unregister_class(settings_panel.StopSlavesWorkOperator)  
    bpy.utils.unregister_class(settings_panel.RenderSlavesWorkOperator)
    bpy.utils.unregister_class(settings_panel.SlavesWork_PT_Panel)
    bpy.utils.unregister_class(settings.SlavesWorkSettings)  