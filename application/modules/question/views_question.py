__author__ = 'wilrona'

from ...modules import *

from models_question import QuestionModel
from forms_question import FormQuestion

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route('/settings/questions')
@login_required
@roles_required(('admin', 'super_admin'))
def Question_Index():
    menu="settings"
    submenu="question"

    items = QuestionModel.query()

    from ..activity.models_activity import ActivityModel
    feed = ActivityModel.query(
        ActivityModel.object == 'QuestionModel',
    ).order(
        -ActivityModel.time
    )

    feed_tab = []
    count = 0
    for feed in feed:
        feed_list = {}
        feed_list['user'] = feed.user_modify
        vess = QuestionModel.get_by_id(feed.identity)
        feed_list['data'] = vess.question
        feed_list['last_value'] = feed.last_value
        feed_list['time'] = feed.time
        feed_list['nature'] = feed.nature
        feed_list['id'] = feed.identity
        feed_tab.append(feed_list)
        count += 1
        if count > 5 and not request.args.get('modal'):
            count += 1
            break

    if request.args.get('modal'):
        return render_template('/question/all_feed.html', **locals())

    return render_template("question/index.html", **locals())


@app.route('/settings/questions/edit', methods=['GET', 'POST'])
@app.route('/settings/questions/edit/<int:question_id>', methods=['GET', 'POST'])
@login_required
@roles_required(('admin', 'super_admin'))
def Question_Edit(question_id=None):
    menu="settings"
    submenu="question"

    from ..activity.models_activity import ActivityModel
    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    activity = ActivityModel()
    activity.user_modify = current_user.key
    activity.object = "QuestionModel"
    activity.time = function.datetime_convert(date_auto_nows)

    feed_tab = []

    if question_id:
        items = QuestionModel.get_by_id(question_id)
        form = FormQuestion(obj=items)


        feed = ActivityModel.query(
            ActivityModel.object == 'QuestionModel',
            ActivityModel.identity == items.key.id()
        ).order(
            -ActivityModel.time
        )

        count = 0
        for feed in feed:
            feed_list = {}
            feed_list['user'] = feed.user_modify
            vess = QuestionModel.get_by_id(feed.identity)
            feed_list['data'] = feed.last_value
            if vess:
                feed_list['data'] = vess.question
            feed_list['last_value'] = feed.last_value
            feed_list['time'] = feed.time
            feed_list['nature'] = feed.nature
            feed_tab.append(feed_list)
            count += 1
            if count > 5:
                count += 1
                break

    else:
        items = QuestionModel()
        form = FormQuestion()

    last_is_pos = items.is_pos
    last_is_obligate = items.is_obligate

    if form.validate_on_submit():
        items.question = form.question.data

        current_is_obligate = False
        if int(form.is_obligate.data) == 1:
            items.is_obligate = True
            current_is_obligate = True
        else:
            items.is_obligate = False

        if question_id and last_is_obligate != current_is_obligate:
            activity.identity = question_id
            activity.nature = 0
            data_obligate = "Not obligated"
            if last_is_obligate:
                data_obligate = "Obligated"
            activity.last_value = data_obligate
            activity.put()

        current_is_pos = False
        if int(form.is_pos.data) == 1:
            items.is_pos = True
            current_is_pos = True
        else:
            items.is_pos = False

        if question_id and last_is_pos != current_is_pos:
            activity.identity = question_id
            activity.nature = 0
            data_pos = "Boarding"
            if last_is_obligate:
                data_pos = "POS"
            activity.last_value = data_pos
            activity.put()

        this_item = items.put()

        if last_is_pos == current_is_pos and last_is_obligate == current_is_obligate:
            activity.identity = this_item.id()
            activity.nature = 4
            activity.put()

        if not question_id:
            activity.identity = this_item.id()
            activity.nature = 1
            activity.put()

        flash(u"Question has been saved!", "success")
        return redirect(url_for("Question_Index"))
    return render_template('question/edit.html', **locals())


@app.route('/questions/active/<int:question_id>')
@login_required
@roles_required(('admin', 'super_admin'))
def Question_Active(question_id):
    from ..activity.models_activity import ActivityModel
    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    activity = ActivityModel()
    activity.user_modify = current_user.key
    activity.object = "QuestionModel"
    activity.time = function.datetime_convert(date_auto_nows)

    items = QuestionModel.get_by_id(int(question_id))

    if items.active:
        items.active = False
        activity.nature = 2
        flash(u"Question has been disabled!", "success")
    else:
        items.active = True
        activity.nature = 5
        flash(u"Question has been activated!", "success")

    activity.identity = items.key.id()
    activity.put()
    items.put()
    return redirect(url_for("Question_Index"))

