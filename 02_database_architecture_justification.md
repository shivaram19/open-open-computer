# DATABASE ARCHITECTURE: PostgreSQL + Redis
## Why This Stack for Education CRM Attribution

---

## The Business Context

Your system needs to handle:
- **Lead capture**: 50-500 leads/day (first-touch attribution locking)
- **Pipeline tracking**: 9-stage funnel with custom fields
- **Ad spend sync**: Meta + Google campaign data (hourly/daily)
- **Dashboard queries**: Multi-dimensional drill-downs (channel → campaign → ad → enrollment → revenue)
- **Daily reports**: Call center + sales manager metrics
- **Data retention**: 2+ years for trend analysis and compliance

---

## Why PostgreSQL (Not BigQuery, MongoDB, or MySQL)

### What the Research Shows

| Factor | PostgreSQL | BigQuery | MongoDB | MySQL |
|--------|-----------|----------|---------|-------|
| **Cost at demo scale** | $50-200/mo (RDS/Self-hosted) | $200-1000/mo (query-based pricing) | $50-150/mo | $50-150/mo |
| **Cost at production scale** | $300-800/mo | $1000-5000/mo | $300-1000/mo | $300-800/mo |
| **Complex JOINs** | Excellent | Good (but expensive at scale) | Poor | Good |
| **Window functions** | Native (critical for attribution) | Native | No | Limited |
| **JSON support** | JSONB (indexed) | Native | Native (but no SQL) | Basic |
| **Time-series** | Good (with partitioning) | Excellent | Good | Good |
| **Real-time dashboards** | Good (materialized views) | Good (but latency) | Good | Good |
| **SQL compatibility** | Full ANSI SQL | Standard SQL | NoSQL | Partial |
| **BI tool support** | Universal | Universal | Limited | Universal |
| **Self-hosted option** | Yes | No (managed only) | Yes | Yes |

### Why PostgreSQL Wins for Your Use Case

**1. Attribution Requires Complex JOINs and Window Functions**

Your core query pattern is:
```sql
-- Match enrollments to original campaigns via first-touch
SELECT 
  c.first_touch_campaign_id,
  c.first_touch_ad_id,
  COUNT(DISTINCT o.id) as enrollments,
  SUM(o.monetary_value) as revenue,
  SUM(mi.spend) as ad_spend,
  SUM(o.monetary_value) / NULLIF(SUM(mi.spend), 0) as roas
FROM contacts c
JOIN opportunities o ON c.id = o.contact_id
LEFT JOIN meta_insights mi ON c.first_touch_campaign_id = mi.campaign_id
WHERE o.status = 'won'
  AND o.closed_at >= '2026-08-01'
GROUP BY c.first_touch_campaign_id, c.first_touch_ad_id;
```

This requires:
- Multi-table JOINs across contacts, opportunities, and ad spend tables
- Window functions for funnel stage analysis (`COUNT(*) OVER (PARTITION BY ...)`)
- `NULLIF` for safe division (prevent division-by-zero on zero spend)
- Date range filtering with indexes

PostgreSQL handles this natively and efficiently. BigQuery can do it but charges per query — at demo scale it's fine, but at production scale with hundreds of dashboard queries per day, costs spiral.

**2. JSONB for Flexible Ad Platform Data**

Meta and Google APIs return nested JSON (targeting objects, creative specs, placement breakdowns). PostgreSQL's `JSONB` type lets you:
- Store raw API responses as JSONB
- Index specific JSON paths for fast filtering
- Query nested data with SQL operators (`->`, `->>`, `@>`, `?`)

```sql
-- Example: Find all Meta ads with video creative
SELECT * FROM meta_ads 
WHERE creative @> '{"object_type": "VIDEO"}';

-- Index for fast JSONB queries
CREATE INDEX idx_meta_ads_creative ON meta_ads USING GIN (creative);
```

**3. Materialized Views for Dashboard Performance**

Dashboards need sub-second response times. PostgreSQL materialized views pre-compute expensive aggregations:

```sql
-- Pre-compute daily campaign performance
CREATE MATERIALIZED VIEW mv_daily_campaign_performance AS
SELECT 
  DATE(o.closed_at) as date,
  c.first_touch_platform as platform,
  c.first_touch_campaign_id as campaign_id,
  COUNT(*) as enrollments,
  SUM(o.monetary_value) as revenue
FROM contacts c
JOIN opportunities o ON c.id = o.contact_id
WHERE o.status = 'won'
GROUP BY DATE(o.closed_at), c.first_touch_platform, c.first_touch_campaign_id;

-- Refresh every hour
CREATE INDEX idx_mv_daily ON mv_daily_campaign_performance(date, platform);
```

Refresh strategy: `REFRESH MATERIALIZED VIEW CONCURRENTLY` every 15-60 minutes.

**4. Row-Level Security for Multi-Location Support**

If you expand to multiple campuses or locations:
```sql
-- Enable RLS
ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;

-- Policy: Users only see contacts from their location
CREATE POLICY location_isolation ON contacts
  USING (location_id = current_setting('app.current_location_id'));
```

**5. Cost Predictability**

BigQuery charges per query ($5/TB scanned). A poorly written dashboard query can cost $50+ per execution. PostgreSQL charges per server — predictable monthly cost regardless of query volume.

For a demo and early production (under 1M leads, under 10M rows), PostgreSQL on a $100-200/month VPS or RDS instance is sufficient.

---

## Why Redis (Not Memcached or In-Memory Store)

### Use Cases in Your System

| Use Case | Why Redis | Alternative | Why Not Alternative |
|----------|-----------|-------------|---------------------|
| **First-touch session storage** | 90-day TTL, persistence options | Memcached | No persistence, no TTL granularity |
| **Attribution fingerprint cache** | Fast lookups by cookie ID | PostgreSQL | Too slow for per-request lookups |
| **Rate limit counters** | Atomic INCR/EXPIRE | In-app memory | Doesn't scale across servers |
| **Webhook queue** | Redis Streams or Lists | RabbitMQ | Overkill for demo scale |
| **Dashboard cache** | Key-value with TTL | PostgreSQL | Adds load to primary DB |

### Redis Configuration for Demo

```conf
# redis.conf for attribution middleware
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000

# 90-day TTL for attribution sessions
# Set via: EXPIRE key 7776000
```

### Redis Data Structures Used

```
# String: First-touch data (JSON serialized)
SET attr:uuid-123 '{"first_touch_source":"meta",...}' EX 7776000

# List: Attribution event log (for debugging)
LPUSH attribution_log '{"event":"first_touch",...}'
LTRIM attribution_log 0 9999  # Keep last 10k events

# Hash: Daily sales report cache
HSET daily_sales:2026-08-25:user_001 calls_made 45 appointments_booked 8
EXPIRE daily_sales:2026-08-25:user_001 86400

# Sorted Set: Campaign performance leaderboard
ZADD campaign_roas:2026-08 28.8 "meta:summer_enrollment"
ZADD campaign_roas:2026-08 30.0 "google:nursing_search"
```

---

## Architecture Pattern: "Hot Path vs. Cold Path"

```
                    +------------------+
                    |   Landing Page   |
                    +--------+---------+
                             |
                    +--------v---------+
                    |  Redis (Hot)     |  <--- First-touch capture (90-day TTL)
                    |  Session Store   |
                    +--------+---------+
                             |
                    +--------v---------+
                    |  GHL API         |  <--- CRM operations
                    +--------+---------+
                             |
                    +--------v---------+
                    |  PostgreSQL      |  <--- Cold storage, analytics, reporting
                    |  (Cold Path)     |
                    +------------------+
                             |
                    +--------v---------+
                    |  Dashboard API   |  <--- Reads from PostgreSQL + Redis cache
                    +------------------+
```

**Hot Path (Redis):**
- First-touch attribution capture (< 5ms response time)
- Session fingerprint lookups
- Rate limiting
- Real-time counters

**Cold Path (PostgreSQL):**
- Historical lead data
- Campaign performance aggregates
- Funnel stage transitions
- Revenue attribution calculations
- Daily sales reports

**Warm Path (Materialized Views):**
- Pre-computed dashboard aggregations
- Refreshed every 15-60 minutes
- Sub-second dashboard load times

---

## Scaling Path (When You Outgrow This Stack)

| Stage | Data Volume | Architecture | Cost |
|-------|-------------|--------------|------|
| **Demo** | < 10k leads | PostgreSQL (1 instance) + Redis (1 instance) | $50-100/mo |
| **Early Production** | 10k-100k leads | PostgreSQL (2 vCPU, 4GB) + Redis (1GB) | $100-200/mo |
| **Growth** | 100k-1M leads | PostgreSQL (read replica) + Redis Cluster + Cron jobs | $300-600/mo |
| **Scale** | 1M+ leads | BigQuery (warehouse) + PostgreSQL (operational) + Redis | $1000+/mo |

**Migration trigger:** When dashboard queries consistently take > 3 seconds despite materialized views, or when ad spend data exceeds 100M rows per year.

---

## What Other Businesses Have Done

**Case Study Pattern (from research):**
- **Fable Food** (education/food tech): Used BigQuery as central hub with Coupler.io for multi-source ETL. Started with PostgreSQL for operational data, moved to BigQuery for analytics at scale.
- **Napkyn (marketing agency)**: Built unified marketing analytics in BigQuery combining GA4, Google Ads, and CRM data. Used PostgreSQL for real-time operational dashboards, BigQuery for long-term trend analysis.
- **Reflective Data**: Used BigQuery for custom attribution models (last-touch, first-touch, linear, Markov) but noted that "the limitation is not what the database can do — it's getting clean data into it consistently."

**Key Insight:** Start with PostgreSQL + Redis. Move to BigQuery only when you need multi-year trend analysis or ML-based attribution modeling. For a demo and first 6-12 months of production, PostgreSQL is the right choice.

---

## Recommended Cloud Setup for Demo

| Component | Service | Specs | Monthly Cost |
|-----------|---------|-------|--------------|
| PostgreSQL | AWS RDS / DigitalOcean / Supabase | 1 vCPU, 2GB RAM, 20GB SSD | $15-30 |
| Redis | AWS ElastiCache / Redis Cloud / Upstash | 250MB-1GB | $0-20 |
| App Server | AWS EC2 / DigitalOcean / Railway | 1 vCPU, 1GB RAM | $10-20 |
| Total | | | **$25-70/month** |

**Free tier options:**
- Supabase: Free PostgreSQL tier (500MB, 2M row reads/day)
- Upstash: Free Redis tier (10k commands/day)
- Railway / Render: Free tier for Node.js apps

**Total demo cost: $0-25/month**
