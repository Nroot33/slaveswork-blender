import bpy

class SlavesWorkRenderEngine(bpy.types.RenderEngine):
    """Slave's Work Rendering Engine"""
    bl_idname = "SLAVES_WORK_RENDER"
    bl_label = "Slave's Work Render"
    bl_description = "Performs distributed rendering using the BitWrk marketplace for compute power"
    
    def render(self, scene):
        print("render")