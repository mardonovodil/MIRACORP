# NATURELLO Sales CRM

## Цель

Создать внутреннюю AI-CRM для NATURELLO, которая каждый день находит новые FMCG-компании на рынке СНГ, оценивает их потенциал, готовит персонализированные письма, ведет историю коммуникаций, напоминает о follow-up и показывает объем потенциальной выручки в работе.

## Что должен делать MVP

1. Ежедневно находить 30-50 новых FMCG-компаний для NATURELLO на рынке СНГ.
2. Собирать базовые данные: сайт, страна, индустрия, размер компании, контактные лица, email, LinkedIn, признаки потребности.
3. Считать lead score от 0 до 100.
4. Оценивать потенциальную выручку по формуле `estimated_deal_value * probability`.
5. Генерировать персонализированное письмо на русском или английском языке.
6. Сохранять всю историю касаний: email, звонки, заметки, статусы, ответы.
7. Автоматически ставить follow-up через 3, 7 и 14 дней.
8. Показывать CRM-воронку: New, Qualified, Contacted, Replied, Meeting, Proposal, Won, Lost.

## Текущий фокус

На этапе теста отбрасываем направления бизнеса и расширение на другие бренды. Работаем только с NATURELLO.

Активный mailbox:

```text
hello@naturello.food
```

CRM готовит и хранит письма, Яндекс 360 отправляет и принимает ответы. После тестирования сервиса и исправления неполадок можно будет расширить CRM на новые бренды.

Backend-коннектор для Яндекс 360 добавлен в `naturello-crm-api`. Его можно запустить локально или развернуть онлайн как HTTPS API.

## ICP для NATURELLO

- Дистрибьюторы продуктов питания и напитков.
- Ритейл-сети, супермаркеты, specialty stores.
- HoReCa, healthy food chains, organic shops.
- Импортеры и дистрибьюторы в Казахстане, Узбекистане, Кыргызстане, Азербайджане, Армении, Беларуси, Таджикистане и Молдове.

## Lead scoring

Рекомендуемая формула:

```text
lead_score =
  market_fit * 0.30 +
  company_size_fit * 0.15 +
  buying_signal * 0.20 +
  contact_quality * 0.15 +
  revenue_potential * 0.15 +
  strategic_value * 0.05
```

Градации:

- `80-100`: горячий лид, писать сегодня.
- `60-79`: хороший лид, добавить в outreach.
- `40-59`: проверить вручную.
- `0-39`: низкий приоритет или в архив.

## Данные CRM

### Company

- `id`
- `name`
- `website`
- `country`
- `city`
- `industry`
- `segment`
- `employee_count`
- `annual_revenue_estimate`
- `lead_score`
- `potential_revenue`
- `stage`
- `source`
- `created_at`
- `last_contact_at`
- `next_follow_up_at`

### Contact

- `id`
- `company_id`
- `name`
- `role`
- `email`
- `linkedin_url`
- `phone`
- `language`
- `confidence`

### Activity

- `id`
- `company_id`
- `contact_id`
- `type`: email, call, linkedin, note, meeting
- `direction`: outbound, inbound, internal
- `subject`
- `body`
- `status`
- `created_at`

### Opportunity

- `id`
- `company_id`
- `product_line`: FMCG, AI, Energy
- `estimated_value`
- `probability`
- `weighted_value`
- `expected_close_date`
- `owner`

## Автоматический ежедневный workflow

1. `07:00` - найти 30-50 новых компаний.
2. `07:20` - обогатить данные по компаниям и контактам.
3. `07:45` - оценить lead score и потенциальную выручку.
4. `08:00` - подготовить письма и записать их как drafts.
5. `09:00` - показать список "Ready to approve".
6. После одобрения - отправить письма.
7. Каждый день - проверять ответы и обновлять стадии.
8. Каждый день - ставить задачи follow-up по просроченным лидам.

## AI-письмо

Шаблон prompt:

```text
Ты Sales AI Manager NATURELLO.
Напиши короткое персонализированное B2B-письмо.

Компания: {{company_name}}
Сайт: {{website}}
Индустрия: {{industry}}
Сегмент NATURELLO: FMCG
Контакт: {{contact_name}}, {{role}}
Причина релевантности: {{fit_reason}}
Предложение: {{offer}}
Язык: {{language}}

Стиль:
- уверенно
- коротко
- без агрессивных продаж
- 90-130 слов
- один понятный CTA
```

## Технологическая архитектура

Для быстрого MVP:

- Frontend: статический CRM dashboard или Next.js.
- Backend: Node.js API в `naturello-crm-api`.
- Database: PostgreSQL.
- Jobs: cron / GitHub Actions / Railway scheduled jobs.
- AI: OpenAI API для scoring, research summary и писем.
- Email: Яндекс 360 SMTP/IMAP через backend-коннектор с обязательным approval перед отправкой.
- CRM Sync: сначала внутренняя таблица, позже HubSpot / Pipedrive / Zoho.

## Безопасность и контроль

- Не отправлять письма без ручного одобрения на MVP-этапе.
- Хранить источник каждого лида.
- Указывать confidence для email и contact data.
- Автоматически исключать компании из blacklist и уже обработанные домены.
- Соблюдать правила cold outreach: opt-out, деловой контекст, без спама.

## MVP-план на 10 дней

1. День 1: утвердить ICP и стадии CRM.
2. День 2: собрать базу данных и dashboard.
3. День 3: добавить импорт/поиск компаний.
4. День 4: добавить scoring.
5. День 5: добавить генерацию писем.
6. День 6: добавить историю коммуникаций.
7. День 7: добавить follow-up задачи.
8. День 8: добавить Яндекс 360 drafts/sending через approved queue.
9. День 9: добавить отчет по pipeline revenue.
10. День 10: тест на 100 компаниях и настройка ежедневного цикла.

## Текущий статус реализации

Первый локальный MVP реализован в `sales-ai-manager.html`.

Что уже работает:

- демо-CRM хранит лиды в `localStorage`;
- активный sender для NATURELLO: `hello@naturello.food`;
- кнопка `Run daily search` генерирует 42 новых FMCG-компании на рынке СНГ;
- лиды автоматически получают сегмент, score, potential revenue, stage и follow-up date;
- фильтры All / FMCG обновляют список лидов;
- карточка компании показывает контакт, email, потенциал, AI draft и историю;
- можно менять stage, дату follow-up, одобрять draft и отмечать ответ;
- pipeline, weighted revenue, hot leads, drafts и follow-ups пересчитываются автоматически.

Следующий технический этап: развернуть `naturello-crm-api` онлайн, добавить переменную `YANDEX360_PASSWORD`, проверить кнопку `Check Yandex 360`, затем подключить реальные источники поиска компаний, email enrichment и PostgreSQL.
