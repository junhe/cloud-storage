import os
import urllib
import webapp2

from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import memcache

class FileKey(db.Model):
  """The key of of the file in memcache and cloud storage"""
  fkey = db.StringProperty()
  blobinfokey = db.StringProperty()

def filelist_key():
  return  db.Key.from_path('Filelist', 'default_filelist')

class MainHandler(webapp2.RequestHandler):
  def get(self):
    upload_url = blobstore.create_upload_url('/upload')
    self.response.out.write('<html><body>')
    self.response.out.write('<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
    self.response.out.write('File Key:<input type="text" name="filekey">')
    self.response.out.write("""Upload File: <input type="file" name="file"><br> <input type="submit"
        name="submit" value="Submit"> </form>""")
    self.response.out.write("""<a href="/list">List</a>""")
    self.response.out.write('</body></html>')

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
    filekey = FileKey(parent=filelist_key())

    # save the file key and blobinfokey to Datastore
    filekey.fkey = self.request.get("filekey")
    self.response.out.write("File key:")
    self.response.out.write(filekey)
         

    upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
    blob_info = upload_files[0]
    filekey.blobinfokey = str(blob_info.key())
    self.response.out.write("Blob info key:")
    self.response.out.write(blob_info.key())
    
    filekey.put()
    #memcache.add("file001", blob_info)
    #self.redirect('/serve/%s' % blob_info.key())

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, resource):
    resource = str(urllib.unquote(resource))
    blob_info = memcache.get("file001") #blobstore.BlobInfo.get(resource)
    self.send_blob(blob_info)

class ListHandler(webapp2.RequestHandler):
  def get(self):
    filekeys = db.GqlQuery("SELECT * "
                            "FROM FileKey "
                            "WHERE ANCESTOR IS :1 ",
                            filelist_key())
    self.response.out.write("List:")
    for filekey in filekeys:
      self.response.out.write(filekey.fkey)
      self.response.out.write('</br>')

app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/upload', UploadHandler),
                               ('/list', ListHandler),
                               ('/serve/([^/]+)?', ServeHandler)],
                              debug=True)
