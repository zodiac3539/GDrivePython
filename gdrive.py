from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from apiclient import http
import oauth2client

from oauth2client import client
from oauth2client import tools

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

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
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
    credentials = get_credentials()
    https = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=https)

    results = service.files().list(
        pageSize=100,
        q="mimeType='application/zip'",
        fields="nextPageToken, files(id, name, parents)"
    ).execute()

    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        i = 0
        for item in items:
            name = item['name']
            ids = item['id']
            parents = item['parents']

            real_name = name.encode("utf-8")
            if i==0:
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
            i = i + 1

if __name__ == '__main__':
    main()

#mimeType='application/zip'
