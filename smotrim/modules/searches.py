import json
import os

import xbmc

from smotrim.kodiutils import get_url
from smotrim.modules import pages


class Search(pages.Page):

    def __init__(self, site) -> None:
        super().__init__(site)
        self.search_history_file = os.path.join(self.site.data_path, "search_history.json")

    def create_root_li(self):
        return self.create_menu_li("search", 30010, is_folder=True, is_playable=False,
                                   url=self.get_nav_url(),
                                   info={"plot": self.site.language(30011)})

    def preload(self) -> None:
        self.list_items.append(self.create_menu_li("search", 30012,
                                                   is_folder=False, is_playable=False,
                                                   url=get_url(self.site.url,
                                                               action="search",
                                                               context="brands",
                                                               url=self.site.url)))

    def set_context_title(self) -> None:
        self.site.context_title = self.site.language(30010)

    def create_element_li(self, element):
        return {"id": element["id"],
                "label": "[B]{}[/B]".format(element["title"]),
                "is_folder": True,
                "is_playable": False,
                "url": get_url(self.site.url,
                               action="search",
                               context="brands",
                               search=element["title"],
                               url=self.site.url),
                "info": {"plot": "{} [{}]".format(self.site.language(30010), element["title"])},
                "art": {"icon": self.site.get_media("search.png"),
                        "fanart": self.site.get_media("background.jpg")},
                }

    def get_data_query(self):
        if os.path.exists(self.search_history_file):
            self.limit = self.get_limit_setting()
            with open(self.search_history_file, "r+") as f:
                sh = json.load(f)
                return {"data": sh[:self.limit]}
        else:
            return {"data": []}

    def create_new_search_element(self):
        return {"id": "newsearch",
                "title": f"[COLOR=FF00FF00]{self.site.language(30012)}[/COLOR]",
                "is_new": "true"}

    def save_to_history(self, keyword) -> None:
        sh = self.get_data_query().get("data",[])
        pos = next((i for i, item in enumerate(sh) if item["title"] == keyword), -1)
        if pos < 0:
            index = sh[0]["id"] + 1 if len(sh) > 0 else 1
            sh.insert(0, {"id": index,
                          "title": keyword,
                          "is_new": "false"})
        else:
            sh.insert(0, sh[pos])
            sh.pop(pos + 1)

        with open(self.search_history_file, "w+") as f:
            json.dump(sh, f)

    def get_nav_url(self, offset=0):
        return get_url(self.site.url, action="load", context="searches", url=self.site.url)

    def add_context_menu(self, category) -> None:
        self.context_menu_items.append((self.site.language(30350),
                                        "RunPlugin({})".format(get_url(self.site.url,
                                                action="clear_history",
                                                context="searches",
                                                url=self.site.url))))

    def clear_history(self) -> None:
        if os.path.exists(self.search_history_file):
            os.remove(self.search_history_file)
            url = self.get_nav_url(offset=0)
            xbmc.executebuiltin(f"Container.Update({url})")
