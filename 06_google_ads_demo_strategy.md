# GOOGLE ADS API: DEMO STRATEGY
## How to Handle Google Ads Integration for the Demo

---

## THE PROBLEM

Google Ads API requires:
1. **Developer Token** — Apply via Google Ads Manager Account (takes days to weeks)
2. **Manager Account (MCC)** — Required to access client accounts
3. **OAuth 2.0 Setup** — Client ID, secret, refresh token
4. **API Access Level** — "Test Accounts" vs "Basic Access" vs "Standard Access"

**For a demo, you cannot wait 2-4 weeks for Google approval.**

---

## SOLUTION OPTIONS (Ranked by Demo Impact)

### OPTION 1: MOCK Google Ads Data in Dashboard (RECOMMENDED)
**Best for:** Stakeholder demos where the focus is on the attribution concept, not live API integration

**Approach:**
- Generate realistic Google Ads data using the mock data generator (File 3)
- Load it into the dashboard alongside live Meta data
- Label Google data as "Simulated" or "Demo Data" with a toggle
- Focus the live integration demo on Meta only

**Pros:**
- Zero Google API setup time
- Instant demo readiness
- Full dashboard functionality (all 6 views work)
- No risk of API errors during demo
- Can show both Meta and Google side-by-side

**Cons:**
- Cannot demonstrate live Google Ads API pull
- Stakeholders may ask "Is this real?" (answer: "Meta is live, Google is simulated based on typical performance data")

**Implementation:**
```javascript
// Dashboard config
const DEMO_MODE = {
  meta: "live",      // Pull from Meta Marketing API
  google: "mock",    // Use pre-generated mock data
  labelMockData: true // Show "Demo Data" badge on Google sections
};

// In the UI, add a small badge:
// "Google data: Simulated for demo | Meta data: Live from API"
```

**Demo Script Adjustment:**
> "For this demo, the Meta data is live from our ad account. The Google data is simulated based on our typical Google Search performance — $50 CPL, 12% enrollment rate, 32x ROAS. Once we get Google API approval, this switches to live data automatically."

---

### OPTION 2: Google Ads API Test Account
**Best for:** Technical demos where you want to show live API integration

**Approach:**
1. Create a Google Ads **Test Account** (https://ads.google.com/aw/billing/summary)
2. Apply for a Developer Token with "Test Accounts" access level
3. Create dummy campaigns in the test account
4. Pull data from the test account via API

**Pros:**
- Shows live API integration working
- No real ad spend required
- Can demonstrate the full technical stack

**Cons:**
- Test account token has limited access (cannot access production data)
- Dummy campaigns have no real performance data
- Still requires Google approval (may take 3-7 days)
- Test account data looks fake (0 impressions, 0 clicks unless you run test ads)

**Steps to Set Up:**
```
1. Go to https://ads.google.com/aw/billing/summary
2. Click "Create Test Account" (requires existing Google Ads account)
3. Create a dummy campaign (Search campaign, any keywords, $1/day budget)
4. Apply for Developer Token at: https://ads.google.com/aw/apicenter
5. Select "Test Account Token" access level
6. Wait for approval (typically 3-7 business days)
7. Set up OAuth 2.0 credentials in Google Cloud Console
8. Use test account Customer ID in API calls
```

**API Call Example (Test Account):**
```python
from google.ads.googleads.client import GoogleAdsClient

# Test account credentials
client = GoogleAdsClient.load_from_dict({
    "developer_token": "YOUR_TEST_TOKEN",
    "client_id": "YOUR_OAUTH_CLIENT_ID",
    "client_secret": "YOUR_OAUTH_CLIENT_SECRET",
    "refresh_token": "YOUR_REFRESH_TOKEN",
    "login_customer_id": "YOUR_MANAGER_ACCOUNT_ID",
    "use_proto_plus": True
})

# Query test account
ga_service = client.get_service("GoogleAdsService")
stream = ga_service.search_stream(
    customer_id="123-456-7890",  # Test account customer ID
    query="SELECT campaign.id, campaign.name, metrics.clicks FROM campaign"
)
```

**Demo Script Adjustment:**
> "This is our Google Ads test account. The campaigns are dummy campaigns, but the API integration is live. When we get Basic Access approval, we switch the Customer ID to our production account and all this data becomes real."

---

### OPTION 3: Google Ads API Basic Access (Production)
**Best for:** Post-demo, production implementation

**Approach:**
1. Apply for Developer Token with "Basic Access" level
2. Submit application with business justification
3. Wait for approval (typically 1-2 weeks, sometimes longer)
4. Once approved, access production campaign data

**Application Requirements:**
- Business website
- Explanation of API use case ("Marketing attribution dashboard for education enrollment tracking")
- Estimated API call volume ("500-1000 requests per day")
- Link to your application/privacy policy

**Pros:**
- Access to real production data
- Full functionality
- No demo limitations

**Cons:**
- 1-2 week approval delay (too slow for demo)
- Requires Manager Account with production access
- Google may reject applications without clear business justification

**Timeline:**
```
Day 1:   Apply for Developer Token (Basic Access)
Day 3-7:  Google reviews application
Day 7-14: Approval granted (or rejected with feedback)
Day 14+:  Integrate production data
```

---

## RECOMMENDED DEMO STRATEGY

### Phase 1: The Demo (This Week)
**Use Option 1: Mock Google Ads Data + Live Meta Data**

```
Dashboard View:
+------------------+------------------+
|   META (LIVE)    |  GOOGLE (MOCK)   |
|                  |  [Demo Data]     |
|  Real campaign   |  Simulated based |
|  data from API   |  on historical   |
|                  |  performance     |
+------------------+------------------+
```

**What to say:**
> "The Meta side is live — this is our actual ad account data. The Google side is simulated based on our typical Google Search performance. The architecture supports both; we just need Google API approval to flip the switch."

**What to show:**
- Live Meta campaign drill-down (real data)
- Simulated Google campaign drill-down (mock data)
- Side-by-side comparison (Meta vs. Google)
- The attribution engine working with Meta data

### Phase 2: Post-Demo (Week 2-3)
**Apply for Google Ads API access in parallel with Phase 1 GHL setup**

```
Week 1: Demo with mock Google data
Week 2: Apply for Google Developer Token (Basic Access)
Week 3: Continue GHL native setup while waiting for Google approval
Week 4: Google approval expected; begin integration
Week 5: Full live integration (Meta + Google)
```

### Phase 3: Production (Week 6-8)
**Both Meta and Google APIs live, real data flowing**

---

## GOOGLE ADS API TEST MODE: TECHNICAL DETAILS

### Test Account vs. Production Account

| Feature | Test Account | Production Account |
|---------|-------------|-------------------|
| Real ad spend | No | Yes |
| Real performance data | No (unless you run test ads) | Yes |
| API access | Yes (with Test Account token) | Yes (with Basic/Standard token) |
| Approval time | Instant | 1-2 weeks |
| Data volume | Minimal | Full |
| Cost to run | $0 (or minimal for test ads) | Normal ad spend |

### Test Account Limitations
- Cannot access production account data
- Test account token cannot be upgraded to Basic Access
- Must create separate production integration later
- Test ads may not serve (no auction participation)

### Mock Data vs. Test Account: Decision Matrix

| Factor | Mock Data | Test Account |
|--------|-----------|--------------|
| Setup time | 1 hour | 3-7 days |
| Demo realism | High (based on real benchmarks) | Low (dummy campaigns) |
| Technical proof | Medium (shows architecture) | High (shows live API) |
| Stakeholder impressiveness | High (realistic numbers) | Medium (empty campaigns) |
| Post-demo utility | High (becomes real with API swap) | Low (must rebuild for production) |
| **RECOMMENDATION** | **USE THIS** | Skip for now |

---

## MOCK GOOGLE ADS DATA SPECIFICATION

The mock data generator (File 3) creates realistic Google Ads data based on these benchmarks:

### Campaign Structure
```
Campaign: Search - Nursing Programs
  Budget: $5,000/month
  Channel: SEARCH

  Ad Group: Nursing Keywords - Exact
    Keyword: "nursing school near me" (Exact match)
      Avg CPC: $4.80
      CTR: 6.2%
      Quality Score: 8

    Keyword: "practical nursing program" (Exact match)
      Avg CPC: $5.20
      CTR: 5.8%
      Quality Score: 9

  Ad Group: Nursing Keywords - Phrase
    Keyword: "how to become a nurse" (Phrase match)
      Avg CPC: $3.50
      CTR: 4.1%
      Quality Score: 7

    Keyword: "nursing certification" (Phrase match)
      Avg CPC: $4.10
      CTR: 3.8%
      Quality Score: 6
```

### Performance Benchmarks Used

| Metric | Value | Source |
|--------|-------|--------|
| Search Impression Share | 45-85% | Typical for education keywords |
| Quality Score | 5-10 | Based on keyword relevance |
| CTR (Search) | 3-8% | Healthcare education industry |
| Avg CPC (Nursing) | $4-6 | Google Ads benchmark data |
| Conversion Rate | 6-15% | Landing page dependent |
| Cost per Conversion | $35-65 | For lead generation campaigns |

### Search Term Report (Mock)
```
Search Term                    Clicks  Cost     Conv    Match Type
------------------------------------------------------------------
nursing school near me         45      $216     7       Exact
practical nursing program      32      $166     5       Exact
how to become a nurse          28      $98      3       Phrase
lpn programs near me           22      $110     4       Broad
nursing schools in [city]      18      $86      2       Broad
best nursing programs          15      $72      1       Broad
```

---

## POST-DEMO: GOOGLE ADS API INTEGRATION CHECKLIST

### Week 2: Application
- [ ] Create Google Ads Manager Account (if not existing)
- [ ] Apply for Developer Token at https://ads.google.com/aw/apicenter
- [ ] Select "Basic Access" level
- [ ] Submit business justification document
- [ ] Create Google Cloud Project for OAuth credentials
- [ ] Configure OAuth consent screen
- [ ] Generate OAuth 2.0 Client ID and Secret

### Week 3-4: Waiting Period
- [ ] Monitor email for Google approval/rejection
- [ ] Prepare fallback: Test Account integration (if Basic Access delayed)
- [ ] Continue Meta API integration (no dependencies)

### Week 5: Integration
- [ ] Receive Developer Token approval
- [ ] Generate refresh token via OAuth flow
- [ ] Update middleware config with production credentials
- [ ] Test API connection with small query
- [ ] Validate data accuracy against Google Ads UI
- [ ] Enable daily sync job for Google insights

### Week 6: Validation
- [ ] Compare dashboard numbers to Google Ads UI (spot check 3 campaigns)
- [ ] Verify attribution matching (5-10 enrollments traced back to Google campaigns)
- [ ] Test date range queries (last 7 days, last 30 days, custom range)
- [ ] Monitor API quota usage

---

## GOOGLE ADS API DEPRECATION EXCLUSIONS (2026)

**DO NOT USE in integration:**
- Smart Campaign creation via API (support ends Aug 3, 2026)
- v23 and earlier for Performance Max channel reporting
- `MIXED` enum for Performance Max placements

**USE v24 FOR:**
- All new integrations
- Performance Max channel reporting (for dates on/after June 1, 2025)
- Lead generation conversion type enumerations
- VTC optimization for Demand Gen and App campaigns

---

## SUMMARY

| Approach | Setup Time | Demo Readiness | Production Path | Recommendation |
|----------|-----------|----------------|-----------------|----------------|
| Mock Data | 1 hour | Immediate | Swap to live API later | **USE FOR DEMO** |
| Test Account | 3-7 days | Medium | Must rebuild for production | Skip |
| Basic Access | 1-2 weeks | N/A (post-demo) | Direct production path | Apply in parallel |

**Recommended Path:**
1. **Demo this week**: Use mock Google data + live Meta data
2. **Week 2**: Apply for Google Ads API Basic Access
3. **Week 5-6**: Integrate live Google data after approval
4. **Ongoing**: Both platforms live, full attribution working
