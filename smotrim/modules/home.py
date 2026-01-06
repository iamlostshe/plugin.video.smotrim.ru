import xbmc

import smotrim.modules.history as histories
from smotrim.kodiutils import get_url
from smotrim.modules import articles, boxes, brands, channels, pages, podcasts, searches


class Home(pages.Page):

    def get_data_query(self):
        search = searches.Search(self.site)
        brand = brands.Brand(self.site)
        podcast = podcasts.Podcast(self.site)
        article = articles.Article(self.site)
        channel = channels.Channel(self.site)
        box = boxes.Box(self.site)
        history = histories.History(self.site)

        home_menu = [search.create_root_li(),
                     self.create_fav_li(),
                     article.create_root_li(),
                     channel.create_root_li(),
                     box.create_root_li(),
                     podcast.create_root_li()]

        home_menu.extend(list(brand.create_search_by_tag_lis()))

        if self.site.addon.getSettingBool("addhistory"):
            home_menu.append(history.create_root_li())

        return {"data": home_menu}

    def set_context_title(self):
        self.site.context_title = self.site.language(30300)

    def create_fav_li(self):
        return self.create_menu_li("favorites", 30023, is_folder=False, is_playable=False,
                                   url=get_url(self.site.url, action="favorites", context="home", url=self.site.url),
                                   info={"plot": self.site.language(30023)})

    def favorites(self):
        xbmc.executebuiltin("ActivateWindow(Favourites)")

