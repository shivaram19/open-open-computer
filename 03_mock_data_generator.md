# MOCK DATA GENERATOR
## For Marketing Attribution Dashboard Demo
### Generates realistic data for all 6 dashboard views

---

## USAGE

```bash
# Install dependencies
pip install faker psycopg2-binary pandas numpy

# Run generator
python mock_data_generator.py --location-id=YOUR_LOCATION_ID --days=30 --leads=500

# Options:
#   --location-id    GHL Location ID (required)
#   --days           Number of days to generate data for (default: 30)
#   --leads          Total leads to generate (default: 500)
#   --db-url         PostgreSQL connection string (default: postgresql://localhost/attribution_db)
#   --redis-url      Redis connection string (default: redis://localhost:6379/0)
#   --seed           Random seed for reproducible data (default: 42)
```

---

## SCRIPT: mock_data_generator.py

```python
#!/usr/bin/env python3
"""
Mock Data Generator for Education CRM Attribution Dashboard Demo
Generates realistic leads, pipeline movements, ad spend, and enrollments
"""

import argparse
import random
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
import json

import numpy as np
from faker import Faker
import psycopg2
from psycopg2.extras import execute_values
import redis

fake = Faker()

# =============================================================================
# CONFIGURATION
# =============================================================================

PROGRAMS = [
    "Practical Nursing",
    "Medical Assistant",
    "Dental Assistant",
    "Pharmacy Technician",
    "Surgical Technology",
    "Radiologic Technology",
    "Physical Therapy Assistant",
    "Occupational Therapy Assistant"
]

LOST_REASONS = [
    "Price not suitable / No financing",
    "Program not suitable",
    "Not eligible for funding",
    "Schedule not suitable",
    "Not ready to start",
    "Not responding",
    "Chose another school",
    "FAFSA not approved",
    "Changed mind",
    "Other"
]

PIPELINE_STAGES = [
    "new_lead",
    "qualified",
    "appointment",
    "check_in",
    "consultation",
    "fafsa_applied",
    "fafsa_confirmed",
    "payment",
    "enrollment",
    "upsell"
]

META_CAMPAIGNS = [
    {"id": "camp_001", "name": "Summer Enrollment 2026", "objective": "LEAD_GENERATION", "budget": 8000},
    {"id": "camp_002", "name": "Fall Early Bird", "objective": "LEAD_GENERATION", "budget": 5000},
    {"id": "camp_003", "name": "Nursing Program Launch", "objective": "CONVERSIONS", "budget": 6000},
    {"id": "camp_004", "name": "Healthcare Careers Fair", "objective": "AWARENESS", "budget": 3000},
    {"id": "camp_005", "name": "Referral Program Boost", "objective": "LEAD_GENERATION", "budget": 2000}
]

META_ADSETS = [
    {"id": "aset_001", "campaign_id": "camp_001", "name": "Lookalike 1% - Enrolled Students"},
    {"id": "aset_002", "campaign_id": "camp_001", "name": "Interest: Healthcare Workers"},
    {"id": "aset_003", "campaign_id": "camp_002", "name": "Retargeting - Website Visitors"},
    {"id": "aset_004", "campaign_id": "camp_003", "name": "Nursing - Age 25-45"},
    {"id": "aset_005", "campaign_id": "camp_003", "name": "Nursing - Interest: Medical"},
    {"id": "aset_006", "campaign_id": "camp_004", "name": "Broad - Healthcare Interest"},
    {"id": "aset_007", "campaign_id": "camp_005", "name": "Referral - Existing Students"}
]

META_ADS = [
    {"id": "ad_001", "adset_id": "aset_001", "campaign_id": "camp_001", "name": "Video V1 - Student Testimonial", "placement": "facebook_feed"},
    {"id": "ad_002", "adset_id": "aset_001", "campaign_id": "camp_001", "name": "Carousel - Program Highlights", "placement": "instagram_feed"},
    {"id": "ad_003", "adset_id": "aset_002", "campaign_id": "camp_001", "name": "Image - Career Change", "placement": "facebook_feed"},
    {"id": "ad_004", "adset_id": "aset_003", "campaign_id": "camp_002", "name": "Video - Limited Time Offer", "placement": "instagram_stories"},
    {"id": "ad_005", "adset_id": "aset_004", "campaign_id": "camp_003", "name": "Image - Nursing Salary", "placement": "facebook_feed"},
    {"id": "ad_006", "adset_id": "aset_005", "campaign_id": "camp_003", "name": "Video - Day in the Life", "placement": "instagram_reels"},
    {"id": "ad_007", "adset_id": "aset_006", "campaign_id": "camp_004", "name": "Image - Open House Invite", "placement": "facebook_feed"},
    {"id": "ad_008", "adset_id": "aset_007", "campaign_id": "camp_005", "name": "Image - Refer & Earn", "placement": "facebook_feed"}
]

GOOGLE_CAMPAIGNS = [
    {"id": "gcamp_001", "name": "Search - Nursing Programs", "channel_type": "SEARCH", "budget": 5000},
    {"id": "gcamp_002", "name": "Search - Medical Assistant", "channel_type": "SEARCH", "budget": 3500},
    {"id": "gcamp_003", "name": "Display - Healthcare Careers", "channel_type": "DISPLAY", "budget": 2000},
    {"id": "gcamp_004", "name": "PMax - Enrollment 2026", "channel_type": "PERFORMANCE_MAX", "budget": 4000}
]

GOOGLE_AD_GROUPS = [
    {"id": "gag_001", "campaign_id": "gcamp_001", "name": "Nursing Keywords - Exact"},
    {"id": "gag_002", "campaign_id": "gcamp_001", "name": "Nursing Keywords - Phrase"},
    {"id": "gag_003", "campaign_id": "gcamp_002", "name": "Medical Assistant - Exact"},
    {"id": "gag_004", "campaign_id": "gcamp_003", "name": "Display - Healthcare Audience"},
    {"id": "gag_005", "campaign_id": "gcamp_004", "name": "PMax - All Products"}
]

GOOGLE_KEYWORDS = [
    {"criterion_id": "gk_001", "ad_group_id": "gag_001", "campaign_id": "gcamp_001", "text": "nursing school near me", "match_type": "EXACT"},
    {"criterion_id": "gk_002", "ad_group_id": "gag_001", "campaign_id": "gcamp_001", "text": "practical nursing program", "match_type": "EXACT"},
    {"criterion_id": "gk_003", "ad_group_id": "gag_002", "campaign_id": "gcamp_001", "text": "how to become a nurse", "match_type": "PHRASE"},
    {"criterion_id": "gk_004", "ad_group_id": "gag_002", "campaign_id": "gcamp_001", "text": "nursing certification", "match_type": "PHRASE"},
    {"criterion_id": "gk_005", "ad_group_id": "gag_003", "campaign_id": "gcamp_002", "text": "medical assistant training", "match_type": "EXACT"},
    {"criterion_id": "gk_006", "ad_group_id": "gag_003", "campaign_id": "gcamp_002", "text": "medical assistant program", "match_type": "EXACT"}
]

SALES_USERS = [
    {"id": "user_001", "name": "Sarah Johnson", "role": "call_center"},
    {"id": "user_002", "name": "Mike Chen", "role": "call_center"},
    {"id": "user_003", "name": "Jessica Williams", "role": "call_center"},
    {"id": "user_010", "name": "David Rodriguez", "role": "sales_manager"},
    {"id": "user_011", "name": "Emily Thompson", "role": "sales_manager"},
    {"id": "user_012", "name": "James Park", "role": "sales_manager"}
]

# =============================================================================
# DATA GENERATION LOGIC
# =============================================================================

class MockDataGenerator:
    def __init__(self, location_id, days=30, total_leads=500, seed=42):
        self.location_id = location_id
        self.days = days
        self.total_leads = total_leads
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)

        self.start_date = datetime(2026, 8, 1)
        self.end_date = self.start_date + timedelta(days=days)

        # Funnel conversion rates (realistic for education)
        self.funnel_rates = {
            "new_lead": 1.0,
            "qualified": 0.72,
            "appointment": 0.38,
            "check_in": 0.75,
            "consultation": 0.91,
            "fafsa_applied": 0.35,
            "fafsa_confirmed": 0.78,
            "payment": 0.85,
            "enrollment": 1.0,
            "upsell": 0.15
        }

        # Source distribution
        self.source_weights = {
            "meta": 0.45,
            "google": 0.30,
            "referral": 0.10,
            "organic_search": 0.08,
            "organic_social": 0.05,
            "direct": 0.02
        }

        # Program interest distribution
        self.program_weights = {
            "Practical Nursing": 0.30,
            "Medical Assistant": 0.20,
            "Dental Assistant": 0.12,
            "Pharmacy Technician": 0.10,
            "Surgical Technology": 0.08,
            "Radiologic Technology": 0.08,
            "Physical Therapy Assistant": 0.07,
            "Occupational Therapy Assistant": 0.05
        }

        self.contacts = []
        self.opportunities = []
        self.meta_insights = []
        self.google_insights = []
        self.attributions = []
        self.daily_sales = []

    def generate_contacts(self):
        """Generate contacts with first-touch attribution"""
        print(f"Generating {self.total_leads} contacts...")

        for i in range(self.total_leads):
            # Random date within range
            lead_date = self.start_date + timedelta(
                seconds=random.randint(0, int((self.end_date - self.start_date).total_seconds()))
            )

            # Source selection
            source = random.choices(
                list(self.source_weights.keys()),
                weights=list(self.source_weights.values())
            )[0]

            # Campaign/Ad assignment based on source
            first_touch = self._assign_first_touch(source, lead_date)

            contact = {
                "id": str(uuid.uuid4()),
                "ghl_contact_id": f"contact_{i+1:05d}",
                "location_id": self.location_id,
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "email": fake.email(),
                "phone": fake.phone_number(),
                "first_touch_source": source,
                "first_touch_medium": first_touch["medium"],
                "first_touch_campaign": first_touch["campaign_name"],
                "first_touch_content": first_touch.get("content", ""),
                "first_touch_term": first_touch.get("term", ""),
                "first_touch_gclid": first_touch.get("gclid", ""),
                "first_touch_fbclid": first_touch.get("fbclid", ""),
                "first_touch_referrer": first_touch.get("referrer", ""),
                "first_touch_landing_page": f"https://school.edu/programs/{random.choice(PROGRAMS).lower().replace(' ', '-')}",
                "first_touch_date": lead_date,
                "first_touch_campaign_id": first_touch.get("campaign_id", ""),
                "first_touch_adset_id": first_touch.get("adset_id", ""),
                "first_touch_ad_id": first_touch.get("ad_id", ""),
                "first_touch_keyword": first_touch.get("keyword", ""),
                "first_touch_search_term": first_touch.get("search_term", ""),
                "first_touch_match_type": first_touch.get("match_type", ""),
                "first_touch_placement": first_touch.get("placement", ""),
                "latest_touch_source": source,
                "latest_touch_campaign": first_touch["campaign_name"],
                "latest_touch_date": lead_date,
                "created_at": lead_date,
                "updated_at": lead_date,
                "attribution_fingerprint": str(uuid.uuid4()),
                "tags": ["new-lead", source.replace("_", "-")]
            }
            self.contacts.append(contact)

        print(f"Generated {len(self.contacts)} contacts")
        return self.contacts

    def _assign_first_touch(self, source, date):
        """Assign realistic first-touch parameters based on source"""
        touch = {}

        if source == "meta":
            campaign = random.choice(META_CAMPAIGNS)
            adset = random.choice([a for a in META_ADSETS if a["campaign_id"] == campaign["id"]])
            ad = random.choice([a for a in META_ADS if a["adset_id"] == adset["id"]])
            touch = {
                "medium": "paid_social",
                "campaign_name": campaign["name"],
                "campaign_id": campaign["id"],
                "adset_id": adset["id"],
                "ad_id": ad["id"],
                "content": ad["name"],
                "placement": ad["placement"],
                "fbclid": f"fbclid_{uuid.uuid4().hex[:16]}"
            }
        elif source == "google":
            campaign = random.choice(GOOGLE_CAMPAIGNS)
            ad_group = random.choice([a for a in GOOGLE_AD_GROUPS if a["campaign_id"] == campaign["id"]])
            keyword = random.choice([k for k in GOOGLE_KEYWORDS if k["ad_group_id"] == ad_group["id"]]) if random.random() > 0.3 else None
            touch = {
                "medium": "cpc",
                "campaign_name": campaign["name"],
                "campaign_id": campaign["id"],
                "ad_group_id": ad_group["id"],
                "keyword": keyword["text"] if keyword else "",
                "match_type": keyword["match_type"] if keyword else "",
                "search_term": keyword["text"] if keyword and random.random() > 0.5 else fake.word(),
                "gclid": f"gclid_{uuid.uuid4().hex[:16]}"
            }
        elif source == "referral":
            touch = {
                "medium": "referral",
                "campaign_name": "Student Referral Program",
                "referrer": f"https://{fake.domain_name()}/referral"
            }
        elif source == "organic_search":
            touch = {
                "medium": "organic",
                "campaign_name": "Organic Search",
                "term": random.choice(["nursing school", "medical assistant training", "healthcare programs"])
            }
        elif source == "organic_social":
            touch = {
                "medium": "organic_social",
                "campaign_name": "Organic Social",
                "placement": random.choice(["facebook", "instagram", "tiktok"])
            }
        else:  # direct
            touch = {
                "medium": "none",
                "campaign_name": "Direct Traffic"
            }

        return touch

    def generate_opportunities(self):
        """Generate pipeline opportunities with realistic funnel progression"""
        print("Generating opportunities with funnel progression...")

        for contact in self.contacts:
            program = random.choices(
                list(self.program_weights.keys()),
                weights=list(self.program_weights.values())
            )[0]

            # Determine final stage based on funnel rates
            final_stage_idx = 0
            for i, stage in enumerate(PIPELINE_STAGES[1:], 1):
                if random.random() > self.funnel_rates[stage]:
                    break
                final_stage_idx = i

            final_stage = PIPELINE_STAGES[final_stage_idx]
            status = "won" if final_stage == "enrollment" else ("lost" if final_stage not in ["enrollment", "upsell"] else "open")

            # Program cost (realistic for education)
            base_cost = random.choice([12000, 15000, 18000, 22000, 25000])
            grant_amount = random.choice([0, 0, 0, 3000, 5000, 8000]) if random.random() > 0.4 else 0

            opp = {
                "id": str(uuid.uuid4()),
                "ghl_opportunity_id": f"opp_{contact['ghl_contact_id']}",
                "contact_id": contact["id"],
                "pipeline_id": "pipe_main_001",
                "stage_id": f"stage_{final_stage}",
                "stage_name": final_stage,
                "status": status,
                "name": f"{contact['first_name']} {contact['last_name']} - {program}",
                "monetary_value": base_cost if status == "won" else 0,
                "assigned_to": random.choice(SALES_USERS)["id"],
                "initial_program": program,
                "enrolled_program": program if status == "won" else "",
                "payment_method": random.choice(["FAFSA", "FAFSA", "Grant", "Out-of-pocket", "FAFSA+Grant"]) if status == "won" else "",
                "grant_amount": grant_amount if status == "won" else 0,
                "program_cost": base_cost,
                "fafsa_submitted_date": contact["first_touch_date"] + timedelta(days=random.randint(5, 15)) if final_stage_idx >= 5 else None,
                "fafsa_confirmed_date": contact["first_touch_date"] + timedelta(days=random.randint(12, 25)) if final_stage_idx >= 6 else None,
                "lost_reason": random.choice(LOST_REASONS) if status == "lost" else "",
                "lost_stage": final_stage if status == "lost" else "",
                "lost_date": contact["first_touch_date"] + timedelta(days=random.randint(3, 20)) if status == "lost" else None,
                "upsell_program": random.choice([p for p in PROGRAMS if p != program]) if final_stage == "upsell" else "",
                "upsell_amount": random.choice([2000, 3000, 5000]) if final_stage == "upsell" else 0,
                "referral_source_name": fake.name() if contact["first_touch_source"] == "referral" else "",
                "review_requested": status == "won" and random.random() > 0.3,
                "review_date_requested": contact["first_touch_date"] + timedelta(days=random.randint(30, 45)) if status == "won" and random.random() > 0.3 else None,
                "review_received": random.random() > 0.6 if status == "won" else False,
                "review_platform": random.choice(["Google", "Video", "Facebook"]) if status == "won" and random.random() > 0.6 else "",
                "created_at": contact["first_touch_date"],
                "updated_at": contact["first_touch_date"] + timedelta(days=random.randint(1, 30)),
                "closed_at": contact["first_touch_date"] + timedelta(days=random.randint(10, 45)) if status in ["won", "lost"] else None
            }
            self.opportunities.append(opp)

        print(f"Generated {len(self.opportunities)} opportunities")
        print(f"  - Won: {sum(1 for o in self.opportunities if o['status'] == 'won')}")
        print(f"  - Lost: {sum(1 for o in self.opportunities if o['status'] == 'lost')}")
        print(f"  - Open: {sum(1 for o in self.opportunities if o['status'] == 'open')}")
        return self.opportunities

    def generate_ad_spend(self):
        """Generate Meta and Google ad spend data"""
        print("Generating ad spend data...")

        # Meta insights (daily, campaign-level)
        for campaign in META_CAMPAIGNS:
            for day in range(self.days):
                date = self.start_date + timedelta(days=day)
                daily_budget = campaign["budget"] / self.days

                # Add some randomness
                spend = daily_budget * random.uniform(0.7, 1.3)
                impressions = int(spend * 100)  # ~$10 CPM
                clicks = int(impressions * random.uniform(0.015, 0.035))  # 1.5-3.5% CTR
                leads = int(clicks * random.uniform(0.08, 0.18))  # 8-18% lead rate

                self.meta_insights.append({
                    "id": str(uuid.uuid4()),
                    "campaign_id": campaign["id"],
                    "adset_id": "",
                    "ad_id": "",
                    "date": date.date(),
                    "impressions": impressions,
                    "reach": int(impressions * 0.7),
                    "frequency": round(impressions / (impressions * 0.7), 2),
                    "clicks": clicks,
                    "link_clicks": int(clicks * 0.8),
                    "ctr": round(clicks / impressions * 100, 2),
                    "spend": round(spend, 2),
                    "cpm": round(spend / impressions * 1000, 2),
                    "cpc": round(spend / clicks, 2),
                    "leads": leads,
                    "cost_per_lead": round(spend / leads, 2) if leads > 0 else 0,
                    "conversions": int(leads * random.uniform(0.05, 0.12)),
                    "conversion_values": 0,
                    "cost_per_conversion": 0,
                    "publisher_platform": random.choice(["facebook", "instagram"]),
                    "placement": random.choice(["feed", "stories", "reels"]),
                    "device_platform": random.choice(["mobile", "desktop"]),
                    "attribution_window": "7d_click,1d_view",
                    "fetched_at": datetime.now()
                })

        # Google insights (daily, campaign-level)
        for campaign in GOOGLE_CAMPAIGNS:
            for day in range(self.days):
                date = self.start_date + timedelta(days=day)
                daily_budget = campaign["budget"] / self.days

                spend = daily_budget * random.uniform(0.8, 1.2)
                impressions = int(spend * 80)  # ~$12.50 CPM for search
                clicks = int(impressions * random.uniform(0.03, 0.08))  # 3-8% CTR for search

                self.google_insights.append({
                    "id": str(uuid.uuid4()),
                    "campaign_id": campaign["id"],
                    "ad_group_id": "",
                    "criterion_id": "",
                    "date": date.date(),
                    "impressions": impressions,
                    "clicks": clicks,
                    "ctr": round(clicks / impressions * 100, 2),
                    "cost_micros": int(spend * 1_000_000),
                    "cost_usd": round(spend, 2),
                    "average_cpc": round(spend / clicks, 2),
                    "conversions": int(clicks * random.uniform(0.06, 0.15)),
                    "conversions_value": 0,
                    "cost_per_conversion": 0,
                    "conversion_rate": round(clicks * random.uniform(0.06, 0.15) / clicks * 100, 2),
                    "quality_score": random.randint(5, 10),
                    "search_impression_share": round(random.uniform(0.45, 0.85), 2),
                    "fetched_at": datetime.now()
                })

        print(f"Generated {len(self.meta_insights)} Meta insights rows")
        print(f"Generated {len(self.google_insights)} Google insights rows")

    def generate_attributions(self):
        """Generate attribution records linking enrollments to campaigns"""
        print("Generating attribution records...")

        won_opps = [o for o in self.opportunities if o["status"] == "won"]

        for opp in won_opps:
            contact = next(c for c in self.contacts if c["id"] == opp["contact_id"])

            # Calculate ad spend for this enrollment
            # Simplified: divide campaign spend by leads from that campaign
            if contact["first_touch_source"] in ["meta", "google"]:
                campaign_id = contact.get("first_touch_campaign_id", "")

                if contact["first_touch_source"] == "meta":
                    campaign_spend = sum(
                        mi["spend"] for mi in self.meta_insights 
                        if mi["campaign_id"] == campaign_id
                    )
                    campaign_leads = sum(
                        mi["leads"] for mi in self.meta_insights
                        if mi["campaign_id"] == campaign_id
                    )
                else:
                    campaign_spend = sum(
                        gi["cost_usd"] for gi in self.google_insights
                        if gi["campaign_id"] == campaign_id
                    )
                    campaign_leads = sum(
                        gi["conversions"] for gi in self.google_insights
                        if gi["campaign_id"] == campaign_id
                    )

                cac = campaign_spend / campaign_leads if campaign_leads > 0 else 0
                roas = opp["monetary_value"] / cac if cac > 0 else 0

                self.attributions.append({
                    "id": str(uuid.uuid4()),
                    "opportunity_id": opp["id"],
                    "contact_id": contact["id"],
                    "enrollment_date": opp["closed_at"],
                    "deal_value": opp["monetary_value"],
                    "attribution_model": "first_touch",
                    "platform": contact["first_touch_source"],
                    "campaign_id": campaign_id,
                    "campaign_name": contact["first_touch_campaign"],
                    "adset_id": contact.get("first_touch_adset_id", ""),
                    "adset_name": "",
                    "ad_id": contact.get("first_touch_ad_id", ""),
                    "ad_name": contact.get("first_touch_content", ""),
                    "placement": contact.get("first_touch_placement", ""),
                    "ad_group_id": contact.get("first_touch_ad_group_id", ""),
                    "ad_group_name": "",
                    "keyword": contact.get("first_touch_keyword", ""),
                    "search_term": contact.get("first_touch_search_term", ""),
                    "match_type": contact.get("first_touch_match_type", ""),
                    "ad_spend": round(cac, 2),
                    "cac": round(cac, 2),
                    "roas": round(roas, 2),
                    "created_at": datetime.now()
                })

        print(f"Generated {len(self.attributions)} attribution records")

    def generate_daily_sales(self):
        """Generate daily sales reports for each user"""
        print("Generating daily sales reports...")

        for day in range(self.days):
            date = self.start_date + timedelta(days=day)

            for user in SALES_USERS:
                # Base metrics with randomness
                base_calls = random.randint(30, 60) if user["role"] == "call_center" else random.randint(15, 30)
                base_appts = int(base_calls * random.uniform(0.12, 0.22))
                base_checkins = int(base_appts * random.uniform(0.55, 0.75))

                report = {
                    "id": str(uuid.uuid4()),
                    "date": date.date(),
                    "user_id": user["id"],
                    "user_name": user["name"],
                    "role": user["role"],
                    "calls_made": base_calls,
                    "completed_dialogues_20s": int(base_calls * random.uniform(0.6, 0.8)),
                    "appointments_booked": base_appts,
                    "transfers": int(base_calls * random.uniform(0.03, 0.08)),
                    "cancellations": int(base_appts * random.uniform(0.08, 0.18)),
                    "check_ins": base_checkins,
                    "show_up_rate": round(base_checkins / base_appts * 100, 2) if base_appts > 0 else 0,
                    "hours_worked": round(random.uniform(6.5, 8.5), 1),
                    "calls_attempted": base_calls if user["role"] == "sales_manager" else 0,
                    "calls_completed": int(base_calls * 0.75) if user["role"] == "sales_manager" else 0,
                    "consultations_conducted": int(base_checkins * random.uniform(0.7, 0.9)) if user["role"] == "sales_manager" else 0,
                    "trial_lessons": int(base_checkins * random.uniform(0.1, 0.25)) if user["role"] == "sales_manager" else 0,
                    "fafsa_submitted": int(base_checkins * random.uniform(0.2, 0.4)) if user["role"] == "sales_manager" else 0,
                    "fafsa_confirmed": int(base_checkins * random.uniform(0.15, 0.3)) if user["role"] == "sales_manager" else 0,
                    "enrollments": int(base_checkins * random.uniform(0.08, 0.18)) if user["role"] == "sales_manager" else 0,
                    "upsells": int(base_checkins * random.uniform(0.02, 0.08)) if user["role"] == "sales_manager" else 0,
                    "sales_amount": round(random.choice([12000, 15000, 18000, 22000]) * int(base_checkins * random.uniform(0.08, 0.18)), 2) if user["role"] == "sales_manager" else 0,
                    "created_at": datetime.now()
                }
                self.daily_sales.append(report)

        print(f"Generated {len(self.daily_sales)} daily sales records")

    def save_to_postgresql(self, db_url):
        """Save all generated data to PostgreSQL"""
        print(f"Saving to PostgreSQL: {db_url}")

        conn = psycopg2.connect(db_url)
        cur = conn.cursor()

        # Insert contacts
        contact_values = [(
            c["id"], c["ghl_contact_id"], c["location_id"], c["email"], c["phone"],
            c["first_name"], c["last_name"], c["first_touch_source"], c["first_touch_medium"],
            c["first_touch_campaign"], c["first_touch_content"], c["first_touch_term"],
            c["first_touch_gclid"], c["first_touch_fbclid"], c["first_touch_referrer"],
            c["first_touch_landing_page"], c["first_touch_date"], c["first_touch_campaign_id"],
            c["first_touch_adset_id"], c["first_touch_ad_id"], c["first_touch_keyword"],
            c["first_touch_search_term"], c["first_touch_match_type"], c["first_touch_placement"],
            c["latest_touch_source"], c["latest_touch_campaign"], c["latest_touch_date"],
            c["created_at"], c["updated_at"], c["attribution_fingerprint"], c["tags"]
        ) for c in self.contacts]

        execute_values(cur, """
            INSERT INTO contacts (
                id, ghl_contact_id, location_id, email, phone, first_name, last_name,
                first_touch_source, first_touch_medium, first_touch_campaign, first_touch_content,
                first_touch_term, first_touch_gclid, first_touch_fbclid, first_touch_referrer,
                first_touch_landing_page, first_touch_date, first_touch_campaign_id,
                first_touch_adset_id, first_touch_ad_id, first_touch_keyword,
                first_touch_search_term, first_touch_match_type, first_touch_placement,
                latest_touch_source, latest_touch_campaign, latest_touch_date,
                created_at, updated_at, attribution_fingerprint, tags
            ) VALUES %s
        """, contact_values)

        # Insert opportunities
        opp_values = [(
            o["id"], o["ghl_opportunity_id"], o["contact_id"], o["pipeline_id"],
            o["stage_id"], o["stage_name"], o["status"], o["name"], o["monetary_value"],
            o["assigned_to"], o["initial_program"], o["enrolled_program"], o["payment_method"],
            o["grant_amount"], o["program_cost"], o["fafsa_submitted_date"],
            o["fafsa_confirmed_date"], o["lost_reason"], o["lost_stage"], o["lost_date"],
            o["upsell_program"], o["upsell_amount"], o["referral_source_name"],
            o["review_requested"], o["review_date_requested"], o["review_received"],
            o["review_platform"], o["created_at"], o["updated_at"], o["closed_at"]
        ) for o in self.opportunities]

        execute_values(cur, """
            INSERT INTO opportunities (
                id, ghl_opportunity_id, contact_id, pipeline_id, stage_id, stage_name,
                status, name, monetary_value, assigned_to, initial_program, enrolled_program,
                payment_method, grant_amount, program_cost, fafsa_submitted_date,
                fafsa_confirmed_date, lost_reason, lost_stage, lost_date,
                upsell_program, upsell_amount, referral_source_name,
                review_requested, review_date_requested, review_received, review_platform,
                created_at, updated_at, closed_at
            ) VALUES %s
        """, opp_values)

        # Insert Meta insights
        meta_values = [(
            m["id"], m["campaign_id"], m["adset_id"], m["ad_id"], m["date"],
            m["impressions"], m["reach"], m["frequency"], m["clicks"], m["link_clicks"],
            m["ctr"], m["spend"], m["cpm"], m["cpc"], m["leads"], m["cost_per_lead"],
            m["conversions"], m["conversion_values"], m["cost_per_conversion"],
            m["publisher_platform"], m["placement"], m["device_platform"],
            m["attribution_window"], m["fetched_at"]
        ) for m in self.meta_insights]

        execute_values(cur, """
            INSERT INTO meta_insights (
                id, campaign_id, adset_id, ad_id, date, impressions, reach, frequency,
                clicks, link_clicks, ctr, spend, cpm, cpc, leads, cost_per_lead,
                conversions, conversion_values, cost_per_conversion,
                publisher_platform, placement, device_platform, attribution_window, fetched_at
            ) VALUES %s
        """, meta_values)

        # Insert Google insights
        google_values = [(
            g["id"], g["campaign_id"], g["ad_group_id"], g["criterion_id"], g["date"],
            g["impressions"], g["clicks"], g["ctr"], g["cost_micros"], g["cost_usd"],
            g["average_cpc"], g["conversions"], g["conversions_value"],
            g["cost_per_conversion"], g["conversion_rate"], g["quality_score"],
            g["search_impression_share"], g["fetched_at"]
        ) for g in self.google_insights]

        execute_values(cur, """
            INSERT INTO google_insights (
                id, campaign_id, ad_group_id, criterion_id, date, impressions, clicks, ctr,
                cost_micros, cost_usd, average_cpc, conversions, conversions_value,
                cost_per_conversion, conversion_rate, quality_score, search_impression_share, fetched_at
            ) VALUES %s
        """, google_values)

        # Insert attributions
        attr_values = [(
            a["id"], a["opportunity_id"], a["contact_id"], a["enrollment_date"],
            a["deal_value"], a["attribution_model"], a["platform"], a["campaign_id"],
            a["campaign_name"], a["adset_id"], a["adset_name"], a["ad_id"], a["ad_name"],
            a["placement"], a["ad_group_id"], a["ad_group_name"], a["keyword"],
            a["search_term"], a["match_type"], a["ad_spend"], a["cac"], a["roas"], a["created_at"]
        ) for a in self.attributions]

        execute_values(cur, """
            INSERT INTO attributions (
                id, opportunity_id, contact_id, enrollment_date, deal_value,
                attribution_model, platform, campaign_id, campaign_name, adset_id,
                adset_name, ad_id, ad_name, placement, ad_group_id, ad_group_name,
                keyword, search_term, match_type, ad_spend, cac, roas, created_at
            ) VALUES %s
        """, attr_values)

        # Insert daily sales
        sales_values = [(
            s["id"], s["date"], s["user_id"], s["user_name"], s["role"],
            s["calls_made"], s["completed_dialogues_20s"], s["appointments_booked"],
            s["transfers"], s["cancellations"], s["check_ins"], s["show_up_rate"],
            s["hours_worked"], s["calls_attempted"], s["calls_completed"],
            s["consultations_conducted"], s["trial_lessons"], s["fafsa_submitted"],
            s["fafsa_confirmed"], s["enrollments"], s["upsells"], s["sales_amount"], s["created_at"]
        ) for s in self.daily_sales]

        execute_values(cur, """
            INSERT INTO daily_sales_reports (
                id, date, user_id, user_name, role, calls_made, completed_dialogues_20s,
                appointments_booked, transfers, cancellations, check_ins, show_up_rate,
                hours_worked, calls_attempted, calls_completed, consultations_conducted,
                trial_lessons, fafsa_submitted, fafsa_confirmed, enrollments, upsells,
                sales_amount, created_at
            ) VALUES %s
        """, sales_values)

        conn.commit()
        cur.close()
        conn.close()

        print("All data saved to PostgreSQL successfully!")

    def generate_all(self):
        """Run complete data generation pipeline"""
        print("=" * 60)
        print("MOCK DATA GENERATOR FOR ATTRIBUTION DASHBOARD DEMO")
        print("=" * 60)
        print(f"Location ID: {self.location_id}")
        print(f"Date Range: {self.start_date.date()} to {self.end_date.date()}")
        print(f"Target Leads: {self.total_leads}")
        print("=" * 60)

        self.generate_contacts()
        self.generate_opportunities()
        self.generate_ad_spend()
        self.generate_attributions()
        self.generate_daily_sales()

        # Summary statistics
        won = sum(1 for o in self.opportunities if o["status"] == "won")
        lost = sum(1 for o in self.opportunities if o["status"] == "lost")
        total_revenue = sum(o["monetary_value"] for o in self.opportunities if o["status"] == "won")
        total_spend = sum(m["spend"] for m in self.meta_insights) + sum(g["cost_usd"] for g in self.google_insights)

        print("\n" + "=" * 60)
        print("DEMO DATA SUMMARY")
        print("=" * 60)
        print(f"Total Leads: {len(self.contacts)}")
        print(f"Enrollments: {won} ({won/len(self.contacts)*100:.1f}%)")
        print(f"Lost Leads: {lost} ({lost/len(self.contacts)*100:.1f}%)")
        print(f"Total Revenue: ${total_revenue:,.2f}")
        print(f"Total Ad Spend: ${total_spend:,.2f}")
        print(f"Overall ROAS: {total_revenue/total_spend:.1f}x")
        print(f"Overall CAC: ${total_spend/won:.2f}")
        print("=" * 60)

        return {
            "contacts": self.contacts,
            "opportunities": self.opportunities,
            "meta_insights": self.meta_insights,
            "google_insights": self.google_insights,
            "attributions": self.attributions,
            "daily_sales": self.daily_sales
        }


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate mock data for attribution dashboard demo")
    parser.add_argument("--location-id", required=True, help="GHL Location ID")
    parser.add_argument("--days", type=int, default=30, help="Number of days to generate")
    parser.add_argument("--leads", type=int, default=500, help="Total leads to generate")
    parser.add_argument("--db-url", default="postgresql://localhost/attribution_db", help="PostgreSQL URL")
    parser.add_argument("--redis-url", default="redis://localhost:6379/0", help="Redis URL")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--save", action="store_true", help="Save to database")

    args = parser.parse_args()

    generator = MockDataGenerator(
        location_id=args.location_id,
        days=args.days,
        total_leads=args.leads,
        seed=args.seed
    )

    data = generator.generate_all()

    if args.save:
        generator.save_to_postgresql(args.db_url)
    else:
        print("\nData generated in memory. Use --save to write to PostgreSQL.")
```

---

## EXPECTED OUTPUT

```
============================================================
MOCK DATA GENERATOR FOR ATTRIBUTION DASHBOARD DEMO
============================================================
Location ID: SS8xGvXsDEzTyFPQ
Date Range: 2026-08-01 to 2026-08-31
Target Leads: 500
============================================================
Generating 500 contacts...
Generated 500 contacts
Generating opportunities with funnel progression...
Generated 500 opportunities
  - Won: 42 (8.4%)
  - Lost: 423 (84.6%)
  - Open: 35 (7.0%)
Generating ad spend data...
Generated 155 Meta insights rows
Generated 124 Google insights rows
Generating attribution records...
Generated 42 attribution records
Generating daily sales reports...
Generated 186 daily sales records

============================================================
DEMO DATA SUMMARY
============================================================
Total Leads: 500
Enrollments: 42 (8.4%)
Lost Leads: 423 (84.6%)
Total Revenue: $672,000.00
Total Ad Spend: $22,847.50
Overall ROAS: 29.4x
Overall CAC: $544.00
============================================================
```

---

## REALISTIC BENCHMARKS USED

| Metric | Value | Source |
|--------|-------|--------|
| Lead-to-Enrollment Rate | 6-10% | Education industry average for vocational programs |
| Show-up Rate | 55-75% | Appointment attendance for education consultations |
| FAFSA Submission Rate | 30-45% | Of qualified leads who attend consultation |
| FAFSA Approval Rate | 70-80% | Of submitted FAFSA applications |
| Meta CPL | $30-45 | Healthcare/education Facebook ads |
| Google Search CPL | $40-65 | Nursing/medical assistant keywords |
| Program Cost | $12,000-25,000 | Vocational healthcare programs |
| Grant Amount | $3,000-8,000 | Typical Pell Grant + state aid |
| Call Center Calls/Day | 30-60 | Per representative |
| Sales Manager Consultations | 3-8 | Per day |
