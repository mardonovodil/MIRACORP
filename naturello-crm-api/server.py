import email
import imaplib
import json
import os
import smtplib
from email.message import EmailMessage
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse


PORT = int(os.getenv("PORT", "8787"))
DAILY_SEND_LIMIT = int(os.getenv("DAILY_SEND_LIMIT", "25"))

CONFIG = {
    "email": os.getenv("YANDEX360_EMAIL", "hello@naturello.food"),
    "from_name": os.getenv("YANDEX360_FROM_NAME", "NATURELLO Partnerships"),
    "password": os.getenv("YANDEX360_PASSWORD", ""),
    "smtp_host": os.getenv("YANDEX360_SMTP_HOST", "smtp.yandex.ru"),
    "smtp_port": int(os.getenv("YANDEX360_SMTP_PORT", "465")),
    "imap_host": os.getenv("YANDEX360_IMAP_HOST", "imap.yandex.ru"),
    "imap_port": int(os.getenv("YANDEX360_IMAP_PORT", "993")),
}


def load_dotenv(path=".env"):
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


load_dotenv()
CONFIG.update(
    {
        "email": os.getenv("YANDEX360_EMAIL", CONFIG["email"]),
        "from_name": os.getenv("YANDEX360_FROM_NAME", CONFIG["from_name"]),
        "password": os.getenv("YANDEX360_PASSWORD", CONFIG["password"]),
        "smtp_host": os.getenv("YANDEX360_SMTP_HOST", CONFIG["smtp_host"]),
        "smtp_port": int(os.getenv("YANDEX360_SMTP_PORT", str(CONFIG["smtp_port"]))),
        "imap_host": os.getenv("YANDEX360_IMAP_HOST", CONFIG["imap_host"]),
        "imap_port": int(os.getenv("YANDEX360_IMAP_PORT", str(CONFIG["imap_port"]))),
    }
)


def configured():
    password = CONFIG["password"]
    return bool(password and "replace_with" not in password)


def json_response(handler, status, payload):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def read_json(handler):
    length = int(handler.headers.get("Content-Length", "0"))
    if length == 0:
        return {}
    raw = handler.rfile.read(length).decode("utf-8")
    return json.loads(raw)


def require_credentials():
    if not configured():
        raise RuntimeError("YANDEX360_PASSWORD is not configured")


def smtp_login():
    require_credentials()
    smtp = smtplib.SMTP_SSL(CONFIG["smtp_host"], CONFIG["smtp_port"], timeout=20)
    smtp.login(CONFIG["email"], CONFIG["password"])
    return smtp


def validate_email_payload(payload):
    if payload.get("approved") is not True:
        return "Email must be approved before sending"
    if "@" not in str(payload.get("to", "")):
        return "Recipient email is invalid"
    if not str(payload.get("subject", "")).strip():
        return "Subject is required"
    if not str(payload.get("text", "")).strip():
        return "Email body is required"
    return ""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_OPTIONS(self):
        json_response(self, 200, {"ok": True})

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/health":
            return json_response(
                self,
                200,
                {
                    "ok": True,
                    "service": "naturello-crm-api-python",
                    "market": "CIS",
                    "mailbox": CONFIG["email"],
                    "dailySendLimit": DAILY_SEND_LIMIT,
                    "yandex360Configured": configured(),
                },
            )

        if parsed.path == "/api/yandex360/status":
            try:
                smtp = smtp_login()
                smtp.quit()
                return json_response(
                    self,
                    200,
                    {
                        "ok": True,
                        "mailbox": CONFIG["email"],
                        "smtp": f"{CONFIG['smtp_host']}:{CONFIG['smtp_port']}",
                        "imap": f"{CONFIG['imap_host']}:{CONFIG['imap_port']}",
                        "message": "Yandex 360 SMTP connection verified",
                    },
                )
            except Exception as error:
                return json_response(self, 503, {"ok": False, "error": str(error)})

        if parsed.path == "/api/yandex360/replies":
            try:
                require_credentials()
                query = parse_qs(parsed.query)
                limit = min(int(query.get("limit", ["10"])[0]), 25)
                imap = imaplib.IMAP4_SSL(CONFIG["imap_host"], CONFIG["imap_port"])
                imap.login(CONFIG["email"], CONFIG["password"])
                imap.select("INBOX")
                status, data = imap.search(None, "ALL")
                ids = data[0].split()[-limit:] if status == "OK" and data and data[0] else []
                replies = []
                for message_id in reversed(ids):
                    status, message_data = imap.fetch(message_id, "(RFC822)")
                    if status != "OK":
                        continue
                    message = email.message_from_bytes(message_data[0][1])
                    text = ""
                    if message.is_multipart():
                        for part in message.walk():
                            if part.get_content_type() == "text/plain":
                                payload = part.get_payload(decode=True)
                                if payload:
                                    text = payload.decode(part.get_content_charset() or "utf-8", errors="replace")
                                    break
                    else:
                        payload = message.get_payload(decode=True)
                        if payload:
                            text = payload.decode(message.get_content_charset() or "utf-8", errors="replace")
                    replies.append(
                        {
                            "from": message.get("From", ""),
                            "subject": message.get("Subject", ""),
                            "date": message.get("Date", ""),
                            "text": text[:1200],
                        }
                    )
                imap.logout()
                return json_response(self, 200, {"ok": True, "mailbox": CONFIG["email"], "replies": replies})
            except Exception as error:
                return json_response(self, 503, {"ok": False, "error": str(error)})

        return json_response(self, 404, {"ok": False, "error": "Not found"})

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/yandex360/send-approved":
            try:
                payload = read_json(self)
                validation_error = validate_email_payload(payload)
                if validation_error:
                    return json_response(self, 400, {"ok": False, "error": validation_error})

                message = EmailMessage()
                message["From"] = f"{CONFIG['from_name']} <{CONFIG['email']}>"
                message["Reply-To"] = CONFIG["email"]
                message["To"] = payload["to"].strip()
                message["Subject"] = payload["subject"].strip()
                if payload.get("leadId"):
                    message["X-NATURELLO-CRM-Lead-ID"] = str(payload["leadId"])
                message.set_content(payload["text"].strip())

                smtp = smtp_login()
                smtp.send_message(message)
                smtp.quit()

                return json_response(
                    self,
                    200,
                    {
                        "ok": True,
                        "provider": "yandex360",
                        "mailbox": CONFIG["email"],
                        "accepted": [payload["to"].strip()],
                    },
                )
            except Exception as error:
                return json_response(self, 503, {"ok": False, "error": str(error)})

        return json_response(self, 404, {"ok": False, "error": "Not found"})


if __name__ == "__main__":
    print(f"NATURELLO CRM API listening on http://localhost:{PORT}")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
