import re
import requests

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend


_EMAIL_RE = re.compile(r"^\s*(?:(?P<name>.*)\s+)?<(?P<email>[^>]+)>\s*$")


def _parse_from(s: str):
    """
    Accepts:
      - "Name <email@x.com>"
      - "email@x.com"
    Returns (name, email)
    """
    if not s:
        return ("", "")
    m = _EMAIL_RE.match(s)
    if m:
        name = (m.group("name") or "").strip().strip('"')
        email = (m.group("email") or "").strip()
        return (name, email)
    return ("", s.strip())


class BrevoEmailBackend(BaseEmailBackend):
    """
    Sends email via Brevo Transactional Email API (HTTPS).
    Endpoint: POST https://api.brevo.com/v3/smtp/email
    """

    def send_messages(self, email_messages):
        api_key = getattr(settings, "BREVO_API_KEY", None)
        if not api_key:
            raise RuntimeError("BREVO_API_KEY is not set")

        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json",
        }

        sent = 0
        timeout = getattr(settings, "BREVO_TIMEOUT_SECONDS", 15)

        for msg in email_messages:
            if not msg.to:
                continue

            from_name, from_email = _parse_from(msg.from_email or settings.DEFAULT_FROM_EMAIL)
            payload = {
                "sender": {"name": from_name or "Ichigo Farms", "email": from_email},
                "to": [{"email": r} for r in msg.to],
                "subject": msg.subject or "",
                "textContent": msg.body or "",
            }

            # If you send HTML emails via EmailMultiAlternatives, include it
            if hasattr(msg, "alternatives"):
                for content, mimetype in msg.alternatives:
                    if mimetype == "text/html":
                        payload["htmlContent"] = content
                        break

            r = requests.post(url, json=payload, headers=headers, timeout=timeout)
            r.raise_for_status()
            sent += 1

        return sent
