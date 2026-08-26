---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #121: Pi config tuning re-verification (plan-033 deferral REQ-YF-TUNE-017)

- **Number:** 121
- **Title:** Pi config tuning re-verification (plan-033 deferral REQ-YF-TUNE-017)
- **URL:** 
- **State:** OPEN
- **Labels:** type::task, priority::medium, deferred, plan-033-followon

## Body

plan-033 shipped Pi skills+rules but DEFERRED Pi config tuning: research-002 Q6 marks Pi's config surface (settings.json/permissions.json/mcp.json) [uncertain] (questionable-tier only), and rust-embedded profiles would commit a guess into a released binary. Re-verify Pi's config surface against a FIRST-PARTY Pi source; if confirmed, ship a pi.json config profile + wire pi config tune. Until then a pi CONFIG tune cleanly refuses (pi skills+rules ARE supported).
