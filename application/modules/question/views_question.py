__author__ = 'wilrona'

from ...modules import *

from models_question import QuestionModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route('/settings/questions')
@login_required
@roles_required(('admin', 'super_admin'))
def Question_Index():
    menu="settings"
    submenu="question"

    items = QuestionModel.query()

    return render_template("question/index.html", **locals())

