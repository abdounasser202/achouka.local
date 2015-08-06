__author__ = 'wilrona'

from lib.flaskext import wtf
from lib.flaskext.wtf import validators

class FormQuestion(wtf.Form):
    question = wtf.StringField(label="Question", validators=[validators.Required()])
    is_pos = wtf.StringField(label="This question is for", validators=[validators.Required()])
    is_obligate = wtf.StringField(label="Is this question required ?", validators=[validators.Required()])
