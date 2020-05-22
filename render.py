import bpy

class Tile:
    def __init__(self, frame, minx, miny, resx, resy, color):
        self.conn = None
        self.result = None
        self.frame = frame
        self.minx = minx
        self.miny = miny
        self.resx = resx
        self.resy = resy
        self.color = color
        self.success = False

    def dispatch(self, settings, data, filepath, engine):
        # TODO
        return

    def collect(self, settings, engine, is_multilayer):
        # TODO
        return
    
    def fileno(self):
        return self.conn.sock.fileno()

    def cancel(self):
        try:
            if self.conn is not None:
                self.conn.close()
        except:
            pass
        finally:
            self.conn = None

class SlavesWorkRenderEngine(bpy.types.RenderEngine):
    """Slave's Work Rendering Engine"""
    bl_idname = "SLAVES_WORK_RENDER"
    bl_label = "Slave's Work Render"
    bl_description = "Performs distributed rendering using the BitWrk marketplace for compute power"

    def render(self, scene):
        settings = bpy.scene.slaves_work_settings
        print("render")
