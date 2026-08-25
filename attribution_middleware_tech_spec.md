# TECHNICAL SPECIFICATION
## Custom Marketing Attribution Middleware (The 20% Build)
### GoHighLevel + Meta Marketing API + Google Ads API Integration

**Version:** 1.0  
**Date:** August 2026  
**Status:** Draft for Implementation

---

## TABLE OF CONTENTS

1. [Architecture Overview](#1-architecture-overview)
2. [API Version Compliance & Deprecation Exclusions](#2-api-version-compliance--deprecation-exclusions)
3. [Component 1: First-Touch Attribution Capture Service](#3-component-1-first-touch-attribution-capture-service)
4. [Component 2: GHL Data Sync Engine](#4-component-2-ghl-data-sync-engine)
5. [Component 3: Meta Marketing API Integration](#5-component-3-meta-marketing-api-integration)
6. [Component 4: Google Ads API Integration](#6-component-4-google-ads-api-integration)
7. [Component 5: Attribution Engine](#7-component-5-attribution-engine)
8. [Component 6: Analytics Data Warehouse](#8-component-6-analytics-data-warehouse)
9. [Component 7: Dashboard API](#9-component-7-dashboard-api)
10. [Data Schema](#10-data-schema)
11. [Security & Rate Limiting](#11-security--rate-limiting)
12. [Error Handling & Retry Logic](#12-error-handling--retry-logic)
13. [Deployment Architecture](#13-deployment-architecture)

---

## 1. ARCHITECTURE OVERVIEW

```
+-----------------------------------------------------------------------------+
|                              CLIENT LAYER                                    |
|  +--------------+  +--------------+  +--------------+  +--------------+      |
|  |  GHL Forms   |  |  Landing     |  |  Direct      |  |  Referral    |      |
|  |  (Webforms)  |  |  Pages       |  |  Traffic     |  |  Links       |      |
|  +------+-------+  +------+-------+  +------+-------+  +------+-------+      |
+--------+-----------------+-----------------+-----------------+---------------+
         |                 |                 |                 |
         +-----------------+--------+-------------------------+
                                     |
                                     v
+-----------------------------------------------------------------------------+
|                    ATTRIBUTION CAPTURE SERVICE (Middleware)                  |
|  +---------------------------------------------------------------------+    |
|  |  * Capture ALL UTM parameters on first visit                        |    |
|  |  * Generate & store first-touch fingerprint (cookie + server-side)  |    |
|  |  * LOCK first-touch data -- NEVER overwrite on subsequent visits     |    |
|  |  * Pass through GCLID, FBCLID, MSCLKID                            |    |
|  |  * Store in Redis/cache with TTL = 90 days                          |    |
|  +---------------------------------------------------------------------+    |
+---------------------------------+-------------------------------------------+
                                  |
          +-----------------------+-----------------------+
          |                       |                       |
          v                       v                       v
+-----------------+    +-----------------+    +-----------------+
|   GHL API V2    |    |  Meta Marketing |    |  Google Ads API |
|                 |    |     API v25     |    |     v24         |
+--------+--------+    +--------+--------+    +--------+--------+
         |                      |                      |
         v                      v                      v
+-----------------------------------------------------------------------------+
|                         ANALYTICS DATA WAREHOUSE                             |
|  +--------------+  +--------------+  +--------------+  +--------------+      |
|  |  leads       |  |  campaigns   |  |  ad_spend    |  |  attributions|      |
|  |  contacts    |  |  adsets      |  |  keywords    |  |  funnel_stage|      |
|  |  opportunities| |  ads         |  |  search_terms|  |  conversions |      |
|  +--------------+  +--------------+  +--------------+  +--------------+      |
+---------------------------------+-------------------------------------------+
                                  |
                                  v
+-----------------------------------------------------------------------------+
|                         ATTRIBUTION ENGINE                                   |
|  +---------------------------------------------------------------------+    |
|  |  * Match GHL enrollments -> original campaign/ad                     |    |
|  |  * Calculate CAC, ROAS, LTV per campaign                            |    |
|  |  * First-touch vs. Last-touch attribution models                    |    |
|  |  * Lead quality scoring by source                                   |    |
|  |  * Lost lead analysis by stage & reason                             |    |
|  +---------------------------------------------------------------------+    |
+---------------------------------+-------------------------------------------+
                                  |
                                  v
+-----------------------------------------------------------------------------+
|                         DASHBOARD API (REST/GraphQL)                         |
|  +---------------------------------------------------------------------+    |
|  |  /api/v1/dashboard/executive     -> ROI, CAC, Revenue               |    |
|  |  /api/v1/dashboard/channel       -> Meta vs Google vs Organic       |    |
|  |  /api/v1/dashboard/campaign      -> Drill-down to ad level          |    |
|  |  /api/v1/dashboard/quality       -> CPL vs Enrollment Rate          |    |
|  |  /api/v1/dashboard/lost-leads    -> Reasons by Source/Stage         |    |
|  |  /api/v1/dashboard/daily-sales   -> Call Center vs Sales Manager    |    |
|  +---------------------------------------------------------------------+    |
+-----------------------------------------------------------------------------+
```

---

## 2. API VERSION COMPLIANCE & DEPRECATION EXCLUSIONS

### 2.1 GoHighLevel API

| Aspect | Requirement | Citation |
|--------|-------------|----------|
| **Active Version** | API V2 (V1 end-of-support Dec 31, 2025) | V1 has reached end-of-support as on 31-December-2025. All developers should migrate to API V2. |
| **Base URL** | `https://services.leadconnectorhq.com` | Official GHL API documentation |
| **Auth** | OAuth 2.0 or Private Integration Token (PIT) | Private Integration Tokens for internal tools; OAuth 2.0 for public apps |
| **Rate Limits** | 100 req/10 sec per resource; 200,000/day per resource | Rate limit headers included in responses |
| **Docs** | https://marketplace.gohighlevel.com/docs/ | Versioned API references available |

**DEPRECATED -- DO NOT USE:**
- GHL API V1 (end-of-support, no updates or technical support)
- Legacy Stoplight documentation (being deprecated)
- Agency/Sub-account API Keys (ability to generate new keys removed)

### 2.2 Meta Marketing API

| Aspect | Requirement | Citation |
|--------|-------------|----------|
| **Active Version** | v24.0 or v25.0 (v23.0 is end of life) | Move integrations to v24.0 or higher, ideally v25.0, now that v23.0 is end of life. |
| **Base URL** | `https://graph.facebook.com/v25.0/` | Graph API structure |
| **Auth** | OAuth 2.0 User/Access Token | Business Manager permissions required |
| **Rate Limits** | 200 calls/hour per app; 5 insights/min per ad account | Ad account limit is most restrictive for reporting |
| **Docs** | https://developers.facebook.com/docs/marketing-api/ | Official Meta Developer documentation |

**DEPRECATED -- DO NOT USE:**
- `7d_view` attribution window (removed Jan 12, 2026 -- returns empty data)
- `28d_view` attribution window (removed Jan 12, 2026 -- returns empty data)
- Combined windows using 7d_view or 28d_view
- v23.0 and lower (end of life)
- Post/Page Reach metrics (retiring from Graph API June 2026)
- Video Impressions, Story Impressions (retiring June 2026)
- Messenger Inbox placement `messenger_home` (deprecated Nov 2025)
- Legacy Advantage+ Shopping/App campaign APIs (phased deprecation)
- `dma_codes` for automotive (replaced by `comscore_market_codes` June 2026)

**Active Attribution Windows (2026):**
| Window | Status | Use Case |
|--------|--------|----------|
| `1d_click` | Active | Flash sales, immediate conversions |
| `7d_click` | Active (default) | Standard campaigns |
| `28d_click` | Active (reporting only) | Long sales cycle comparison |
| `1d_view` | Active | View-through only |
| `1d_engaged_view` | Active | Video engagement |
| `7d_view` | REMOVED Jan 12, 2026 | DO NOT USE |
| `28d_view` | REMOVED Jan 12, 2026 | DO NOT USE |

### 2.3 Google Ads API

| Aspect | Requirement | Citation |
|--------|-------------|----------|
| **Active Version** | v24 (released April 22, 2026) | Latest stable version |
| **Protocol** | REST or gRPC | gRPC recommended for production scale |
| **Auth** | OAuth 2.0 + Developer Token | Manager account required; approval takes a few business days |
| **Rate Limits** | Operation-based quota system | Every operation counts against quota |
| **Docs** | https://developers.google.com/google-ads/api/docs/start | Official Google Ads API documentation |

**DEPRECATED -- DO NOT USE:**
- Smart Campaign creation via API (removing support Aug 3, 2026)
- v23 and earlier for certain Performance Max reporting features
- `MIXED` enum for Performance Max channel breakdowns (replaced in v23)

---

## 3. COMPONENT 1: FIRST-TOUCH ATTRIBUTION CAPTURE SERVICE

### 3.1 Purpose
Capture and LOCK first-touch UTM parameters, GCLID, FBCLID, and referrer data at the moment of lead creation. Prevent GHL from overwriting this data on subsequent visits.

### 3.2 Implementation

#### 3.2.1 GHL Custom Fields Setup (One-Time Configuration)

Create the following **Contact Custom Fields** via GHL API:

```http
POST https://services.leadconnectorhq.com/locations/{locationId}/customFields
Authorization: Bearer {ACCESS_TOKEN}
Content-Type: application/json

{
  "name": "First Touch Source",
  "fieldKey": "first_touch_source",
  "placeholder": "Original traffic source",
  "dataType": "text",
  "model": "contact"
}
```

**Required Custom Fields (Contact Level):**

| Field Name | Field Key | Data Type | Purpose |
|-----------|-----------|-----------|---------|
| First Touch Source | `first_touch_source` | text | utm_source at first visit |
| First Touch Medium | `first_touch_medium` | text | utm_medium at first visit |
| First Touch Campaign | `first_touch_campaign` | text | utm_campaign at first visit |
| First Touch Content | `first_touch_content` | text | utm_content at first visit |
| First Touch Term | `first_touch_term` | text | utm_term at first visit |
| First Touch GCLID | `first_touch_gclid` | text | Google Click ID |
| First Touch FBCLID | `first_touch_fbclid` | text | Facebook Click ID |
| First Touch Referrer | `first_touch_referrer` | text | Original referrer URL |
| First Touch Date | `first_touch_date` | date | Timestamp of first visit |
| First Touch Landing Page | `first_touch_landing_page` | text | URL of first landing page |
| First Touch Campaign ID | `first_touch_campaign_id` | text | Meta/Google Campaign ID |
| First Touch Ad Set ID | `first_touch_adset_id` | text | Meta Ad Set ID |
| First Touch Ad ID | `first_touch_ad_id` | text | Meta/Google Ad ID |
| First Touch Keyword | `first_touch_keyword` | text | Google Ads keyword |
| First Touch Search Term | `first_touch_search_term` | text | Google Ads search term |
| First Touch Match Type | `first_touch_match_type` | text | Google Ads match type |
| First Touch Placement | `first_touch_placement` | text | Meta placement |
| Latest Touch Source | `latest_touch_source` | text | Last known source (updated) |
| Latest Touch Campaign | `latest_touch_campaign` | text | Last known campaign (updated) |

**Required Custom Fields (Opportunity Level):**

| Field Name | Field Key | Data Type | Purpose |
|-----------|-----------|-----------|---------|
| Enrolled Program | `enrolled_program` | text | Actual program enrolled |
| Initial Program Interest | `initial_program_interest` | text | Program lead first asked about |
| Payment Method | `payment_method` | text | FAFSA / Grant / Out-of-pocket |
| Grant Amount | `grant_amount` | number | Financial aid amount |
| Program Cost | `program_cost` | number | Total program cost |
| FAFSA Submitted Date | `fafsa_submitted_date` | date | When FAFSA was applied |
| FAFSA Confirmed Date | `fafsa_confirmed_date` | date | When FAFSA was confirmed |
| Lost Reason | `lost_reason` | text | Reason for closure (dropdown) |
| Lost Stage | `lost_stage` | text | Pipeline stage when lost |
| Lost Date | `lost_date` | date | When lead was marked lost |
| Upsell Program | `upsell_program` | text | Program upsold to |
| Upsell Amount | `upsell_amount` | number | Additional revenue |
| Referral Source Name | `referral_source_name` | text | Who referred the student |
| Review Requested | `review_requested` | boolean | Yes/No |
| Review Date Requested | `review_date_requested` | date | When review was requested |
| Review Received | `review_received` | boolean | Yes/No |
| Review Platform | `review_platform` | text | Google / Video / Other |
| Review Link | `review_link` | text | URL to published review |

#### 3.2.2 Capture Middleware (Node.js/Express Example)

```javascript
/**
 * First-Touch Attribution Capture Service
 * Intercepts all form submissions and landing page visits before GHL
 * Stores first-touch data in Redis with 90-day TTL
 */

const express = require("express");
const Redis = require("ioredis");
const { v4: uuidv4 } = require("uuid");

const app = express();
const redis = new Redis(process.env.REDIS_URL);

// Generate or retrieve attribution fingerprint
async function getOrCreateAttributionFingerprint(req) {
  const fingerprintCookie = req.cookies?.["_attr_fp"];

  if (fingerprintCookie) {
    const existing = await redis.get(`attr:${fingerprintCookie}`);
    if (existing) {
      return { fingerprint: fingerprintCookie, data: JSON.parse(existing), isNew: false };
    }
  }

  // New visitor -- create fingerprint and capture first-touch
  const fingerprint = uuidv4();
  const firstTouchData = {
    fingerprint,
    first_touch_source: req.query.utm_source || req.query.source || "direct",
    first_touch_medium: req.query.utm_medium || req.query.medium || "none",
    first_touch_campaign: req.query.utm_campaign || "",
    first_touch_content: req.query.utm_content || "",
    first_touch_term: req.query.utm_term || "",
    first_touch_gclid: req.query.gclid || "",
    first_touch_fbclid: req.query.fbclid || "",
    first_touch_msclkid: req.query.msclkid || "",
    first_touch_referrer: req.headers.referer || "",
    first_touch_landing_page: `${req.protocol}://${req.get("host")}${req.originalUrl}`,
    first_touch_date: new Date().toISOString(),
    first_touch_campaign_id: req.query.campaign_id || "",
    first_touch_adset_id: req.query.adset_id || "",
    first_touch_ad_id: req.query.ad_id || "",
    first_touch_keyword: req.query.keyword || "",
    first_touch_search_term: req.query.search_term || "",
    first_touch_match_type: req.query.matchtype || "",
    first_touch_placement: req.query.placement || "",
    // Latest touch (will be updated on each visit)
    latest_touch_source: req.query.utm_source || "direct",
    latest_touch_campaign: req.query.utm_campaign || "",
    latest_touch_date: new Date().toISOString(),
    visit_count: 1
  };

  // Store in Redis with 90-day TTL
  await redis.setex(`attr:${fingerprint}`, 7776000, JSON.stringify(firstTouchData));

  return { fingerprint, data: firstTouchData, isNew: true };
}

// Middleware: Attach attribution to form submissions
app.use("/forms/*", async (req, res, next) => {
  const { fingerprint, data, isNew } = await getOrCreateAttributionFingerprint(req);

  // Set cookie for 90 days
  res.cookie("_attr_fp", fingerprint, { maxAge: 7776000000, httpOnly: true, sameSite: "strict" });

  // Inject first-touch data into request body before forwarding to GHL
  req.body.customFields = {
    ...req.body.customFields,
    ...data
  };

  // Log attribution event
  await redis.lpush("attribution_log", JSON.stringify({
    fingerprint,
    event: isNew ? "first_touch" : "return_visit",
    timestamp: new Date().toISOString(),
    data
  }));

  next();
});

// Endpoint: Receive GHL webhook and update attribution on pipeline changes
app.post("/webhooks/ghl/pipeline-stage-changed", async (req, res) => {
  const { contactId, opportunityId, newStage, oldStage } = req.body;

  // Fetch contact to get fingerprint
  const contact = await fetchGHLContact(contactId);
  const fingerprint = contact.customFields?.find(f => f.key === "attribution_fingerprint")?.value;

  if (fingerprint) {
    const attrData = await redis.get(`attr:${fingerprint}`);
    if (attrData) {
      const parsed = JSON.parse(attrData);
      parsed.pipeline_stages = parsed.pipeline_stages || [];
      parsed.pipeline_stages.push({
        stage: newStage,
        entered_at: new Date().toISOString(),
        opportunity_id: opportunityId
      });
      await redis.setex(`attr:${fingerprint}`, 7776000, JSON.stringify(parsed));
    }
  }

  res.status(200).send("OK");
});
```

**Docs Cited:**
- GHL Custom Fields API: POST /locations/{locationId}/customFields -- create custom fields for contacts and opportunities
- GHL Rate Limits: 100 requests per 10 seconds per resource
- GHL Auth: OAuth 2.0 or Private Integration Token

---

## 4. COMPONENT 2: GHL DATA SYNC ENGINE

### 4.1 Purpose
Synchronize contact, opportunity, pipeline, and appointment data from GHL into the analytics warehouse. Listen for real-time changes via webhooks and poll for bulk sync.

### 4.2 GHL API Endpoints Used

#### 4.2.1 Contacts API

```http
# List Contacts (with pagination)
GET https://services.leadconnectorhq.com/contacts/
  ?locationId={locationId}
  &limit=100
  &page=1
  &query={searchQuery}
Authorization: Bearer {ACCESS_TOKEN}

# Get Single Contact
GET https://services.leadconnectorhq.com/contacts/{contactId}
Authorization: Bearer {ACCESS_TOKEN}

# Create Contact (with custom fields)
POST https://services.leadconnectorhq.com/contacts/
Authorization: Bearer {ACCESS_TOKEN}
Content-Type: application/json

{
  "locationId": "{locationId}",
  "firstName": "John",
  "lastName": "Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "customFields": [
    { "key": "first_touch_source", "value": "meta" },
    { "key": "first_touch_campaign", "value": "summer_enrollment_2026" },
    { "key": "first_touch_ad_id", "value": "123456789" }
  ],
  "tags": ["new-lead", "meta-ads"],
  "source": "Meta Ads"
}

# Update Contact
PUT https://services.leadconnectorhq.com/contacts/{contactId}
Authorization: Bearer {ACCESS_TOKEN}
Content-Type: application/json

{
  "customFields": [
    { "key": "latest_touch_source", "value": "google" }
  ]
}
```

#### 4.2.2 Opportunities API (Pipeline)

```http
# List Opportunities
GET https://services.leadconnectorhq.com/opportunities/
  ?locationId={locationId}
  &pipelineId={pipelineId}
  &stageId={stageId}
  &limit=100
  &page=1
Authorization: Bearer {ACCESS_TOKEN}

# Get Single Opportunity
GET https://services.leadconnectorhq.com/opportunities/{opportunityId}
Authorization: Bearer {ACCESS_TOKEN}

# Create Opportunity
POST https://services.leadconnectorhq.com/opportunities/
Authorization: Bearer {ACCESS_TOKEN}
Content-Type: application/json

{
  "locationId": "{locationId}",
  "pipelineId": "{pipelineId}",
  "pipelineStageId": "{stageId}",
  "contactId": "{contactId}",
  "name": "John Doe - Nursing Program",
  "monetaryValue": 15000,
  "status": "open",
  "assignedTo": "{userId}",
  "customFields": [
    { "key": "initial_program_interest", "value": "Nursing" },
    { "key": "enrolled_program", "value": "" },
    { "key": "payment_method", "value": "FAFSA" }
  ]
}

# Update Opportunity (e.g., move stage, close deal)
PUT https://services.leadconnectorhq.com/opportunities/{opportunityId}
Authorization: Bearer {ACCESS_TOKEN}
Content-Type: application/json

{
  "pipelineStageId": "{newStageId}",
  "status": "won",
  "monetaryValue": 15000,
  "customFields": [
    { "key": "enrolled_program", "value": "Practical Nursing" },
    { "key": "program_cost", "value": "15000" }
  ]
}
```

#### 4.2.3 Custom Fields API

```http
# Get All Custom Fields for Location
GET https://services.leadconnectorhq.com/locations/{locationId}/customFields
  ?model=contact
Authorization: Bearer {ACCESS_TOKEN}

# Response Schema:
{
  "customFields": [
    {
      "id": "cf_abc123",
      "name": "First Touch Source",
      "fieldKey": "first_touch_source",
      "dataType": "text",
      "model": "contact",
      "locationId": "loc_xyz789"
    }
  ]
}
```

#### 4.2.4 Users API (for Sales Team Reporting)

```http
# Get All Users in Location
GET https://services.leadconnectorhq.com/users/
  ?locationId={locationId}
  &limit=100
Authorization: Bearer {ACCESS_TOKEN}

# Get Single User
GET https://services.leadconnectorhq.com/users/{userId}
Authorization: Bearer {ACCESS_TOKEN}
```

#### 4.2.5 Appointments API

```http
# Get Appointments
GET https://services.leadconnectorhq.com/calendars/events/
  ?locationId={locationId}
  &startTime={isoDate}
  &endTime={isoDate}
  &limit=100
Authorization: Bearer {ACCESS_TOKEN}

# Get Single Appointment
GET https://services.leadconnectorhq.com/calendars/events/{eventId}
Authorization: Bearer {ACCESS_TOKEN}
```

### 4.3 GHL Webhooks (Real-Time Sync)

Configure outbound webhooks in GHL to push events to the middleware:

**Webhook URL:** `https://middleware.yourdomain.com/webhooks/ghl`

**Required Events:**
| Event | Trigger | Action in Middleware |
|-------|---------|---------------------|
| `contact.created` | New lead captured | Store contact + attribution data |
| `contact.updated` | Contact fields changed | Sync updated fields to warehouse |
| `opportunity.created` | New deal created | Create opportunity record |
| `opportunity.stage_changed` | Lead moved pipeline stage | Update funnel analytics, trigger attribution match |
| `opportunity.status_changed` | Deal won/lost | Calculate revenue attribution, record lost reason |
| `appointment.booked` | Appointment scheduled | Record appointment |
| `appointment.checked_in` | Check-in marked | Update show-up rate metrics |
| `form.submitted` | Web form submitted | Capture UTM + first-touch data |

**Webhook Payload Verification:**
```javascript
// GHL sends signature header for verification
const crypto = require("crypto");

function verifyGHLWebhook(payload, signature, secret) {
  const expected = crypto
    .createHmac("sha256", secret)
    .update(JSON.stringify(payload))
    .digest("hex");
  return crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expected));
}
```

**Docs Cited:**
- GHL API Base URL: https://services.leadconnectorhq.com
- GHL V1 end-of-support: Dec 31, 2025
- GHL Webhooks: 50+ events available, real-time notifications
- GHL Rate Limits: 100 req/10s, 200,000/day

---

## 5. COMPONENT 3: META MARKETING API INTEGRATION

### 5.1 Purpose
Pull campaign, ad set, ad, and spend data from Meta. Map Meta campaign/ad IDs to GHL leads for revenue attribution.

### 5.2 Meta API Configuration

```
Base URL: https://graph.facebook.com/v25.0/
Auth: OAuth 2.0 Access Token (requires ads_read, ads_management permissions)
Rate Limits: 200 calls/hour per app; 5 insights requests/minute per ad account
```

### 5.3 Core Endpoints

#### 5.3.1 Campaign Data

```http
# Get All Campaigns
GET https://graph.facebook.com/v25.0/act_{AD_ACCOUNT_ID}/campaigns
  ?fields=id,name,status,objective,daily_budget,lifetime_budget,bid_strategy
  &access_token={ACCESS_TOKEN}

# Get Campaign Insights
GET https://graph.facebook.com/v25.0/{CAMPAIGN_ID}/insights
  ?fields=campaign_name,impressions,clicks,link_clicks,spend,cpm,cpc,ctr,
         reach,frequency,actions,action_values,cost_per_action_type,
         leads,cost_per_lead
  &date_preset=last_30d
  &time_increment=1
  &action_attribution_windows=["7d_click","1d_view"]
  &access_token={ACCESS_TOKEN}
```

#### 5.3.2 Ad Set Data

```http
# Get All Ad Sets
GET https://graph.facebook.com/v25.0/act_{AD_ACCOUNT_ID}/adsets
  ?fields=id,name,campaign_id,daily_budget,targeting,status
  &access_token={ACCESS_TOKEN}

# Get Ad Set Insights
GET https://graph.facebook.com/v25.0/{ADSET_ID}/insights
  ?fields=adset_name,impressions,clicks,spend,actions,action_values,
         cost_per_action_type,leads
  &breakdowns=age,gender,country,device_platform,publisher_platform,placement
  &date_preset=last_30d
  &access_token={ACCESS_TOKEN}
```

#### 5.3.3 Ad-Level Data

```http
# Get All Ads
GET https://graph.facebook.com/v25.0/act_{AD_ACCOUNT_ID}/ads
  ?fields=id,name,adset_id,campaign_id,creative,status
  &access_token={ACCESS_TOKEN}

# Get Ad Insights (Creative Performance)
GET https://graph.facebook.com/v25.0/{AD_ID}/insights
  ?fields=ad_name,impressions,clicks,link_clicks,spend,ctr,cpc,cpm,
         actions,action_values,conversions,conversion_values,
         cost_per_conversion,video_p25_watched_actions,
         video_p50_watched_actions,video_p75_watched_actions,
         video_p95_watched_actions,video_p100_watched_actions
  &breakdowns=placement,publisher_platform
  &date_preset=last_30d
  &time_increment=1
  &action_attribution_windows=["7d_click","1d_view"]
  &access_token={ACCESS_TOKEN}
```

#### 5.3.4 Account-Level Aggregated Insights

```http
# Account-Level Insights with Campaign Breakdown
GET https://graph.facebook.com/v25.0/act_{AD_ACCOUNT_ID}/insights
  ?level=campaign
  &fields=campaign_id,campaign_name,adset_id,adset_name,ad_id,ad_name,
         impressions,clicks,link_clicks,spend,reach,frequency,
         actions,action_values,cost_per_action_type
  &breakdowns=publisher_platform,placement
  &date_preset=last_30d
  &time_increment=1
  &action_attribution_windows=["7d_click","1d_view"]
  &access_token={ACCESS_TOKEN}
```

### 5.4 Meta API -- Handling Rate Limits & Async Jobs

```javascript
/**
 * Meta API Rate Limit Handler
 * 5 insights requests per minute per ad account
 * Use async jobs for large data pulls
 */

class MetaAPIClient {
  constructor(accessToken, adAccountId) {
    this.accessToken = accessToken;
    this.adAccountId = adAccountId;
    this.baseURL = "https://graph.facebook.com/v25.0";
    this.lastRequestTime = 0;
    this.minInterval = 12000; // 12 seconds between requests (5/min)
  }

  async rateLimitDelay() {
    const now = Date.now();
    const elapsed = now - this.lastRequestTime;
    if (elapsed < this.minInterval) {
      await new Promise(r => setTimeout(r, this.minInterval - elapsed));
    }
    this.lastRequestTime = Date.now();
  }

  async getInsights(endpoint, params) {
    await this.rateLimitDelay();

    const url = new URL(`${this.baseURL}/${endpoint}/insights`);
    url.searchParams.append("access_token", this.accessToken);
    Object.entries(params).forEach(([key, value]) => {
      url.searchParams.append(key, typeof value === "object" ? JSON.stringify(value) : value);
    });

    const response = await fetch(url);
    const data = await response.json();

    // Handle rate limit error (code 80004)
    if (data.error && data.error.code === 80004) {
      const retryAfter = data.error.error_subcode === 1 ? 60000 : 300000;
      console.log(`Rate limited. Retrying after ${retryAfter}ms`);
      await new Promise(r => setTimeout(r, retryAfter));
      return this.getInsights(endpoint, params);
    }

    return data;
  }

  // Async job for large reports
  async submitAsyncJob(endpoint, params) {
    const url = `${this.baseURL}/${endpoint}/insights`;
    const body = {
      ...params,
      async: true,
      access_token: this.accessToken
    };

    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });

    const data = await response.json();
    const reportRunId = data.report_run_id;

    // Poll for completion
    let status = "Job Not Started";
    while (status !== "Job Completed") {
      await new Promise(r => setTimeout(r, 10000));
      const statusRes = await fetch(`${this.baseURL}/${reportRunId}?access_token=${this.accessToken}`);
      const statusData = await statusRes.json();
      status = statusData.async_status;
      console.log(`Job status: ${status} (${statusData.async_percent_completion}%)`);
    }

    // Download results
    const resultsRes = await fetch(`${this.baseURL}/${reportRunId}/insights?access_token=${this.accessToken}`);
    return resultsRes.json();
  }
}
```

### 5.5 Meta Attribution Window Configuration (2026 Compliant)

```javascript
// CORRECT: Use only active attribution windows
const VALID_ATTRIBUTION_WINDOWS = {
  standard: ["7d_click", "1d_view"],        // Default for most campaigns
  conservative: ["1d_click", "1d_view"],    // Flash sales
  click_only: ["7d_click"],                  // Performance comparison
  reporting_only: ["28d_click"]             // Long cycle analysis only
};

// INCORRECT -- DO NOT USE (deprecated Jan 12, 2026):
// ["7d_view"], ["28d_view"], ["7d_click", "7d_view"], ["7d_click", "28d_view"]
```

**Docs Cited:**
- Meta Marketing API v25.0: Active version (v23 end of life)
- Attribution windows: 7d_view and 28d_view removed Jan 12, 2026
- Rate limits: 5 insights/min per ad account; async jobs for large pulls
- Insights endpoint: 70+ metrics available; hierarchical (account -> campaign -> adset -> ad)
- Breakdowns: age, gender, country, device_platform, publisher_platform, placement

---

## 6. COMPONENT 4: GOOGLE ADS API INTEGRATION

### 6.1 Purpose
Pull campaign, ad group, keyword, and search term data from Google Ads. Map Google campaign/ad group IDs to GHL leads.

### 6.2 Google Ads API Configuration

```
Version: v24 (released April 22, 2026)
Protocol: gRPC (recommended) or REST
Auth: OAuth 2.0 + Developer Token
Base URL (REST): https://googleads.googleapis.com/v24/
Rate Limits: Operation-based quota system
```

### 6.3 Core Queries (GAQL -- Google Ads Query Language)

#### 6.3.1 Campaign Performance Report

```sql
-- Campaign-level performance with metrics
SELECT
  campaign.id,
  campaign.name,
  campaign.status,
  campaign.advertising_channel_type,
  metrics.impressions,
  metrics.clicks,
  metrics.cost_micros,
  metrics.conversions,
  metrics.conversions_value,
  metrics.cost_per_conversion,
  metrics.search_impression_share,
  segments.date
FROM campaign
WHERE segments.date DURING LAST_30_DAYS
ORDER BY metrics.cost_micros DESC
```

#### 6.3.2 Ad Group Performance Report

```sql
-- Ad Group-level performance
SELECT
  campaign.id,
  campaign.name,
  ad_group.id,
  ad_group.name,
  ad_group.status,
  metrics.impressions,
  metrics.clicks,
  metrics.cost_micros,
  metrics.conversions,
  metrics.conversions_value,
  metrics.ctr,
  metrics.average_cpc,
  segments.date
FROM ad_group
WHERE segments.date DURING LAST_30_DAYS
```

#### 6.3.3 Keyword Performance Report

```sql
-- Keyword-level performance (Search campaigns only)
SELECT
  campaign.id,
  campaign.name,
  ad_group.id,
  ad_group.name,
  ad_group_criterion.criterion_id,
  ad_group_criterion.keyword.text,
  ad_group_criterion.keyword.match_type,
  metrics.impressions,
  metrics.clicks,
  metrics.cost_micros,
  metrics.conversions,
  metrics.conversions_value,
  metrics.quality_score,
  metrics.search_impression_share,
  segments.date
FROM keyword_view
WHERE segments.date DURING LAST_30_DAYS
```

#### 6.3.4 Search Term Report

```sql
-- Search terms that triggered ads (critical for attribution)
SELECT
  campaign.id,
  campaign.name,
  ad_group.id,
  ad_group.name,
  search_term_view.search_term,
  search_term_view.status,
  metrics.impressions,
  metrics.clicks,
  metrics.cost_micros,
  metrics.conversions,
  metrics.conversions_value,
  segments.date
FROM search_term_view
WHERE segments.date DURING LAST_30_DAYS
  AND metrics.clicks > 0
ORDER BY metrics.cost_micros DESC
```

#### 6.3.5 Campaign-Level Conversion Report

```sql
-- Conversion tracking by campaign
SELECT
  campaign.id,
  campaign.name,
  segments.conversion_action_name,
  segments.conversion_action_category,
  metrics.conversions,
  metrics.conversions_value,
  metrics.cost_per_conversion,
  metrics.conversion_rate,
  segments.date
FROM campaign
WHERE segments.date DURING LAST_30_DAYS
  AND segments.conversion_action_category = "LEAD"
```

### 6.4 Google Ads API Client Implementation (Python)

```python
"""
Google Ads API v24 Client
Requires: google-ads==24.0.0
"""

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import pandas as pd

class GoogleAdsAPIClient:
    def __init__(self, developer_token, client_id, client_secret, 
                 refresh_token, login_customer_id=None):
        self.client = GoogleAdsClient.load_from_dict({
            "developer_token": developer_token,
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "login_customer_id": login_customer_id,
            "use_proto_plus": True
        })
        self.ga_service = self.client.get_service("GoogleAdsService")
        self.customer_id = None

    def execute_query(self, customer_id, query):
        """Execute GAQL query and return results as DataFrame"""
        self.customer_id = customer_id

        try:
            stream = self.ga_service.search_stream(
                customer_id=customer_id,
                query=query
            )

            results = []
            for batch in stream:
                for row in batch.results:
                    results.append(self._parse_row(row))

            return pd.DataFrame(results)

        except GoogleAdsException as ex:
            self._handle_error(ex)
            return pd.DataFrame()

    def _parse_row(self, row):
        """Parse protobuf row into dict"""
        result = {}

        # Campaign fields
        if row.campaign:
            result["campaign_id"] = row.campaign.id
            result["campaign_name"] = row.campaign.name
            result["campaign_status"] = row.campaign.status.name
            result["channel_type"] = row.campaign.advertising_channel_type.name

        # Ad group fields
        if row.ad_group:
            result["ad_group_id"] = row.ad_group.id
            result["ad_group_name"] = row.ad_group.name

        # Keyword fields
        if row.ad_group_criterion:
            result["criterion_id"] = row.ad_group_criterion.criterion_id
            if row.ad_group_criterion.keyword:
                result["keyword_text"] = row.ad_group_criterion.keyword.text
                result["match_type"] = row.ad_group_criterion.keyword.match_type.name

        # Search term
        if row.search_term_view:
            result["search_term"] = row.search_term_view.search_term

        # Metrics
        if row.metrics:
            result["impressions"] = row.metrics.impressions
            result["clicks"] = row.metrics.clicks
            result["cost_micros"] = row.metrics.cost_micros
            result["cost_usd"] = row.metrics.cost_micros / 1_000_000
            result["conversions"] = row.metrics.conversions
            result["conversions_value"] = row.metrics.conversions_value
            result["ctr"] = row.metrics.ctr
            result["avg_cpc"] = row.metrics.average_cpc

        # Segments
        if row.segments:
            result["date"] = row.segments.date
            if row.segments.conversion_action_name:
                result["conversion_action"] = row.segments.conversion_action_name

        return result

    def _handle_error(self, ex):
        """Handle Google Ads API errors"""
        for error in ex.failure.errors:
            print(f"Error code: {error.error_code}")
            print(f"Message: {error.message}")
            if error.location:
                for field_path in error.location.field_path_elements:
                    print(f"Field: {field_path.field_name}")

    def get_campaign_spend(self, customer_id, days=30):
        """Get campaign spend data for attribution"""
        query = f"""
        SELECT
          campaign.id,
          campaign.name,
          metrics.cost_micros,
          metrics.conversions,
          metrics.conversions_value,
          segments.date
        FROM campaign
        WHERE segments.date DURING LAST_{days}_DAYS
        ORDER BY metrics.cost_micros DESC
        """
        return self.execute_query(customer_id, query)

    def get_keyword_performance(self, customer_id, days=30):
        """Get keyword-level data for search term attribution"""
        query = f"""
        SELECT
          campaign.id,
          campaign.name,
          ad_group.id,
          ad_group.name,
          ad_group_criterion.criterion_id,
          ad_group_criterion.keyword.text,
          ad_group_criterion.keyword.match_type,
          metrics.impressions,
          metrics.clicks,
          metrics.cost_micros,
          metrics.conversions,
          segments.date
        FROM keyword_view
        WHERE segments.date DURING LAST_{days}_DAYS
        """
        return self.execute_query(customer_id, query)

    def get_search_terms(self, customer_id, days=30):
        """Get search term report for quality analysis"""
        query = f"""
        SELECT
          campaign.id,
          campaign.name,
          ad_group.id,
          ad_group.name,
          search_term_view.search_term,
          metrics.impressions,
          metrics.clicks,
          metrics.cost_micros,
          metrics.conversions,
          segments.date
        FROM search_term_view
        WHERE segments.date DURING LAST_{days}_DAYS
          AND metrics.clicks > 0
        ORDER BY metrics.cost_micros DESC
        """
        return self.execute_query(customer_id, query)
```

### 6.5 Google Ads API -- Deprecation Exclusions

**DO NOT USE:**
- Smart Campaign creation via API (support ends Aug 3, 2026)
- v23 and earlier for Performance Max channel reporting
- `MIXED` enum for Performance Max placements (replaced in v23)

**USE v24 FOR:**
- `CartDataSalesView` for product-level reporting
- Lead generation conversion type enumerations
- VTC optimization for Demand Gen and App campaigns
- Expanded product reporting for all campaign types (from June 15, 2026)

**Docs Cited:**
- Google Ads API v24: Released April 22, 2026
- Smart Campaign API deprecation: Creation support ends Aug 3, 2026
- Performance Max channel reporting: Available in v23+ for dates on/after June 1, 2025
- GAQL: Primary query language for reporting

---

## 7. COMPONENT 5: ATTRIBUTION ENGINE

### 7.1 Purpose
Match GHL enrollments (opportunities marked "won") to original ad campaigns using first-touch data. Calculate CAC, ROAS, and lead quality metrics.

### 7.2 Attribution Logic

```python
"""
Attribution Engine Core Logic
Matches GHL closed deals to Meta/Google campaigns using first-touch data
"""

class AttributionEngine:
    def __init__(self, db, meta_client, google_client):
        self.db = db
        self.meta = meta_client
        self.google = google_client

    async def process_enrollment(self, opportunity_id):
        """
        When an opportunity is marked WON in GHL:
        1. Fetch opportunity + contact
        2. Extract first-touch campaign IDs
        3. Pull corresponding ad spend from Meta/Google
        4. Calculate CAC and ROAS
        5. Store attribution record
        """
        # 1. Get opportunity and contact
        opportunity = await self.db.opportunities.find_one({"_id": opportunity_id})
        contact = await self.db.contacts.find_one({"_id": opportunity["contact_id"]})

        first_touch = contact.get("first_touch", {})
        deal_value = opportunity.get("monetary_value", 0)

        attribution = {
            "opportunity_id": opportunity_id,
            "contact_id": contact["_id"],
            "enrollment_date": opportunity.get("closed_at"),
            "deal_value": deal_value,
            "first_touch": first_touch,
            "ad_spend": 0,
            "cac": 0,
            "roas": 0,
            "attribution_model": "first_touch"
        }

        # 2. Match to Meta campaign
        if first_touch.get("source") == "meta" and first_touch.get("campaign_id"):
            meta_spend = await self.get_meta_campaign_spend(
                first_touch["campaign_id"],
                first_touch["adset_id"],
                first_touch["ad_id"],
                first_touch["first_touch_date"]
            )
            attribution["ad_spend"] = meta_spend
            attribution["platform"] = "meta"
            attribution["campaign_id"] = first_touch["campaign_id"]
            attribution["adset_id"] = first_touch["adset_id"]
            attribution["ad_id"] = first_touch["ad_id"]
            attribution["placement"] = first_touch.get("placement", "")

        # 3. Match to Google campaign
        elif first_touch.get("source") == "google" and first_touch.get("campaign_id"):
            google_spend = await self.get_google_campaign_spend(
                first_touch["campaign_id"],
                first_touch.get("ad_group_id"),
                first_touch["first_touch_date"]
            )
            attribution["ad_spend"] = google_spend
            attribution["platform"] = "google"
            attribution["campaign_id"] = first_touch["campaign_id"]
            attribution["ad_group_id"] = first_touch.get("ad_group_id")
            attribution["keyword"] = first_touch.get("keyword", "")
            attribution["search_term"] = first_touch.get("search_term", "")
            attribution["match_type"] = first_touch.get("match_type", "")

        # 4. Calculate metrics
        if attribution["ad_spend"] > 0:
            attribution["cac"] = attribution["ad_spend"]
            attribution["roas"] = deal_value / attribution["ad_spend"] if attribution["ad_spend"] > 0 else 0

        # 5. Store attribution
        await self.db.attributions.insert_one(attribution)

        # 6. Update campaign performance aggregate
        await self.update_campaign_aggregate(attribution)

        return attribution

    async def get_meta_campaign_spend(self, campaign_id, adset_id, ad_id, touch_date):
        """Get spend for specific Meta campaign/ad from first-touch date to enrollment"""
        # Query Meta Insights API for spend
        # Use async job if date range is large
        pass

    async def get_google_campaign_spend(self, campaign_id, ad_group_id, touch_date):
        """Get spend for specific Google campaign from first-touch date to enrollment"""
        # Query Google Ads API for spend
        pass

    async def calculate_lead_quality(self, campaign_id, platform, days=30):
        """
        Lead Quality Matrix:
        Leads -> Qualified -> Appointment -> Show-up -> Enrollment -> Revenue
        """
        pipeline = await self.db.opportunities.aggregate([
            {"$match": {
                "first_touch.campaign_id": campaign_id,
                "first_touch.platform": platform,
                "created_at": {"$gte": datetime.now() - timedelta(days=days)}
            }},
            {"$group": {
                "_id": "$stage",
                "count": {"$sum": 1},
                "total_value": {"$sum": "$monetary_value"}
            }}
        ]).to_list()

        return {
            "campaign_id": campaign_id,
            "platform": platform,
            "total_leads": sum(p["count"] for p in pipeline),
            "qualified": next((p["count"] for p in pipeline if p["_id"] == "qualified"), 0),
            "appointments": next((p["count"] for p in pipeline if p["_id"] == "appointment"), 0),
            "check_ins": next((p["count"] for p in pipeline if p["_id"] == "check_in"), 0),
            "consultations": next((p["count"] for p in pipeline if p["_id"] == "consultation"), 0),
            "enrollments": next((p["count"] for p in pipeline if p["_id"] == "enrollment"), 0),
            "total_revenue": sum(p["total_value"] for p in pipeline if p["_id"] == "enrollment")
        }

    async def lost_lead_analysis(self, source=None, stage=None, days=30):
        """
        Lost Lead Analytics:
        - Number of lost leads by source/stage
        - % lost leads
        - Most common reasons for refusal
        """
        match_stage = {"status": "lost"}
        if source:
            match_stage["first_touch.source"] = source
        if stage:
            match_stage["lost_stage"] = stage

        results = await self.db.opportunities.aggregate([
            {"$match": match_stage},
            {"$group": {
                "_id": {
                    "source": "$first_touch.source",
                    "lost_reason": "$lost_reason",
                    "lost_stage": "$lost_stage"
                },
                "count": {"$sum": 1},
                "total_value": {"$sum": "$monetary_value"}
            }},
            {"$sort": {"count": -1}}
        ]).to_list()

        return results
```

### 7.3 Attribution Models Supported

| Model | Description | Use Case |
|-------|-------------|----------|
| **First Touch** | 100% credit to first interaction | Understanding acquisition channels |
| **Last Touch** | 100% credit to last interaction before conversion | Understanding closing channels |
| **Linear** | Equal credit to all touchpoints | Full journey analysis |
| **Time Decay** | More credit to recent touches | Long sales cycles |

---

## 8. COMPONENT 6: ANALYTICS DATA WAREHOUSE

### 8.1 Purpose
Centralized data store for all attribution, campaign, and pipeline data. Enables fast querying for dashboard views.

### 8.2 Recommended Stack

| Layer | Technology | Reason |
|-------|-----------|--------|
| Database | PostgreSQL 16+ or BigQuery | Structured data + time-series analytics |
| Cache | Redis 7+ | First-touch session storage (90-day TTL) |
| Queue | RabbitMQ or AWS SQS | Async processing of webhooks and API syncs |
| Scheduler | Celery + Redis or AWS EventBridge | Daily sync jobs, report generation |

### 8.3 Core Schema

#### 8.3.1 Contacts Table
```sql
CREATE TABLE contacts (
    id UUID PRIMARY KEY,
    ghl_contact_id VARCHAR(255) UNIQUE NOT NULL,
    location_id VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    first_name VARCHAR(255),
    last_name VARCHAR(255),

    -- First Touch Attribution (LOCKED -- never updated)
    first_touch_source VARCHAR(100),
    first_touch_medium VARCHAR(100),
    first_touch_campaign VARCHAR(255),
    first_touch_content VARCHAR(255),
    first_touch_term VARCHAR(255),
    first_touch_gclid VARCHAR(255),
    first_touch_fbclid VARCHAR(255),
    first_touch_referrer TEXT,
    first_touch_landing_page TEXT,
    first_touch_date TIMESTAMP,
    first_touch_campaign_id VARCHAR(255),
    first_touch_adset_id VARCHAR(255),
    first_touch_ad_id VARCHAR(255),
    first_touch_keyword VARCHAR(255),
    first_touch_search_term VARCHAR(255),
    first_touch_match_type VARCHAR(50),
    first_touch_placement VARCHAR(100),

    -- Latest Touch Attribution (updated on each visit)
    latest_touch_source VARCHAR(100),
    latest_touch_campaign VARCHAR(255),
    latest_touch_date TIMESTAMP,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    attribution_fingerprint VARCHAR(255),
    tags TEXT[],

    INDEX idx_ghl_contact (ghl_contact_id),
    INDEX idx_first_touch_campaign (first_touch_campaign_id),
    INDEX idx_first_touch_source (first_touch_source),
    INDEX idx_created_at (created_at)
);
```

#### 8.3.2 Opportunities (Pipeline) Table
```sql
CREATE TABLE opportunities (
    id UUID PRIMARY KEY,
    ghl_opportunity_id VARCHAR(255) UNIQUE NOT NULL,
    contact_id UUID REFERENCES contacts(id),
    pipeline_id VARCHAR(255),
    stage_id VARCHAR(255),
    stage_name VARCHAR(255),
    status VARCHAR(50), -- open, won, lost
    name VARCHAR(255),
    monetary_value DECIMAL(12,2),
    assigned_to VARCHAR(255),

    -- Enrollment-specific fields
    initial_program VARCHAR(255),
    enrolled_program VARCHAR(255),
    payment_method VARCHAR(100), -- FAFSA, Grant, Out-of-pocket
    grant_amount DECIMAL(12,2),
    program_cost DECIMAL(12,2),
    fafsa_submitted_date TIMESTAMP,
    fafsa_confirmed_date TIMESTAMP,

    -- Lost lead tracking
    lost_reason VARCHAR(255),
    lost_stage VARCHAR(255),
    lost_date TIMESTAMP,

    -- Upsell tracking
    upsell_program VARCHAR(255),
    upsell_amount DECIMAL(12,2),
    upsell_date TIMESTAMP,

    -- Referral tracking
    referral_source_name VARCHAR(255),

    -- Review tracking
    review_requested BOOLEAN DEFAULT FALSE,
    review_date_requested TIMESTAMP,
    review_received BOOLEAN DEFAULT FALSE,
    review_platform VARCHAR(100),
    review_link TEXT,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    closed_at TIMESTAMP,

    INDEX idx_ghl_opp (ghl_opportunity_id),
    INDEX idx_contact (contact_id),
    INDEX idx_stage (stage_name),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);
```

#### 8.3.3 Meta Campaigns Table
```sql
CREATE TABLE meta_campaigns (
    id UUID PRIMARY KEY,
    campaign_id VARCHAR(255) UNIQUE NOT NULL,
    ad_account_id VARCHAR(255),
    name VARCHAR(255),
    status VARCHAR(50),
    objective VARCHAR(100),
    daily_budget BIGINT, -- in cents
    lifetime_budget BIGINT,
    bid_strategy VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_campaign_id (campaign_id),
    INDEX idx_ad_account (ad_account_id)
);
```

#### 8.3.4 Meta Ad Sets Table
```sql
CREATE TABLE meta_adsets (
    id UUID PRIMARY KEY,
    adset_id VARCHAR(255) UNIQUE NOT NULL,
    campaign_id VARCHAR(255) REFERENCES meta_campaigns(campaign_id),
    name VARCHAR(255),
    status VARCHAR(50),
    daily_budget BIGINT,
    targeting JSONB,
    created_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_adset_id (adset_id),
    INDEX idx_campaign (campaign_id)
);
```

#### 8.3.5 Meta Ads Table
```sql
CREATE TABLE meta_ads (
    id UUID PRIMARY KEY,
    ad_id VARCHAR(255) UNIQUE NOT NULL,
    adset_id VARCHAR(255) REFERENCES meta_adsets(adset_id),
    campaign_id VARCHAR(255) REFERENCES meta_campaigns(campaign_id),
    name VARCHAR(255),
    status VARCHAR(50),
    creative JSONB,
    created_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_ad_id (ad_id),
    INDEX idx_adset (adset_id)
);
```

#### 8.3.6 Meta Insights Table
```sql
CREATE TABLE meta_insights (
    id UUID PRIMARY KEY,
    campaign_id VARCHAR(255),
    adset_id VARCHAR(255),
    ad_id VARCHAR(255),
    date DATE,

    -- Delivery metrics
    impressions BIGINT,
    reach BIGINT,
    frequency DECIMAL(8,2),
    clicks BIGINT,
    link_clicks BIGINT,
    ctr DECIMAL(8,4),

    -- Cost metrics
    spend DECIMAL(12,2), -- in USD
    cpm DECIMAL(12,2),
    cpc DECIMAL(12,2),

    -- Conversion metrics
    leads BIGINT,
    cost_per_lead DECIMAL(12,2),
    conversions BIGINT,
    conversion_values DECIMAL(12,2),
    cost_per_conversion DECIMAL(12,2),

    -- Breakdowns
    publisher_platform VARCHAR(100),
    placement VARCHAR(100),
    device_platform VARCHAR(100),
    age VARCHAR(20),
    gender VARCHAR(20),
    country VARCHAR(10),

    -- Attribution window used
    attribution_window VARCHAR(50),

    fetched_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_campaign_date (campaign_id, date),
    INDEX idx_ad_date (ad_id, date),
    INDEX idx_date (date)
);
```

#### 8.3.7 Google Campaigns Table
```sql
CREATE TABLE google_campaigns (
    id UUID PRIMARY KEY,
    campaign_id VARCHAR(255) UNIQUE NOT NULL,
    customer_id VARCHAR(255),
    name VARCHAR(255),
    status VARCHAR(50),
    advertising_channel_type VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_campaign_id (campaign_id),
    INDEX idx_customer (customer_id)
);
```

#### 8.3.8 Google Ad Groups Table
```sql
CREATE TABLE google_ad_groups (
    id UUID PRIMARY KEY,
    ad_group_id VARCHAR(255) UNIQUE NOT NULL,
    campaign_id VARCHAR(255) REFERENCES google_campaigns(campaign_id),
    name VARCHAR(255),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_ad_group (ad_group_id),
    INDEX idx_campaign (campaign_id)
);
```

#### 8.3.9 Google Keywords Table
```sql
CREATE TABLE google_keywords (
    id UUID PRIMARY KEY,
    criterion_id VARCHAR(255) UNIQUE NOT NULL,
    ad_group_id VARCHAR(255) REFERENCES google_ad_groups(ad_group_id),
    campaign_id VARCHAR(255) REFERENCES google_campaigns(campaign_id),
    keyword_text VARCHAR(255),
    match_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_criterion (criterion_id),
    INDEX idx_ad_group (ad_group_id)
);
```

#### 8.3.10 Google Insights Table
```sql
CREATE TABLE google_insights (
    id UUID PRIMARY KEY,
    campaign_id VARCHAR(255),
    ad_group_id VARCHAR(255),
    criterion_id VARCHAR(255),
    date DATE,

    -- Delivery metrics
    impressions BIGINT,
    clicks BIGINT,
    ctr DECIMAL(8,4),

    -- Cost metrics
    cost_micros BIGINT,
    cost_usd DECIMAL(12,2),
    average_cpc DECIMAL(12,2),

    -- Conversion metrics
    conversions DECIMAL(12,2),
    conversions_value DECIMAL(12,2),
    cost_per_conversion DECIMAL(12,2),
    conversion_rate DECIMAL(8,4),

    -- Quality
    quality_score INT,
    search_impression_share DECIMAL(8,4),

    fetched_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_campaign_date (campaign_id, date),
    INDEX idx_keyword_date (criterion_id, date),
    INDEX idx_date (date)
);
```

#### 8.3.11 Search Terms Table
```sql
CREATE TABLE google_search_terms (
    id UUID PRIMARY KEY,
    campaign_id VARCHAR(255),
    ad_group_id VARCHAR(255),
    search_term VARCHAR(255),
    date DATE,

    impressions BIGINT,
    clicks BIGINT,
    cost_micros BIGINT,
    cost_usd DECIMAL(12,2),
    conversions DECIMAL(12,2),
    conversions_value DECIMAL(12,2),

    fetched_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_campaign_date (campaign_id, date),
    INDEX idx_search_term (search_term)
);
```

#### 8.3.12 Attributions Table
```sql
CREATE TABLE attributions (
    id UUID PRIMARY KEY,
    opportunity_id UUID REFERENCES opportunities(id),
    contact_id UUID REFERENCES contacts(id),

    -- Deal info
    enrollment_date TIMESTAMP,
    deal_value DECIMAL(12,2),

    -- Attribution model
    attribution_model VARCHAR(50), -- first_touch, last_touch, linear

    -- Platform data
    platform VARCHAR(50), -- meta, google, organic, referral
    campaign_id VARCHAR(255),
    campaign_name VARCHAR(255),

    -- Meta-specific
    adset_id VARCHAR(255),
    adset_name VARCHAR(255),
    ad_id VARCHAR(255),
    ad_name VARCHAR(255),
    placement VARCHAR(100),

    -- Google-specific
    ad_group_id VARCHAR(255),
    ad_group_name VARCHAR(255),
    keyword VARCHAR(255),
    search_term VARCHAR(255),
    match_type VARCHAR(50),

    -- Calculated metrics
    ad_spend DECIMAL(12,2),
    cac DECIMAL(12,2),
    roas DECIMAL(8,2),

    created_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_opportunity (opportunity_id),
    INDEX idx_contact (contact_id),
    INDEX idx_campaign (campaign_id),
    INDEX idx_platform (platform),
    INDEX idx_enrollment_date (enrollment_date)
);
```

#### 8.3.13 Daily Sales Reports Table
```sql
CREATE TABLE daily_sales_reports (
    id UUID PRIMARY KEY,
    date DATE NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    user_name VARCHAR(255),
    role VARCHAR(50), -- call_center, sales_manager

    -- Call Center Metrics
    calls_made INT DEFAULT 0,
    completed_dialogues_20s INT DEFAULT 0,
    appointments_booked INT DEFAULT 0,
    transfers INT DEFAULT 0,
    cancellations INT DEFAULT 0,
    check_ins INT DEFAULT 0,
    show_up_rate DECIMAL(5,2),
    hours_worked DECIMAL(5,2),

    -- Sales Manager Metrics
    calls_attempted INT DEFAULT 0,
    calls_completed INT DEFAULT 0,
    consultations_conducted INT DEFAULT 0,
    trial_lessons INT DEFAULT 0,
    fafsa_submitted INT DEFAULT 0,
    fafsa_confirmed INT DEFAULT 0,
    enrollments INT DEFAULT 0,
    upsells INT DEFAULT 0,
    sales_amount DECIMAL(12,2),

    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(date, user_id),
    INDEX idx_date (date),
    INDEX idx_user (user_id)
);
```

---

## 9. COMPONENT 7: DASHBOARD API

### 9.1 Purpose
REST API serving pre-aggregated data to the frontend dashboard. All endpoints return JSON.

### 9.2 API Specification

#### 9.2.1 Executive Dashboard

```http
GET /api/v1/dashboard/executive
  ?start_date=2026-08-01
  &end_date=2026-08-31
  &location_id={locationId}
Authorization: Bearer {DASHBOARD_TOKEN}

Response:
{
  "period": { "start": "2026-08-01", "end": "2026-08-31" },
  "summary": {
    "total_marketing_spend": 45230.50,
    "total_leads": 1245,
    "qualified_leads": 890,
    "cost_per_lead": 36.33,
    "appointments": 456,
    "lead_to_appointment_rate": 36.6,
    "check_ins": 342,
    "appointment_to_checkin_rate": 75.0,
    "consultations": 310,
    "enrollments": 85,
    "lead_to_enrollment_rate": 6.8,
    "total_revenue": 1275000.00,
    "average_deal_value": 15000.00,
    "cac": 532.12,
    "roas": 28.2,
    "roi_percentage": 2720,
    "lost_leads": 1160,
    "lost_lead_percentage": 93.2
  },
  "trend": [
    { "date": "2026-08-01", "leads": 45, "enrollments": 3, "revenue": 45000 },
    // ... daily trend
  ]
}
```

#### 9.2.2 Channel Breakdown

```http
GET /api/v1/dashboard/channel
  ?start_date=2026-08-01
  &end_date=2026-08-31
  &location_id={locationId}

Response:
{
  "channels": [
    {
      "name": "Meta",
      "spend": 25000.00,
      "leads": 680,
      "qualified_leads": 510,
      "cpl": 36.76,
      "appointments": 280,
      "check_ins": 210,
      "enrollments": 48,
      "revenue": 720000.00,
      "cac": 520.83,
      "roas": 28.8
    },
    {
      "name": "Google",
      "spend": 15000.00,
      "leads": 420,
      "qualified_leads": 294,
      "cpl": 35.71,
      "appointments": 140,
      "check_ins": 105,
      "enrollments": 30,
      "revenue": 450000.00,
      "cac": 500.00,
      "roas": 30.0
    },
    {
      "name": "Referral",
      "spend": 0,
      "leads": 85,
      "qualified_leads": 68,
      "cpl": 0,
      "appointments": 25,
      "check_ins": 20,
      "enrollments": 5,
      "revenue": 75000.00,
      "cac": 0,
      "roas": null
    },
    {
      "name": "Organic Search",
      "spend": 0,
      "leads": 60,
      "qualified_leads": 18,
      "cpl": 0,
      "appointments": 11,
      "check_ins": 7,
      "enrollments": 2,
      "revenue": 30000.00,
      "cac": 0,
      "roas": null
    }
  ]
}
```

#### 9.2.3 Campaign Drill-Down

```http
GET /api/v1/dashboard/campaign
  ?start_date=2026-08-01
  &end_date=2026-08-31
  &platform=meta
  &campaign_id=123456789

Response:
{
  "campaign": {
    "id": "123456789",
    "name": "Summer Enrollment 2026",
    "platform": "meta",
    "spend": 15000.00,
    "leads": 420,
    "qualified_leads": 315,
    "cpl": 35.71,
    "appointments": 175,
    "check_ins": 131,
    "enrollments": 30,
    "conversion_rate": 7.1,
    "revenue": 450000.00,
    "cac": 500.00,
    "roas": 30.0
  },
  "adsets": [
    {
      "id": "987654321",
      "name": "Lookalike 1%",
      "spend": 8000.00,
      "leads": 240,
      "enrollments": 18,
      "revenue": 270000.00,
      "roas": 33.75
    },
    {
      "id": "987654322",
      "name": "Interest: Healthcare",
      "spend": 7000.00,
      "leads": 180,
      "enrollments": 12,
      "revenue": 180000.00,
      "roas": 25.71
    }
  ],
  "ads": [
    {
      "id": "111222333",
      "name": "Video V1 - Testimonial",
      "spend": 5000.00,
      "leads": 150,
      "enrollments": 12,
      "revenue": 180000.00,
      "roas": 36.0,
      "placement": "facebook_feed"
    }
  ]
}
```

#### 9.2.4 Lead Quality Matrix

```http
GET /api/v1/dashboard/quality
  ?start_date=2026-08-01
  &end_date=2026-08-31

Response:
{
  "campaigns": [
    {
      "name": "Summer Enrollment 2026",
      "platform": "meta",
      "cpl": 35.71,
      "leads": 420,
      "qualified_rate": 75.0,
      "appointment_rate": 41.7,
      "showup_rate": 75.0,
      "enrollment_rate": 7.1,
      "revenue_per_lead": 1071.43,
      "roas": 30.0,
      "quality_score": 9.2
    },
    {
      "name": "Google Search - Nursing",
      "platform": "google",
      "cpl": 55.00,
      "leads": 200,
      "qualified_rate": 85.0,
      "appointment_rate": 50.0,
      "showup_rate": 80.0,
      "enrollment_rate": 12.0,
      "revenue_per_lead": 1800.00,
      "roas": 32.7,
      "quality_score": 9.8
    }
  ]
}
```

#### 9.2.5 Lost Lead Analysis

```http
GET /api/v1/dashboard/lost-leads
  ?start_date=2026-08-01
  &end_date=2026-08-31
  &source=meta
  &stage=consultation

Response:
{
  "summary": {
    "total_lost": 1160,
    "lost_percentage": 93.2,
    "total_potential_revenue": 17400000.00
  },
  "by_source": [
    { "source": "meta", "lost": 580, "percentage": 50.0 },
    { "source": "google", "lost": 348, "percentage": 30.0 },
    { "source": "referral", "lost": 116, "percentage": 10.0 },
    { "source": "organic", "lost": 116, "percentage": 10.0 }
  ],
  "by_stage": [
    { "stage": "new_lead", "lost": 200, "percentage": 17.2 },
    { "stage": "qualified", "lost": 150, "percentage": 12.9 },
    { "stage": "appointment", "lost": 180, "percentage": 15.5 },
    { "stage": "check_in", "lost": 120, "percentage": 10.3 },
    { "stage": "consultation", "lost": 310, "percentage": 26.7 },
    { "stage": "fafsa_applied", "lost": 100, "percentage": 8.6 },
    { "stage": "fafsa_confirmed", "lost": 50, "percentage": 4.3 },
    { "stage": "payment", "lost": 50, "percentage": 4.3 }
  ],
  "by_reason": [
    { "reason": "Price not suitable / No financing", "count": 290, "percentage": 25.0 },
    { "reason": "Program not suitable", "count": 232, "percentage": 20.0 },
    { "reason": "Not eligible for funding", "count": 174, "percentage": 15.0 },
    { "reason": "Schedule not suitable", "count": 116, "percentage": 10.0 },
    { "reason": "Not ready to start", "count": 116, "percentage": 10.0 },
    { "reason": "Not responding", "count": 87, "percentage": 7.5 },
    { "reason": "Chose another school", "count": 58, "percentage": 5.0 },
    { "reason": "FAFSA not approved", "count": 29, "percentage": 2.5 },
    { "reason": "Changed mind", "count": 29, "percentage": 2.5 },
    { "reason": "Other", "count": 29, "percentage": 2.5 }
  ]
}
```

#### 9.2.6 Daily Sales Report

```http
GET /api/v1/dashboard/daily-sales
  ?date=2026-08-25
  &location_id={locationId}

Response:
{
  "date": "2026-08-25",
  "call_center": [
    {
      "user_id": "user_001",
      "name": "Sarah Johnson",
      "calls_made": 45,
      "completed_dialogues_20s": 32,
      "appointments_booked": 8,
      "transfers": 3,
      "cancellations": 1,
      "check_ins": 5,
      "show_up_rate": 62.5,
      "hours_worked": 8.0
    }
  ],
  "sales_managers": [
    {
      "user_id": "user_010",
      "name": "Michael Chen",
      "calls_attempted": 20,
      "calls_completed": 15,
      "appointments": 5,
      "check_ins": 4,
      "consultations_conducted": 3,
      "trial_lessons": 1,
      "fafsa_submitted": 2,
      "fafsa_confirmed": 1,
      "enrollments": 1,
      "upsells": 0,
      "sales_amount": 15000.00
    }
  ]
}
```

---

## 10. DATA SCHEMA

### 10.1 Entity Relationship Diagram

```
+-------------+       +-------------+       +-------------+
|  contacts   |<------|opportunities|       |  meta_ads   |
|  (GHL)      | 1:M   |  (GHL)      |       |  (Meta)     |
+------+------+       +------+------+       +------+------+
       |                     |                      |
       |              +------+------+              |
       |              | attributions|              |
       +------------->|  (JOIN)     |<-------------+
                      +-------------+
                             |
                      +------+------+
                      |  dashboard  |
                      |  aggregates |
                      +-------------+
```

### 10.2 Data Flow

1. **Lead Capture** -> GHL Form -> Attribution Middleware captures first-touch -> Stores in Redis + GHL custom fields
2. **Pipeline Movement** -> GHL Webhook -> Middleware updates stage tracking in warehouse
3. **Deal Close** -> GHL Webhook (opportunity.won) -> Attribution Engine matches to campaign -> Pulls ad spend -> Calculates CAC/ROAS -> Stores attribution
4. **Daily Sync** -> Scheduled job pulls Meta/Google spend data -> Updates insights tables
5. **Dashboard Query** -> Frontend calls Dashboard API -> Returns pre-aggregated metrics

---

## 11. SECURITY & RATE LIMITING

### 11.1 Authentication

| System | Method | Token Type |
|--------|--------|-----------|
| GHL API | OAuth 2.0 or PIT | Bearer token |
| Meta API | OAuth 2.0 | User access token |
| Google Ads API | OAuth 2.0 + Developer Token | Bearer + developer_token header |
| Dashboard API | JWT | Bearer token (internal) |

### 11.2 Rate Limit Handling

| API | Limit | Strategy |
|-----|-------|----------|
| GHL | 100 req/10s | Batch operations, cache responses |
| Meta Insights | 5 req/min per ad account | Queue requests, use async jobs |
| Meta Core | 200 req/hour per app | Exponential backoff |
| Google Ads | Operation quota | Batch mutations, stream reports |

### 11.3 Data Protection

- All API tokens stored in environment variables or secrets manager (AWS Secrets Manager / HashiCorp Vault)
- Redis sessions encrypted at rest
- PostgreSQL encrypted with AES-256
- Webhook payloads verified with HMAC signature
- PII (email, phone) hashed in analytics warehouse where possible
- GDPR/CCPA compliance for EU leads (Meta EU privacy options)

---

## 12. ERROR HANDLING & RETRY LOGIC

### 12.1 Retry Strategy

```javascript
const RETRY_CONFIG = {
  maxRetries: 5,
  baseDelay: 1000,      // 1 second
  maxDelay: 60000,      // 60 seconds
  backoffMultiplier: 2, // Exponential
  retryableErrors: [
    "ETIMEDOUT", "ECONNRESET", "ECONNREFUSED",
    "RATE_LIMIT", "SERVER_ERROR", "SERVICE_UNAVAILABLE"
  ]
};

async function retryWithBackoff(operation, context) {
  let attempt = 0;

  while (attempt < RETRY_CONFIG.maxRetries) {
    try {
      return await operation();
    } catch (error) {
      attempt++;

      if (!RETRY_CONFIG.retryableErrors.includes(error.code)) {
        throw error; // Non-retryable error
      }

      const delay = Math.min(
        RETRY_CONFIG.baseDelay * Math.pow(RETRY_CONFIG.backoffMultiplier, attempt),
        RETRY_CONFIG.maxDelay
      );

      console.log(`[${context}] Retry ${attempt}/${RETRY_CONFIG.maxRetries} after ${delay}ms`);
      await new Promise(r => setTimeout(r, delay));
    }
  }

  throw new Error(`[${context}] Max retries exceeded`);
}
```

### 12.2 Dead Letter Queue

Failed operations (webhook processing, API syncs) are pushed to a dead letter queue for manual review:

```sql
CREATE TABLE dead_letter_queue (
    id UUID PRIMARY KEY,
    source VARCHAR(100), -- ghl, meta, google
    operation VARCHAR(255),
    payload JSONB,
    error_message TEXT,
    error_code VARCHAR(100),
    retry_count INT DEFAULT 0,
    status VARCHAR(50), -- pending, resolved, failed
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP
);
```

---

## 13. DEPLOYMENT ARCHITECTURE

### 13.1 Recommended Infrastructure

```
+-------------------------------------------------------------+
|                         AWS / GCP / Azure                    |
|  +--------------+  +--------------+  +--------------+      |
|  |   Load       |  |   API        |  |   Worker     |      |
|  |   Balancer   |  |   Servers    |  |   Nodes      |      |
|  |   (ALB/NGINX)|  |   (Node.js)  |  |   (Celery)   |      |
|  +------+-------+  +------+-------+  +------+-------+      |
|         |                 |                 |               |
|  +------+-----------------+-----------------+-------+      |
|  |              PostgreSQL (Primary)                 |      |
|  |         +---------------------+                   |      |
|  |         |   Redis (Cache/Queue) |                  |      |
|  |         +---------------------+                   |      |
|  +---------------------------------------------------+      |
|                                                             |
|  +--------------+  +--------------+  +--------------+      |
|  |  CloudWatch  |  |   Sentry     |  |   Datadog    |      |
|  |  (Logs)      |  |  (Errors)    |  |  (Metrics)   |      |
|  +--------------+  +--------------+  +--------------+      |
+-------------------------------------------------------------+
```

### 13.2 Environment Variables

```bash
# GHL
GHL_BASE_URL=https://services.leadconnectorhq.com
GHL_ACCESS_TOKEN=ghl_oauth_token_or_pit
GHL_LOCATION_ID=your_location_id
GHL_WEBHOOK_SECRET=whsec_your_webhook_secret

# Meta
META_API_VERSION=v25.0
META_ACCESS_TOKEN=EAAG...
META_AD_ACCOUNT_ID=act_123456789
META_APP_SECRET=your_app_secret

# Google Ads
GOOGLE_DEVELOPER_TOKEN=your_developer_token
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REFRESH_TOKEN=...
GOOGLE_CUSTOMER_ID=123-456-7890
GOOGLE_LOGIN_CUSTOMER_ID=your_manager_account_id

# Database
DATABASE_URL=postgresql://user:pass@host:5432/attribution_db
REDIS_URL=redis://host:6379/0

# Dashboard
JWT_SECRET=your_jwt_secret
DASHBOARD_API_PORT=3000

# Environment
NODE_ENV=production
LOG_LEVEL=info
```

### 13.3 Daily Sync Schedule

| Job | Frequency | Description |
|-----|-----------|-------------|
| sync_meta_insights | Every 6 hours | Pull campaign/ad spend from Meta |
| sync_google_insights | Every 6 hours | Pull campaign/keyword spend from Google |
| sync_ghl_contacts | Every 2 hours | Bulk sync contacts from GHL |
| sync_ghl_opportunities | Every 2 hours | Bulk sync pipeline data |
| calculate_attributions | Every 4 hours | Process new enrollments, calculate CAC/ROAS |
| generate_daily_sales_report | Daily at 23:59 | Aggregate call center + sales manager metrics |
| cleanup_expired_sessions | Daily at 03:00 | Remove Redis keys older than 90 days |

---

## APPENDIX A: DEPRECATED COMPONENTS (DO NOT USE)

| Platform | Deprecated Component | Replacement | Removal Date |
|----------|---------------------|-------------|--------------|
| GHL | API V1 | API V2 | Dec 31, 2025 (end-of-support) |
| GHL | Stoplight docs | marketplace.gohighlevel.com/docs | Coming months |
| GHL | Agency/Sub-account API Keys | Private Integration Tokens | New generation removed |
| Meta | 7d_view attribution | 1d_view | Jan 12, 2026 |
| Meta | 28d_view attribution | 1d_view | Jan 12, 2026 |
| Meta | v23.0 API | v24.0 or v25.0 | End of life |
| Meta | Post/Page Reach metrics | Media Views / Page Viewer | June 2026 |
| Meta | Video Impressions | Media Views | June 2026 |
| Meta | Story Impressions | Media Views | June 2026 |
| Meta | Messenger Inbox placement | N/A | Nov 11, 2025 |
| Meta | dma_codes (automotive) | comscore_market_codes | June 22, 2026 |
| Meta | Legacy Advantage+ APIs | Automation Unification | May 19, 2026 |
| Google | Smart Campaign creation API | Performance Max | Aug 3, 2026 |
| Google | v23 for PMax channel reporting | v24 | April 2026 |
| Google | MIXED enum (PMax) | Specific channel enums | v23+ |

---

## APPENDIX B: DOCUMENTATION REFERENCES

| Resource | URL | Status |
|----------|-----|--------|
| GHL API Docs | https://marketplace.gohighlevel.com/docs/ | Active (V2) |
| GHL Custom Fields | https://help.gohighlevel.com/support/solutions/articles/48001161579 | Active |
| GHL Webhooks | https://help.gohighlevel.com/support/solutions/articles/155000003299 | Active |
| Meta Marketing API | https://developers.facebook.com/docs/marketing-api/ | Active (v25) |
| Meta Insights API | https://developers.facebook.com/docs/marketing-api/insights/ | Active |
| Meta Attribution Windows | https://developers.facebook.com/docs/marketing-api/insights/attributionwindow | Updated Jan 2026 |
| Google Ads API | https://developers.google.com/google-ads/api/docs/start | Active (v24) |
| Google Ads API Release Notes | https://developers.google.com/google-ads/api/docs/release-notes | Active |
| Google Ads Reporting | https://developers.google.com/google-ads/api/docs/reporting/overview | Active |

---

Document Version: 1.0
Last Updated: August 2026
Author: Technical Architecture Team
