# SOVRA Truth Engine — Commercial Tiers & Sponsorship Model

This document outlines the operational tiers for **SOVRA Truth Engine v4.0**.

---

## 1. Free & Open-Source Layer (MIT Licensed)

The entire core engine is **100% free, open-source, and un-throttled** under the [MIT License](https://github.com/user/SSOT_Agentic_Brain/blob/main/LICENSE).

### Included in the Free Tier:
- **All Pre-Compiled Binaries**: macOS arm64 (`.dylib` & CLI), Linux x86_64 (`.so` & static `musl`), Windows x86_64 (`.dll` & `.exe`).
- **Complete Verification Core**: Compositional scope parser, double-negative litotes, inclusive idiom handling, and unindexed predicate grounding.
- **Cryptographic Merkle Audit Trail**: SHA-256 evidence chain log receipts committed locally.
- **Zero API & Zero Pip Dependencies**: Fully offline execution with no telemetry or external callouts.

---

## 2. Enterprise & Custom Deployment Layer

For organizations needing specialized integration, custom domain graph ingestion, or dedicated SLAs:

| Tier | Focus Area | Features & Deliverables | Access Model |
|------|------------|-------------------------|--------------|
| **Community / Developer** | Individual Devs & Open Source | Full native binaries, MIT license, GitHub release binaries, self-hosted audit logs. | **Free (MIT)** |
| **Sovereign Enterprise** | Custom Ingestion & Sidecar Daemon | Custom knowledge graph ingestion pipelines, lock-free IPC daemon sockets, priority bug fixes, tailored C/Rust bindings. | **Contact / Direct Invoice** |
| **Sustaining Sponsor** | Project Support & Hardening | Direct contribution to continuous fuzzing, cross-platform build infrastructure, and red-team benchmark suites. | **Stripe / GitHub Sponsors** |

---

## 3. Sponsorship & Direct Payment Links

To support ongoing maintenance, continuous integration hardware, and cross-platform verification:

- **GitHub Sponsors**: [github.com/sponsors/user](https://github.com/sponsors/user)
- **Direct Stripe Payment Link**: [buy.stripe.com/eVq00jcRof7W3jp158dIA00](https://buy.stripe.com/eVq00jcRof7W3jp158dIA00)

### Stripe Buy Button Embed Snippet (HTML Web Embeds)
```html
<script async src="https://js.stripe.com/v3/buy-button.js"></script>
<stripe-buy-button
  buy-button-id="buy_btn_1UMvNZDvwBN84qg66VqfyYeE"
  publishable-key="pk_live_51TVkhdDvwBN84qg6xvgNc7EmIqwfPn5JuWPlt26pIoHAD4Nh5FCVtbGW0nhH276AAOgzZGWO3Z3L0ioidVbAcqUv00tRy9YkDm">
</stripe-buy-button>
```

---

## 4. Verification & Link Integrity

All payment links and repository URLs are continuously validated via automated workflow checks. For custom billing inquiries or enterprise support contracts, submit an issue or reach out directly through the project repository.
