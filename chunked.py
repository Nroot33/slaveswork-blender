import struct, os, io
from . import resources

class Chunked:
    def __init__(self, conn):
        self.conn = conn
        self.aliases = {}

    def wrapping(self, data):
        if type(data) != bytes:
            data = data.encode('utf-8')
        if len(data) == 0:
            return
        self.conn.send(("%x" % len(data)).encode('ascii'))
        self.conn.send(b'\r\n')
        self.conn.send(data)
        self.conn.send(b'\r\n')

    def close(self):
        self.conn.send(b'0\r\n\r\n')

    def writeResource(self, file, origpath, abspath):
        """Writes a resource linked by the blend file into the stream.
        Chunk format is:
         'rsrc' CHUNKLENGTH
                ALIASLENGTH alias...
                ORIGLENGTH origpath...
                FILELENGTH filedata...
        """
        
        if abspath in self.aliases:
            return self.aliases[abspath]
         
        if type(origpath) != bytes:
            origpath = origpath.encode('utf-8')
         
        if origpath in self.aliases:
            # Only write resources not written yet
            return
        
        alias = resources.resource_id(abspath).encode('utf-8')
        
        file.seek(0, os.SEEK_END)
        filelength = file.tell()
        file.seek(0, os.SEEK_SET)

        # chunk size must not exceed MAX_INT
        chunklength = filelength + len(origpath) + len(alias) + 12
        if chunklength > 0x8fffffff:
            raise RuntimeError('File is too big to be written: %d bytes' % chunklength)
        
        self.aliases[origpath] = alias
        self.wrapping(struct.pack('>4sI', b'rsrc', chunklength))
        self.wrapping(struct.pack('>I', len(alias)))
        self.wrapping(alias)
        self.wrapping(struct.pack('>I', len(origpath)))
        self.wrapping(origpath)
        self.wrapping(struct.pack('>I', filelength))
        while filelength > 0:
            data = file.read(min(filelength, 4096))
            filelength = filelength - len(data)
            self.wrapping(data)
        self.aliases[abspath] = alias
        return alias
        
    def writeFile(self, tag, f):
        """Writes the contents of a file into the stream"""
        if type(tag) != bytes:
            tag = tag.encode('utf-8')
        if len(tag) != 4:
            raise RuntimeError('Tag must be 4 byte long (was: %x)' % tag)
        f.seek(0, os.SEEK_END)
        length = f.tell()
        if length > 0x8fffffff:
            raise RuntimeError('File is too big to be written: %d bytes' % length)
        f.seek(0, os.SEEK_SET)
        
        self.wrapping(struct.pack('>4sI', tag, length))
        while length > 0:
            data = f.read(min(length, 4096))
            length = length - len(data)
            self.wrapping(data)
            
    def writeData(self, tag, value):
        if type(tag) != bytes:
            tag = tag.encode('utf-8')
        if type(value) != bytes:
            value = value.encode('utf-8')
        if len(tag) != 4:
            raise RuntimeError('Tag must be 4 byte long (was: %x)' % tag)
        if len(value) > 0x8fffffff:
            raise RuntimeError('Values too long: len(value)=%d' % len(value))
        self.wrapping(struct.pack('>4sI', tag, len(value)))
        print(value)
        self.wrapping(value)
        
    def writeInt(self, tag, value):
        self.writeData(tag, struct.pack(">i", value))
        
    def bundleResources(self, engine, data):
        for collection_name in resources.RESOURCE_COLLECTIONS:
            collection = getattr(data, collection_name)
            for obj in collection:
                try:
                    if hasattr(obj, 'packed_file') and obj.packed_file is not None:
                        file = io.BytesIO(obj.packed_file.data)
                    else:
                        path = resources.object_filepath(obj)
                        if path:
                            file = open(path, "rb")
                        else:
                            continue
                    
                    with file:
                        alias = self.writeResource(file, obj.filepath, resources.bject_uniqpath(obj))
                        engine.report({'INFO'}, "Successfully bundled {} resource {} = {}".format(collection_name, alias, obj.name))
                        print("'INFO' Successfully bundled {} resource {} = {}".format(collection_name, alias, obj.name))
                except (FileNotFoundError, NotADirectoryError) as e:
                    engine.report({'WARNING'}, "Error bundling {} resource {}: {}".format(collection_name, obj.name, e))
                    print("'WARNING' Error bundling {} resource {}: {}".format(collection_name, obj.name, e))
