import bpy
from bpy.props import BoolProperty, StringProperty, IntProperty, PointerProperty, FloatProperty

class SlavesWorkSettings(bpy.types.PropertyGroup):
    
    @classmethod
    def register(settings):
        settings.slaves_work_host = StringProperty(
            name="Slave's Work Host Ip",
            description="IP or name of host running local Slaves Work Host",
            maxlen=180,
            default="127.0.0.1")

        settings.slaves_work_port = IntProperty(
            name="Slave's Work Host Port",
            description="TCP port the local Slave's Work Host listens on",
            default=8080,
            min=1,
            max=65535)

        settings.boost_factor = FloatProperty(
            name="Boost factor",
            description="Makes rendering faster (and more expensive) by making tiles smaller than they need to be",
            default=1.0,
            min=1.0,
            max=64.0,
            precision=2,
            subtype='FACTOR')

        settings.slaves_work_app_running = BoolProperty(
            name="Slave's Work running check",
            description="check slaves work app is running",
            default=False)

        bpy.types.Scene.slaves_work_settings = PointerProperty(type=SlavesWorkSettings, name="Slave's Work Settings", description="Settings for using the Slave's Work service")

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.slaves_work_settings