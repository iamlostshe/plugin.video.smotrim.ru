"""WSGI server for Smotrim.ru addon."""

from wsgiref.simple_server import WSGIServer

import xbmc


class SmotrimWsgiServer(WSGIServer):

    def start(self) -> None:
        self.monitor = xbmc.Monitor()

        try:
            self.serve_forever()
        except StopIteration:
            xbmc.log("SmotrimWsgiServer - shutdown complete!", xbmc.LOGDEBUG)

    def service_actions(self) -> None:
        if self.monitor.abortRequested():
            xbmc.log("SmotrimWsgiServer - abortRequested!", xbmc.LOGDEBUG)
            raise StopIteration
