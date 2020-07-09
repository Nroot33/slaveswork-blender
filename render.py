import bpy
import colorsys
import tempfile
import os
import traceback
import http.client
import json

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
        return

    def setIndex(self, index):
        self.index = index

    # def dispatch(self, settings, data, filepath, engine):
    #     """Dispatches one tile to the bitwrk client.
    #     The complete blender data is packed into the transmission.
    #     """
    #     # draw rect in preview color
    #     tile = engine.begin_result(self.minx, self.miny, self.resx, self.resy)
    #     tile.layers[0].passes[0].rect = [self.color] * (self.resx*self.resy)
    #     engine.end_result(tile)

    #     self.result = engine.begin_result(self.minx, self.miny, self.resx, self.resy)
    #     self.conn = http.client.HTTPConnection(
    #         "localhost", 8080,
    #         timeout=600)
    #     try:
    #         self.conn.putrequest("POST", "/buy/")
    #         self.conn.putheader('Transfer-Encoding', 'chunked')
    #         self.conn.endheaders()
    #         chunk = chunked.Chunked(self.conn)
    #         try:
    #             chunk.writeInt('xmin', self.minx)
    #             chunk.writeInt('ymin', self.miny)
    #             chunk.writeInt('xmax', self.minx+self.resx-1)
    #             chunk.writeInt('ymax', self.miny+self.resy-1)
    #             chunk.writeInt('fram', self.frame)
    #             chunk.bundleResources(engine, bpy.data)
    #             with open(filepath, "rb") as file:
    #                 chunk.writeFile('blen', file)
    #         finally:
    #             chunk.close()
    #     except:
    #         print("Exception in dispatch:", sys.exc_info())
    #         engine.report({'ERROR'}, "Exception in dispatch: {}".format(traceback.format_exc()))
    #         self.conn.close()
    #         self.conn = None
    #         self.result.layers[0].passes[0].rect = [[1,0,0,1]] * (self.resx*self.resy)
    #         engine.end_result(self.result)
    #         self.result = None
    #         return False
    #     else:
    #         return True

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
            # if not hasattr(scene, 'bitwrk_settings'):
            #     self.report({'ERROR'}, "Must first setup BitWrk")
            #     return
            # if not probe_bitwrk_client(scene.bitwrk_settings):
            #     self.report({'ERROR'}, "Must first connect to BitWrk client")
            #     return
            with tempfile.TemporaryDirectory() as tmpdir:
                self._doRender(scene, tmpdir)
        except:
            self.report({'ERROR'}, "Exception while rendering: {}".format(
                traceback.format_exc()))
        finally:
            _render_count -= 1

    def _doRender(self, scene, tmpdir):
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

        # a = bpy.app.binary_path_python
        # print("python_path : ", a)
        # b = bpy.app.binary_path
        # print("blender : ", b)
        # c = os.path.join(os.path.abspath(os.path.dirname(__file__)), "blender-slave.py")
        # print("worker_path : ", c)

        # Sort by distance to center
        tiles.sort(key=lambda t: abs(t.minx + t.resx/2 - resx/2) +
                   abs(t.miny + t.resy/2 - resy/2))

        settings = scene.slaves_work_settings

        # 1. 커넥션을 맺는다.
        # 2. 파일 정보를 app에 전송한다.
        # 3. 결과를 돌려받으면 break;
        host = "localhost"
        port = 8080

        print("filename: ", filename)

        self.sendTiles("POST", "/", tiles, host, port)
        self.sendResources("POST", "/", filename, host, port)

        for tile in tiles:
            tile.previewDrawing(self)

        # num_active = 0
        # while not self.test_break():
        #     remaining = [t for t in tiles if not t.success]
        #     if not remaining:
        #         self.report({'INFO'}, "Successfully render Done {} ".format(len(tiles)))
        #         break

        #     # Dispatch some unfinished tiles
        #     for tile in remaining:
        #         if tile.conn is None and num_active < 4:
        #             if tile.dispatch(settings, bpy.data, filename, self):
        #                 num_active += 1

            # Poll from all tiles currently active
            # active = filter(lambda tile: tile.conn is not None, tiles)
            # rlist, wlist, xlist = select.select(active, [], active, 2.0)

            # Collect from all tiles where data has arrived
            # for list in rlist, xlist:
            #     for tile in list:
            #         if tile.conn is not None:
            #             tile.collect(settings, self, is_multilayer)
            #             # collect has either failed or not. In any case, the tile is
            #             # no longer active.
            #             num_active -= 1

            # Report status
        #     successful = 0
        #     for tile in tiles:
        #         if tile.success:
        #             successful += 1
        #     self.update_progress(successful / len(tiles))
        # if self.test_break():
        #     for tile in filter(lambda tile: tile.conn is not None, tiles):
        #         tile.cancel()

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
            jsonTiles.append({'index': index, 'xmin': tiles[index].minx, 'ymin': tiles[index].miny, 'xmax': tiles[index].minx +
                              tiles[index].resx-1, 'ymax': tiles[index].miny + tiles[index].resy-1, 'fram': tiles[index].frame})
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
