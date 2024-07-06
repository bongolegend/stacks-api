import firebase_admin
from firebase_admin import auth, credentials
import jwt
import datetime
import structlog

# Initialize the Firebase Admin SDK
cred = credentials.Certificate('/app/secrets/firebase_stacks_confidential_credentials.json')
firebase_admin.initialize_app(cred)

# Initialize structlog
structlog.configure()
log = structlog.get_logger()

def verify_token(authorization: str):
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
    # TODO change secret key and move out of version control
    # Secret key for JWT encoding
    SECRET_KEY = "your_secret_key"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    to_encode = data.copy()
    access_token_expiration = (datetime.datetime.now(datetime.timezone.utc) 
                               + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": access_token_expiration})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt