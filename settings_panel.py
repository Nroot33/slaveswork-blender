import bpy

class SlavesWorkPanel(bpy.types.Panel):
    bl_idname = "slaves_work_Panel"
    bl_label = "Slave's Work"
    bl_category = "Test Addon"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        settings = context.scene.slaves_work_settings
        self.layout.label(text="Slaves's work Checker",icon='INFO')
        layout = self.layout.column()
        row = layout.split(factor=0.5)
        row.label(text="Slave's Work host:")
        row.prop(settings, "slaves_work_host", text="")
        row = layout.split(factor=0.5)
        row.label(text="Slave's Work port:")
        row.prop(settings, "slaves_work_port", text="")
        row = self.layout.row()
        row.operator("slaves_work.is_running")
        
        self.layout.separator()
        
        self.layout.label(text="Slaves's work is not working",icon='ERROR')
        row = self.layout.row(align=True)
        row.operator("slaves_work.render", icon='PLAY')
        row.operator("slaves_work.stop", icon='X')
        row = self.layout.row()
        
class RenderSlavesWorkOperator(bpy.types.Operator):
    """Slave's Work Render"""
    bl_idname = "slaves_work.render"
    bl_label = "Render"
   
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        print("Render")
        return {'FINISHED'}
    
class StopSlavesWorkOperator(bpy.types.Operator):
    """Slave's Work Rendering Stop"""
    bl_idname = "slaves_work.stop"
    bl_label = "Stop"
    
    @classmethod
    def poll(cls, context):
        return False
    
    def execute(self, context):
        print("Stop")
        return {'FINISHED'}

class SlavesWorkChecker(bpy.types.Operator):
    """Slave's Work Rendering Stop"""
    bl_idname = "slaves_work.is_running"
    bl_label = "Running Check"
    
    def execute(self, context):
        print("Checker")
        return {'FINISHED'}