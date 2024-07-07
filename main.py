from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
import pprint
from dotenv import load_dotenv
load_dotenv()
import os

# Configuration
config = Config('.env')
oauth = OAuth(config)
oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url=os.getenv('GOOGLE_SERVER_METADATA_URL'),
    client_kwargs={'scope': os.getenv('GOOGLE_CLIENT_SCOPE')}
)

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv('SECRET_KEY'))

@app.get('/')
async def homepage(request: Request):
    user = request.session.get('user')
    if user:
        return f'Hello, {user["name"]}!'
    return 'Hello, you are not logged in!'

@app.get('/login')
async def login(request: Request):
    user = request.session.get('user')
    if user:
        return RedirectResponse(url='/')
    else:
        redirect_uri = request.url_for('auth_callback')
        return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get('/auth/callback', name='auth_callback')
async def auth_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    request.session['user'] = dict(token['userinfo'])
    return RedirectResponse(url='/')

@app.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')