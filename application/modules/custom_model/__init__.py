__author__ = 'Vercossa'

from google.appengine.ext import ndb
from google.appengine.api import datastore, datastore_errors


class BaseModel(ndb.Model):

    def Key(self):
        key = ndb.Key(self._get_kind(), self.key.id())
        return key.urlsafe()

    @classmethod
    def get_by_key(self, key):
        try:
            key_instance = datastore.Key(key)
            _id = self.get_by_id(key_instance.id())
        except datastore_errors.BadKeyError:
            _id = None
        return _id
