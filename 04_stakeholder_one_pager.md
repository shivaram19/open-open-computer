# THE 80/20 SPLIT: NATIVE GHL vs. CUSTOM ATTRIBUTION
## One-Pager for Stakeholder Demo

---

## THE PROBLEM

> "We spend $25,000/month on Meta and Google ads. We know we got 500 leads. But which **campaign**? Which **ad**? How many **enrolled**? What's the **ROAS**?"

**GHL's native reporting stops at "Leads by Source."** It cannot drill down to campaign level, cannot preserve first-touch attribution when leads return, and cannot calculate true CAC or ROAS per ad.

**Without this data, you're flying blind.** You cannot:
- Kill underperforming campaigns before they burn budget
- Double down on high-ROAS ads
- Coach sales teams with data on lead quality by source
- Prove marketing ROI to leadership

---

## THE SOLUTION: TWO LAYERS

```
+-------------------------------------------------------------+
|  LAYER 1: NATIVE GHL (80% of features, 0% custom code)      |
|                                                             |
|  * Lead capture forms with UTM tracking                     |
|  * 9-stage enrollment pipeline (New Lead -> Enrollment)     |
|  * Custom fields (FAFSA dates, program interest, lost reasons)|
|  * Email/SMS automation (appointment reminders, follow-ups)  |
|  * Appointment scheduling & check-in tracking               |
|  * Review request workflows                                 |
|  * Basic dashboard widgets                                  |
|                                                             |
|  SETUP TIME: 2-3 weeks | COST: GHL subscription only        |
+-------------------------------------------------------------+
                            |
                            |  <-- GHL API V2 + Webhooks
                            |
+-------------------------------------------------------------+
|  LAYER 2: CUSTOM ATTRIBUTION MIDDLEWARE (20% build)         |
|                                                             |
|  * First-touch attribution LOCK (prevents overwrite)        |
|  * Campaign -> Ad Set -> Ad -> Enrollment -> Revenue drill-down |
|  * CAC and ROAS per campaign/ad                             |
|  * Lead quality matrix (CPL vs. enrollment rate)            |
|  * Lost lead analysis by source, stage, and reason          |
|  * Daily sales reports (Call Center vs. Sales Manager)      |
|  * Marketing dashboard with channel breakdown               |
|                                                             |
|  BUILD TIME: 4-6 weeks | COST: $8K-15K one-time            |
+-------------------------------------------------------------+
```

---

## THE 80/20 RULE IN ACTION

| Aspect | Native GHL | Custom Middleware | Combined Impact |
|--------|-----------|-------------------|-----------------|
| **Lead capture** | 100% | 0% | Operational baseline |
| **Pipeline management** | 100% | 0% | Team workflow |
| **Email/SMS automation** | 100% | 0% | Engagement engine |
| **Appointment scheduling** | 100% | 0% | Show-up tracking |
| **Basic reporting** | 70% | 30% | Lead counts by source |
| **Campaign-level ROI** | 0% | **100%** | **Profit optimization** |
| **First-touch persistence** | 0% | **100%** | **Data integrity** |
| **Lead quality scoring** | 0% | **100%** | **Budget allocation** |
| **Lost lead analytics** | 20% | **80%** | **Conversion optimization** |
| **Daily sales accountability** | 30% | **70%** | **Team performance** |

**The 20% custom build unlocks 80% of the business value.**

---

## WHAT YOU GET: THE DASHBOARD

### View 1: Executive Summary
```
Period: August 2026

Marketing Spend:     $22,848
Total Leads:         500
Cost per Lead:       $45.70
Enrollments:         42 (8.4%)
Revenue:             $672,000
CAC:                 $544
ROAS:                29.4x
Lost Leads:          423 (84.6%)
```

### View 2: Channel Breakdown
```
Channel      Spend    Leads   CPL     Enroll   Revenue    CAC     ROAS
------------------------------------------------------------------------
Meta         $15,000  225     $66.67  18       $288,000   $833    19.2x
Google       $7,500   150     $50.00  15       $240,000   $500    32.0x
Referral     $0       50      $0.00   5        $75,000    $0      N/A
Organic      $0       75      $0.00   4        $69,000    $0      N/A
```

**Insight:** Google has lower CPL and higher ROAS than Meta. Reallocate 20% of Meta budget to Google.

### View 3: Campaign Drill-Down
```
Campaign: Summer Enrollment 2026 (Meta)
Spend: $8,000 | Leads: 120 | Enrollments: 12 | Revenue: $192,000 | ROAS: 24.0x

Ad Set                  Leads   Enroll   Revenue    ROAS
-----------------------------------------------------------
Lookalike 1%            72      9        $144,000   36.0x  <-- WINNER
Interest: Healthcare    48      3        $48,000    12.0x  <-- KILL
```

**Insight:** Lookalike 1% ad set has 3x the ROAS of interest targeting. Shift budget to lookalikes.

### View 4: Lead Quality Matrix
```
Campaign                  CPL     Enroll%   Rev/Lead   Quality
----------------------------------------------------------------
Google - Nursing Search   $55     12.0%     $1,800     9.8/10  <-- BEST
Meta - Lookalike 1%       $45     10.5%     $1,500     9.2/10
Meta - Interest Target    $60     4.2%      $500       5.1/10  <-- WORST
```

**Insight:** Cheap leads (Meta Interest, $60 CPL) that don't enroll are more expensive than expensive leads (Google, $55 CPL) that do.

### View 5: Lost Lead Analysis
```
Top Reasons for Lost Leads:
1. Price / No financing:     25.0% (106 leads, $1.6M potential revenue)
2. Program not suitable:     20.0% (85 leads)
3. Not eligible for funding: 15.0% (63 leads)
4. Schedule not suitable:    10.0% (42 leads)
5. Not ready to start:       10.0% (42 leads)

Stage with Most Losses: Consultation (26.7% of all lost leads)
```

**Insight:** 25% of lost leads cite price. Create a financing FAQ and train sales managers to address this objection earlier in the funnel.

### View 6: Daily Sales Report
```
Date: August 25, 2026

CALL CENTER:
Sarah Johnson     | 45 calls | 32 completed (20s+) | 8 appts | 5 check-ins | 62.5% show-up | 8 hrs
Mike Chen         | 38 calls | 28 completed          | 6 appts | 4 check-ins | 66.7% show-up | 7.5 hrs

SALES MANAGERS:
David Rodriguez   | 20 calls | 15 completed | 5 consultations | 2 FAFSA submitted | 1 enrollment | $15,000
Emily Thompson    | 25 calls | 20 completed | 6 consultations | 3 FAFSA submitted | 2 enrollments | $30,000
```

**Insight:** Emily Thompson has 2x the enrollment rate of David Rodriguez. Analyze her consultation approach and replicate.

---

## THE BUSINESS CASE

### Without Custom Attribution
- **Marketing budget allocation**: Based on gut feel, not data
- **Sales coaching**: Generic, not targeted to lead quality by source
- **Lead quality**: Unknown — all leads treated equally
- **ROI reporting**: "We spent $25K and got 500 leads" (so what?)
- **Decision speed**: Monthly reviews, reactive adjustments

### With Custom Attribution
- **Marketing budget allocation**: Reallocate from $60 CPL / 4% enroll campaigns to $55 CPL / 12% enroll campaigns
- **Sales coaching**: "Sarah, your Meta leads need earlier financing discussion. David, your Google leads are higher intent — close faster."
- **Lead quality**: Scored by revenue per lead, not just CPL
- **ROI reporting**: "We spent $25K, generated $672K revenue, 29.4x ROAS. Campaign X is the winner."
- **Decision speed**: Daily dashboard reviews, proactive optimization

### Expected Impact (Conservative)

| Metric | Before | After (6 months) | Improvement |
|--------|--------|------------------|-------------|
| Cost per Enrollment | $833 | $600 | -28% |
| Lead-to-Enrollment Rate | 6% | 9% | +50% |
| Marketing ROAS | 15x | 25x | +67% |
| Sales Team Productivity | Baseline | +20% | Data-driven coaching |

**At $25K/month ad spend, a 28% reduction in CAC = $84K saved per year.**
**A 50% improvement in lead-to-enrollment rate = 63 additional enrollments per year.**
**At $16K average deal value = $1M additional revenue per year.**

---

## THE INVESTMENT

| Component | Effort | Cost |
|-----------|--------|------|
| Native GHL setup (pipeline, fields, workflows) | 2-3 weeks | Internal team time |
| Custom Attribution Middleware | 4-6 weeks | $8K-15K (one-time) |
| Dashboard UI (embedded in GHL or standalone) | 2-3 weeks | Included in middleware |
| Data migration & team training | 1 week | Internal team time |
| **Total** | **7-10 weeks** | **$8K-15K + internal time** |

**Infrastructure:** $25-70/month (PostgreSQL + Redis + app server)

**ROI Timeline:** Break-even in 1-2 months from improved ad efficiency alone.

---

## NEXT STEPS

1. **Approve Phase 1**: Configure native GHL (pipeline, fields, workflows) — 2 weeks
2. **Approve Phase 2**: Build custom Attribution Middleware — 4-6 weeks
3. **Demo to team**: Show live dashboard with mock data — Week 3
4. **Go live**: Migrate existing leads, start tracking new leads — Week 8
5. **Optimize**: Weekly dashboard reviews, campaign adjustments — Ongoing

---

*"The 20% custom build is the difference between knowing you got leads and knowing which ad made you money."*
