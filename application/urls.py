"""
urls.py

URL dispatch route mappings and error handlers

"""
from flask import render_template

from application import app
from application.modules import home, user, currency, agency, \
    vessel, departure, travel, ticket_type, ticket, transaction, customer, profil, role, \
    question


## Error handlers
# Handle 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Handle 500 errors
@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

@app.route('/Unauthorized')
def server_Unauthorized():
    return render_template('401.html'), 401

