# LIVE DEMO SCRIPT
## Marketing Attribution Dashboard
### Exact Click Paths, Talking Points, and Transitions

---

## PRE-DEMO SETUP (Do This 30 Minutes Before)

### Environment Check
- [ ] PostgreSQL running with mock data loaded (500 leads, 30 days)
- [ ] Redis running (session cache)
- [ ] Dashboard API server running on `localhost:3000` or deployed URL
- [ ] Dashboard frontend loaded in browser (Chrome/Edge, incognito mode)
- [ ] GHL account open in second tab (pipeline view, contact record)
- [ ] Mock Meta Ads Manager data visible (screenshot or test account)
- [ ] Google Ads data: MOCK data loaded in dashboard (see File 6)
- [ ] Second screen or projector connected and tested
- [ ] Demo data verified: 500 leads, 42 enrollments, $672K revenue, 29.4x ROAS

### Data Verification Query
```sql
-- Run this to verify demo data is loaded
SELECT 
  COUNT(*) as total_leads,
  COUNT(CASE WHEN o.status = 'won' THEN 1 END) as enrollments,
  SUM(CASE WHEN o.status = 'won' THEN o.monetary_value END) as revenue,
  SUM(mi.spend) + SUM(gi.cost_usd) as total_spend
FROM contacts c
LEFT JOIN opportunities o ON c.id = o.contact_id
CROSS JOIN (SELECT SUM(spend) as spend FROM meta_insights) mi
CROSS JOIN (SELECT SUM(cost_usd) as cost_usd FROM google_insights) gi;
```

Expected result: ~500 leads, ~42 enrollments, ~$672K revenue, ~$22.8K spend

---

## DEMO STRUCTURE (Total: 12-15 minutes)

| Section | Time | What You Show |
|---------|------|---------------|
| **1. The Hook** | 1 min | The problem: "We got 500 leads, but which ad made us money?" |
| **2. Native GHL** | 2 min | Pipeline, custom fields, workflows — the foundation |
| **3. The Gap** | 1 min | Show GHL's native report — it stops at "Leads by Source" |
| **4. The Solution** | 8-10 min | Custom dashboard: 6 views, live drill-downs |
| **5. The Ask** | 1 min | Investment, timeline, next steps |

---

## SECTION 1: THE HOOK (1 minute)

**Opening Line:**
> "We spend $25,000 a month on Meta and Google ads. Last month we got 500 leads. Here's what I can tell you from GHL right now: 225 came from Meta, 150 from Google, 50 from referrals, and 75 from organic."

**Click Path:**
1. Open GHL → Reports → Sources
2. Show the bar chart: Meta 225, Google 150, Referral 50, Organic 75

**The Pivot:**
> "But here's the question I cannot answer: Which **campaign** on Meta? Which **ad**? How many of those 225 leads actually **enrolled**? And how much **revenue** did that specific ad generate?"

**Pause. Let the silence land.**

> "Without that data, we're flying blind. We might be spending $8,000 on a Meta campaign that generates leads but zero enrollments, while a $5,000 Google campaign generates half the leads but twice the revenue."

---

## SECTION 2: NATIVE GHL — THE FOUNDATION (2 minutes)

**Narrative:**
> "Before I show you the solution, let me show you what GHL already does brilliantly. This is our operational engine — no custom code needed."

**Click Path 2A: The Pipeline**
1. Open GHL → Opportunities → Main Pipeline
2. Show the 9 stages: New Lead → Qualified → Appointment → Check-in → Consultation → FAFSA Applied → FAFSA Confirmed → Payment → Enrollment → Upsell
3. Drag a sample lead from "New Lead" to "Qualified"
4. Click on the lead card → show custom fields: Program Interest, Qualification Status, Deferred flag

**Talking Point:**
> "Every lead moves through these stages. At qualification, the manager marks them qualified or not qualified, selects the program they're interested in, and notes if they're deferred."

**Click Path 2B: Appointment & Check-in**
1. Click on an "Appointment" stage lead
2. Show the appointment details: Date, Time, Program, Assigned Employee
3. Show the "Check-in" custom field: Yes/No toggle
4. Show the show-up rate calculation in a custom field

**Talking Point:**
> "When a lead books an appointment, we record the date, program, and assigned employee. When they show up, we mark check-in. This gives us show-up rate by employee and by source."

**Click Path 2C: Enrollment / Deal Close**
1. Click on an "Enrollment" stage lead
2. Show the opportunity value: $15,000
3. Show custom fields: Enrolled Program, Payment Method (FAFSA/Grant/Out-of-pocket), Grant Amount

**Talking Point:**
> "When a lead enrolls, we record the actual program they joined, how they're paying, and the deal value. This is the revenue data we need for ROI calculation."

**Click Path 2D: Email/SMS Automation**
1. Open GHL → Automation → Workflows
2. Show: "Appointment Confirmation" workflow (triggers on appointment booked)
3. Show: "FAFSA Follow-up" workflow (triggers 3 days after FAFSA submitted)
4. Show: "Review Request" workflow (triggers 30 days after enrollment)

**Talking Point:**
> "All our communication is automated. Appointment confirmations, FAFSA reminders, review requests — all triggered by pipeline stage changes. No manual work."

**Transition:**
> "So GHL handles our entire operational workflow. But when it comes to understanding which marketing channel, campaign, or ad actually drove the enrollment and revenue — GHL hits a wall."

---

## SECTION 3: THE GAP (1 minute)

**Click Path:**
1. Open GHL → Reports → Sources (again)
2. Hover over Meta bar: "225 leads"
3. Try to click for drill-down: **Nothing happens**
4. Open GHL → Reports → Opportunities
5. Filter by "Won" status
6. Try to filter by source + campaign: **No campaign filter available**

**Narrative:**
> "GHL tells me I got 225 leads from Meta. But I cannot click through to see which campaign. I cannot see how many of those 225 enrolled. I cannot see the revenue. And here's the critical part:"

**Click Path 3B: The Attribution Overwrite Problem**
1. Open a contact record that came from Meta
2. Show the UTM parameters: `utm_source=meta`, `utm_campaign=summer_enrollment`
3. Explain: "This lead clicked our Meta ad on August 1st."
4. Now show: The same lead visited again on August 5th from Google search
5. Show: GHL has overwritten the UTM data. Now it says `utm_source=google`, `utm_campaign=organic_search`

**Talking Point:**
> "GHL overwrites the original source when the lead returns. So our 'Meta' lead is now recorded as 'Google.' We lost the true origin. This means our source reporting is inaccurate — we don't know where leads actually came from."

**The Punchline:**
> "This is why we built the custom Attribution Middleware. It captures the first touch — the original source, campaign, ad, keyword — and locks it. Forever."

---

## SECTION 4: THE SOLUTION — CUSTOM DASHBOARD (8-10 minutes)

**Transition:**
> "Let me show you what the custom dashboard looks like. This is the 20% build that unlocks 80% of the value."

**Open the dashboard in a new tab. Full screen.**

---

### VIEW 1: EXECUTIVE SUMMARY (1.5 minutes)

**Click Path:**
1. Dashboard loads on "Executive Summary" view by default
2. Date range: August 1-31, 2026 (pre-selected)

**What They See:**
```
Period: August 2026

Marketing Spend:     $22,848
Total Leads:         500
Cost per Lead:       $45.70
Appointments:        190 (38.0%)
Check-ins:           133 (70.0% show-up)
Consultations:       121
Enrollments:         42 (8.4%)
Revenue:             $672,000
Average Deal Value:  $16,000
CAC:                 $544
ROAS:                29.4x
Lost Leads:          423 (84.6%)
```

**Talking Points:**
- "In August, we spent $22,848 and generated $672,000 in revenue. That's a 29.4x return on ad spend."
- "Our cost per lead is $45.70, but our cost per enrollment is $544. That's the number that matters."
- "84.6% of leads are lost — but now we know exactly where and why. I'll show you that in a moment."
- "The trend chart shows daily leads, enrollments, and revenue. You can see spikes after campaign launches."

**Interaction:**
- Hover over the trend chart: "August 15th — we launched the Google Nursing campaign. Leads jumped from 12 to 28, and enrollments followed 10 days later."
- Change date range to "Last 7 Days" → watch numbers update in real-time

---

### VIEW 2: CHANNEL BREAKDOWN (1.5 minutes)

**Click Path:**
1. Click "Channel Breakdown" tab

**What They See:**
```
Channel      Spend    Leads   CPL     Appts   Check-ins  Enroll   Revenue    CAC     ROAS
--------------------------------------------------------------------------------------------
Meta         $15,000  225     $66.67  86      60         18       $288,000   $833    19.2x
Google       $7,500   150     $50.00  68      52         15       $240,000   $500    32.0x
Referral     $0       50      $0.00   20      16         5        $75,000    $0      N/A
Organic      $0       75      $0.00   16      5          4        $69,000    $0      N/A
```

**Talking Points:**
- "Meta generated the most leads — 225 — but at $66.67 per lead. Google generated 150 leads at $50 per lead."
- "But look at ROAS: Google is 32.0x, Meta is 19.2x. Google leads are more valuable."
- "Referral leads are free and have a 10% enrollment rate — our highest. We should invest more in the referral program."
- "Organic search leads have low show-up rate — only 31%. We need better landing page messaging to pre-qualify these leads."

**Interaction:**
- Click on "Meta" row → drills down to Meta campaigns
- "Let me show you which Meta campaigns are working."

---

### VIEW 3: CAMPAIGN DRILL-DOWN (2 minutes)

**Click Path:**
1. Already drilled into Meta from Channel Breakdown
2. Show Meta campaigns list

**What They See:**
```
Campaign: Summer Enrollment 2026
Spend: $8,000 | Leads: 120 | Enrollments: 12 | Revenue: $192,000 | ROAS: 24.0x

Ad Set                  Leads   Enroll   Revenue    ROAS
-----------------------------------------------------------
Lookalike 1%            72      9        $144,000   36.0x  [GREEN]
Interest: Healthcare    48      3        $48,000    12.0x  [YELLOW]
```

**Talking Points:**
- "The 'Summer Enrollment' campaign spent $8,000 and generated $192,000 — 24x ROAS."
- "But look at the ad sets: Lookalike 1% has a 36x ROAS. Interest targeting has only 12x."
- "The Lookalike ad set is 3x more profitable. We should shift budget from Interest to Lookalike."
- "If we reallocate $2,000 from Interest to Lookalike, we project an additional $48,000 in revenue next month."

**Interaction:**
- Click on "Lookalike 1%" ad set → shows individual ads

**What They See:**
```
Ad: Video V1 - Student Testimonial
Spend: $5,000 | Leads: 50 | Enrollments: 7 | Revenue: $112,000 | ROAS: 22.4x | Placement: facebook_feed

Ad: Carousel - Program Highlights
Spend: $3,000 | Leads: 22 | Enrollments: 2 | Revenue: $32,000 | ROAS: 10.7x | Placement: instagram_feed
```

**Talking Point:**
- "The video testimonial on Facebook Feed is our best performer. The carousel on Instagram Feed is weaker. We should create more video testimonials and test them on Instagram Reels."

**Interaction:**
- Click back to Campaign view
- Switch platform filter to "Google"
- Show Google campaign drill-down

**What They See:**
```
Campaign: Search - Nursing Programs
Spend: $5,000 | Leads: 80 | Enrollments: 10 | Revenue: $160,000 | ROAS: 32.0x

Keyword                           CPL     Enroll%   Rev/Lead
-------------------------------------------------------------
"nursing school near me"          $48     15.0%     $2,000
"practical nursing program"       $52     12.5%     $1,800
"how to become a nurse"           $65     8.0%      $1,200
```

**Talking Point:**
- "Google Search 'nursing school near me' has a 15% enrollment rate and $2,000 revenue per lead. 'How to become a nurse' has only 8% enrollment. We should increase bids on the high-intent keywords and reduce bids on the research-phase keywords."

---

### VIEW 4: LEAD QUALITY MATRIX (1.5 minutes)

**Click Path:**
1. Click "Lead Quality" tab

**What They See:**
```
Campaign                  CPL     Enroll%   Rev/Lead   Quality Score
--------------------------------------------------------------------
Google - Nursing Search   $55     12.0%     $1,800     9.8/10  [GREEN]
Meta - Lookalike 1%       $45     10.5%     $1,500     9.2/10  [GREEN]
Meta - Fall Early Bird    $50     9.0%      $1,350     8.5/10  [GREEN]
Google - Medical Assistant $58    8.5%      $1,200     7.8/10  [YELLOW]
Meta - Interest: Healthcare $60   4.2%      $500       5.1/10  [RED]
Meta - Careers Fair       $75     3.0%      $400       4.2/10  [RED]
```

**Talking Points:**
- "This is the most important view for budget allocation. It shows not just cost per lead, but quality per lead."
- "Meta Interest targeting has a $60 CPL — not terrible. But only 4.2% enroll, and revenue per lead is $500. Compare that to Google Nursing at $55 CPL, 12% enroll, $1,800 revenue per lead."
- "The 'Careers Fair' campaign has a $75 CPL and 3% enrollment. That's $2,500 per enrollment. We should pause this campaign immediately."
- "The Quality Score combines CPL, enrollment rate, and revenue into a single number. Anything below 6.0 should be reviewed for pausing or optimization."

**Interaction:**
- Sort by Quality Score (descending) → best campaigns at top
- Sort by CPL (ascending) → cheap campaigns at top, but notice the quality disconnect
- "See? Cheap CPL does not equal good ROI."

---

### VIEW 5: LOST LEAD ANALYSIS (1.5 minutes)

**Click Path:**
1. Click "Lost Leads" tab

**What They See:**
```
Summary:
Total Lost: 423 (84.6%)
Potential Revenue Lost: $6.3M

By Source:
Meta:     212 lost (50.1%)  [RED segment]
Google:   127 lost (30.0%)  [YELLOW segment]
Referral: 42 lost (9.9%)    [GREEN segment]
Organic:  42 lost (9.9%)    [GREEN segment]

By Stage:
Consultation:     113 lost (26.7%)  <-- BIGGEST DROP-OFF
New Lead:         73 lost (17.3%)
Appointment:      65 lost (15.4%)
Qualified:        55 lost (13.0%)
FAFSA Applied:    42 lost (9.9%)
Check-in:         42 lost (9.9%)
Payment:          21 lost (5.0%)
FAFSA Confirmed:  12 lost (2.8%)

By Reason:
Price / No financing:     106 (25.0%)
Program not suitable:     85 (20.0%)
Not eligible for funding: 63 (15.0%)
Schedule not suitable:    42 (10.0%)
Not ready to start:       42 (10.0%)
Not responding:           32 (7.6%)
Chose another school:     21 (5.0%)
FAFSA not approved:       11 (2.6%)
Changed mind:             11 (2.6%)
Other:                    11 (2.6%)
```

**Talking Points:**
- "423 leads were lost — that's $6.3M in potential revenue. But now we know exactly why."
- "The biggest drop-off is at Consultation — 26.7% of all lost leads. This is our biggest optimization opportunity."
- "The #1 reason for loss is price/financing — 25%. We need to address financing earlier in the funnel, not wait until consultation."
- "The #2 reason is program not suitable — 20%. We need better pre-qualification on our landing pages and forms."
- "Compare Meta vs. Google lost reasons: Meta has 30% 'not responding' vs. Google has 12%. Meta leads go cold faster — we need faster follow-up for Meta leads."

**Interaction:**
- Filter by source = "Meta" → show Meta-specific lost reasons
- Filter by stage = "Consultation" → show consultation lost reasons
- "See? When we filter to consultation stage, price jumps to 35%. This tells us our sales managers need better financing objection handling."

---

### VIEW 6: DAILY SALES REPORT (1.5 minutes)

**Click Path:**
1. Click "Daily Sales" tab
2. Date selector: August 25, 2026 (pre-selected)

**What They See:**
```
Date: August 25, 2026

CALL CENTER:
Name              Calls  Completed(20s+)  Appts  Check-ins  Show-up%  Hours
--------------------------------------------------------------------------------
Sarah Johnson     45     32               8      5          62.5%     8.0
Mike Chen         38     28               6      4          66.7%     7.5
Jessica Williams  42     30               7      5          71.4%     8.0

SALES MANAGERS:
Name              Calls  Completed  Consults  FAFSA Sub  FAFSA Conf  Enroll  Sales
-------------------------------------------------------------------------------------
David Rodriguez   20     15         5         2          1           1       $15,000
Emily Thompson    25     20         6         3          2           2       $30,000
James Park        18     14         4         2          1           1       $16,000
```

**Talking Points:**
- "This is our daily accountability view. Every morning, the team sees yesterday's numbers."
- "Call Center: Sarah made 45 calls, booked 8 appointments, 5 showed up. 62.5% show-up rate."
- "Sales Managers: Emily had 6 consultations, 2 FAFSA submissions, 2 enrollments, $30,000 in sales. She's our top performer today."
- "Jessica has the highest show-up rate at 71.4%. We should ask her what she's saying differently in her appointment confirmation calls."
- "James Park has fewer calls but the same enrollment rate. He's more efficient — maybe he needs more leads."

**Interaction:**
- Change date to previous day → show different numbers
- Click on "Sarah Johnson" → shows her 7-day trend
- "Sarah's show-up rate has dropped from 75% to 62.5% over the last 3 days. Let's check if there's a scheduling issue or if her confirmation script changed."

---

## SECTION 5: THE ASK (1 minute)

**Transition:**
> "So that's the full picture. GHL handles our operations. The custom middleware handles our intelligence. Together, they answer the question: 'Which ad made us money?'"

**The Investment Slide:**
```
PHASE 1: Native GHL Setup (2-3 weeks)
- Pipeline, custom fields, workflows, templates
- Cost: Internal team time + GHL subscription

PHASE 2: Custom Attribution Middleware (4-6 weeks)
- First-touch capture, Meta API integration, dashboard
- Cost: $8,000-15,000 one-time development
- Infrastructure: $25-70/month

PHASE 3: Team Training & Go-Live (1 week)
- Dashboard training, process documentation
- Cost: Internal team time

TOTAL: 7-10 weeks | $8K-15K | $25-70/month
```

**The ROI Pitch:**
> "At $25K monthly ad spend, if this dashboard helps us reallocate just 20% of budget from low-ROAS campaigns to high-ROAS campaigns, we save $60K per year in wasted spend."
> "If we improve lead-to-enrollment rate by 2 percentage points — from 8% to 10% — that's 10 additional enrollments per month. At $16K per enrollment, that's $160K additional revenue per month."
> "This pays for itself in the first month."

**The Ask:**
> "I need approval to start Phase 1 this week. We can have the pipeline and custom fields configured in 2 weeks. Then we start building the middleware."
> "Who has questions?"

---

## ANTICIPATED QUESTIONS & ANSWERS

**Q: "Why can't GHL just build this?"**
A: "GHL is a general-purpose CRM. Campaign-level attribution with ad spend integration requires access to Meta and Google APIs, custom data warehousing, and complex attribution logic. This is outside GHL's product scope. Agencies build this as a custom layer on top."

**Q: "What if Meta or Google changes their API?"**
A: "We use the latest stable API versions (Meta v25, Google v24) and monitor deprecation notices. The middleware is designed with adapter patterns — if an API changes, we update the adapter, not the entire system. Typical API maintenance is 2-4 hours per quarter."

**Q: "How accurate is the attribution?"**
A: "We use first-touch attribution — 100% credit to the first interaction. This is the most conservative model and best for understanding acquisition channels. We can also add last-touch and linear models later for comparison."

**Q: "What about leads who call instead of filling out forms?"**
A: "We can integrate call tracking (CallRail, CallTrackingMetrics) to capture the source of phone leads. The middleware can match phone numbers to campaigns. This is a Phase 2 enhancement."

**Q: "Can we see this data inside GHL instead of a separate dashboard?"**
A: "Yes — two options. Option 1: Embed the dashboard as a custom iframe inside GHL. Option 2: Build GHL Custom Menu links that open the dashboard in a new tab. Both give the team one-click access without leaving GHL."

**Q: "What happens to our existing leads?"**
A: "We backfill first-touch data where possible using GHL's existing UTM history. For leads where UTM data is missing, we mark them as 'Unknown Source' and start tracking new leads from Day 1. Historical trends will be partial for the first 30 days, then fully accurate."

**Q: "Who maintains this after it's built?"**
A: "The system is designed to be self-maintaining. Daily sync jobs run automatically. API token refresh is automated. Alerts notify us if any sync fails. A junior developer or tech-savvy operations person can handle 95% of maintenance. For major changes, we budget 4-8 hours per quarter."

---

## POST-DEMO CHECKLIST

- [ ] Collect feedback: What resonated? What concerns?
- [ ] Identify the decision-maker and their criteria
- [ ] Schedule follow-up: Technical deep-dive with IT/ops team?
- [ ] Send one-pager PDF within 24 hours
- [ ] Share dashboard demo link (if hosted) for self-exploration
- [ ] Set deadline for Phase 1 approval
