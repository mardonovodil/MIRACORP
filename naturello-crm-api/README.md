# NATURELLO CRM API

Backend connector for NATURELLO Sales CRM and Yandex 360.

The frontend must not store or use Yandex 360 passwords/tokens. This API keeps credentials in `.env` and exposes only safe CRM endpoints.

## Setup: Python version, no external packages

1. Copy `.env.example` to `.env`.
2. Put the real mailbox password or OAuth token into `YANDEX360_PASSWORD`.
3. In Yandex Mail settings, allow IMAP/SMTP access for `hello@naturello.food`.
4. Start the connector:

```bash
python server.py
```

If Python is not in PATH, use the bundled Codex Python runtime.

## Setup: Node version

1. Copy `.env.example` to `.env`.
2. Put the real mailbox password or OAuth token into `YANDEX360_PASSWORD`.
3. In Yandex Mail settings, allow IMAP/SMTP access for `hello@naturello.food`.
4. Install dependencies:

```bash
npm install
```

5. Start the connector:

```bash
npm start
```

## Endpoints

- `GET /health` — local API health and configuration status.
- `GET /api/yandex360/status` — verifies SMTP access.
- `POST /api/yandex360/send-approved` — sends only approved CRM email.
- `GET /api/yandex360/replies?limit=10` — reads recent inbox replies via IMAP.

## Online Deployment

Deploy `naturello-crm-api` as a small web service with HTTPS. Good targets are Yandex Cloud, Render, Railway, Fly.io, VPS, or any Python-compatible host.

Required environment variables on the server:

```text
PORT=8787
YANDEX360_EMAIL=hello@naturello.food
YANDEX360_FROM_NAME=NATURELLO Partnerships
YANDEX360_PASSWORD=<real app password or OAuth token>
YANDEX360_SMTP_HOST=smtp.yandex.ru
YANDEX360_SMTP_PORT=465
YANDEX360_IMAP_HOST=imap.yandex.ru
YANDEX360_IMAP_PORT=993
DAILY_SEND_LIMIT=25
```

After deployment, set the online API URL in the browser console on `sales-ai-manager.html`:

```js
localStorage.setItem("naturello-crm-api-base", "https://your-api-domain.example");
location.reload();
```

Then click `Check Yandex 360` in the CRM.

## Send Payload

```json
{
  "approved": true,
  "leadId": "lead-123",
  "to": "buyer@example.com",
  "subject": "NATURELLO partnership",
  "text": "Hello..."
}
```

## Notes

- Start with 20-25 emails/day while warming up `naturello.food`.
- Keep SPF, DKIM and DMARC configured for the domain.
- Keep manual approval before sending during MVP testing.
