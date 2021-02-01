import sys
import logging
import httplib2
from mimetypes import guess_type
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from apiclient.errors import ResumableUploadError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage


logging.basicConfig(level="ERROR")
token_file = sys.path[0] + '/auth_token.txt'
CLIENT_ID = '669177415122-aan128gfm671kjq5mieai6d6qfkdhus4.apps.googleusercontent.com'
CLIENT_SECRET = 'Z_3OVkwt_Dp7TrvXpuq7SFW2'
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive.file'
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

def file_ops(file_path):
    mime_type = guess_type(file_path)[0]
    mime_type = mime_type if mime_type else 'text/plain'
    file_name = file_path.split('/')[-1]
    return file_name, mime_type

def create_token_file(token_file):
    flow = OAuth2WebServerFlow(
        CLIENT_ID,
        CLIENT_SECRET,
        OAUTH_SCOPE,
        redirect_uri=REDIRECT_URI
        )
    authorize_url = flow.step1_get_authorize_url()
    print('Go to the following link in your browser: ' + authorize_url)
    code = input('Enter verification code: ').strip()
    credentials = flow.step2_exchange(code)
    storage = Storage(token_file)
    storage.put(credentials)
    return storage

def createFolder(folderName,folder_id=None):
    http = authorize("./auth_token.txt", None)
    drive_service = build('drive', 'v3', http=http)
    body = {
        'name': folderName,
        'mimeType': "application/vnd.google-apps.folder"
    }
    if folder_id:
        body['parents']=[{'id':folder_id}]
    root_folder = drive_service.files().create(body = body).execute()
    return root_folder['id']

def authorize(token_file, storage):
    if storage is None:
        storage = Storage(token_file)
    credentials = storage.get()
    http = httplib2.Http()
    credentials.refresh(http)
    http = credentials.authorize(http)
    return http


def upload_file(file_path, file_name, mime_type,folder_id=None):
    drive_service = build('drive', 'v2', http=http)
    media_body = MediaFileUpload(file_path,mimetype=mime_type,resumable=True)
    body = {
        'title': file_name,
        'description': 'backup',
        'mimeType': mime_type
    }
    if folder_id:
        body['parents']=[{'id':folder_id}]
    permissions = {
        'role': 'reader',
        'type': 'anyone',
        'value': None,
        'withLink': True
    }
    file = drive_service.files().insert(body=body, media_body=media_body).execute()
    drive_service.permissions().insert(fileId=file['id'], body=permissions).execute()
    file = drive_service.files().get(fileId=file['id']).execute()
    download_url = file.get('webContentLink')
    return download_url

http=None
def getLink(file_path,folder_id):
    global http
    try:
        with open(file_path) as f: 
            pass
    except IOError as e:
        print(e)
        sys.exit(1)
    try:
        with open('./auth_token.txt') as f: pass
    except IOError:
        http = authorize(token_file, create_token_file(token_file))
    http = authorize("./auth_token.txt", None)
    file_name, mime_type = file_ops(file_path)
    try:
        return upload_file(file_path, file_name, mime_type,folder_id)
    except ResumableUploadError as e:
        print("Error occured while first upload try:", e)
        print("Trying one more time.")
        return upload_file(file_path, file_name, mime_type,folder_id)
