__author__ = 'wilrona'


from ...modules import *
from ..ticket.models_ticket import TicketPoly, TicketModel, AgencyModel, DepartureModel, QuestionModel, TicketQuestion
cache = Cache(app)


@app.route('/Boarding')
@login_required
@roles_required(('employee_Boarding', 'super_admin'))
def Boarding():
    menu = 'boarding'

    #implementation de l'heure local
    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    heure = function.datetime_convert(date_auto_nows).time()

    departure = DepartureModel.query(
        DepartureModel.departure_date == datetime.date.today(),
        DepartureModel.schedule >= heure
    ).order(
        -DepartureModel.departure_date,
        DepartureModel.schedule,
        DepartureModel.time_delay
    )

    if current_user.have_agency():
        agence_id = session.get('agence_id')
        user_agence = AgencyModel.get_by_id(int(agence_id))

        for dep in departure:
            if dep.destination.get().destination_start == user_agence.destination:
                current_departure = dep
                break
    else:
        current_departure = departure.get()

    return render_template('/index/boarding.html', **locals())


@app.route('/Search_Ticket_Boarding/<int:ticket_id>', methods=['GET', 'POST'])
@app.route('/Search_Ticket_Boarding', methods=['GET', 'POST'])
@login_required
@roles_required(('employee_Boarding', 'super_admin'))
def Search_Ticket_Boarding(ticket_id=None):

    if ticket_id:
        number_ticket = str(ticket_id)
    else:
        number_ticket = request.form['number_ticket']
    departure_id = request.form['departure_id']
    departure_id = DepartureModel.get_by_id(int(departure_id))

    number_ticket = ''.join(number_ticket.split('*'))

    if len(number_ticket) < 16:
        ticket_sold = TicketPoly.query(
            TicketPoly.selling == True,
            TicketPoly.statusValid == True,
            TicketPoly.is_boarding == False,
            TicketPoly.departure == departure_id.key
        )
        departure_id = departure_id.key.id()
    else:
        ticket = TicketPoly.get_by_id(int(number_ticket))

        ticket_count = TicketPoly.query(
            TicketPoly.key == ticket.key,
            TicketPoly.selling == True,
            TicketPoly.statusValid == True,
            TicketPoly.is_boarding == False,
            TicketPoly.departure == departure_id.key
        ).count()

        if ticket_count:
            #liste des questions
            questions = QuestionModel.query(
                QuestionModel.is_pos == False,
                QuestionModel.active == True
            )
            return render_template('/boarding/ticket_found.html', **locals())
        ticket_sold = []

    list_ticket_sold = []
    for ticket in ticket_sold:
        find_ticket_sold = function.find(str(ticket.key.id())+" ", str(number_ticket))
        if find_ticket_sold:
            list_ticket_sold.append(ticket.key.id())
    return render_template('/boarding/search_ticket.html', **locals())


@app.route('/Update_Ticket_For_Boarding/<int:ticket_id>', methods=['POST'])
@login_required
@roles_required(('employee_Boarding', 'super_admin'))
def Update_Ticket_For_Boarding(ticket_id):

    ticket = TicketPoly.get_by_id(ticket_id)

    question_request = request.form.getlist('questions')

    from ..activity.models_activity import ActivityModel

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    #liste des questions
    questions = QuestionModel.query(
        QuestionModel.is_pos == True,
        QuestionModel.active == True
    )

    #Traitement des questions obligatoires
    quest_obligated = []
    obligated = False
    number_obligated_question = QuestionModel.query(
        QuestionModel.is_pos == True,
        QuestionModel.active == True,
        QuestionModel.is_obligate == True
    ).count()

    obligated_question = QuestionModel.query(
        QuestionModel.is_pos == True,
        QuestionModel.active == True,
        QuestionModel.is_obligate == True
    )

    # s'il n'y a pas de question envoye et qu'il y'a des questions obligatoires definient
    if number_obligated_question >= 1 and question_request is None:
        obligated = True
        quest_obligated = [question.key.id() for question in obligated_question]
    else:
        if question_request:
            count = 0
            #boucle la liste des questions envoyees et verifie si c'est dans la liste des questions obligatoires
            for quest in question_request:
                ks = QuestionModel.get_by_id(int(quest))
                if ks.is_obligate:
                    count += 1
                    quest_obligated.append(int(quest))

            # verifie que le quota de question obligatoire est atteint dans le questionnaire
            if count < number_obligated_question:
                obligated = True

    modal = 'false'
    if not obligated:
        for kest in questions:
            Answers = TicketQuestion()
            Answers.ticket_id = ticket.key
            Answers.question_id = kest.key
            if kest.is_obligate:
                Answers.response = True
            else:
                if str(kest.key.id()) in question_request:
                    Answers.response = True
                else:
                    Answers.response = False
            Answers.put()
        ticket.is_boarding = True
        if not ticket.journey_name.get().returned and not ticket.is_return:
            ticket.statusValid = False
        this_ticket = ticket.put()

        activity = ActivityModel()
        activity.user_modify = current_user.key
        activity.object = "TicketPoly"
        activity.time = function.datetime_convert(date_auto_nows)
        activity.identity = this_ticket.id()
        activity.nature = 4
        activity.put()

        modal = 'true'

    return render_template('/boarding/ticket_found.html', **locals())


@app.route('/modal_generate_pdf_boarding')
@app.route('/modal_generate_pdf_boarding/<int:ticket_id>')
@login_required
@roles_required(('employee_Boarding', 'super_admin'))
def modal_generate_pdf_boarding(ticket_id=None):
    return render_template('/boarding/view-pdf.html', **locals())


@app.route('/generate_pdf_boarding/<int:ticket_id>')
@login_required
@roles_required(('employee_Boarding', 'super_admin'))
def generate_pdf_boarding(ticket_id):
    Ticket_print = TicketPoly.get_by_id(ticket_id)

    import cStringIO
    output = cStringIO.StringIO()

    style = getSampleStyleSheet()
    width, height = 595.27, 280.63
    p = canvas.Canvas(output, pagesize=(595.27, 280.63))

    code = str(Ticket_print.key.id())
    barcode = code39.Standard39(code, barHeight=20, stop=1)
    barcode.humanReadable = 1

    string = '<font name="Times-Roman" size="14">%s</font>'
    string_2 = '<font name="Times-Roman" size="13">%s</font>'

    journey = string % 'Return T.'
    if Ticket_print.journey_name:
        journey = string % Ticket_print.journey_name.get().name

    econo = string % Ticket_print.class_name.get().name+" - "+string % Ticket_print.type_name.get().name+" - "+journey
    name = string % Ticket_print.customer.get().first_name+" "+string % Ticket_print.customer.get().last_name
    froms = string % Ticket_print.departure.get().destination.get().destination_start.get().name
    destination = string % Ticket_print.departure.get().destination.get().destination_check.get().name
    date = string % str(function.format_date(Ticket_print.departure.get().departure_date, '%d-%m-%Y'))
    time = string % str(function.format_date(function.add_time(Ticket_print.departure.get().schedule, Ticket_print.departure.get().time_delay), "%H:%M"))
    lieu = string % Ticket_print.agency.get().name
    agent = string % str(Ticket_print.ticket_seller.get().key.id())

    econo_2 = string_2 % Ticket_print.class_name.get().name+" - "+string_2 % Ticket_print.type_name.get().name+" - "+journey
    name_2 = string_2 % Ticket_print.customer.get().first_name+" "+string_2 % Ticket_print.customer.get().last_name
    froms_2 = string_2 % Ticket_print.departure.get().destination.get().destination_start.get().name
    destination_2 = string_2 % Ticket_print.departure.get().destination.get().destination_check.get().name
    date_2 = string_2 % str(function.format_date(Ticket_print.departure.get().departure_date, '%d-%m-%Y'))
    time_2 = string_2 % str(function.format_date(function.add_time(Ticket_print.departure.get().schedule, Ticket_print.departure.get().time_delay), "%H:%M"))
    lieu_2 = string_2 % Ticket_print.agency.get().name

    p.drawImage(url_for('static', filename='BOARDING-ONLY.jpg', _external=True), 0, 0, width=21*cm, height=9.9*cm, preserveAspectRatio=True)

    c = Paragraph(econo_2, style=style['Normal'])
    c.wrapOn(p, width, height)
    c.drawOn(p, 15*cm, 7.9*cm)

    c = Paragraph(econo, style=style['Normal'])
    c.wrapOn(p, width, height)
    c.drawOn(p, 7.8*cm, 7.9*cm)

    c = Paragraph(name_2, style=style['Normal'])
    c.wrapOn(p, width, height)
    c.drawOn(p, 16*cm, 6.65*cm)

    c = Paragraph(name, style=style['Normal'])
    c.wrapOn(p, width, height)
    c.drawOn(p, 2.97*cm, 6.42*cm)

    c = Paragraph(froms_2, style=style['Normal'])
    c.wrapOn(p, width, height)
    c.drawOn(p, 16*cm, 5.67*cm)


    c = Paragraph(froms, style=style['Normal'])
    c.wrapOn(p, width, height)
    c.drawOn(p, 2.97*cm, 4.9*cm)

    c = Paragraph(destination_2, style=style['Normal'])
    c.wrapOn(p, width, height)
    c.drawOn(p, 16*cm, 4.70*cm)

    c = Paragraph(destination, style=style['Normal'])
    c.wrapOn(p, width, height)
    c.drawOn(p, 8.56*cm, 4.9*cm)

    c = Paragraph(date_2, style=style['Normal'])
    c.wrapOn(p, width, height)
    c.drawOn(p, 16*cm, 2.75*cm)

    c = Paragraph(date, style=style['Normal'])
    c.wrapOn(p, width, height)
    c.drawOn(p, 2.97*cm, 3.42*cm)

    c = Paragraph(time_2, style=style['Normal'])
    c.wrapOn(p, width, height)
    c.drawOn(p, 16*cm, 3.70*cm)

    c = Paragraph(time, style=style['Normal'])
    c.wrapOn(p, width, height)
    c.drawOn(p, 8.56*cm, 3.42*cm)

    c = Paragraph(lieu_2, style=style['Normal'])
    c.wrapOn(p, width, height)
    c.drawOn(p, 16*cm, 1.75*cm)

    c = Paragraph(lieu, style=style['Normal'])
    c.wrapOn(p, width, height)
    c.drawOn(p, 2.97*cm, 1.9*cm)

    c = Paragraph(agent, style=style['Normal'])
    c.wrapOn(p, width, height)
    c.drawOn(p, 8.56*cm, 1.9*cm)


    p.saveState()
    p.translate(2*cm, 13.9*cm)
    p.setFillColorRGB(255, 255, 255)
    p.setStrokeColorRGB(255, 255, 255)
    p.rect(-1.1*cm, -12.5*cm, 1.2*cm, 5.5*cm, fill=1)
    p.rotate(-90)
    p.setFillColorRGB(0, 0, 0)
    barcode.drawOn(p, 6.6*cm, -0.80*cm)
    p.restoreState()


    barcode2 = code39.Standard39(code, barHeight=11, stop=1)
    barcode2.humanReadable = 1

    p.saveState()
    p.setFillColorRGB(255, 255, 255)
    p.setStrokeColorRGB(255, 255, 255)
    p.rect(14.5*cm, 0.6*cm, 5.5*cm, 0.9*cm, fill=1)
    p.setFillColorRGB(0, 0, 0)
    barcode2.drawOn(p, 14.2*cm, 1*cm)
    p.restoreState()


    p.showPage()
    p.save()

    pdf_out = output.getvalue()
    output.close()

    response = make_response(pdf_out)
    response.headers["Content-Type"] = "application/pdf"

    return response

