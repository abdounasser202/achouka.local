__author__ = 'wilrona'

from google.appengine.ext import ndb

class QuestionModel(ndb.Model):
    question = ndb.StringProperty()
    is_pos = ndb.BooleanProperty() # Appartenance
    is_obligate = ndb.BooleanProperty(default=False)
    active = ndb.BooleanProperty(default=True)
