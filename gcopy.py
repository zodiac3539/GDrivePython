from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from apiclient import http
from apiclient import errors
import oauth2client

from oauth2client import client
from oauth2client import tools

import sys

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive  https://www.googleapis.com/auth/drive.file  https://www.googleapis.com/auth/drive.metadata'
CLIENT_SECRET_FILE = 'client_secret.json'
CLIENT_SECRET_FILE2 = 'client_secret2.json'
APPLICATION_NAME = 'Drive API Python Quickstart'
DIR_FOR_THIS = '/Users/seokbongchoi/Documents/folder/'
TARGET_DIR_ID='0BytZMivljGnOMzhTX2c5b1hoRFU'

def printProgress (iteration, total, prefix = '', suffix = '', decimals = 2, barLength = 100):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : number of decimals in percent complete (Int)
        barLength   - Optional  : character length of bar (Int)
    """
    filledLength    = int(round(barLength * iteration / float(total)))
    percents        = round(100.00 * (iteration / float(total)), decimals)
    bar             = '#' * filledLength + '-' * (barLength - filledLength)
    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),
    sys.stdout.flush()
    if iteration == total:
        sys.stdout.write('\n')
        sys.stdout.flush()

def get_credentials1():

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

def get_credentials2():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'drive-python-quickstart2.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE2, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def getDirectoryList(service):
    results = service.files().list(
        pageSize=1,
        q="mimeType='application/vnd.google-apps.folder' and '0Bxx7rAqKqwURUW5VTTU1Yk1LbFk' in parents",
        fields="nextPageToken, files(id, name, parents)"
    ).execute()

    items = results.get('files', [])

    ret = {
        'name': '',
        'id' : '',
        'parents' : ''
    };

    if not items:
        return ret
    else:
        item = items[0]
        print ('Retrieving: ' + item['name'])
        return item

def getFileList(service, parents):
    query = "'{0}' in parents".format(parents)
    print(query)
    results = service.files().list(
        pageSize=150,
        q=query,
        fields="nextPageToken, files(id, name, parents)"
    ).execute()
    items = results.get('files', [])

    if not items:
        print('No File!')
        exit()
    else:
        return items

def findAndCreateFolder(service, foldername):
    query = "name='{0}' and mimeType='application/vnd.google-apps.folder' and '{1}' in parents".format(foldername, TARGET_DIR_ID)
    print('Find Query:' + query)
    results = service.files().list(
        pageSize=1,
        q=query,
        fields="nextPageToken, files(id, name, parents)"
    ).execute()
    items = results.get('files', [])

    if not items:
        print('No Folder Create it...')
        file_metadata = {
            'name': [foldername],
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [TARGET_DIR_ID]
        }
        file = service.files().create(body=file_metadata,
                                            fields='id').execute()
        return file.get('id')
    else:
        print('Found it...')
        item = items[0]
        if item['name'] != foldername:
            print('fuck.')
            exit()
        return item['id']

def delete_file(service, file_id):
    service.files().delete(fileId=file_id).execute()

def delete_ifexist(service, file_name, folderid):
    query = "name='{0}' and '{1}' in parents".format(file_name, folderid)
    results = service.files().list(
        pageSize=1,
        q=query,
        fields="nextPageToken, files(id, name, parents)"
    ).execute()
    items = results.get('files', [])

    if not items:
        return True
    else:
        print('')

        item = items[0]
        if item['name'] != file_name:
            print('File name is different????')
            exit()
        print('Duplicate File: ' + item['name'])
        service.files().delete(fileId=item['id']).execute()
        return False

def download_file(service, file_id, file_name):
    request = service.files().get_media(fileId=file_id)
    real_name = DIR_FOR_THIS + file_name
    fh = open(real_name, 'wb')
    downloader = http.MediaIoBaseDownload(fh, request)
    done = False
    current = 0
    while done is False:
        status, done = downloader.next_chunk()
        if current != int(status.progress() * 100):
            current = int(status.progress() * 100)
    fh.close()


def upload_file(service, file_name, folderid):
    file_metadata = {
        'name': [file_name],
        'mimeType': 'image/jpg',
        'parents': [folderid]
    }

    fullpath = DIR_FOR_THIS + file_name
    media = http.MediaFileUpload(fullpath,
                                     mimetype='image/jpg',
                                     resumable=True)
    file = service.files().create(body=file_metadata,
                                  media_body=media,
                                  fields='id, name').execute()

def main():
    credentials1 = get_credentials2()
    https1 = credentials1.authorize(httplib2.Http())
    service1 = discovery.build('drive', 'v3', http=https1)

    # Get Directory List
    # Use First Directory
    first_item = getDirectoryList(service1)
    source_items = getFileList(service1, first_item['id'])

    #for source_item in source_items:
    #    print(source_item['name'])

    #Activate Service2
    credentials2 = get_credentials1()
    https2 = credentials2.authorize(httplib2.Http())
    service2 = discovery.build('drive', 'v3', http=https2)

    #See if there's same directory
    #If not -> Create one
    targetfolder = findAndCreateFolder(service2, first_item['name'])

    #Start copy, stop if it encouters error
    print('Copy File')

    cnt = 1
    #Try twice. if it fails
    for copy_item in source_items:
        download_file(service1, copy_item['id'], copy_item['name'])

        #Before Upload you should delete, if it exists.
        delete_ifexist(service2, copy_item['name'], targetfolder)

        #Upload
        upload_file(service2, copy_item['name'], targetfolder)

        #Delete that file in copy source
        delete_file(service1, copy_item['id'] )
        printProgress(cnt, len(source_items))
        cnt = cnt + 1

    #Delete folder in copy source
    delete_file(service1, first_item['id'])

    print('Delete temporary files.')
    #Delete whole folder too.
    filelist = [f for f in os.listdir(DIR_FOR_THIS)]
    for f in filelist:
        if f == '.DS_Store':
            print('We do not need to delete .DS_Store.')
        else:
            os.remove(DIR_FOR_THIS + f)

    print('Finished.')

if __name__ == '__main__':
    main()