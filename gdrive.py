from __future__ import print_function
import httplib2
import os

from apiclient import errors
from apiclient import discovery
from apiclient import http
import oauth2client

from oauth2client import client
from oauth2client import tools

import zipfile,os.path
from os import walk

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive  https://www.googleapis.com/auth/drive.file  https://www.googleapis.com/auth/drive.metadata'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API Python Quickstart'


def delete_file(service, file_id):
    try:
        service.files().delete(fileId=file_id).execute()
    except errors.HttpError, error:
        print ('An error occurred While delete: %s' % error)

def createfolder(drive_service, parents, name):
    file_metadata = {
        'name': [name],
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parents]
    }
    file = drive_service.files().create(body=file_metadata,
                                        fields='id').execute()
    return file.get('id')

def unzip(source_filename, dest_dir):
    with zipfile.ZipFile(source_filename) as zf:
        for member in zf.infolist():
            # Path traversal defense copied from
            # http://hg.python.org/cpython/file/tip/Lib/http/server.py#l789
            words = member.filename.split('/')
            path = dest_dir
            for word in words[:-1]:
                while True:
                    drive, word = os.path.splitdrive(word)
                    head, word = os.path.split(word)
                    if not drive:
                        break
                if word in (os.curdir, os.pardir, ''):
                    continue
                path = os.path.join(path, word)
            zf.extract(member, path)

def get_credentials():

    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    #Google doesn't use file name as a primary key.
    #It uses unique ID as a key to access to the specific file or folder.
    #The goal of this application is to download ZIP file from Google Drive
    #And extract it, and then upload only jpg files to your Google Drive.

    #m:0BytZMivljGnOMzhTX2c5b1hoRFU
    #e:0BytZMivljGnOZkFlQWhHV0JwVjg
    targetFolder = '0BytZMivljGnOZkFlQWhHV0JwVjg'
    credentials = get_credentials()

    #This single line is different from what Google provides you.
    #In order to download and upload you should import http from API Client
    #However, if you use the variable 'http' prior to download or upload,
    #you would not be able to use 'http API from API Client'
    #Thus, you should avoid using the variable 'http'
    #Actually, the communication protocol is https, so that it more makes sense to use 'https'
    https = credentials.authorize(httplib2.Http())

    #This variable actually provides you with Google APIs.
    #It uses https communication to allow you to use API sets that Google provides to you.
    service = discovery.build('drive', 'v3', http=https)

    results = service.files().list(
        pageSize=3,
        q="mimeType='application/zip' and '0BytZMivljGnOZkFlQWhHV0JwVjg' in parents",
        fields="nextPageToken, files(id, name, parents)"
    ).execute()

    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        i = 0
        for item in items:
            https = credentials.authorize(httplib2.Http())
            service = discovery.build('drive', 'v3', http=https)

            name = item['name']
            ids = item['id']
            parents = item['parents']

            real_name = name.encode("utf-8")

            #File Download
            print('{0} ({1}, {2})'.format(real_name, ids, parents))
            request = service.files().get_media(fileId=ids)
            fh = open(real_name, 'wb')
            downloader = http.MediaIoBaseDownload(fh, request)
            done = False
            current = 0
            while done is False:
                status, done = downloader.next_chunk()
                if current != int(status.progress() * 100):
                    current = int(status.progress() * 100)
                    print("Download %d%%." % current)
            fh.close()

            currentpath = os.path.dirname(__file__)

            ### Unzip and Upload
            filename = real_name

            destination = currentpath + "/" + filename + "_folder"

            print("Start to unzip...")
            unzip(filename, destination)
            print("Unzip Done.")

            f = []
            for (dirpath, dirnames, filenames) in walk(destination):
                if (len(dirnames) == 0):
                    folderid = createfolder(service, targetFolder, lastplace)

                    for file in filenames:
                        # Upload files.
                        file_metadata = {
                            'name': [file],
                            'mimeType': 'image/jpg',
                            'parents': [folderid]
                        }
                        if file.endswith(".jpg") or file.endswith(".JPG"):
                            fullpath = dirpath + "/" + file
                            media = http.MediaFileUpload(fullpath,
                                                         mimetype='image/jpg',
                                                         resumable=True)
                            file = service.files().create(body=file_metadata,
                                                          media_body=media,
                                                          fields='id').execute()
                            print('File ID: %s' % file.get('id'))
                else:
                    #Len (Dir name) > 0
                    lastplace = dirnames[0]
            #End For File Loop
            #File Delete
            delete_file(service, ids)
            print("file deleted.")

            i = i + 1

if __name__ == '__main__':
    main()

#mimeType='application/zip'
