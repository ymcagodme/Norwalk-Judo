from datetime import datetime
from datetime import date
import time
import csv

# SEE: http://www.traddicts.org/webdevelopment/flexible-and-simple-json-serialization-for-django/ 
from fix_json import JSONSerializer

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.utils import simplejson
import json

from members.models import Member, Parent, Tournament, Membership_fee, USJF_membership, Last_modify_ip, Address, Phone, Belt, Announce, Notification

from members.forms import AnnounceForm

from google.appengine.api import mail

@login_required
def index(request):
    return render_to_response('index.html', {}, context_instance=RequestContext(request))

def query_all(request):
    jsonSerializer = JSONSerializer()
    m_all = Member.objects.all()
    m_list = []
    for m in m_all:
        details = get_details(m)
        key_details = process_details(details)
        json_string = jsonSerializer.serialize(m)
        temp_dict = json.loads(json_string)
        for key, val in key_details.iteritems():
            temp_dict[key] = val
        m_list.append(temp_dict)

    data = jsonSerializer.serialize({'aaData': m_list})

    return HttpResponse(data, mimetype="application/json")

def member_query(request, pk):
    # Flexable json serializer
    jsonSerializer = JSONSerializer()

    m = Member.objects.filter(pk=pk)[0]
    details = get_details(m)
    d = {'aaData': details }

    data = jsonSerializer.serialize(d)
    return HttpResponse(data, mimetype="application/json")

def get_details(m):
    # Flexable json serializer
    jsonSerializer = JSONSerializer()

    phone = m.phone_set.all()
    addr = m.address_set.all()
    belt = m.belt_set.all()
    parent = m.parent_set.all()
    m_fee = m.membership_fee_set.all()
    tournament = m.tournament_set.all()
    usjf = m.usjf_membership_set.all()

    info = jsonSerializer.serialize(phone)
    phone = json.loads(info)
    info = jsonSerializer.serialize(addr)
    addr = json.loads(info)
    info = jsonSerializer.serialize(belt)
    belt = json.loads(info)
    info = jsonSerializer.serialize(parent)
    parent = json.loads(info)
    info = jsonSerializer.serialize(m_fee)
    m_fee = json.loads(info)
    info = jsonSerializer.serialize(tournament)
    tournament = json.loads(info)
    info = jsonSerializer.serialize(usjf)
    usjf = json.loads(info)

    bday = m.birthday

    data = {'phone': phone, 'addr': addr, 'belt': belt, 'parent': parent, 'm_fee': m_fee, 'tournament': tournament, 'usjf': usjf, 'bday': bday}
    return data

def process_details(d):
    key_data = {}
    phone_list = d['phone']
    belt_list = d['belt']
    parent_list = d['parent']

    # Get the preferred phone number
    if len(phone_list) > 0:
        preferred_list = [p for p in phone_list if p['preferred'] == True]
        try:
            key_data.update(preferred_phone=preferred_list[0]['phone_number'])
        except IndexError:
            key_data.update(preferred_phone=phone_list[0]['phone_number'])
    else:
        key_data.update(preferred_phone='N/A')

    # Get current belt color(sort the date)
    belt_color = get_current_belt(belt_list)
    key_data.update(belt_color=belt_color)

    # Get parent's email address
    parent_email_list = []
    for p in parent_list:
        if len(p['email']) > 0:
            parent_email_list.append(p['email'])
    key_data.update(parent_email=parent_email_list)

    # Get USJF #
    usjf = d['usjf']
    if len(usjf) == 0:
        usjf_number = 'N/A'
    else:
        usjf_number = usjf[0]['number']
    key_data.update(usjf=usjf_number)

    # Calculate age
    bday = d['bday']
    age = get_age(bday)
    key_data.update(age=age)
    print key_data


    return key_data

def get_age(bday):
    today = bday.today()
    age = today.year - bday.year
    if bday.month > today.month or (bday.month == today.month and bday.day > today.day):
        age -= 1
    return age

def get_current_belt(belt_list):
    # Get current belt color(sort the date)
    if len(belt_list) > 0:
        belt_list.sort(key=lambda item: item['completed_date'], reverse=True)
        belt_color=belt_list[0]['color']
        return belt_color
    else:
        return 'N/A'

@csrf_exempt
def gen_email_info(request):
    if request.method == 'POST':
        try: m = simplejson.loads(request.raw_post_data)
        except ValueError: return HttpResponse('Invalid Json String')
        try: id_list = m['members']
        except KeyError: return HttpResponse('Invalid Key')
        total_parent_emails = []
        total_member_emails = []
        for i in id_list:
            m = Member.objects.filter(pk=i)[0]
            if m.email != '':
                total_member_emails.append(m.email)
            total_parent_emails.extend(get_parent_email_without_name(m))

        # Flexable json serializer
        jsonSerializer = JSONSerializer()
        #FIXME: Cannot convert this object to json object in the index function, it's weird...
        parent_emails = ' ,'.join(total_parent_emails)
        member_emails = ' ,'.join(total_member_emails)
        d = {'parent_emails': parent_emails, 'member_emails': member_emails }
        data = jsonSerializer.serialize(d)
        return HttpResponse(data, mimetype="application/json")
    return HttpResponse('Invalid http method')

def get_parent_email_without_name(m):
    parent_email = []
    parent_list = get_details(m)['parent']
    for p in parent_list:
        if p['email'] == '':
            continue
        parent_email.append(p['email'])
    return parent_email


# Global variable for serving the csv output with GET(HTTP)
M_CSV_RESPONSE = HttpResponse()

def serve_csv(request):
    global M_CSV_RESPONSE
    response = M_CSV_RESPONSE
    return response

@csrf_exempt
def gen_csv(request):
    time = datetime.now()
    FILENAME = 'judo_members(%s).csv' % (date.isoformat(time), )
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s' % (FILENAME, )
    w = csv.writer(response, dialect='excel')
    if request.method == 'POST':
        try: m = simplejson.loads(request.raw_post_data)
        except ValueError: return HttpResponse('Invalid Json String')
        try: id_list = m['members']
        except KeyError: return HttpResponse('Invalid Key')
        total_cols = get_total_cols(id_list)
        cols_header = get_csv_header(total_cols)
        w.writerow(cols_header)
        for i in id_list:
            m = Member.objects.filter(pk=i)[0]
            row = get_csv_row(m, total_cols)
            w.writerow(row)
        #FIXME: work around for generating a prompt dialog
        global M_CSV_RESPONSE
        M_CSV_RESPONSE = HttpResponse()
        M_CSV_RESPONSE = response
        return HttpResponse('serve_csv')
    return HttpResponse('Invalid http method')

def get_csv_row(m, total_cols):
    d = get_details(m)
    phone_list = d['phone']
    parent_list = d['parent']
    try:
        addr = d['addr'][0]
    except IndexError:
        addr = {}

    #FIXME: DateField object handler
    if m.joined_date == None:
        m.joined_date = 'N/A'
    else:
        m.joined_date = m.joined_date.isoformat()

    FIXED_COLS = [m.first_name, m.last_name, m.gender, m.birthday.isoformat(), get_age(m.birthday), 
                  get_current_belt(d['belt']), m.emergency_number, m.email, 
                  m.grade, addr.get('street', 'N/A'), addr.get('city', 'N/A'), addr.get('state', 'N/A'), 
                  addr.get('postal', 'N/A'), addr.get('country', 'N/A'), m.joined_date, m.activation]

    USJF_COLS = []
    PHONE_COLS = []
    BELT_COLS = []
    PARENT_COLS = []
    M_FEE_COLS = []
    TOURNAMENT_COLS = []

    # Calculate cols of USJF
    usjf_list = d['usjf']
    for i in range(total_cols['usjf']):
        try:
            u = usjf_list[i]
            USJF_COLS.extend([ u['number'], u['expired_date'], u['renew_status'] ])
        except IndexError:
            USJF_COLS.extend([ '', '', '' ])

    # Calculate cols of phone
    phone_list = d['phone']
    for i in range(total_cols['phone']):
        try:
            p = phone_list[i]
            PHONE_COLS.extend([ p['phone_type'], p['phone_number'], p['ext'], p['preferred'] ])
        except IndexError:
            PHONE_COLS.extend([ '', '', '' , '' ])

    # Calculate cols of belt
    belt_list = d['belt']
    for i in range(total_cols['belt']):
        try:
            b = belt_list[i]
            BELT_COLS.extend([ b['color'], b['completed_date'] ])
        except IndexError:
            BELT_COLS.extend([ '', '' ])
            
    # Calculate cols of parent
    parent_list = d['parent']
    for i in range(total_cols['parent']):
        try:
            p = parent_list[i]
            PARENT_COLS.extend([ p['first_name'], p['last_name'], p['relationship'],
                                 p['occupation'], p['phone_number'], p['email'] ])
        except IndexError:
            PARENT_COLS.extend([ '', '', '', '', '', '' ])

    # Calculate cols of member fee
    m_fee_list = d['m_fee']
    for i in range(total_cols['m_fee']):
        try:
            m = m_fee_list[i]
            M_FEE_COLS.extend([ m['amount'], m['paid_date'], m['due_date'], m['status'] ])
        except IndexError:
            M_FEE_COLS.extend([ '', '', '', '' ])

    # Calculate cols of tournament
    tournament_list = d['tournament']
    for i in range(total_cols['tournament']):
        try:
            t = tournament_list[i]
            TOURNAMENT_COLS.extend([ t['title'], t['score'], t['level'], t['hosted_date'], t['belt_color'] ])
        except IndexError:
            TOURNAMENT_COLS.extend([ '', '', '', '' , '' ])

    row = []
    row.extend(FIXED_COLS)
    row.extend(USJF_COLS)
    row.extend(PHONE_COLS)
    row.extend(BELT_COLS)
    row.extend(PARENT_COLS)
    row.extend(M_FEE_COLS)
    row.extend(TOURNAMENT_COLS)
    return row

def get_csv_header(total_cols):
    FIXED_COLS = ['First Name', 'Last Name', 'Gender', 'D.O.B', 'Age', 'Current Belt', 
                  'Emergency #', 'Email', 'Grade', 'Street', 'City', 'State', 'Postal', 
                  'Country', 'Joined Date', 'Activation']
    USJF_COLS = ['USJF #', 'Expiration Date', 'Renew Status']
    PHONE_COLS = ['Phone Type', 'Phone #', 'Ext #', 'Preferred']
    BELT_COLS = ['Belt Color', 'Upgraded Date']
    PARENT_COLS = ['Parent First Name', 'Parent Last Name', 'Relationship', 'Parent Occupation',
                   'Parent Phone #', 'Parent Email']
    M_FEE_COLS = ['Member Fee Amount', 'Paid Date', 'Due Date', 'Pay Status']
    TOURNAMENT_COLS = ['Tournament Title', 'Score', 'Level', 'Hosted Date', 'Belt(while participating)']

    cols_header = []
    cols_header.extend(FIXED_COLS)
    for i in range(total_cols['usjf']):
        cols_header.extend(USJF_COLS)
    for i in range(total_cols['phone']):
        cols_header.extend(PHONE_COLS)
    for i in range(total_cols['belt']):
        cols_header.extend(BELT_COLS)
    for i in range(total_cols['parent']):
        cols_header.extend(PARENT_COLS)
    for i in range(total_cols['m_fee']):
        cols_header.extend(M_FEE_COLS)
    for i in range(total_cols['tournament']):
        cols_header.extend(TOURNAMENT_COLS)
    return cols_header
    

def get_total_cols(id_list):
    cols = {'usjf': 1, 'phone': 1, 'belt': 1, 'parent': 1, 'm_fee': 1, 'tournament': 1}

    for i in id_list:
        m = Member.objects.filter(pk=i)[0]
        d = get_details(m)
        # Calculate cols of USJF
        usjf_list = d['usjf']
        if len(usjf_list) > cols['usjf']:
            cols['usjf'] = len(usjf_list)
        # Calculate cols of phone #
        phone_list = d['phone']
        if len(phone_list) > cols['phone']:
            cols['phone'] = len(phone_list)
        # Calculate cols of belt color
        belt_list = d['belt']
        if len(belt_list) > cols['belt']:
            cols['belt'] = len(belt_list)
        # Calculate cols of parent
        parent_list = d['parent']
        if len(parent_list) > cols['parent']:
            cols['parent'] = len(parent_list)
        # Calculate cols of member fee
        m_fee_list = d['m_fee']
        if len(m_fee_list) > cols['m_fee']:
            cols['m_fee'] = len(m_fee_list)
        # Calculate cols of tournament
        tournament_list = d['tournament']
        if len(tournament_list) > cols['tournament']:
            cols['tournament'] = len(tournament_list)
    return cols

def gen_tournament_report(request):
    time = datetime.now()
    FILENAME = 'tournament_score(%s).csv' % (date.isoformat(time), )
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s' % (FILENAME, )
    w = csv.writer(response, dialect='excel')

    # Get non-repetitive titles
    m_all = Member.objects.all()
    t_list = [ d.get('tournament') for d in [ get_details(m) for m in m_all ] ]
    title_list = []
    for t in t_list:
        title_list.extend(t)
    title_list.sort(key=lambda item: item['hosted_date'])
    titles = [ t.get('title') for t in title_list ]
    union = list( set(titles) )
    for u in union:
        if(titles.count(u) > 1):
            titles.remove(u)

    # Generate the header for csv file
    cols_header = [ 'Last', 'First' , 'Belt Color']
    cols_header.extend(titles)
    cols_header.append('Pts.')

    # Generate rows for csv file
    rows = []
    for m in m_all:
        row = []
        row.append(m.last_name)
        row.append(m.first_name)
        current_belt = get_current_belt([ b for b in ( get_details(m) ).get('belt') ])
        row.append(current_belt)
        t_list = [ d for d in ( get_details(m) ).get('tournament') ]
        score = 0
        for head in titles:
            if head not in [ t for t in get_tournament_titles(t_list) ]:
                row.append('')
                continue
            for t in t_list:
                if head == t['title']:
                    if t['score'] == "3":
                        row.append('1st')
                    if t['score'] == "2":
                        row.append('2nd')
                    if t['score'] == "1":
                        row.append('3rd')
                    if t['score'] == "0.5":
                        row.append('X')
                    score += float(t['score'])
        row.append(score)
        rows.append(row)
    rows.sort(key=lambda l: l[-1:], reverse=True)
    w.writerow(cols_header)
    w.writerows(rows)
    return response


def get_tournament_titles(t_list):
    titles = []
    for t in t_list:
        titles.append(t.get('title'))
    return titles


def announce(request):
    SUCCESS = False
    if request.method == 'POST':
        announce_form = AnnounceForm(request.POST)
        if announce_form.is_valid():
            subject = announce_form.cleaned_data['subject']
            body = announce_form.cleaned_data['body']
            pub_date = datetime.now()
            ip = request.META['REMOTE_ADDR']
            announce_event = Announce()
            announce_event.subject = subject
            announce_event.body = body
            announce_event.pub_date = pub_date
            announce_event.ip = ip
            announce_event.save()
            sender = 'Norwalk Judo <service@norwalkjudo.appspotmail.com>'
            m_all = Member.objects.all()    
            recipients = []
            for m in m_all:
                recipients.extend(get_parent_emails(m))
            mail.send_mail(sender=sender, to=recipients, subject=subject, body=body)
            SUCCESS = True
    else:
        announce_form = AnnounceForm()
    ctx = {'announce_form': announce_form, 'SUCCESS': SUCCESS}
    return render_to_response('announce.html', ctx, context_instance=RequestContext(request))

def get_parent_emails(m):
    parent_list = get_details(m)['parent']
    emails = []
    for p in parent_list:
        if p['email'] == '':
            continue
        addr = '%s %s <%s>' % (p['first_name'], p['last_name'], p['email'])
        emails.append(addr)
    return emails

def usjf_expiration(days, repetitive=False):
    m_all = Member.objects.all()    
    u_list = [ u.get('usjf') for u in [ get_details(m) for m in m_all ] ]
    usjf_list = []
    for u in u_list:
        usjf_list.extend(u)
    expired_member = {}
    for u in usjf_list:
        expired_date = datetime.strptime(u['expired_date'], '%Y-%m-%d')
        delta = expired_date - datetime.now()
        if u['renew_status'] or (delta.days < 0):
            continue
        elif repetitive:
            if days >= delta.days:
                expired_member[ u['member']['pk'] ] = u
        else:
            if days == delta.days:
                expired_member[ u['member']['pk'] ] = u
    return expired_member
    
def m_fee_expiration(days, repetitive=False):
    m_all = Member.objects.all()    
    f_list = [ f.get('m_fee') for f in [ get_details(m) for m in m_all ] ]
    m_fee_list = []
    for f in f_list:
        m_fee_list.extend(f)
    expired_member = {}
    for m in m_fee_list:
        due_date = datetime.strptime(m['due_date'], '%Y-%m-%d')
        delta = due_date - datetime.now()
        if m['status'] or (delta.days < 0):
            continue
        elif repetitive:
            if days >= delta.days:
                expired_member[ m['member']['pk'] ] = m
        else:
            if days == delta.days:
                expired_member[ m['member']['pk'] ] = m
    return expired_member

def notify_expiration(request):
    usjf = {}
    m_fee = {}
    n_all = Notification.objects.all()
    for n in n_all:
        if n.event == 'usjf':
            usjf.update( usjf_expiration(n.days, repetitive=n.repetitive) )
        elif n.event == 'm_fee':
            m_fee.update( m_fee_expiration(n.days, repetitive=n.repetitive) )

    for key, val in m_fee.iteritems():
        m = Member.objects.filter(pk=key)[0]
        due_date = datetime.strptime(val['due_date'], '%Y-%m-%d')
        delta = due_date - datetime.now()

        sender = 'Norwalk Judo <service@norwalkjudo.appspotmail.com>'
        recipients = get_parent_emails(m)
        recipients.append( '%s %s <%s>' % (m.first_name, m.last_name, m.email) )
        subject = "[Notification] Membersip Fee Due Soon"
        body = """

        Dear %s, 
        
        Your Norwalk Judo membership fee due to %s (%s days leave). Please renew it asap.
        
        ------------
        Amount: %s (USD.)
        Due Date: %s
        ------------

        """ % (m.first_name, val['due_date'], delta.days, val['amount'], val['due_date'] )
        mail.send_mail(sender=sender, to=recipients, subject=subject, body=body)

    for key, val in usjf.iteritems():
        m = Member.objects.filter(pk=key)[0]
        expired_date = datetime.strptime(val['expired_date'], '%Y-%m-%d')
        delta = expired_date - datetime.now()

        sender = 'Norwalk Judo <service@norwalkjudo.appspotmail.com>'
        recipients = get_parent_emails(m)
        recipients.append( '%s %s <%s>' % (m.first_name, m.last_name, m.email) )
        subject = "[Notification] USJF Expiration Soon"
        body = """

        Dear %s, 
        
        Your USJF membership is going to expire on %s (%s days leave). Please renew it asap.
        
        ------------
        USJF #: %s
        Expiration Date: %s
        ------------

        """ % (m.first_name, val['expired_date'], delta.days, val['number'], val['expired_date'])
        mail.send_mail(sender=sender, to=recipients, subject=subject, body=body)

    return HttpResponse('Successfully Sent')

def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')
