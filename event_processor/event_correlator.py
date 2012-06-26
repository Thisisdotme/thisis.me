import requests
import hashlib
import base64

from tim_commons import normalize_uri


def correlate_event(event_json):
  # Extract the origin url
  uri = event_json.original_content_uri()

  if uri:
    # Normalize the URL: follow redirect
    normalized_uri = _normalize_uri(uri)
    # Generate id for this
    return (_generate_id(normalized_uri), normalized_uri)

  return (None, None)


def _normalize_uri(uri):
  request = requests.head(uri, allow_redirects=True)
  return normalize_uri(request.url)


def _generate_id(url):
  encrypt = hashlib.sha256()
  encrypt.update(url)
  return base64.urlsafe_b64encode(encrypt.digest())[:-1]
