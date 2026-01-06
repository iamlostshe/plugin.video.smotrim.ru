import json
import os
from stat import S_ISREG, ST_CTIME, ST_MODE

import xbmc

from smotrim.kodiutils import get_url
from smotrim.modules import brands, pages


class History(pages.Page):
    def __init__(self, site):
        super(History, self).__init__(site)
        self.brand = brands.Brand(self.site)

    def get_data_query(self):

        cfiles = (os.path.join(self.site.history_path, fn) for fn in os.listdir(self.site.history_path))
        cfiles = ((os.stat(path), path) for path in cfiles)

        cfiles = ((stat[ST_CTIME], path)
                  for stat, path in cfiles if S_ISREG(stat[ST_MODE]))
        elements = {"data": [] }
        for cdate, path in sorted(cfiles, reverse=True):
            with open(path, "r+") as f:
                xbmc.log("history len = %s" % len(elements["data"]), xbmc.LOGDEBUG)
                if len(elements["data"]) < self.limit:
                    elements["data"].append(json.load(f))
                else:
                    # autocleanup
                    os.remove(path)

        return elements

    def create_root_li(self):
        return self.create_menu_li("history", 30050, is_folder=True, is_playable=False,
                                   url=get_url(self.site.url, action="load", context="history", url=self.site.url),
                                   info={"plot": self.site.language(30051)})

    def set_context_title(self):
        self.site.context_title = self.site.language(30050)

    def create_element_li(self, element):
        return self.brand.create_element_li(element)
