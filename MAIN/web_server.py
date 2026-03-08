from fastapi import FastAPI, Request
from google_auth_oauthlib.flow import Flow
from db.database import save_user
from db.database import init_db
from fastapi.responses import RedirectResponse

app = FastAPI()
init_db()

CLIENT_SECRETS_FILE = "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/calendar"]

user_states = {}

@app.get("/login/{discord_id}")
def login(discord_id: str):

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri="http://localhost:8000/callback"
    )

    auth_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent"
    )

    user_states[state] = discord_id

    return RedirectResponse(auth_url)


@app.get("/callback")
def callback(request: Request):

    state = request.query_params.get("state")

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri="http://localhost:8000/callback"
    )

    flow.fetch_token(authorization_response=str(request.url))

    creds = flow.credentials

    discord_id = user_states.get(state)

    save_user(discord_id, {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes
    })

    return {"message": "Google 綁定成功，可以回 Discord 使用"}