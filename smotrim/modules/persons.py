import json
import os
import re

import xbmc

from smotrim import kodiutils, smotrim, users
from smotrim.kodiutils import get_url
from smotrim.modules import pages

CONTEXT = "persons"
CONTEXT_LIMIT = 30


class Person(pages.Page):

    def __init__(self, site) -> None:
        super().__init__(site)
        self.cache_enabled = True
        self.persons_path = kodiutils.create_folder(os.path.join(self.site.data_path, "persons"))

    def get_load_url(self):
        return get_url(baseurl=self.site.api_url + f"/{CONTEXT}",
                       brands=self.params.get("brands", 0),
                       offset=self.offset,
                       limit=CONTEXT_LIMIT)

    def download_brand_persons(self) -> None:
        brand_id = self.params.get("brands", "")
        xbmc.log(f"Smotrim: start downloading actor thumbnails ({brand_id})", xbmc.LOGDEBUG)

        self.cache_file = get_brand_persons_file_name(brand_id)
        self.data = self.get_data_query()
        if "data" in self.data:
            self.cache_data()
            xbmc.log("Smotrim: thumbnails downloaded", xbmc.LOGDEBUG)
        else:
            xbmc.log("Smotrim: thumbnails failed to download", xbmc.LOGDEBUG)

    def cache_data(self) -> None:
        if self.cache_enabled and not os.path.exists(self.cache_file):
            with open(self.cache_file, "w+") as f:
                json.dump(self.data, f)

    def get_cache_filename_prefix(self):
        return get_brand_persons_file_name_prefix(self.params.get("brands", 0))


def get_brand_persons_file_name_prefix(brand_id) -> str:
    return os.path.join(CONTEXT, f"brand_{brand_id}")


def get_brand_persons_file_name(brand_id) -> str:
    return os.path.join(smotrim.get_data_path(), f"{get_brand_persons_file_name_prefix(brand_id)}_{CONTEXT_LIMIT}_{0}.json")


def get_persons_path(data_path="") -> str:
    if not data_path:
        data_path = smotrim.get_data_path()
    return kodiutils.create_folder(os.path.join(data_path, CONTEXT))


def get_brand_persons_from_cache(brand_id) -> list:
    if brand_id:
        fname = get_brand_persons_file_name(brand_id)
        xbmc.log(f"persons.get_brand_persons_from_cache fname={fname}", xbmc.LOGDEBUG)

        if not os.path.exists(fname):
            site = smotrim.Smotrim()
            site.params["brands"] = brand_id
            site.user = users.User()
            site.user.init_session(site)
            person = Person(site)
            person.download_brand_persons()
            site.user.session.close()
            return person.data.get("data", [])

        if os.path.exists(fname):
            with open(fname) as f:
                return json.load(f).get("data", [])
    return []


def get_person_remote_thumbnail_url(brand_id, person_name) -> str:
    m = re.match(r"(.+)(\s|\+)(.+)", person_name)
    if m:
        first_name = m.group(1)
        last_name = m.group(3)
        xbmc.log(f"persons.get_person_remote_thumbnail_url searching tumbnail for {first_name} {last_name}",
                 xbmc.LOGDEBUG)
        persons = get_brand_persons_from_cache(brand_id)
        xbmc.log(f"persons.get_person_remote_thumbnail_url found {len(persons)} persons",
                 xbmc.LOGDEBUG)
        try:
            sp = list(filter(lambda p: p.get("name", "") == first_name and
                                  p.get("surname", "") == last_name, persons))

            if sp:
                return pages.get_pic_from_element(sp[0], "bq", append_headers=False)
            return ""
        except IndexError:
            return ""
    return None


def get_person_thumbnail(brand_id, person_name) -> str:
    return get_url(f"http://{smotrim.SERVER_ADDR}:{smotrim.SERVER_PORT}/brands/{brand_id}", person_name=person_name)
