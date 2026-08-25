# VALIDATED GHL API ENDPOINTS (August 2026)
## Verified Against Live Documentation

**Base URL:** `https://services.leadconnectorhq.com`  
**Auth:** Private Integration Token (PIT) or OAuth 2.0 Bearer Token  
**Required Header:** `Version: 2021-07-28`  
**Rate Limits:** 100 requests per 10 seconds per resource; 200,000 per day per resource

---

## DEPRECATED ENDPOINTS (DO NOT USE)

| Endpoint | Status | Replacement | Source |
|----------|--------|-------------|--------|
| `GET /contacts/` | **DEPRECATED** | `GET /contacts/lookup` or search | marketplace.gohighlevel.com/docs |
| `GET /oauth/installedLocations` | **REMOVED** | `GET /oauth/installed-locations` | Changelog 2026-08-03 |
| `POST /oauth/locationToken` | **REMOVED** | `POST /oauth/location-token` | Changelog 2026-08-03 |
| API V1 (all endpoints) | **END-OF-SUPPORT** | API V2 | help.gohighlevel.com |
| Stoplight documentation | **BEING DEPRECATED** | marketplace.gohighlevel.com/docs | help.gohighlevel.com |
| Agency/Sub-account API Keys | **NEW GENERATION REMOVED** | Private Integration Tokens | help.gohighlevel.com |

---

## ACTIVE ENDPOINTS (CONFIRMED)

### Contacts

```http
# CREATE CONTACT (Active)
POST https://services.leadconnectorhq.com/contacts/
Authorization: Bearer {PIT_OR_OAUTH_TOKEN}
Version: 2021-07-28
Content-Type: application/json

{
  "locationId": "{LOCATION_ID}",
  "firstName": "John",
  "lastName": "Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "customFields": [
    { "key": "first_touch_source", "value": "meta" },
    { "key": "first_touch_campaign", "value": "summer_enrollment_2026" }
  ],
  "tags": ["new-lead", "meta-ads"],
  "source": "Meta Ads"
}

# Response: 201 Created
# Returns: GetContactByIdSchemaV3 (as of 2026-08-03 changelog)
```

```http
# UPSERT CONTACT (Active - preferred for updates)
POST https://services.leadconnectorhq.com/contacts/upsert
Authorization: Bearer {PIT_OR_OAUTH_TOKEN}
Version: 2021-07-28
Content-Type: application/json

{
  "locationId": "{LOCATION_ID}",
  "email": "john@example.com",
  "firstName": "John",
  "customFields": [
    { "key": "latest_touch_source", "value": "google" }
  ]
}

# Response: 200 OK
# Returns: GetContactByIdSchemaV3
```

```http
# GET SINGLE CONTACT (Active)
GET https://services.leadconnectorhq.com/contacts/{contactId}
Authorization: Bearer {PIT_OR_OAUTH_TOKEN}
Version: 2021-07-28

# Response: 200 OK
# Returns: GetContactByIdSchemaV3
# Note: Only returns FILLED custom fields, not all custom fields
```

```http
# LOOKUP CONTACT (Active - REPLACEMENT for deprecated GET /contacts/)
GET https://services.leadconnectorhq.com/contacts/lookup
  ?locationId={LOCATION_ID}
  &email={EMAIL}
  &phone={PHONE}
  &limit=100
  &pageToken={PAGE_TOKEN}
Authorization: Bearer {PIT_OR_OAUTH_TOKEN}
Version: 2021-07-28

# Added: 2026-08-03 (Changelog)
# Response: 200 OK
```

```http
# UPDATE CONTACT (Active)
PUT https://services.leadconnectorhq.com/contacts/{contactId}
Authorization: Bearer {PIT_OR_OAUTH_TOKEN}
Version: 2021-07-28
Content-Type: application/json

{
  "customFields": [
    { "key": "latest_touch_source", "value": "google" }
  ],
  "dndSettings": { /* DndSettingsSchemaV3 as of 2026-08-03 */ }
}

# Response: 200 OK
# Returns: GetContactByIdSchemaV3
# Note: "succeded" property REMOVED from response as of 2026-08-03
```

```http
# DELETE CONTACT CAMPAIGNS (Active - NEW as of 2026-08-03)
DELETE https://services.leadconnectorhq.com/contacts/{contactId}/campaigns/remove-all
Authorization: Bearer {PIT_OR_OAUTH_TOKEN}
Version: 2021-07-28
```

### Opportunities (Pipeline)

```http
# UPDATE OPPORTUNITY (Active)
PUT https://services.leadconnectorhq.com/opportunities/{opportunityId}
Authorization: Bearer {PIT_OR_OAUTH_TOKEN}
Version: 2021-07-28
Content-Type: application/json

{
  "pipelineId": "{PIPELINE_ID}",
  "pipelineStageId": "{STAGE_ID}",
  "status": "won",
  "name": "John Doe - Nursing Program",
  "monetaryValue": 15000,
  "assignedTo": "{USER_ID}",
  "customFields": [
    { "key": "enrolled_program", "value": "Practical Nursing" },
    { "key": "program_cost", "value": "15000" }
  ]
}

# Status options: open, won, lost, abandoned, all
# Response: 200 OK
```

```http
# GET OPPORTUNITY (Active)
GET https://services.leadconnectorhq.com/opportunities/{opportunityId}
Authorization: Bearer {PIT_OR_OAUTH_TOKEN}
Version: 2021-07-28
```

### Custom Fields

```http
# GET CUSTOM FIELDS (Active)
GET https://services.leadconnectorhq.com/locations/{locationId}/customFields
  ?model=contact
  &limit=100
Authorization: Bearer {PIT_OR_OAUTH_TOKEN}
Version: 2021-07-28

# model options: contact, opportunity, all
# Response: 200 OK
```

```http
# CREATE CUSTOM FIELD (Active)
POST https://services.leadconnectorhq.com/locations/{locationId}/customFields
Authorization: Bearer {PIT_OR_OAUTH_TOKEN}
Version: 2021-07-28
Content-Type: application/json

{
  "name": "First Touch Source",
  "fieldKey": "first_touch_source",
  "placeholder": "Original traffic source",
  "dataType": "text",
  "model": "contact"
}

# dataType options: text, number, date, datetime, boolean, single_select, multi_select
```

### Users

```http
# GET USERS (Active)
GET https://services.leadconnectorhq.com/users/
  ?locationId={LOCATION_ID}
  &limit=100
Authorization: Bearer {PIT_OR_OAUTH_TOKEN}
Version: 2021-07-28
```

```http
# GET SINGLE USER (Active)
GET https://services.leadconnectorhq.com/users/{userId}
Authorization: Bearer {PIT_OR_OAUTH_TOKEN}
Version: 2021-07-28
```

### Appointments (Calendar Events)

```http
# GET CALENDAR EVENTS (Active)
GET https://services.leadconnectorhq.com/calendars/events/
  ?locationId={LOCATION_ID}
  &startTime={ISO_DATE}
  &endTime={ISO_DATE}
  &limit=100
Authorization: Bearer {PIT_OR_OAUTH_TOKEN}
Version: 2021-07-28
```

### OAuth (Token Management)

```http
# TOKEN ENDPOINT (Updated 2026-08-10 - BACKWARD COMPATIBLE)
POST https://services.leadconnectorhq.com/oauth/token
Content-Type: application/x-www-form-urlencoded

# NEW FORMAT (snake_case - preferred):
client_id={CLIENT_ID}
&client_secret={CLIENT_SECRET}
&grant_type=refresh_token
&refresh_token={REFRESH_TOKEN}

# OLD FORMAT (camelCase - still works but deprecated):
# clientId, clientSecret, grantType, refreshToken

# Response:
{
  "access_token": "...",
  "refresh_token": "...",
  "expires_in": 86400,
  "token_type": "Bearer"
}

# NOTE: Access tokens expire every 24 hours. Must implement refresh flow.
```

---

## WEBHOOKS (Active)

**Configuration:** Set outbound webhook URL in GHL: `https://middleware.yourdomain.com/webhooks/ghl`

**Verified Events:**
- `contact.created` — New lead captured
- `contact.updated` — Contact fields changed
- `opportunity.created` — New deal created
- `opportunity.stage_changed` — Lead moved pipeline stage
- `opportunity.status_changed` — Deal won/lost
- `appointment.booked` — Appointment scheduled
- `form.submitted` — Web form submitted

**Webhook Verification:**
```javascript
const crypto = require("crypto");

function verifyGHLWebhook(payload, signature, secret) {
  const expected = crypto
    .createHmac("sha256", secret)
    .update(JSON.stringify(payload))
    .digest("hex");
  return crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expected));
}
```

---

## CRITICAL IMPLEMENTATION NOTES

1. **GET /contacts/ is DEPRECATED** — Use `GET /contacts/lookup` or implement search
2. **Custom Fields V2** — "Only supports Custom Objects and Company (Business) today. Will be extended to other Standard Objects in the future." For Contacts/Opportunities, use the inline `customFields` array in create/update calls.
3. **OAuth tokens expire every 24 hours** — Must implement automatic refresh flow
4. **Version header is REQUIRED** — `Version: 2021-07-28`
5. **Rate limit headers** included in responses — monitor `X-RateLimit-Remaining`
6. **Schema V3 migration** — As of 2026-08-03, contact responses use `GetContactByIdSchemaV3` and `DndSettingsSchemaV3`

---

## DOCUMENTATION SOURCES

| Resource | URL | Last Verified |
|----------|-----|---------------|
| Official API Docs | https://marketplace.gohighlevel.com/docs/ | 2026-08-25 |
| API Changelog | https://marketplace.gohighlevel.com/docs/Changelog/ | 2026-08-10 |
| Private Integrations | https://help.gohighlevel.com/support/solutions/articles/155000003054 | 2026-06-24 |
| API FAQ | https://help.gohighlevel.com/support/solutions/articles/48001060529 | 2026-08-19 |
