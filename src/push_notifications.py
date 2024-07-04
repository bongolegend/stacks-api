from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushServerError,
    PushTicketError,
)
import os
import requests
from requests.exceptions import ConnectionError, HTTPError
import structlog


log = structlog.get_logger()

# Optionally providing an access token within a session if you have enabled push security
token = os.getenv('EXPO_TOKEN')
if token:
    auth = f"Bearer {token}"
else:
    auth = None

session = requests.Session()
session.headers.update(
    {
        "Authorization": auth,
        "accept": "application/json",
        "accept-encoding": "gzip, deflate",
        "content-type": "application/json",
    }
)

# Basic arguments. You should extend this function with the push features you
# want to use, or simply pass in a `PushMessage` object.
def send_push_message(device_token, message, extra=None):
    try:
        response = PushClient(session=session).publish(
            PushMessage(to=device_token,
                        body=message,
                        data=extra))
    except PushServerError as exc:
        # Encountered some likely formatting/validation error.
        log.error("PushServerError", exc=exc, token=device_token, message=message, extra=extra)
        raise exc
    except (ConnectionError, HTTPError) as exc:
        # Encountered some Connection or HTTP error - retry a few times in
        # case it is transient.
        log.error("ConnectionError/HTTPError", exc=exc, token=device_token, message=message, extra=extra)
        raise exc

    try:
        # We got a response back, but we don't know whether it's an error yet.
        # This call raises errors so we can handle them with normal exception
        # flows.
        response.validate_response()
    except DeviceNotRegisteredError:
        # Mark the push token as inactive
        # from notifications.models import PushToken
        # PushToken.objects.filter(token=device_token).update(active=False)
        log.error("DeviceNotRegisteredError", token=device_token, message=message, extra=extra)
    except PushTicketError as exc:
        # Encountered some other per-notification error.
        log.error("PushTicketError", exc=exc, token=device_token, message=message, extra=extra, push_response=exc.push_response._asdict())
        raise exc
    
TOKEN = "ExponentPushToken[77KOQsOsQxm9UAp2Qbjsps]"
send_push_message(TOKEN, "Hello, world!")