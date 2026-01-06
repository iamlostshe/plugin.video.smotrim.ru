from wsgiref.simple_server import make_server

import xbmc

from smotrim import rssbuilder
from smotrim.server import wsgi_app, wsgi_server


class Daemon:
    def __init__(self, site: any) -> None:
        self.site = site
        self.wsgi = None
        self.rb = None

    def load(self) -> None:
        if not self.site.addon.getSettingBool("infoservice"):
            xbmc.log(
                "Smotrim.ru extended info service disabled, skipped",
                xbmc.LOGDEBUG,
            )
            return

        self.rb = rssbuilder.RSSBuilder()
        self.rb.add_news_to_rss(
            self.site, self.site.addon.getSettingBool("addnewstorss"),
        )

        xbmc.log(
            "Starting Smotrim.ru extended info service "
            f"on port {self.site.server_port}",
            xbmc.LOGDEBUG,
        )
        self.wsgi = make_server(
            "",
            port=self.site.server_port,
            app=wsgi_app.default_app,
            server_class=wsgi_server.SmotrimWsgiServer,
        )
        self.wsgi.start()
