# Copyright 2011 Google Inc. All Rights Reserved.
"""Create, Write, Read and Finalize Google Cloud Storage objects.

EchoPage will create, write and read the Cloud Storage object in one request:
  http://your_app_id.appspot.com/echo?message=Leeroy+Jenkins

MainPage, CreatePage, AppendPage and ReadPage will do the same in multiple
requests:
  http://your_app_id.appspot.com/
"""

import cgi
import urllib
import webapp2
from google.appengine.api import files
from google.appengine.ext import db

try:
    files.gs
except AttributeError:
    import gs
    files.gs = gs


class EchoPage(webapp2.RequestHandler):
    """A simple echo page that writes and reads the message parameter."""

    # TODO: Change to a bucket your app can write to.
    READ_PATH = '/gs/buckcs553pa3/myobj'

    def get(self):
        # Create a file that writes to Cloud Storage and is readable by everyone
        # in the project.
        write_path = files.gs.create(self.READ_PATH, mime_type='text/plain',
                                     acl='public-read')
        # Write to the file.
        with files.open(write_path, 'a') as fp:
            fp.write(self.request.get('message'))

        # Finalize the file so it is readable in Google Cloud Storage.
        files.finalize(write_path)

        # Read the file from Cloud Storage.
        with files.open(self.READ_PATH, 'r') as fp:
            buf = fp.read(1000000)
            while buf:
                self.response.out.write(buf)
                buf = fp.read(1000000)


class EventLog(db.Model):
    """Stores information used between requests."""
    title = db.StringProperty(required=True)
    read_path = db.StringProperty(required=True)
    write_path = db.TextProperty(required=True)  # Too long for StringProperty
    finalized = db.BooleanProperty(default=False)


class MainPage(webapp2.RequestHandler):
    """Prints a list of event logs and a link to create a new one."""

    def get(self):
        """Page to list event logs or create a new one.

        Web page looks like the following:
          Event Logs
            * Dog barking
            * Annoying Squirrels (ongoing)
            * Buried Bones
          [New Event Log]
        """
        self.response.out.write(
            """
            <html> <body>
            <h1>Event Logs</h1>
            <ul>
            """)
        # List all the event logs in the datastore.
        for event_log in db.Query(EventLog):
            # Each EventLog has a unique key.
            key_id = event_log.key().id()
            if event_log.finalized:
                # Finalized events must be read
                url = '/read/%d' % key_id
                title = '%s' % cgi.escape(event_log.title)
            else:
                # Can only append to writable events.
                url = '/append/%d' % key_id
                title = '%s (ongoing)' % cgi.escape(event_log.title)
            self.response.out.write(
                """
                <li><a href="%s">%s</a></li>
                """ % (url, title))
        # A form to allow the user to create a new Cloud Storage object.
        self.response.out.write(
            """
            </ul>
            <form action="create" method="post">
              Title: <input type="text" name="title" />
              <input type="submit" value="New Event Log" />
            </form>
            </body> </html>
            """)


class CreatePage(webapp2.RequestHandler):
    """Creates a Cloud Storage object that multiple requests can write to."""

    BUCKET = '/gs/buckcs553pa3'  # TODO: Change to a bucket your app can write to.

    def post(self):
        """Create a event log that multiple requests can build.

        This creates an appendable Cloud Storage object and redirects the user
        to the append page.
        """
        # Choose an interesting title for the event log.
        title = self.request.get('title') or 'Unnamed'

        # We will store the event log in a Google Cloud Storage object.
        # The Google Cloud Storage object must be in a bucket the app has access
        # to, and use the title for the key.
        read_path = '/gs/%s/%s' % (self.BUCKET, title)
        # Create a writable file that eventually become our Google Cloud Storage
        # object after we finalize it.
        write_path = files.gs.create(read_path, mime_type='text/plain')
        # Save these paths as well as the title in the datastore so we can find
        # this during later requests.
        event_log = EventLog(
            read_path=read_path, write_path=write_path, title=title)
        event_log.put()
        # Redirect the user to the append page, where they can start creating
        # the file.
        self.redirect('/append/%d?info=%s' % (
            event_log.key().id(), urllib.quote('Created %s' % title)))


class AppendPage(webapp2.RequestHandler):
    """Appends data to a Cloud Storage object between multiple requests."""

    @property
    def key_id(self):
        """Extract 123 from /append/123."""
        return int(self.request.path[len('/append/'):])

    def get(self):
        """Display a form the user can use to build the event log.

        Web page looks like:
          Append to Event Title

          /--------------\
          |Log detail... |
          |              |
          |              |
          \--------------/

          [ ] Finalize log
          [ Append message ]
        """

        # Grab the title, which we saved to an EventLog object in the datastore.
        event_log = db.get(db.Key.from_path('EventLog', self.key_id))
        title = event_log.title
        # Display a form that allows the user to append a message to the log.
        self.response.out.write(
            """
            <html> <body>
            <h1>Append to %s</h1>
            <div>%s</div>
            <form method="post">
            <div><textarea name="message" rows="5" cols="80"></textarea></div>
            <input type="checkbox" name="finalize" value="1">Finalize log</input>
            <input type="submit" value="Append message" />
            </form>
            </body> </html>
            """ % (
                cgi.escape(title),
                cgi.escape(self.request.get('info')),
                ))

    def post(self):
        """Append the message to the event log.

        Find the writable Cloud Storage path from the specified EventLog.
        Append the form's message to this path.
        Optionally finalize the object if the user selected the checkbox.
        Redirect the user to a page to append more or read the finalized object.
        """
        # Use the id in the post path to find the EventLog object we saved in the
        # datastore.
        event_log = db.get(db.Key.from_path('EventLog', self.key_id))
        # Get writable Google Cloud Storage path, which we saved to an EventLog
        # object in the datastore.
        write_path = event_log.write_path
        # Get the posted message from the form.
        message = self.request.get('message')
        # Append the message to the Google Cloud Storage object.
        with files.open(event_log.write_path, 'a') as fp:
            fp.write(message)
        # Check to see if the user is finished writing.
        if self.request.get('finalize'):
            # Finished writing.  Finalize the object so it becomes readable.
            files.finalize(write_path)
            # Tell the datastore that we finalized this object. This makes the
            # main page display a link that reads the object.
            event_log.finalized = True
            event_log.put()
            self.redirect('/read/%d' % self.key_id)
        else:
            # User is not finished writing.  Redirect to the append form.
            self.redirect('/append/%d?info=%s' % (
                self.key_id, urllib.quote('Appended %d bytes' % len(message))))


class ReadPage(webapp2.RequestHandler):
    """Reads a Cloud Storage object and prints it to the page."""

    @property
    def key_id(self):
        """Extract 123 from /read/123."""
        return int(self.request.path[len('/read/'):])

    def get(self):
        """Display the EventLog to the user.

        Web page looks like the following:
          Event Log Title

          Event log description.
          [ Download from Cloud Storage ]
        """
        self.response.out.write(
            """
            <html> <body>
            """)
        # Use the get request path to find the event log in the datastore.
        event_log = db.get(db.Key.from_path('EventLog', self.key_id))
        read_path = event_log.read_path
        title = event_log.title
        # Print the title
        self.response.out.write(
            """
            <h1>%s</h1>
            """ % cgi.escape(title))
        # Read the object from Cloud Storage and write it out to the web page.
        self.response.out.write(
            """
            <pre>
            """)
        with files.open(read_path, 'r') as fp:
            buf = fp.read(1000000)
            while buf:
                self.response.out.write(cgi.escape(buf))
                buf = fp.read(1000000)
        self.response.out.write(
            """
            </pre>
            """)

        self.response.out.write(
            """
            <div><a href="/">Event Logs</a></div>
            </body> </html>
            """)

app = webapp2.WSGIApplication(
    [
        ('/create', CreatePage),
        ('/append/.*', AppendPage),
        ('/read/.*', ReadPage),
        ('/echo', EchoPage),
        ('/.*', MainPage),
    ], debug=True)