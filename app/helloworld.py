import os
import urllib
import webapp2

from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import memcache

class FileKey(db.Model):
  """The key of of the file in memcache and cloud storage"""
  #fkey = db.StringProperty()
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
    # check    
    self.response.out.write("""
          <hr>
          <form action="/check" method="post">
            <div>File Key:<input type="text" name="filekey"></div>
            <div><input type="submit" value="Check This File Key"></div>
          </form>
          <hr>""")
    # delete
    self.response.out.write("""
          <hr>
          <form action="/remove" method="post">
            <div>File Key:<input type="text" name="filekey"></div>
            <div><input type="submit" value="Remove"></div>
          </form>
          <hr>""")          
    # Download     
    self.response.out.write("""
          <hr>
          <form action="/download" method="post">
            <div>File Key:<input type="text" name="filekey"></div>
            <div><input type="submit" value="Find/Download"></div>
          </form>
          <hr>""")
    # List
    self.response.out.write("""<a href="/list">List</a>""")
    self.response.out.write('</body></html>')

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
    # save the file key and blobinfokey to Datastore
    mykey = self.request.get("filekey")
    filekey = FileKey(key_name =mykey, parent=filelist_key())
    self.response.out.write("File key:")
    self.response.out.write(filekey.key().id_or_name())
         

    upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
    blob_info = upload_files[0]
    filekey.blobinfokey = str(blob_info.key())
    self.response.out.write("Blob info key:")
    self.response.out.write(blob_info.key())
    
    memcache.add(mykey, blob_info)
    
    filekey.put()
    
    #self.redirect('/serve/%s' % blob_info.key())

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, resource):
    resource = str(urllib.unquote(resource))
    blob_info = memcache.get("file001") #blobstore.BlobInfo.get(resource)
    self.send_blob(blob_info)

class ListHandler(webapp2.RequestHandler):
  def get(self):
    #filekeys = db.GqlQuery("SELECT * "
    #                        "FROM FileKey "
    #                        "WHERE ANCESTOR IS :1",# AND fkey IN ('ttt')",
    #                        filelist_key())
    filekeys = FileKey.all()
    self.response.out.write("<b>List</b>:</br>")
    for filekey in filekeys:
      self.response.out.write(filekey.key().id_or_name())
      self.response.out.write('</br>')

class CheckHandler(webapp2.RequestHandler):
  def post(self):
    fkeystr = self.request.get("filekey")
    filekeys = FileKey.all()
    filekeys.filter('__key__ =', db.Key.from_path("FileKey", fkeystr, parent=filelist_key()))
    if filekeys.count() == 0:
      self.response.out.write("Key(%s) does NOT exists." % fkeystr)
    else:
      self.response.out.write("Key(%s) exists." % fkeystr)

class DownloadHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def post(self):
    fkeystr = self.request.get("filekey")
    filekeys = FileKey.all()
    filekeys.filter('__key__ =', db.Key.from_path("FileKey", fkeystr, parent=filelist_key()))
    if filekeys.count() == 0:
      self.response.out.write("Key(%s) does NOT exists." % fkeystr)
    else:
      blob_info = memcache.get(fkeystr) #blobstore.BlobInfo.get(resource)
      self.send_blob(blob_info)
    
class RemoveHandler(webapp2.RequestHandler):
  def post(self):
    fkeystr = self.request.get("filekey")
    filekeys = FileKey.all()
    thekey = db.Key.from_path("FileKey", fkeystr, parent=filelist_key())
    filekeys.filter('__key__ =', thekey)
    if filekeys.count() == 0:
      self.response.out.write("Key(%s) does NOT exists." % fkeystr)
    else:
      db.delete(thekey)
      self.response.out.write("Key(%s) removed." % fkeystr)
      
  
  
  
  
      
app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/upload', UploadHandler),
                               ('/list', ListHandler),
                               ('/check', CheckHandler),
                               ('/download', DownloadHandler),
                               ('/remove', RemoveHandler),
                               ('/serve/([^/]+)?', ServeHandler)],
                              debug=True)
