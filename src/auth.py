import firebase_admin
from firebase_admin import auth, credentials
import jwt
from jose import JWTError, jwt
import datetime
import structlog

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
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 14

class InvalidTokenError(Exception):
    """Raised if userToken does not contain valid Secret String"""

    def __init__(self, message="Unauthorized Request: invalid token"):
        self.message = message
        super().__init__(self.message)


def verify_firebase_token(authorization: str):
    try:
        id_token = authorization.split(" ")[1]
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except ValueError as e:
        log.error("Invalid token", error=str(e))
        raise
    except firebase_admin.exceptions.ExpiredIdTokenError as e:
        log.error("Expired token", error=str(e))
        raise
    except firebase_admin.exceptions.RevokedIdTokenError as e:
        log.error("Revoked token", error=str(e))
        raise
    except firebase_admin.exceptions.InvalidIdTokenError as e:
        log.error("Invalid signature", error=str(e))
        raise
    except Exception as e:
        log.error("Error verifying token", error=str(e))
        raise


def create_access_token(data: dict):
    to_encode = data.copy()
    access_token_expiration = (datetime.datetime.now(datetime.timezone.utc) 
                               + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": access_token_expiration})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict):
    expire = datetime.utcnow() + datetime.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        userid: str = payload.get("sub")
        if userid is None:
            log.error("Could not verify access token")
            raise InvalidTokenError()
    except JWTError:
        raise InvalidTokenError()
    return userid 