import bpy

class SlavesWorkPanel(bpy.types.Panel):
    bl_idname = "slaves_work_Panel"
    bl_label = "Slave's Work"
    bl_category = "Test Addon"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        # check = isOpenSlavesWork()
        self.layout.separator()
        
        self.layout.label(text="Slaves's work is not working",icon='ERROR')
        row = self.layout.row(align=True)
        row.operator("slaves_work.render", text='Render', icon='PLAY')
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
