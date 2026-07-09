# Future Roadmap

Phase 1 ships the local-first foundation (LLM + personality + local voice +
Docker + docs). The phases below outline where the system goes next. Ordering
is indicative, not contractual.

## Phase 2 — Voice in, smarter voice out

### Speech-to-text (STT) pipeline
Add a local STT stage (e.g. `whisper.cpp`, `faster-whisper`) in front of the
LLM so the assistant listens as well as speaks. The `Assistant` core already
accepts text from any source, so STT slots in ahead of it to close the voice
loop (wake word → STT → LLM → TTS).

### Refined voice model
Move beyond first-pass XTTS styling toward a higher-fidelity, consistent voice:
better sample curation, longer/cleaner references, optional fine-tuning, and
latency tuning for near-real-time responses. Still local, still with clear
licensing and no impersonation claims.

## Phase 3 — Home integration

### Home Assistant Assist integration
Connect the assistant to **Home Assistant Assist** so it can understand and act
on home-control intents (lights, climate, scenes, media). Likely shape: the
assistant becomes a Home Assistant *conversation agent* that maps natural
language to HA service calls, with confirmation flows for sensitive actions.

## Phase 4 — Security & network isolation

### VPN / whitelisting
Place the Mac Mini on an isolated network segment (VLAN) reachable only through
a VPN (e.g. WireGuard / Tailscale) with strict device whitelisting. Because the
Phase 1 core makes no outbound calls, hardening the perimeter is
straightforward.

## Phase 5 — Scale & resilience

### Multi-node / offline architecture
Extend beyond a single Mac Mini: multiple local nodes for redundancy and load
sharing, a fully offline operating mode, and graceful degradation if a node is
unavailable. Keep everything on-premises.

## Phase 6 — Presence & perception (research / opt-in)

These are more speculative and carry meaningful privacy considerations; they
would be strictly opt-in and local.

### Facial recognition
Local, consent-based recognition to personalize responses per household member.

### Emotion recognition
Local affect cues to adjust tone. Treated cautiously due to accuracy and
privacy concerns.

### Desktop avatar / companion
An optional on-screen animated presence (desktop or dedicated display) that
lip-syncs and reacts to the assistant's voice and state.

---

### Guiding principles across all phases
- **Local-first & private** — keep processing on the household's hardware.
- **Modular** — each capability is a clean add-on to the `Assistant` core.
- **Honest** — no impersonation claims; clear about what is and isn't real.
- **Consent-driven** — perception features are opt-in and transparent.
