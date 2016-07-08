from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from apiclient import http
from apiclient import errors
import oauth2client

from oauth2client import client
from oauth2client import tools
import io

import sys

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive  https://www.googleapis.com/auth/drive.file  https://www.googleapis.com/auth/drive.metadata'
CLIENT_SECRET_FILE = 'client_secret2.json'
APPLICATION_NAME = 'Drive API Python Quickstart'
DIR_FOR_THIS = '/Users/seokbongchoi/Documents/folder2/'

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

def get_credentials():

    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart2.json')

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

def get_file_list(service):
    query = "(mimeType='{0}' or mimeType='{1}') and (name contains '{2}' or name contains '{3}')".format(
        'video/mp4',
        'video/x-msvideo',
        'carib',
        'heyzo'
    )
    print('Query: ' + query)

    results = service.files().list(
        pageSize=2,
        q=query,
        fields="nextPageToken, files(id, name, parents)"
    ).execute()

    items = results.get('files', [])

    if not items:
        print('nothing')
        return []
    else:
        return items

def delete_file(service, file_id):
    service.files().delete(fileId=file_id).execute()

def download_file(service, file_id, file_name):
    request = service.files().get_media(fileId=file_id)

    real_name = DIR_FOR_THIS + file_name
    fh = open(real_name, 'wb')
    #fh = io.BytesIO()
    downloader = http.MediaIoBaseDownload(fh, request)

    done = False
    while done is False:
        status, done = downloader.next_chunk()
        printProgress(iteration=int(status.progress() * 100), total=100)

    fh.close()

def main():
    credentials = get_credentials()
    https = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=https)

    items = get_file_list(service)
    for item in items:
        file_name = item['name'].encode('utf-8')
        download_file(service,item['id'], file_name)
        delete_file(service, item['id'])

if __name__ == '__main__':
    main()