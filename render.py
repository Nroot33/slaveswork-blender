import bpy
import colorsys
import tempfile
import os
import traceback
import http.client
import json
import http.server
import socketserver

# import sys
from . import common, tiling, chunked, blendfile

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

    def previewDrawing(self, engine):
        tile = engine.begin_result(self.minx, self.miny, self.resx, self.resy)
        tile.layers[0].passes[0].rect = [self.color] * (self.resx*self.resy)
        engine.end_result(tile)

        self.result = engine.begin_result(self.minx, self.miny, self.resx, self.resy)
        return

    def rendering(self, engine, filename):
        self.result.layers[0].load_from_file(filename)
        engine.end_result(self.result)

        self.success = True
        return

    def setIndex(self, index):
        self.index = index

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

    def pretty_print(self):
        print("self.minx : ", self.minx)
        print("self.miny : ", self.miny)
        print("self.resx : ", self.resx)
        print("self.resy : ", self.resy)
        print("self.color : ", self.color)


_render_count = 0
global_tiles = []
global_engine = None

def is_render_active():
    global _render_count
    return _render_count > 0


class SlavesWorkRenderEngine(bpy.types.RenderEngine):
    """Slave's Work Rendering Engine"""
    bl_idname = "SLAVES_WORK_RENDER"
    bl_label = "Slave's Work Render"
    bl_description = "Performs distributed rendering using the BitWrk marketplace for compute power"

    def render(self, depsgraph):
        print("render")
        scene = depsgraph.scene
        global _render_count
        _render_count += 1
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                self._doRender(scene, tmpdir)
        except:
            self.report({'ERROR'}, "Exception while rendering: {}".format(
                traceback.format_exc()))
        finally:
            _render_count -= 1

    def _doRender(self, scene, tmpdir):
        global global_engine
        global global_tiles
        global_engine = self
        filename = os.path.join(tmpdir, "mainfile.blend")
        blendfile.save_copy(filename)
        blendfile.process_file(filename)

        self.report(
            {'INFO'}, "mainfile.blend successfully exported: {}".format(filename))

        max_pixels_per_tile = common.max_tilesize(scene)
        # is_multilayer = len(scene.render.layers) > 1 and not scene.render.use_single_layer
        resx, resy = common.render_resolution(scene)

        tiles = self._makeTiles(scene.frame_current,
                                resx, resy, max_pixels_per_tile)

        # Sort by distance to center
        tiles.sort(key=lambda t: abs(t.minx + t.resx/2 - resx/2) +
                   abs(t.miny + t.resy/2 - resy/2))
        global_tiles = tiles
        
        settings = scene.slaves_work_settings

        # 1. 커넥션을 맺는다.
        # 2. 파일 정보를 app에 전송한다.
        # 3. 결과를 돌려받으면 break;
        host = settings.slaves_work_host
        port = settings.slaves_work_port

        print("filename: ", filename)

        self.sendTiles("POST", "/task/tiles", tiles, host, port)
        self.sendResources("POST", "/task/resource", filename, host, port)

        for tile in tiles:
            tile.previewDrawing(self)

        # 4. tcp 서버를 열고 데이터를 받는다.  
        server_address = ("", 8000)
        handler = MyHandler

        with socketserver.TCPServer(server_address, handler) as httpd:
            print("serving at port", 8000)
            httpd.serve_forever()

        print("rendering DONE!!!!!")

    angle = 0.0

    @classmethod
    def _getcolor(self):
        self.angle += 0.61803399
        if self.angle >= 1:
            self.angle -= 1
        return colorsys.hsv_to_rgb(self.angle, 0.5, 0.2)

    def _makeTiles(self, frame, resx, resy, max_pixels):
        #print("make tiles:", minx, miny, resx, resy, max_pixels)
        print("resx : ", resx)
        print("resy : ", resy)
        print("max_pixels : ", max_pixels)
        U, V = tiling.optimal_tiling(resx, resy, max_pixels)
        print("U : ", U)
        print("V : ", V)
        result = []
        for v in range(V):
            ymin = resy * v // V
            ymax = resy * (v+1) // V
            for u in range(U):
                xmin = resx * u // U
                xmax = resx * (u+1) // U
                c = SlavesWorkRenderEngine._getcolor()
                result.append(Tile(frame, xmin, ymin, xmax-xmin,
                                   ymax-ymin, [c[0], c[1], c[2], 1]))

        return result

    def sendTiles(self, method, url, tiles, host="localhost", port=8080):
        conn = http.client.HTTPConnection(host, port, 600)

        jsonTiles = []
        for index in range(len(tiles)):
            tiles[index].setIndex(index)
            jsonTiles.append({'index': str(index), 'xmin': str(tiles[index].minx), 'ymin': str(tiles[index].miny),
                              'xmax': str(tiles[index].minx + tiles[index].resx-1), 'ymax': str(tiles[index].miny + tiles[index].resy-1), 'fram': str(tiles[index].frame)})
        jsonTiles = json.dumps(jsonTiles)

        try:
            headers = {'Content-type': 'application/json'}

            conn.request(method, url, jsonTiles, headers)

        except:
            self.report({'ERROR'}, "Exception in sending Tiles : {}".format(
                traceback.format_exc()))
            conn.close()

    def sendResources(self, method, url, filename, host="localhost", port=8080):
        conn = http.client.HTTPConnection(host, port, 600)

        try:
            conn.putrequest(method, url)
            conn.putheader('Transfer-Encoding', 'chunked')
            conn.endheaders()
            chunk = chunked.Chunked(conn)
            try:
                chunk.bundleResources(self, bpy.data)
                with open(filename, "rb") as file:
                    chunk.writeFile('blen', file)
            finally:
                chunk.close()

        except:
            self.report({'ERROR'}, "Exception in sending Resources : {}".format(
                traceback.format_exc()))
            conn.close()

class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # self.rfile is a file-like object created by the handler;
        # we can now use e.g. readline() instead of raw recv() calls
    
        if self.checkDone(): self.server.shutdonw()
       
        path = None
        index = None

        headers = self.headers.items()
        for name, value in headers:
            if name == 'Index':
                index = int(value)
            if name == 'Filename':
                path = value
            print(name + " : " + value)
        print("do_get ", path)

        global_tiles[index].rendering(global_engine, path)

        self.send_response(200)
        self.end_headers()
        
    def checkDone(self):
        for tile in global_tiles:
            if tile.success != True:
                return False 
        return True