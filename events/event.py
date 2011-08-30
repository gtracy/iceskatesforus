#!/usr/bin/env python
#
import os
import logging

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import util
from google.appengine.runtime import apiproxy_errors
from google.appengine.api import mail

from dataModel import *



EVENT_SKATE_ADD      = 0
EVENT_SKATE_CHECKOUT = 1

EVENT_USER_NOTE      = 2
EVENT_USER_ADD       = 3

EVENT_USER_COMMENT   = 10


class EmailWorker(webapp.RequestHandler):
    def post(self):        
        try:
            ownerEmail = self.request.get('ownerEmail')
            borrowerEmail = self.request.get('borrowerEmail')
            body = self.request.get('body')
            logging.debug("email task running for %s", ownerEmail)
        
            # send email 
            message = mail.EmailMessage()
            message.subject = "iceskatesfor.us request notification"
            message.sender='info@iceskatesfor.us'                 
            message.to = ownerEmail+','+borrowerEmail
            message.html = body
            message.send()

        except apiproxy_errors.DeadlineExceededError:
            logging.info("DeadlineExceededError exception!?! Try to set status and return normally")
            self.response.clear()
            self.response.set_status(200)
            self.response.out.write("Task took to long for %s - BAIL!" % email)

## end EmailWorker

def createEvent(eventType, 
                user,
                skate,
                metaNoteOne='',
                metaNoteTwo=''):

    logging.debug("EVENT: logging user event from %s, meta: %s" % (user.nickname,metaNoteOne))
    event = UserEvent()
    event.eventType = eventType
    event.user = user
    event.skate = skate
    event.metaOne = metaNoteOne
    event.metaTwo = metaNoteTwo
    event.put()
    
## end createEvent()    


def main():
    application = webapp.WSGIApplication([('/event/email', EmailWorker),
                                         ],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

