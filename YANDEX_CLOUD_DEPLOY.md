# Deploy NATURELLO CRM API to Yandex Cloud

Use this for the online backend that connects CRM to Yandex 360.

## What We Deploy

Frontend:

- GitHub Pages: `sales-ai-manager.html`

Backend:

- Yandex Cloud Serverless Containers
- Docker image from `naturello-crm-api/Dockerfile`
- Environment variables for Yandex 360

Mail:

- Yandex 360 mailbox: `hello@naturello.food`

## Step 1: Open Yandex Cloud

1. Go to Yandex Cloud Console.
2. Open or create a cloud and folder.
3. Make sure billing is enabled.

## Step 2: Create Container Registry

1. Open **Container Registry**.
2. Create a registry, for example:

```text
naturello-crm
```

3. This registry will store the Docker image for the API.

## Step 3: Build and Push Docker Image

From the project root:

```bash
cd naturello-crm-api
docker build -t cr.yandex/<registry-id>/naturello-crm-api:latest .
docker push cr.yandex/<registry-id>/naturello-crm-api:latest
```

Replace `<registry-id>` with the Container Registry ID from Yandex Cloud.

## Step 4: Create Serverless Container

1. Open **Serverless Containers**.
2. Create a container:

```text
naturello-crm-api
```

3. Create a revision from the image:

```text
cr.yandex/<registry-id>/naturello-crm-api:latest
```

4. Runtime mode: **HTTP server**.
5. Add environment variables:

```text
YANDEX360_EMAIL=hello@naturello.food
YANDEX360_FROM_NAME=NATURELLO Partnerships
YANDEX360_PASSWORD=<real app password or OAuth token>
YANDEX360_SMTP_HOST=smtp.yandex.ru
YANDEX360_SMTP_PORT=465
YANDEX360_IMAP_HOST=imap.yandex.ru
YANDEX360_IMAP_PORT=993
DAILY_SEND_LIMIT=25
```

Do not put `YANDEX360_PASSWORD` in GitHub.

## Step 5: Make Container Public

Enable public HTTPS invocation for the container.

You will get a URL similar to:

```text
https://<container-id>.containers.yandexcloud.net
```

## Step 6: Test API

Open:

```text
https://<container-url>/health
https://<container-url>/api/yandex360/status
```

Expected status:

```json
{
  "ok": true,
  "mailbox": "hello@naturello.food"
}
```

## Step 7: Connect CRM

Open the CRM page and run in the browser console:

```js
localStorage.setItem("naturello-crm-api-base", "https://<container-url>");
location.reload();
```

Then click:

```text
Check Yandex 360
```

## Notes

- Start with `DAILY_SEND_LIMIT=25`.
- Keep SPF, DKIM, and DMARC configured for `naturello.food`.
- During MVP testing, keep manual approval before every send.

