"""
Initialize Flask app

"""
from flask import Flask
import os
from datetime import timedelta
from lib.flask_debugtoolbar import DebugToolbarExtension
from lib.werkzeug.debug import DebuggedApplication
from flask.ext.login import LoginManager

app = Flask('application')

if os.getenv('FLASK_CONF') == 'TEST':
    app.config.from_object('application.settings.Testing')

elif 'SERVER_SOFTWARE' in os.environ and os.environ['SERVER_SOFTWARE'].startswith('Dev'):
    # Development settings
    app.config.from_object('application.settings.Development')

    # Flask-DebugToolbar
    # toolbar = DebugToolbarExtension(app)
    #
    # # Google app engine mini profiler
    # # https://github.com/kamens/gae_mini_profiler
    # app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)
    #
    # from lib.gae_mini_profiler import profiler, templatetags
    #
    # @app.context_processor
    # def inject_profiler():
    #     return dict(profiler_includes=templatetags.profiler_includes())
    # app.wsgi_app = profiler.ProfilerWSGIMiddleware(app.wsgi_app)
else:
    app.config.from_object('application.settings.Production')

# Enable jinja2 loop controls extension
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
APP_STATIC = os.path.join(APP_ROOT, 'static')

app.permanent_session_lifetime = timedelta(seconds=1200)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'Home'

# function for jinja2
import function

# Pull in URL dispatch routes
import urls
