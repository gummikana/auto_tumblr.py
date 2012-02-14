#!/usr/bin/env python

import sys, time, os, shelve, string, mimetools, mimetypes

#
#   auto_tumblr.py
#
#   Email images and text files placed within a directory to your Tumblr blog.
#   Or anywhere else for that matter. I'm mostly using it to auto update a 
#   tumblr blog.
#
#   Inspired by:
#        http://micampe.it/things/flickruploadr
#
#   Usage:
#
#   The script scans the folder and it's subfolders and emails files it finds 
#   to TUMBLR_EMAIL. The subfolders are used as tags in the post. So you can
#   tag your stuff by creating subfolders. 
#
#   Here's a nice write up of how to use this script. Just replace uploadr.py 
#   with auto_tumblr.py
#   http://lifehacker.com/#!262311/automatically-upload-a-folders-photos-to-flickr
#   Including how to setup it to run in the background
#
#   February 2012  Petri Purho
#
#   You may use this code however you see fit in any form whatsoever. 
#   See LICENSE for more info.
#
##
##  Items you will want to change
## 

#
# Location to scan for new images
#   
TUMBLR_DIR = "c:/temp/your_tumblr_folder/"  
#
# The slash used for this system... 
# On windows it's \ on other operating systems it's /
#
SYSTEM_PATH_SLASH = "\\"
#
#   How often to check for new images to upload  (in seconds )
#
SLEEP_TIME = 1 * 60
#
#   File we keep the history of uploaded images in.
#
HISTORY_FILE = "auto_tumblr.history"

#
# Email address to which you can email tumblr posts to
#
TUMBLR_EMAIL = "your_secret_tumblr_email_address@tumblr.com"


#------------------------------------------------------------------------------
#
# Your gmail data, to email this. I'm using a gmail account to email these
# because it's a nice reliable way of doing it. You can setup what ever email
# you want to use, by tweaking the send_mail function below. But if you're 
# happy using a gmail account to email things, just fill out the variables 
# below
#
GMAIL_FROMADDR = "your.gmail.address@gmail.com"
GMAIL_LOGIN    = GMAIL_FROMADDR
GMAIL_PASSWORD = "YOUR_GMAIL_PASSWORD"


#------------------------------------------------------------------------------
# <send_mail>
import smtplib
import os
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

def send_mail(send_to, subject, text, files=[]):
	assert type(send_to)==list
	assert type(files)==list

	msg = MIMEMultipart()
	msg['From'] = GMAIL_FROMADDR
	msg['To'] = COMMASPACE.join(send_to)
	msg['Date'] = formatdate(localtime=True)
	msg['Subject'] = subject

	msg.attach( MIMEText(text) )

	for f in files:
		image_type = "jpeg"
		ext = f.lower().split(".")[-1]
                if ( ext == "gif" ):
		    image_type = "gif"
		if ( ext == "png" ):
		    image_type = "png"
		
	
		part = MIMEBase('image', image_type)
		part.set_payload( open(f,"rb").read() )
		Encoders.encode_base64(part)
		part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
		msg.attach(part)

	# smtp = smtplib.SMTP(server)
	server = smtplib.SMTP('smtp.gmail.com', 587)
	# server.set_debuglevel(1)
	server.ehlo()
	server.starttls()
	server.login(GMAIL_LOGIN, GMAIL_PASSWORD)
	# print text
	server.sendmail(GMAIL_FROMADDR, send_to, msg.as_string())
	server.quit()

#------------------------------------------------------------------------------


class AutoTumblr:
     
    def upload( self ):
        newFiles = self.grabNewFiles()
        self.uploaded = shelve.open( HISTORY_FILE )
        for file in newFiles:
            self.uploadFile( file )
        self.uploaded.close()
        
    def grabNewFiles( self ):
        files = []
        foo = os.walk( TUMBLR_DIR )
        for data in foo:
            (dirpath, dirnames, filenames) = data
            for f in filenames :
                ext = f.lower().split(".")[-1]
                if ( ext == "jpg" or ext == "gif" or ext == "png" or ext == "txt" ):
                    files.append( os.path.normpath( dirpath + "/" + f ) )
        files.sort()
        return files

    
    def uploadFile( self, file ):
        if ( not self.uploaded.has_key( file ) ):
            print "Uploading ", file , "...",
	    subject = file.split(SYSTEM_PATH_SLASH)[-1].split(".")[0]
	    subject = subject.replace("_", " ").title()

	    tags = ""
	    if(SYSTEM_PATH_SLASH in file[len(TUMBLR_DIR):]):
		all_tags = file[len(TUMBLR_DIR):].split(SYSTEM_PATH_SLASH)
		all_tags.pop() 
		tags = "\n\n"
		for tag in all_tags:
			tags += "#" + tag + " "
	
	    if( file.lower().split(".")[-1] == "txt" ):
	        content = open(file, 'r').read()
		send_mail( [TUMBLR_EMAIL], subject, content + tags, [])
	    else:
                send_mail( [TUMBLR_EMAIL], subject, tags, [file])
		
            print "successful."            
	    self.logUpload( file )


    def logUpload( self, file ):
        file = str( file )
        self.uploaded[ file ] = 1
            
  
    def run( self ):
        while ( True ):
            self.upload()
            print "Last check: " , str( time.asctime(time.localtime()))
            time.sleep( SLEEP_TIME )
      
if __name__ == "__main__":
    auto_tumblr = AutoTumblr()

    if ( len(sys.argv) >= 2  and sys.argv[1] == "-d"):
        auto_tumblr.run()
    else:
        auto_tumblr.upload()
