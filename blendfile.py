import bpy, subprocess, sys, traceback
from . import resources

def save_copy(filepath):
    bpy.ops.wm.save_as_mainfile(filepath=filepath, check_existing=False, copy=True, relative_remap=True, compress=False)

def process_file(filepath):
    """Opens the given blend file in a separate Blender process and substitutes
    file paths to those which will exist on the worker side."""
    ret = subprocess.call([sys.argv[0], "-b", "--enable-autoexec", "-noaudio", filepath, "-P", __file__, "--", "process", filepath])
    if ret != 0:
        raise RuntimeError("Error processing file '{}': Calling blender returned code {}".format(filepath, ret))

def _repath():
    """Modifies all included paths to point to files named by the pattern
    '//rsrc.' + md5(absolute original path) + '.data'
    This method is called in a special blender session.
    """
    
    # Switch to object mode for make_local
    bpy.ops.object.mode_set(mode='OBJECT')
    # Make linked objects local to current blend file.
    bpy.ops.object.make_local(type='ALL')
    
    def repath_obj(obj):
        path = resources.object_uniqpath(obj)
        if path:
            obj.filepath = resources.resource_path(path)
        else:
            print("...skipped")
            
    # Iterate over all resource types (including libraries) and assign paths
    # to them that will correspond to valid files on the remote side.
    for collection_name in resources.RESOURCE_COLLECTIONS:
        collection = getattr(bpy.data, collection_name)
        print("Repathing {}:".format(collection_name))
        for obj in collection:
            print("  {} ({})".format(obj.filepath, resources.object_filepath(obj)))
            repath_obj(obj)
            print("   -> " + obj.filepath)

def _remove_scripted_drivers():
    """Removes Python drivers which will not execute on the seller side.
    Removing them has the benefit of materializing the values they have evaluated to
    in the current context."""

    for collection_name in dir(bpy.data):
        collection = getattr(bpy.data, collection_name)
        if not isinstance(collection, type(bpy.data.objects)):
            continue
        
        # Iterate through ID objects with animation data
        for idobj in collection:
            if not isinstance(idobj, bpy.types.ID) or not hasattr(idobj, "animation_data"):
                break
            anim = idobj.animation_data
            if not anim:
                continue
            for fcurve in anim.drivers:
                driver = fcurve.driver
                if not driver or driver.type != 'SCRIPTED':
                    continue
                print("Removing SCRIPTED driver '{}' for {}['{}'].{}".format(driver.expression, collection_name, idobj.name, fcurve.data_path))
                try:
                    idobj.driver_remove(fcurve.data_path)
                except TypeError as e:
                    print("  -> {}".format(e))
   
if __name__ == "__main__":
    try:
        idx = sys.argv.index("--")
    except:
        raise Exception("This script must be given a special parameter: -- process")
    
    try:
        args = sys.argv[idx + 1:]
        if len(args) > 1 and args[0] == 'process':
            _repath()
            _remove_scripted_drivers()
            bpy.ops.wm.save_as_mainfile(filepath=args[1], check_existing=False, compress=False)
    except:
        traceback.print_exc()
        sys.exit(-1)
