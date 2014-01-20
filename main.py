#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import jinja2
import webapp2
import requests

#importing no sqldb
from google.appengine.ext import ndb

#setting up Jinja environment to be use for templates
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

	
smsapilog_key = ndb.Key('SMSAPILog', 'default_smsapilog')

#Log class corresponds to each row in database
#Has following properties
#content: Result of the api call
#responseTime: Is the actual response time for api call
#date: Used to store the date time stamp, when api call was made(Is used to sort results to display in descending order)
class Log(ndb.Model):
  content = ndb.TextProperty()
  responseTime = ndb.TextProperty()
  date = ndb.DateTimeProperty(auto_now_add=True)
  
#Main Handler class, setup query to get top 10 results. Setup values to be passed to Jinja template and call template so that it can be rendered.
class MainHandler(webapp2.RequestHandler):
  def get(self):
    logs = ndb.gql('SELECT * '
                        'FROM Log '
                        'WHERE ANCESTOR IS :1 '
                        'ORDER BY date DESC LIMIT 10',
                        smsapilog_key)

    template_values = {
            'logs': logs
        }
    template = JINJA_ENVIRONMENT.get_template('index.html')
    self.response.write(template.render(template_values))

#SMSAPILog class calls the api; this class will be initiated when manual test will be run and also from scheduling task. it write the results using Log class.
class SMSAPILog(webapp2.RequestHandler):
  def get(self):
    log = Log(parent=smsapilog_key)

    request = requests.get("http://c4.commercetel.com/C4CServices/ExternalWebServices/SendDynamicSMS.aspx?PhoneNumber=16022848690&MessageText=test&login=Interview3API&password=Interview3API&targetid=299624")
	
    log.content = request.content
	
    seconds = request.elapsed.seconds
    milliseconds = request.elapsed.microseconds/1000
	
    if seconds > 0:
        responseTime = str(seconds) +'.'+str(milliseconds) + ' s'
    else:
        responseTime = str(milliseconds) + ' ms'

    log.responseTime = responseTime 
	
    log.put()
    self.redirect('/')
    self.response.http_status_message(200)
app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/run', SMSAPILog)	
], debug=True)
