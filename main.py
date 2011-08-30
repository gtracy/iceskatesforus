#!/usr/bin/env python

import os
import logging

from django.utils import simplejson

from google.appengine.api import users
from google.appengine.api import images
from google.appengine.api.taskqueue import Task
from google.appengine.ext import db
from google.appengine.ext.db import Key
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from dataModel import *

from facebook import facebook
from users import user
from events import event

class MainHandler(user.BaseHandler):
    def get(self):
      user = self.current_user
      if user:
          if user.fbProfile_url:
              greeting = ('<span class="user-name">%s<br/><a href="javascript:void()" onclick="fbLogout()">sign out</a></span><img src=http://graph.facebook.com/%s/picture>' % (user.nickname,user.userID))
          else:
              greeting = ('%s (<a href="%s">sign out</a>)' % (user.nickname, users.create_logout_url("/")))
      else:
          greeting = '' #("<a href=\"%s\">Sign in with Google</a>" %
                        #'/_ah/login_required')#users.create_login_url("/"))
          # generate the html
          template_values = {'greeting':greeting,}
          path = os.path.join(os.path.dirname(__file__), 'splash.html')
          self.response.out.write(template.render(path, template_values))
          
          #self.redirect("/splash.html")
          return
      
      # get a list of ALL existing skates
      results = []
      skateQuery = db.GqlQuery("SELECT * FROM Skate WHERE swapped = false")
      skates = skateQuery.fetch(100)
      for s in skates:
        #logging.debug('found a skate!')
        if s.owner.first:
            name = s.owner.first + ' ' + s.owner.last
        else:
            name = s.owner.nickname
        if s.picture:
            picture = '/img?id=%s'%s.key()
        else:
            picture = '/img/iceskater.png'
			
		# set styling for price
        if( not s.price or s.price == 0.0 ):
            priceStyle = 'free'
            price = 'free!'
        else:
            priceStyle = 'notfree'
            price = '$'+str(s.price)
            
        # the action is dependent on the logged in user
        if s.owner.userID == user.userID:
            action = '<span class="action-btn delete-btn" skateid="%s">+ Delete</span>' % s.key()
        else:
            action = '<span class="action-btn reserve-btn" skateid="%s">+ Request</span>' % s.key()
            
        if s.owner.fbProfile_url is None:
            profilePic = '<img src="/img/no-avatar.gif">'
        else:
            profilePic = ('<img src=http://graph.facebook.com/%s/picture>' % s.owner.userID)

        results.append({'owner':name,
                        'size':s.size,
                        'color':s.color,
                        'price':price,
                        'picture':picture,
                        'profilePic':profilePic,
                        'note':s.note,
                        'key':s.key(),
						'priceStyle':priceStyle,
                        'action':action,
                       })      
      
      # get a list of recent events
      eventResults = []
      eventQuery = db.GqlQuery("SELECT * FROM UserEvent order by dateAdded DESC")
      events = eventQuery.fetch(20)
      for e in events:
          #logging.debug("found event %s" % str(e.eventType))
          if e.eventType == event.EVENT_SKATE_ADD:
              body = ' has added a new pair of skates.'
          elif e.eventType == event.EVENT_USER_COMMENT:
              body = ' says... %s' % e.metaOne
          elif e.eventType == event.EVENT_USER_ADD:
              body = ' just joined iceskatesfor.us!'
          elif e.eventType == event.EVENT_SKATE_CHECKOUT:
              body = ' has claimed some skates!'
          else:
              body = ''

          if e.user.fbProfile_url is None:
              profilePic = '<img src="/img/no-avatar.gif">'
          else:
              profilePic = ('<img src=http://graph.facebook.com/%s/picture>' % e.user.userID)

          eventResults.append({'body':body,
                               'owner':e.user.nickname,
                               'profilePic':profilePic,
                              })

      if user.fbProfile_url is None:
          facebook_plugin = ''
      else:
          facebook_plugin = '<fb:facepile width="400px"></fb:facepile>'
    
      # add the counter to the template values
      template_values = {'greeting':greeting,
                         'skates':results,
                         'facepile':facebook_plugin,
                         'events':eventResults,
                        }
      
      # generate the html
      path = os.path.join(os.path.dirname(__file__), 'index.html')
      self.response.out.write(template.render(path, template_values))

class AddCommentHandler(user.BaseHandler):
    def post(self):
        activeUser = self.current_user
        event.createEvent(event.EVENT_USER_COMMENT,
                          activeUser,
                          None,
                          self.request.get('comment'),
                          None)
        if activeUser.fbProfile_url is None:
            profilePic = '<img src="/img/no-avatar.gif">'
        else:
            profilePic = ('<img src=http://graph.facebook.com/%s/picture>' % activeUser.userID)

        # encapsulate response in json
        response_dict = {}
        response_dict.update({'profilePic':profilePic,
                              'body':self.request.get('comment'),
                             })
        logging.debug('json response %s' % response_dict);
            
        self.response.headers['Content-Type'] = 'application/javascript'
        self.response.out.write(simplejson.dumps(response_dict))

## end AddCommentHandler

        
class AddSkateHandler(user.BaseHandler):
    
    def post(self):
      activeUser = self.current_user
      
      skate = Skate()
      skate.owner = activeUser
      if self.request.get('size'): 
          skate.size = float(self.request.get('size'))
      if self.request.get('price'):
          if self.request.get('price') == 'FREE!':
              skate.price = 0
          else:
              skate.price = int(self.request.get('price'))
      skate.note = self.request.get('notes')
      if self.request.get('image'):
          skatePic = True
          logging.info('image being stored as a blob');
          uploadImage = images.resize(self.request.get('image'),300)
          skate.picture = db.Blob(uploadImage)
      else:
          skatePic = False

      # @todo fill out other properties
      skate.swapped = False
      skate.status = 0
      skate.put()
      
      # log event
      event.createEvent(event.EVENT_SKATE_ADD, activeUser, skate, ('price=%s' % skate.price))

      # set styling for price
      if( not skate.price or skate.price == 0.0 ):
          priceStyle = 'free'
          price = 'free!'
      else:
          priceStyle = 'notfree'
          price = '$'+str(skate.price)
      
      # encapsulate in json
      response_dict = {}
      if activeUser.first:
          owner = activeUser.first + ' ' + activeUser.last
      else:
          owner = activeUser.nickname
      response_dict.update({'owner':owner,
                            'size':skate.size,
                            'color':skate.color,
                            'price':price,
                            'priceStyle':priceStyle,
                            'note':skate.note,
                            'picture':'/img?id=%s'%skate.key() if skatePic else '/img/iceskater.png',
                           })
      logging.debug('json response %s' % response_dict);
            
      self.response.headers['Content-Type'] = 'application/javascript'
      self.response.out.write(simplejson.dumps(response_dict))

## end AddSkateHandler

class DeleteSkateHandler(user.BaseHandler):
    def post(self):
        activeUser = self.current_user
        skateKey = self.request.get("key")
        logging.info("deleting skate %s for user %s" % (skateKey,activeUser.nickname))
        skate = db.get(skateKey)
        if skate is None:
            logging.error("Whoops. Someone is deleting a skate with an illegal key!?!")
            self.response.set_status(403)
            return

        logging.info("removing the skate from the live list...")
        skate.status = 1
        skate.swapped = True
        skate.put()
        
        self.response.set_status(200)
        return        
        
## end DeleteSkateHandler

class ReserveSkateHandler(user.BaseHandler):
    
    def post(self):
        activeUser = self.current_user;
        skateKey = self.request.get("key")
        logging.debug("looking for skate key %s" % skateKey)
        skate = db.get(skateKey)
        if skate is None:
            logging.error("Impossible. I couldn't find skate with that key")
            self.response.set_status(403)
            return
        else:
            logging.info("I found your skate! From %s, size %s (%s)" % (skate.owner.nickname, skate.size,skate.note))
        
        skate.status = 1
        skate.put() 

        # construction the email with the transaction details
        template_values = {'owner':skate.owner.nickname, 
                           'borrower':activeUser.nickname,
                           'borrowerEmail':activeUser.email,
                           'size':skate.size,
                           'price':skate.price,
                           'style':skate.style,
                           'note':skate.note,
                           }       
        path = os.path.join(os.path.dirname(__file__), 'checkout-email.html')
        body = template.render(path, template_values)
    
        # log event
        event.createEvent(event.EVENT_SKATE_CHECKOUT, activeUser, skate, str(skate.price))
      
        # send out email notification
        logging.debug("creating email task for checkout... send to owner %s and borrower %s" % (skate.owner.email,activeUser.email))
        task = Task(url='/event/email', params={'ownerEmail':skate.owner.email,
                                                'borrowerEmail':activeUser.email,
                                                'body':body})
        task.add('emailqueue')
        self.response.set_status(200)
        return

## end ReserveSkateHandler

class Image (webapp.RequestHandler):
    def get(self):
      skate = db.get(self.request.get("id"))
      if skate.picture:
          self.response.headers['Content-Type'] = "image/png"
          self.response.out.write(skate.picture)
      else:
          self.error(404)

## end Image

def main():
    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication([('/', MainHandler),
                                          ('/addskate', AddSkateHandler),
                                          ('/addcomment', AddCommentHandler),
                                          ('/skate/checkout', ReserveSkateHandler),
                                          ('/skate/delete', DeleteSkateHandler),
                                          ('/img', Image),
                                         ],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
