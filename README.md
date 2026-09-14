# 🌌 Karen Web — Emotional Support Sanctuary

> *A quiet, empathetic digital refuge for your thoughts and feelings.*

**Karen** is a mobile-first, privacy-focused emotional support Progressive Web Application (PWA) built with **SvelteKit 2**, **Svelte 5 Runes**, and **TailwindCSS**. Designed around a calming, non-clinical therapeutic visual identity, Karen offers an unhurried sanctuary for emotional grounding, thoughtful conversation, and reflective journaling.

---

## ✨ Features

- **Atmospheric Emotion Engine**: Dynamic, subtle 5-second background transitions that gently shift according to conversational emotion (`neutral`, `sadness`, `fear`, `anger`, `joy`).
- **Signature Breathing Orb**: Interactive visual breathing anchor guiding transitions across welcome, grounding, and wrap-up states.
- **Privacy-First Architecture**: Conversational transcripts and reflections are stored locally in **IndexedDB** on the user's device.
- **Real-Time Therapeutic Chat**: Unhurried conversational dialogue with left-aligned floating assistant messages, tap-to-reveal timestamps, and soft-pulse typing indicators.
- **Crisis Support System**: Immediate emergency guidance with direct access to hotlines (988 Lifeline, iCall Helpline, and Vandrevala Foundation) that safely preserves the ongoing conversation upon dismissal.
- **Session Wrap-up & Reflection Cards**: Two-step closure allowing users to generate and download structured 6-section personal reflections as PDF.
- **Session Journal & History**: Complete replay of past sessions with emotion trajectory dots and distress indicators.
- **Companion FastAPI Backend Integration**: Connects with the Karen FastAPI backend for JWT authentication, real-time response generation, and AI-synthesized reflection summaries.

---

## 🛠️ Tech Stack

- **Framework**: [SvelteKit 2](https://kit.svelte.dev/) with [Svelte 5 Runes](https://svelte.dev/docs/svelte/v5-migration-guide) (`$state`, `$derived`, `$effect`, `$props`)
- **Styling**: [TailwindCSS](https://tailwindcss.com/) + Custom Glassmorphic CSS & Keyframe Animations
- **Local Database**: [IndexedDB via `idb`](https://github.com/jakearchibald/idb)
- **Icons**: [Lucide Svelte](https://lucide.dev/)
- **PDF Generation**: [jsPDF](https://github.com/parallax/jsPDF)
- **E2E Testing**: Autonomous testing with [TestSprite MCP](https://www.testsprite.com/) + Playwright

---

## 📁 Project Structure

```
Karen-web/
├── src/
│   ├── lib/
│   │   ├── components/       # Reusable UI (Orb, CrisisOverlay, Drawer, etc.)
│   │   ├── api.ts            # REST client with offline fallback heuristics
│   │   ├── db.ts             # IndexedDB stores (sessions, reports, preferences)
│   │   └── state.svelte.ts   # Global reactive state management
│   └── routes/
│       ├── +page.svelte      # Welcome / Splash screen with breathing orb
│       ├── enter/            # Timed grounding sequence ("I'm here with you.")
│       ├── chat/             # Main conversation space
│       ├── auth/             # Sign-in & account creation
│       ├── end/              # Session wrap-up & reflection prompt
│       ├── complete/         # Farewell completion screen with bottom navigation
│       ├── history/          # Journal list & session replay
│       └── report/           # 6-section reflection report & PDF exporter
├── testsprite_tests/         # Autonomous E2E test scripts & reports
├── static/                   # Static assets, fonts, icons
├── svelte.config.js          # SvelteKit configuration
├── tailwind.config.js        # Tailwind theme tokens & ambient utilities
└── vite.config.ts            # Vite bundler configuration
```

---

## 🚀 Getting Started

### Prerequisites
- [Node.js](https://nodejs.org/) v18 or later
- [npm](https://www.npmjs.com/) or [pnpm](https://pnpm.io/)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/krishneshkrish/karen-web.git
   cd karen-web
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env.local
   ```
   Set `PUBLIC_API_URL` to your backend instance:
   ```env
   PUBLIC_API_URL=http://localhost:8001
   ```

4. **Start the development server**:
   ```bash
   npm run dev
   ```
   Open `http://localhost:5180` in your browser.

---

## 🔗 Companion Backend Setup

Karen-web integrates seamlessly with the companion **Karen FastAPI** backend:

```bash
# In your backend directory
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001
```

*Note: If the backend is unreachable or in offline mode, Karen-web operates gracefully using client-side offline heuristics and IndexedDB local storage.*

---

## 🧪 Testing

End-to-end tests are located in `testsprite_tests/` and can be reviewed via the TestSprite test report:

- 📄 Report: [`testsprite_tests/testsprite-mcp-test-report.md`](./testsprite_tests/testsprite-mcp-test-report.md)
- Production build verification:
  ```bash
  npm run build
  ```

---

## 🔒 Privacy & Safety Notice

Karen is an emotional support and grounding companion, **not a clinical healthcare provider or substitute for medical diagnosis/treatment**. Transcripts remain private on the user's local device. If you or someone you know is in distress or immediate danger, please reach out directly to emergency services or call **988** (US/Canada), **9152987821** (iCall India), or your local crisis helpline.
