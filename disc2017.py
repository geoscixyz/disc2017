import cgi
import datetime
import webapp2

from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.api import mail
from google.appengine.api import urlfetch

import os
import jinja2
import urllib, hashlib
import json


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__).split('/')[:-1])),
    extensions=['jinja2.ext.autoescape'],
    autoescape=False)


def setTemplate(self, template_values, templateFile):
    _templateFolder = 'templates/'
    # add Defaults
    template_values['_templateFolder'] = _templateFolder
    template_values['_year'] = str(datetime.datetime.now().year)


    path = os.path.normpath(_templateFolder+templateFile)
    template = JINJA_ENVIRONMENT.get_template(path)
    self.response.write(template.render(template_values))


class MainPage(webapp2.RequestHandler):
    def get(self, mailSent=False):
        # packages = [
        #                 dict(name="SimPEG", link="simpeg", status="check", color="green", description="A framework for simulation and gradient based parameter estimation in geophysics."),
        #                 dict(name="simpegEM", link="simpegem", status="refresh", color="green", description="A electromagnetic forward modeling and inversion package for SimPEG."),
        #                 dict(name="simpegMT", link="simpegmt", status="refresh", color="orange", description="Magnetotellurics forward and inverse codes for SimPEG"),
        #                 dict(name="simpegFLOW", link="simpegflow", status="flask", color="green", description="Groundwater (vadose zone) flow equations written in the SimPEG framework."),
        #                 dict(name="simpegDC", link="simpegdc", status="flask", color="orange", description="A DC resistivity forward modelling and inversion package for SimPEG."),
        #                 dict(name="simpegPF", link="simpegpf", status="flask", color="orange", description="Potential fields codes for SimPEG. Gravity and Magnetics."),
        #                 dict(name="simpegSEIS", link="simpegseis", status="wrench", color="grey", description="Time and frequency domain forward modeling and inversion of seismic wave."),
        #                 dict(name="simpegGPR", link="simpeggpr", status="wrench", color="grey", description="Forward modelling and inversion of Ground-Penetrating Radar (GPR)."),
        #            ]
        setTemplate(self, {"indexPage":True, 'mailSent':mailSent}, 'index.html')
        # data = {'mailSent':mailSent}
        # setTemplate(self, data, 'index.html')

    def post(self):
        email   = self.request.get('email')
        name    = self.request.get('name')
        message = self.request.get('message')

        sender_address = "doug@eos.ubc.ca"
        email_to = "Doug Oldenburg <doug@eos.ubc.ca>"
        email_subject = "DISC2017"
        email_message = "New email from:\n\n%s<%s>\n\n\n%s\n" % (name, email, message)

        mail.send_mail(sender_address, email_to, email_subject, email_message)
        self.get(mailSent=True)


class Why(webapp2.RequestHandler):
    def get(self):
        setTemplate(self, {}, 'why.html')


def getJournals():
    url = baseURL + "/api/blogs/group?match=simpeg&brief=True"
    result = urlfetch.fetch(url)
    if not result.status_code == 200:
        return None
    return json.loads(result.content)


class Journals(webapp2.RequestHandler):
    def get(self):
        js = getJournals()
        for i, j in enumerate(js):
            j['index'] = i
        setTemplate(self, {'blogs': js, 'numBlogs': len(js)}, 'journals.html')


def getJournal(uid):
    url = baseURL + "/api/blog/"+uid
    result = urlfetch.fetch(url)
    if not result.status_code == 200:
        return None
    return json.loads(result.content)


class Journal(webapp2.RequestHandler):
    def get(self):
        slug = self.request.path.split('/')[-1]

        j = getJournal(slug)
        if j is None or len(j) == 0:
            setTemplate(self, {}, 'error.html')
            return

        j['date'] = datetime.datetime.strptime(j['date'], "%Y-%m-%dT%H:%M:%SZ")
        setTemplate(self, {'blog': j}, 'journal.html')


# class Contact(webapp2.RequestHandler):
#     def get(self, mailSent=False):
#         data = {'mailSent':mailSent}
#         # setTemplate(self, data, 'index.html')

#     def post(self):
#         email   = self.request.get('email')
#         name    = self.request.get('name')
#         message = self.request.get('message')

#         sender_address = "lindseyheagy@gmail.com"
#         email_to = "Lindsey Heagy <lindseyheagy@gmail.com>"
#         email_subject = "DISC2017"
#         email_message = "New email from:\n\n%s<%s>\n\n\n%s\n" % (name, email, message)

#         mail.send_mail(sender_address, email_to, email_subject, email_message)
#         self.get(mailSent=True)


class Images(webapp2.RequestHandler):
    def get(self):
        self.redirect('http://disc2017.geosci.xyz'+self.request.path)


class Error(webapp2.RequestHandler):
    def get(self):
        setTemplate(self, {}, 'error.html')


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/img/.*', Images),
    ('/.*', Error),
], debug=os.environ.get("SERVER_SOFTWARE", "").startswith("Dev"))
