#!/usr/bin/python
import sys
from xml.etree import ElementTree
from ConfigParser import ConfigParser
from StringIO import StringIO
import os
import os.path
import requests
from zipfile import ZipFile

def unpack_attachment(path):
    f = ZipFile(path)
    names = f.namelist()
    issue_dir = os.path.dirname(path)
    if len(names) == 1:
        f.extract(names[0], issue_dir)
        print "Unpacked " + names[0]
        return os.path.join(issue_dir, names[0])
    else:
        out_path = path[:-4]
        for name in names:
            f.extract(name, out_path)
            print "Unpacked " + name + " to " + out_path

def grab_attachment(youtrack_url, session, attachments_dir, attachment):
    name = attachment.get('name')
    
    if name.endswith('.jpg') or name.endswith('.png'):
        print "Skipping download of image attachment " + name
        return None
    
    if name.find('/') >= 0 or name.find('\\') >= 0:
        print "Attachment name contains invalid characters, download skipped"
        return None

    attachment_url = youtrack_url + attachment.get('url')
    out_path = os.path.join(attachments_dir, name)
    out = open(out_path, 'wb')
    try:
        r = session.get(attachment_url, stream=True)
        for chunk in r.iter_content(16384):
            out.write(chunk)
        print "Downloaded attachment " + name
    finally:
        out.close()
    if name.endswith('.zip'):
        unpacked = unpack_attachment(out_path)
        os.remove(out_path)
        out_path = unpacked
    return out_path

def grab(youtrack_url, session, directory, issue_id):
    r = session.get(youtrack_url + "/rest/issue/byid/" + issue_id)
    issueXml = ElementTree.parse(StringIO(r.text))
    issue = issueXml.getroot()
    attachments = issue.find('attachments')
    if not len(attachments):
        print "Issue " + issue_id + " does not have any attachments"
    attachments_dir = os.path.join(directory, issue_id)
    if not os.path.exists(attachments_dir):
        os.makedirs(attachments_dir)
    downloaded_paths = []
    for attachment in attachments:
        out = grab_attachment(youtrack_url, session, attachments_dir, attachment)
        if out: downloaded_paths.append(out)
    if len(downloaded_paths) == 1:
        command = 'start' if os.name == 'nt' else 'open'
        os.system(command + ' ' + downloaded_paths[0])

if len(sys.argv) != 3 or sys.argv[1] != "grab":
    print "Usage: yt grab <issue-id>"
    sys.exit(0)

issue_id = sys.argv[2]

config = ConfigParser()
config.read(['jbcl.conf', os.path.expanduser('~/jbcl.conf')])

youtrack_url = config.get("youtrack", "url")
if youtrack_url[-1] == '/': youtrack_url = youtrack_url[:-1]

s = requests.Session()
login = config.get("youtrack", "login")
password = config.get("youtrack", "password")
if login and password:
    r = s.post(youtrack_url + "/rest/user/login", params={'login': login, 'password': password})
    if r.status_code != 200:
       print "YouTrack login failed"
       sys.exit(0)

attachments_dir = os.path.expanduser(config.get("youtrack", "attachments"))
grab(youtrack_url, s, attachments_dir, sys.argv[2])
