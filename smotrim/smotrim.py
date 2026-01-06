import inspect
import os
import sys
from importlib import import_module
from urllib.parse import parse_qsl
from urllib.parse import quote as encode4url

import xbmc
import xbmcaddon
import xbmcvfs

from . import kodiutils

ADDON_ID = "plugin.video.smotrim.ru"
SERVER_ADDR = "127.0.0.1"
SERVER_PORT = 47122

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) Gecko/20100101 Firefox/101.0"


class Smotrim:
    def __init__(self) -> None:
        self.id_ = ADDON_ID
        self.server_port = SERVER_PORT
        self.addon = xbmcaddon.Addon(self.id_)
        self.path = self.addon.getAddonInfo("path")
        self.media_path = os.path.join(self.path, "resources", "media")
        self.data_path = get_data_path(self.addon)
        self.history_path = kodiutils.create_folder(
            os.path.join(self.data_path, "history"),
        )

        self.user = None

        self.url = sys.argv[0] if len(sys.argv) > 0 else ""
        self.handle = int(sys.argv[1]) if len(sys.argv) > 1 else 0

        self.params = {}

        self.domain = "smotrim.ru"
        self.api_host = "api.smotrim.ru"
        self.cdnapi_host = "cdnapi.smotrim.ru"
        self.api_url = f"https://{self.api_host}/api/v1"
        self.cdnapi_url = f"https://{self.cdnapi_host}/api/v1"
        self.liveapi_host = "player.smotrim.ru"
        self.liveapi_url = f"https://{self.liveapi_host}"

        self.language = self.addon.getLocalizedString

        # to save current context
        self.context = "home"
        self.action = "load"
        self.context_title = self.language(30300)

    def show_to(self, user, context: str | None = "") -> None:
        self.user = user

        xbmc.log(f"Addon: {self.id_}", xbmc.LOGDEBUG)
        xbmc.log(f"Handle: {self.handle}", xbmc.LOGDEBUG)
        xbmc.log(f"User: {user.phone}", xbmc.LOGDEBUG)

        if context:
            self.params = {"context": context}
            xbmc.log("Params ignored")
        else:
            params_ = sys.argv[2]
            xbmc.log(f"Params: {params_}", xbmc.LOGDEBUG)
            self.params = dict(parse_qsl(params_[1:]))

        self.context = (
            self.params["context"]
            if self.params and ("context" in self.params)
            else "home"
        )
        self.action = (
            self.params["action"]
            if self.params and ("action" in self.params)
            else "load"
        )
        xbmc.log(f"Context: {self.context}", xbmc.LOGDEBUG)
        xbmc.log(f"Action: {self.action}", xbmc.LOGDEBUG)

        self.load_context_items()

    def load_context_items(self) -> None:
        mod = import_module(f"smotrim.modules.{self.context}")
        classes = [cls for _, cls in inspect.getmembers(mod, inspect.isclass(mod))]
        getattr(classes[0](self), self.action)()

    def request(self, url: str, output: str | None = "text", headers=None):
        xbmc.log(f"Query site url: {url}", xbmc.LOGDEBUG)
        is_stream = output == "stream"
        response = self.user.get_http(url, headers=headers, stream=is_stream)
        err = response.status_code != 200  # noqa: PLR2004
        if err:
            xbmc.log(f"Query {url} returned HTTP error {response.status_code}")
        if output == "json":
            return {} if err else response.json()
        if output == "text":
            return "" if err else response.text
        return response

    # *** Add-on helpers

    def get_media(self, file_name: str):
        return os.path.join(self.media_path, file_name)

    def get_user_input(self):
        kbd = xbmc.Keyboard()
        kbd.setDefault("")
        kbd.setHeading(self.language(30010))
        kbd.doModal()
        keyword = None

        if kbd.isConfirmed():
            keyword = kbd.getText()

        return keyword

    @staticmethod
    def prepare_url(url: str):
        return "|".join(
            [
                url,
                "&".join(
                    [
                        f"User-Agent={encode4url(USER_AGENT)}",
                        "Origin={}".format(encode4url("https://player.smotrim.ru")),
                        "Referer={}".format(encode4url("https://player.smotrim.ru/")),
                        "!Sec-Fetch-Dest=empty",
                        "!Sec-Fetch-Mode=cors",
                        "!Sec-Fetch-Site=cross-site",
                        "!Sec-GPC=1",
                        "Connection=keep-alive",
                    ],
                ),
            ],
        )


def get_data_path(addon: object = None):
    if addon is None:
        addon = xbmcaddon.Addon(ADDON_ID)
    return kodiutils.create_folder(
        os.path.join(xbmcvfs.translatePath(addon.getAddonInfo("profile")), "data"),
    )
