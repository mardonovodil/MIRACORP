# NATURELLO CRM on GitHub

Yes, the CRM core should live on GitHub.

Put these files in the repository:

- `sales-ai-manager.html` — browser CRM screen.
- `sales-ai-manager.md` — product and technical brief.
- `naturello-crm-api/` — online backend connector for Yandex 360.
- `render.yaml` — example online deployment manifest.

Do not put secrets in GitHub:

- `.env`
- `YANDEX360_PASSWORD`
- OAuth tokens
- mailbox passwords

## Recommended Online Setup

1. Push this folder to GitHub.
2. Deploy `naturello-crm-api` from GitHub to Render, Railway, Yandex Cloud, Fly.io, or a VPS.
3. Add server environment variable:

```text
YANDEX360_PASSWORD=<real app password or OAuth token>
```

4. Open deployed API:

```text
https://your-api-domain/health
https://your-api-domain/api/yandex360/status
```

5. Connect the browser CRM to the online API:

```js
localStorage.setItem("naturello-crm-api-base", "https://your-api-domain");
location.reload();
```

6. Click `Check Yandex 360` in the CRM.

## Current Local Note

Local Windows testing reached the API, but SMTP/IMAP TLS checks were reset by the local runtime/network. Deploying the API on Linux hosting is the cleanest next test.

