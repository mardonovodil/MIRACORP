const express = require("express");
const cors = require("cors");
const nodemailer = require("nodemailer");
const { ImapFlow } = require("imapflow");
const { simpleParser } = require("mailparser");
require("dotenv").config();

const app = express();
const port = Number(process.env.PORT || 8787);
const dailySendLimit = Number(process.env.DAILY_SEND_LIMIT || 25);

const config = {
  email: process.env.YANDEX360_EMAIL || "hello@naturello.food",
  fromName: process.env.YANDEX360_FROM_NAME || "NATURELLO Partnerships",
  password: process.env.YANDEX360_PASSWORD,
  smtpHost: process.env.YANDEX360_SMTP_HOST || "smtp.yandex.ru",
  smtpPort: Number(process.env.YANDEX360_SMTP_PORT || 465),
  imapHost: process.env.YANDEX360_IMAP_HOST || "imap.yandex.ru",
  imapPort: Number(process.env.YANDEX360_IMAP_PORT || 993),
};

app.use(cors({ origin: process.env.CRM_ALLOWED_ORIGIN || true }));
app.use(express.json({ limit: "1mb" }));

function requireMailCredentials() {
  if (!config.password || config.password.includes("replace_with")) {
    const error = new Error("YANDEX360_PASSWORD is not configured");
    error.status = 503;
    throw error;
  }
}

function createTransporter() {
  requireMailCredentials();
  return nodemailer.createTransport({
    host: config.smtpHost,
    port: config.smtpPort,
    secure: config.smtpPort === 465,
    auth: {
      user: config.email,
      pass: config.password,
    },
  });
}

function createImapClient() {
  requireMailCredentials();
  return new ImapFlow({
    host: config.imapHost,
    port: config.imapPort,
    secure: true,
    auth: {
      user: config.email,
      pass: config.password,
    },
    logger: false,
  });
}

function cleanString(value) {
  return typeof value === "string" ? value.trim() : "";
}

function validateApprovedEmail(payload) {
  const to = cleanString(payload.to);
  const subject = cleanString(payload.subject);
  const text = cleanString(payload.text);
  const approved = payload.approved === true;

  if (!approved) return "Email must be approved before sending";
  if (!to || !to.includes("@")) return "Recipient email is invalid";
  if (!subject) return "Subject is required";
  if (!text) return "Email body is required";
  return "";
}

app.get("/health", (req, res) => {
  res.json({
    ok: true,
    service: "naturello-crm-api",
    market: "CIS",
    mailbox: config.email,
    dailySendLimit,
    yandex360Configured: Boolean(config.password && !config.password.includes("replace_with")),
  });
});

app.get("/api/yandex360/status", async (req, res, next) => {
  try {
    const transporter = createTransporter();
    await transporter.verify();
    res.json({
      ok: true,
      mailbox: config.email,
      smtp: `${config.smtpHost}:${config.smtpPort}`,
      imap: `${config.imapHost}:${config.imapPort}`,
      message: "Yandex 360 SMTP connection verified",
    });
  } catch (error) {
    next(error);
  }
});

app.post("/api/yandex360/send-approved", async (req, res, next) => {
  try {
    const validationError = validateApprovedEmail(req.body || {});
    if (validationError) {
      return res.status(400).json({ ok: false, error: validationError });
    }

    const transporter = createTransporter();
    const info = await transporter.sendMail({
      from: `"${config.fromName}" <${config.email}>`,
      replyTo: config.email,
      to: cleanString(req.body.to),
      subject: cleanString(req.body.subject),
      text: cleanString(req.body.text),
      html: req.body.html || undefined,
      headers: {
        "X-NATURELLO-CRM-Lead-ID": cleanString(req.body.leadId),
      },
    });

    res.json({
      ok: true,
      provider: "yandex360",
      mailbox: config.email,
      messageId: info.messageId,
      accepted: info.accepted,
      rejected: info.rejected,
    });
  } catch (error) {
    next(error);
  }
});

app.get("/api/yandex360/replies", async (req, res, next) => {
  const limit = Math.min(Number(req.query.limit || 10), 25);
  const client = createImapClient();

  try {
    await client.connect();
    const lock = await client.getMailboxLock("INBOX");
    const replies = [];

    try {
      const exists = client.mailbox.exists || 0;
      const fromSeq = Math.max(1, exists - limit + 1);
      for await (const message of client.fetch(`${fromSeq}:*`, { envelope: true, source: true, uid: true })) {
        const parsed = await simpleParser(message.source);
        replies.push({
          uid: message.uid,
          from: parsed.from?.text || "",
          subject: parsed.subject || message.envelope?.subject || "",
          date: parsed.date || message.envelope?.date || null,
          text: (parsed.text || "").slice(0, 1200),
        });
      }
    } finally {
      lock.release();
    }

    await client.logout();
    res.json({ ok: true, mailbox: config.email, replies: replies.reverse() });
  } catch (error) {
    try {
      await client.logout();
    } catch (_) {
      // Ignore logout errors after failed IMAP connection.
    }
    next(error);
  }
});

app.use((error, req, res, next) => {
  const status = error.status || 500;
  res.status(status).json({
    ok: false,
    error: error.message,
  });
});

app.listen(port, () => {
  console.log(`NATURELLO CRM API listening on http://localhost:${port}`);
});

