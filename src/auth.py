import structlog
import time 
import datetime
import os

import firebase_admin
from firebase_admin import auth, credentials
import jwt
from jose import JWTError, jwt
from firebase_admin._auth_utils import InvalidIdTokenError
from uuid import UUID


# Initialize the Firebase Admin SDK
cred = credentials.Certificate('/app/secrets/firebase_stacks_confidential_credentials.json')
firebase_admin.initialize_app(cred)

# Initialize structlog
structlog.configure()
log = structlog.get_logger()

# TODO change secret key and move out of version control
# Secret key for JWT encoding
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 365

ENV = os.getenv("ENV")

class InvalidJWTError(Exception):
    """Raised if accessToken is not valid"""

    def __init__(self, message="Unauthorized Request: invalid token"):
        self.message = message
        super().__init__(self.message)


def verify_firebase_token(authorization: str):
    # TODO: adding delay is a hack fix for clock skew issue with firebase - find better solution?
    attempt = 0 
    retries = 3
    delay = 1.0
    while attempt < retries:
        try:
            id_token = authorization.split(" ")[1]
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token['uid']
        except InvalidIdTokenError as e:
            if "Token used too early" in str(e):
                log.error(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay} seconds...")
                time.sleep(delay)
                attempt += 1
            else:
                log.error("Error verifying token", error=str(e))
                raise
        except Exception as e:
            log.error("Error verifying token", error=str(e))
            raise


def create_access_token(userid: UUID):
    to_encode = {"userid": str(userid)}
    access_token_expiration = (datetime.datetime.now(datetime.timezone.utc) 
                               + datetime.timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": access_token_expiration})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(authorization: str):
    if ENV == "test":
        log.debug("Bypass token verification")
        return 'fakeid'
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        userid: str = payload.get("userid")
        if not userid:
            log.error("Token valid, user not found")
            # TODO: is this the right error to raise here?
            raise JWTError()
        return userid
    except JWTError:
        raise ()
