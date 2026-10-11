# AI Plant Care — Implementation Plan

## Overview

This plan transforms the base Plant Disease Detection System into the
**AI Plant Care — Intelligent Plant Disease Detection and Agricultural Assistance Platform**.

Implementation follows the 12 phases defined in the master prompt.

---

## Phase 0 — Repository Audit ✅ COMPLETE

- [x] Inspect repository structure
- [x] Document existing routes, model, database, templates
- [x] Identify reusable code vs. what needs upgrade
- [x] Produce `CURRENT_STATE.md`

---

## Phase 1 — Foundation

Refactor the monolithic `app.py` into a modular architecture.

### Tasks

1. **Project structure** — Create the `app/` package with domain modules
2. **Configuration** — Centralized config class with env-based settings
3. **Database layer** — Repository pattern with MongoDB indexes and validation
4. **Authentication hardening** — CSRF, session expiry, rate limiting
5. **Logging** — Structured logging replacing print statements
6. **Error handling** — Centralized error handlers with consistent JSON/HTML responses
7. **Validation** — Input validation utilities
8. **Health checks** — `/health`, `/health/model`, `/health/database`

### Exit Criteria

- Application starts with modular structure
- Database connects with proper indexes
- Authentication works with CSRF and session expiry
- Structured logging active
- Health endpoints return status

---

## ✅ Phase 2 — Core ML

### Tasks

1. **ModelManager** — Load once, version tracking, health check
2. **Preprocessing service** — Abstracted image preprocessing pipeline
3. **Inference service** — Prediction with model version recording
4. **Prediction persistence** — Store model version, preprocessing version
5. **Confidence evaluation** — HIGH/MEDIUM/LOW confidence categorization
6. **Severity placeholder** — Return `severity_status: "not_available"`

### Exit Criteria

- Upload → preprocess → predict → database → result works reliably
- Every prediction records model version metadata
- Low-confidence results show appropriate warnings

---

## ✅ Phase 3 — Disease Knowledge

### Tasks

1. **Disease collection** — MongoDB collection with structured disease data
2. **Treatment collection** — Organic/chemical/preventive categories
3. **Seed script** — Populate initial disease/treatment data
4. **Treatment recommendation engine** — Lookup by crop + disease
5. **Safety disclaimers** — Every recommendation includes disclaimers

### Exit Criteria

- Every supported prediction resolves to structured disease information
- Treatments separated by category with safety info
- Admin can manage diseases/treatments (basic)

---

## ✅ Phase 4 — Farmer History

### Tasks

1. **Plants collection** — User's plant profiles
2. **Enhanced history** — Filter by crop, disease, date
3. **Prediction detail** — Full prediction view with disease + treatment
4. **Care cases** — Before/after tracking structure

---

## ✅ Phase 5 — Treatment & Follow-up

### Tasks

1. **Treatment plans** — Track what treatment was applied
2. **Reminders** — Schedule follow-up checks
3. **Care events** — Log treatment activities
4. **Follow-up images** — Compare initial vs follow-up
5. **Notification service** — Abstracted notification delivery

---

## Phase 6 — Weather

### Tasks

1. **Weather provider interface** — Abstract provider
2. **OpenWeatherMap adapter** — Default implementation
3. **Caching** — TTL-based weather cache
4. **Failure handling** — Graceful degradation
5. **Irrigation advice** — Basic crop + weather recommendations

---

## Phase 7 — Risk Engine

### Tasks

1. **Risk rules** — Configurable crop + disease + weather rules
2. **Risk evaluator** — Rule-based risk scoring
3. **Risk alerts** — Alert generation and storage
4. **Alert display** — User-facing alert UI

---

## Phase 8 — Location Services

### Tasks

1. **Expert discovery** — Agricultural expert listings
2. **Store discovery** — Agricultural store listings
3. **Map integration** — Directions links (external)

---

## Phase 9 — Multilingual

### Tasks

1. **i18n framework** — Flask-Babel or custom localization
2. **English translations** — Base language
3. **Kannada translations** — कन्नड
4. **Hindi translations** — हिंदी
5. **Language switcher** — UI component

---

## Phase 10 — Offline Capability

### Tasks

1. **Service worker** — Basic PWA setup
2. **Local model strategy** — TFLite or cached model
3. **Cached disease data** — Local storage
4. **Sync queue** — Offline predictions synced when online

---

## Phase 11 — Admin ✅ COMPLETE

### Tasks

1. [x] **Admin dashboard** — Analytics overview & metrics
2. [x] **User management** — List, suspend, role protection
3. [x] **Disease management** — CRUD for diseases
4. [x] **Treatment management** — CRUD for multi-tier treatments
5. [x] **Risk rules management** — Configure alert rules & thresholds
6. [x] **Audit logs** — Track admin actions with user & timestamp

---

## Phase 12 — Hardening ✅ COMPLETE

### Tasks

1. [x] **Security testing** — Unauthorized access, injection, uploads, CSRF, and user isolation
2. [x] **Performance testing** — Response times, model fallback and memory isolation
3. [x] **Integration tests** — 36 unit and integration tests passing in pytest
4. [x] **Docker** — Hardened Dockerfile with non-root user, healthchecks, and docker-compose.yml
5. [x] **CI** — GitHub Actions automated workflow (.github/workflows/ci.yml)
6. [x] **Documentation** — All 12 docs + DECISIONS.md + README updated

---

## Documentation Tracking

| Document | Status |
|----------|--------|
| 01-product-requirements.md | ✅ Complete |
| 02-user-stories-and-acceptance-criteria.md | ✅ Complete |
| 03-information-architecture.md | ✅ Complete |
| 04-system-architecture.md | ✅ Complete |
| 05-database-schema.md | ✅ Complete |
| 06-api-contracts.md | ✅ Complete |
| 07-monorepo-structure.md | ✅ Complete |
| 08-scoring-engine-specs.md | ✅ Complete |
| 09-engineering-scope-definition.md | ✅ Complete |
| 10-development-phases.md | ✅ Complete |
| 11-environment-and-devops.md | ✅ Complete |
| 12-testing-strategy.md | ✅ Complete |
| DECISIONS.md | ✅ Complete |
| CURRENT_STATE.md | ✅ Complete |
