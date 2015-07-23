__author__ = 'bapetel'

"""
La nature d'une modification peut etre:
    1: creation ou enregistrement
    2: desactivation
    3: suppression
    4: modification sans stockage de l'ancienne valeur
    5: activation
    6: is_default
    7: is_not_default
    8: is_special
    9: is_not_special
    0: modification avec stockage de l'ancienne valeur dans ActivityModel.object
"""

from google.appengine.ext import ndb
from ..user.models_user import UserModel


class ActivityModel(ndb.Model):
    user_modify = ndb.KeyProperty(kind=UserModel) # utilisateur
    nature = ndb.IntegerProperty() # nature de la modification
    object = ndb.StringProperty() # type objet qui a ete modifie par exemple vessel
    identity = ndb.IntegerProperty() # id() de l'objet qui a ete modifie
    time = ndb.DateTimeProperty() # date de la modification
    last_value = ndb.StringProperty() # stocke l'ancienne valeur