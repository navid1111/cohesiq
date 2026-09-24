# Cohesiq Backend API Testing Reference

Code-derived catalog of the FastAPI routes registered by `backend/app/main.py`.

## Setup

- Base URL: `http://localhost:8000`
- Swagger/OpenAPI: `/docs`, `/redoc`, `/openapi.json`
- Auth: `Authorization: Bearer {{access_token}}`
- JSON: `Content-Type: application/json`
- `redirect_slashes=False`: `/creators/` and `/brands/` require the slash. Both `/campaigns` and `/campaigns/` exist.

> **Known issue:** `POST /auth/login` references an undefined `token` in `app/auth/router.py` and currently errors. With Clerk enabled, use a Clerk session token.

## All routes

Access labels: Public, Auth, Owner, Brand, Creator, Party, Admin, or Webhook.

```text
GET    /health                                                        Public
POST   /auth/register                                                 Public
POST   /auth/login                                                    Public
GET    /auth/me                                                       Auth
POST   /auth/onboarding                                               Auth

GET    /creators/                                                     Public
GET    /creators/me                                                   Creator
GET    /creators/{creator_id}                                         Public
PUT    /creators/{creator_id}                                         Owner
POST   /creators/{creator_id}/platforms                               Owner
POST   /creators/{creator_id}/platforms/youtube/enrich                Owner
POST   /creators/{creator_id}/platforms/instagram/enrich              Owner
POST   /creators/{creator_id}/platforms/tiktok/enrich                 Owner
PUT    /creators/{creator_id}/platforms/{platform_id}                 Owner
DELETE /creators/{creator_id}/platforms/{platform_id}                 Owner
POST   /creators/{creator_id}/rate-cards                              Owner
PUT    /creators/{creator_id}/rate-cards/{rate_card_id}               Owner
DELETE /creators/{creator_id}/rate-cards/{rate_card_id}               Owner
POST   /creators/{creator_id}/portfolio                               Owner
DELETE /creators/{creator_id}/portfolio/{item_id}                     Owner
POST   /creators/{creator_id}/history                                 Owner
DELETE /creators/{creator_id}/history/{history_id}                    Owner
GET    /creators/{creator_id}/applications                            Owner
GET    /creators/{creator_id}/reviews                                 Public

GET    /brands/                                                       Public
GET    /brands/me                                                     Brand
GET    /brands/{brand_id}                                             Public
PUT    /brands/{brand_id}                                             Owner
GET    /brands/{brand_id}/campaigns                                   Public
GET    /brands/{brand_id}/applications                                Owner
GET    /brands/{brand_id}/reviews                                     Public

GET    /campaigns or /campaigns/                                      Public
POST   /campaigns or /campaigns/                                      Brand
GET    /campaigns/{campaign_id}                                       Public
PUT    /campaigns/{campaign_id}                                       Brand owner
PATCH  /campaigns/{campaign_id}/status                                Brand owner
POST   /campaigns/{campaign_id}/apply                                 Creator
GET    /campaigns/{campaign_id}/applications                          Brand owner
PATCH  /campaigns/{campaign_id}/applications/{application_id}/status  Brand owner
POST   /campaigns/{campaign_id}/invite                                Brand owner
PATCH  /campaigns/{campaign_id}/applications/{application_id}/respond-invite Creator
POST   /campaigns/{campaign_id}/shortlist                             Brand owner
POST   /campaigns/{campaign_id}/applications/{application_id}/offer   Brand owner
POST   /campaigns/{campaign_id}/applications/{application_id}/negotiate Party
POST   /campaigns/{campaign_id}/applications/{application_id}/offer/accept Party
POST   /campaigns/{campaign_id}/applications/{application_id}/offer/decline Party
GET    /campaigns/{campaign_id}/applications/{application_id}/negotiation Party
POST   /campaigns/reviews/                                            Auth
POST   /campaigns/{campaign_id}/run-matching                          Brand owner
GET    /campaigns/{campaign_id}/matches                               Brand owner
POST   /campaigns/{campaign_id}/applications/{application_id}/contract Brand
GET    /campaigns/{campaign_id}/applications/{application_id}/contract Auth
PATCH  /campaigns/contracts/{contract_id}/submit-draft                Creator
PATCH  /campaigns/contracts/{contract_id}/approve                     Brand
PATCH  /campaigns/contracts/{contract_id}/request-revision            Brand
PATCH  /campaigns/contracts/{contract_id}/publish                     Creator
PATCH  /campaigns/contracts/{contract_id}/close                       Brand
POST   /campaigns/contracts/{contract_id}/sync-metrics                Brand
GET    /campaigns/contracts/{contract_id}/analytics                   Brand
GET    /campaigns/brands/me/contracts                                 Brand
GET    /campaigns/creators/me/contracts                               Creator
GET    /campaigns/{campaign_id}/live-analytics                        Brand

GET    /youtube/search                                                Public
GET    /youtube/videos/{video_id}                                     Public
GET    /youtube/channels                                              Public
GET    /youtube/channels/enrichment                                   Public

GET    /admin/stats                                                   Admin
GET    /admin/users                                                   Admin
GET    /admin/campaigns                                               Admin
GET    /admin/reviews                                                 Admin
DELETE /admin/reviews/{review_id}                                     Admin
DELETE /admin/users/{user_id}                                         Admin
PATCH  /admin/users/{user_id}/toggle-active                           Admin
PATCH  /admin/campaigns/{campaign_id}/status                          Admin
POST   /webhooks/clerk                                                Webhook
```

## Query parameters

- `/creators/`: `search`, `niche`, `platform`, `min_followers`, `max_followers`, `language`, `city`, `is_available`, `max_rate`, `sort_by=followers_desc`, `limit=20` (max 100), `offset=0`.
- `/brands/`: `limit=20`, `offset=0`.
- `/campaigns`: `niche`, `platform`, `min_budget`, `max_budget`, `language`, `status=active`, `limit=20` (max 100), `offset=0`.
- `/campaigns/brands/me/contracts`: optional `campaign_id`.
- `/youtube/search`: required `q`; `max_results=5` (1–50); `type=video|channel|playlist`; `order=date|rating|relevance|title|videoCount|viewCount`; optional `page_token`, `region_code`, `relevance_language`.
- `/youtube/channels`: exactly one of `id`, `handle`, `username`.
- `/youtube/channels/enrichment`: required `channel_ref`; `recent_video_limit=10` (1–50).
- Admin lists: `page=1`, `limit=20`; users also accept `role`, `is_active`, `search`; campaigns accept `status`, `visibility`.

## Copy-ready bodies

### Auth

```json
{"email":"creator@example.com","password":"StrongPassword123!","role":"creator","display_name":"Nadia Rahman","brand_name":null}
```

```json
{"email":"creator@example.com","password":"StrongPassword123!"}
```

```json
{"role":"creator","creatorProfile":{"displayName":"Nadia Rahman","bio":"Tech creator","tagline":"Tech made simple","city":"Dhaka","gender":"female"},"creatorNiches":{"primary":1,"sub":[7,8]},"creatorPlatforms":[{"platform":"youtube","handle":"@nadiatech","profileUrl":"https://youtube.com/@nadiatech","followerCount":85000}],"brandProfile":null}
```

Brand onboarding uses `{"role":"brand","creatorProfile":null,"creatorNiches":null,"creatorPlatforms":null,"brandProfile":{"brandName":"Acme Bangladesh","description":"Technology company","website":"https://example.com","city":"Dhaka"}}`.

### Creator, social, rates, portfolio, history

```json
{"display_name":"Nadia Rahman","full_name":"Nadia Tasnim Rahman","profile_photo_url":"https://example.com/nadia.jpg","bio":"Technology creator","tagline":"Tech made simple","country_code":"BD","city":"Dhaka","timezone":"Asia/Dhaka","gender":"female","date_of_birth":"1995-05-12","is_available":true,"min_budget":25000,"response_time_hours":12,"preferred_collaboration_types":["sponsored_post","product_review"],"contact_whatsapp":"+8801700000000","contact_email":"nadia@example.com","niches":[{"niche_id":1,"is_primary":true}],"languages":[{"language_code":"bn","is_primary":true}]}
```

```json
{"platform":"youtube","handle":"@nadiatech","profile_url":"https://youtube.com/@nadiatech","platform_user_id":"UC123456789","display_name_on_platform":"Nadia Tech","follower_count":85000,"following_count":150,"avg_views_per_post":45000,"avg_likes_per_post":3200,"avg_comments_per_post":250,"avg_shares_per_post":120,"engagement_rate":7.8,"posts_per_month":8.0,"is_primary_platform":true,"account_created_year":2018,"is_monetized":true,"has_verified_badge":false,"audience_country_primary":"BD","audience_city_primary":"Dhaka","audience_age_range_min":18,"audience_age_range_max":34,"audience_gender_majority":"female","audience_gender_pct":58,"content_languages":["bn","en"],"notes":"Tech audience","stats_reported_for_period":"2026-08"}
```

Social update accepts the mutable fields above except `platform`, `platform_user_id`, `display_name_on_platform`, and `account_created_year`; all are optional.

```json
{"channel_ref":"@nadiatech","recent_video_limit":10}
```

```json
{"profile_ref":"https://instagram.com/nadiatech","recent_post_limit":12}
```

```json
{"platform":"youtube","deliverable_type":"dedicated_video","deliverable_code":"youtube_video","price_bdt":75000,"suggested_price_bdt":80000,"price_usd":650,"includes":"One video","excludes":"Paid usage","turnaround_days":14,"is_negotiable":true}
```

Rate update excludes `platform`, adds optional `is_active`, and makes every field optional.

```json
{"platform":"youtube","content_url":"https://youtube.com/watch?v=example","title":"Budget Phones","thumbnail_url":"https://example.com/thumb.jpg","niche_id":1,"views":125000,"likes":7500,"comments":430,"published_at":"2026-08-15","is_featured":true,"sort_order":1}
```

```json
{"brand_name":"Example Electronics","brand_website":"https://example.com","niche_id":1,"platform":"youtube","collaboration_type":"product_review","collaborated_on":"2026-07-10","deliverable_description":"Phone review","content_url":"https://youtube.com/watch?v=example"}
```

### Brand

```json
{"brand_name":"Acme Bangladesh","legal_name":"Acme Bangladesh Limited","logo_url":"https://example.com/logo.png","description":"Technology company","tagline":"Technology for everyone","website":"https://example.com","facebook_page_url":"https://facebook.com/acme","instagram_url":"https://instagram.com/acme","niche_id":1,"brand_category":"consumer_electronics","company_size":"51-200","country_code":"BD","city":"Dhaka","contact_name":"Arif Hasan","contact_phone":"+8801800000000","contact_whatsapp":"+8801800000000"}
```

### Campaign

```json
{"title":"Launch Our New Smartphone","description":"Create authentic product content.","objectives":"Awareness and pre-orders","primary_niche_id":1,"brand_category":"consumer_electronics","required_platforms":["youtube","instagram"],"visibility":"public","campaign_type":null,"budget_per_creator_min":40000,"budget_per_creator_max":100000,"creator_min_followers":10000,"creator_max_followers":500000,"target_countries":["BD"],"target_cities":["Dhaka"],"target_age_min":18,"target_age_max":35,"target_gender":null,"deliverables_description":"One video","number_of_creators":5,"application_deadline":"2026-10-15","content_deadline":"2026-11-15","kpi_targets":{"reach":1000000,"engagement_rate":5.5,"conversions":500,"roi_target":2.5},"hashtags":["#AcmePhone"],"tracking_notes":"Use UTM links","niche_targets":[7,8],"language_targets":[{"language_code":"bn","is_required":true}],"deliverable_requirements":[{"platform":"youtube","deliverable_type":"dedicated_video","deliverable_code":"youtube_video","quantity":1,"notes":"At least eight minutes"}],"application_questions":[{"question_text":"Describe your concept","question_type":"text","options_json":null,"is_required":true,"sort_order":0}],"acknowledgments":[{"statement_text":"I will disclose sponsorship","is_required":true,"sort_order":0}]}
```

Only `title`, `description`, and `budget_per_creator_max` are required. Campaign update makes fields optional but does not accept `niche_targets` or `language_targets`. Question types: `text`, `single_choice`, `multi_choice`.

```json
{"status":"active"}
```

Campaign status: `active`, `cancelled`, `in_progress`, `completed`, `archived`.

### Application and offer flow

```json
{"proposal_text":"I would create a hands-on review.","proposed_rate":75000,"answers":[{"question_id":"{{question_id}}","answer_text":"My content concept","answer_options":null}],"accepted_acknowledgment_ids":["{{acknowledgment_id}}"]}
```

```json
{"status":"shortlisted","brand_notes":"Strong fit","rejection_reason":null,"agreed_rate":75000,"agreed_deliverables":"One video"}
```

Application status: `shortlisted`, `pending_agreement`, `accepted`, `rejected`, `withdrawn`, `completed`.

```json
{"creator_id":"{{creator_id}}","brand_notes":"Strong fit"}
```

```json
{"action":"accept","proposal_text":"Happy to participate","proposed_rate":75000,"answers":[],"accepted_acknowledgment_ids":[]}
```

```json
{"creator_id":"{{creator_id}}","note":"Excellent audience match"}
```

```json
{"contract_type":"content_collaboration","payment_structure":"flat_fee","payment_amount_bdt":75000,"payment_schedule":"on_delivery","non_cash_compensation":"Creator keeps device","has_product_transfer":true,"product_disposition":"keep","deliverable_notes":"One video","deliverables":[{"requirement_id":"{{deliverable_requirement_id}}","quantity":1,"notes":"Before deadline"}],"exclusivity_days":30,"usage_rights_days":90,"max_revision_rounds":2,"kill_fee_percentage":25,"message":"We would like to work with you"}
```

Contract type: `content_collaboration`, `product_seeding`, `talent_engagement`. Payment structure: `flat_fee`, `non_cash`, `none`. Schedule: `upfront`, `on_delivery`, `milestone`. Product disposition: `keep`, `return`. Direct contract creation uses the same body without `message`.

```json
{"message":"I propose adjusted terms","proposed_rate":85000,"proposed_terms":{"exclusivity_days":14,"usage_rights_days":60}}
```

