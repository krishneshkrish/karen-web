# Karen Web — Features & Functionalities Documentation

**Karen** is a mobile-first, privacy-focused emotional support Progressive Web Application (PWA) built with SvelteKit, TailwindCSS, and Svelte 5 Runes. Designed around a calm, therapeutic visual identity, Karen offers an unhurried digital sanctuary for emotional grounding, reflection, and open dialogue.

---

## 🌌 1. Core Visual & Aesthetic Identity

- **Dark Navy Sanctuary**: Rooted in `#0d0d1a` dark navy base with subtle, non-distracting atmospheric glows.
- **Breathing Glowing Orb**: A signature interactive/ambient visual element (120px on splash, 60px on auth, 160px on space transition, 80px on end session, 100px warm-glow on complete, 32px top-bar header).
  - Uses CSS keyframe pulse (`scale 1 → 1.08 → 1`, `opacity 0.6 → 1 → 0.6` over 4s).
- **Emotion-Driven Ambient Engine**: Dynamic 5-second background gradient transitions reflecting detected conversational emotions:
  - `neutral`: `#0d0d1a`
  - `sadness`: `linear-gradient(135deg, #0a1020 0%, #0d0d1a 100%)` (Soft blue depth)
  - `fear`: `linear-gradient(135deg, #1a1008 0%, #0d0d1a 100%)` (Amber undertone)
  - `anger`: `linear-gradient(135deg, #1a0808 0%, #0d0d1a 100%)` (Muted red undertone)
  - `joy`: `linear-gradient(135deg, #081a10 0%, #0d0d1a 100%)` (Soft green undertone)
- **Paper in the Dark Input Styling**: Borderless form inputs with delicate bottom border lines (`border-b border-purple-300/20`) and high-contrast, non-harsh text.

---

## 📱 2. Screen-by-Screen Features & Workflows

### 1. Welcome / Splash Screen (`/`)
- **Time-Based Ambient Greeting**:
  - `00:00 - 06:00` → *"Quiet • Still • Deep"*
  - `06:00 - 12:00` → *"Gentle • Present • Yours"*
  - `12:00 - 18:00` → *"Warm • Calm • Grounded"*
  - `18:00 - 24:00` → *"Easy • Unhurried • Safe"*
- **Staggered Mount Animations**: Fade-in sequence starting with the orb, followed by title/subtitles, and concluding with the CTA button.
- **CTA Navigation**: *"Begin when ready"* pill button navigating to `/enter`.
- **Privacy Lock Note**: Footnote reassuring users that conversations stay private on the device.

### 2. Authentication Screen (`/auth`)
- **Dual Mode Toggle**: Minimalist underline-style tabs switching between *"Sign in"* and *"Create account"* without page reflow.
- **Fields**: Email and Password inputs (plus Confirm Password in registration mode).
- **Soft Error Handling**: Displays human-readable messages (e.g., handling HTTP `401` invalid credentials and `409` user conflict) in gentle inline text without jarring alerts.
- **Token & User Storage**: Saves `karen_jwt_token` and `karen_user_hash` in `localStorage` upon success and proceeds to `/enter`.

### 3. Space Transition Screen (`/enter`)
- **Timed Entrance Sequence**:
  - `0ms`: Fade in from black.
  - `400ms`: 160px bright orb blooms.
  - `900ms`: *"I'm here with you."* drifts up (`translateY: 10px → 0px`).
  - `1500ms`: *"You don't have to explain everything at once."* fades in.
  - `2800ms`: Screen fades to black, auto-navigating to `/chat`.
- **Session Setup**: Automatically generates a crypto UUID `karen_session_id` in `sessionStorage` and initializes session metadata in IndexedDB.

### 4. Main Chat Interface (`/chat`)
- **Header**: 32px breathing orb menu icon (left), *"Karen"* title (center), and circle icon to end session (right).
- **Message Rendering**:
  - **Karen (Assistant)**: Left-aligned floating text (no bubble container) with a 2px purple left-border accent, generous `1.7` line height, and tap-to-reveal 11px timestamp.
  - **User**: Right-aligned muted purple pill bubble (`rgba(100,80,180,0.25)`).
  - **Typing Indicator**: Soft 3-dot pulse animation shown while waiting for backend response.
- **Floating Input Bar**: Auto-resizing `<textarea>` (max 4 lines) with `backdrop-filter: blur(20px)` and soft glowing send button.
- **Slide-Out Settings Drawer**: Options to end session, view past sessions history, or read *"About Karen"*.
- **Crisis Detection**: Triggers gentle crisis modal if API response flags `crisis === true`.

### 5. Crisis Support Overlay (`src/lib/components/CrisisOverlay.svelte`)
- **Non-Alarming Tone**: Semi-transparent dark overlay (`rgba(0,0,0,0.7)`) with backdrop blur and soft red heart icon.
- **Support Directory**:
  - 🫂 *"Find support now"*
  - 📞 **iCall Helpline** (`tel:9152987821`)
  - 📞 **Vandrevala Foundation** (`tel:18602662345`)
  - 🔗 External support website link (`https://icallhelpline.org`)
- **Accessibility & Focus**: Traps keyboard focus inside modal while visible and restores focus upon dismissal with *"I'm okay for now"*.

### 6. End Session Screen (`/end`)
- **Unhurried Two-Step Choice**:
  - **Step 1 (`confirm`)**: *"I'm glad you told me how you were feeling."*
    - *"Stay a little longer"* → Navigates back to `/chat`.
    - *"End for now"* → Triggers `POST /api/v1/chat/end-session`.
  - **Step 2 (`reflection`)**: *"Would you like a reflection of this conversation?"*
    - *"Save reflection"* → Calls `POST /api/v1/report/generate` and routes to `/report`.
    - *"No, thank you"* → Directs to `/complete`.

### 7. Session Complete Screen (`/complete`)
- **Warmer Orb Aesthetic**: Centered 100px orb with amber glow highlights (`rgba(255,180,80,0.15)`).
- **Time-Contextual Farewell**:
  - Morning (`05:00 - 12:00`): *"That's a good way to start the day."*
  - Afternoon (`12:00 - 17:00`): *"That took courage."*
  - Evening/Night (`17:00 - 05:00`): *"That's enough for tonight."*
- **Persistent Bottom Navigation**: Introduces bottom bar linking to Chat, History, and Space transition.
- **Session Cleanup**: Clears active `sessionStorage` keys while preserving IndexedDB transcript data.

### 8. Session History List & Detail (`/history` & `/history/[session_id]`)
- **History List (`/history`)**:
  - Displays list of past sessions from IndexedDB and backend metadata.
  - Card elements: Date/time, topic pill, emotion arc dot sequence, distress badges (`High distress` / `Crisis`), and reflection indicators.
  - Shimmer skeleton loaders during data fetch.
- **Journal Detail View (`/history/[session_id]`)**:
  - Read-only transcript replay with full timestamps visible.
  - Metadata bar (topic + emotion arc).
  - Bottom card to view existing reflection or generate a new reflection on demand.
  - Floating *"Jump to top"* button.

### 9. Session Report / Reflection Screen (`/report`)
- **Therapeutic 6-Section Summary**:
  1. *What brought you here* (`presenting_concern`)
  2. *How you were feeling* (`emotional_tone` + emotion arc dots)
  3. *Themes that came up* (Pill tags)
  4. *Directions explored* (Numbered list)
  5. *Flags noted* (Rendered calmly if present)
  6. *Recommendation*
- **Client-Side PDF Generation**: Generates downloadable PDF reports formatted for therapists using `jsPDF` completely in-browser without re-fetching data.

---

## 🔒 3. Storage & Data Privacy Architecture

- **Local-First IndexedDB (`karen-db`, version 2)**:
  - `sessions` store (`keyPath: 'session_id'`): Holds transcripts (`messages[]`), timestamps, and `emotion_arc[]`.
  - `reports` store (`keyPath: 'session_id'`): Holds generated reflections.
  - `preferences` store (`keyPath: 'key'`): User settings.
- **Zero-Trace Session Storage**: Active session keys stored in `sessionStorage` are cleared upon session completion.
- **Local Authentication**: Tokens (`karen_jwt_token`) stored locally; zero cookies used.

---

## 🛠️ 4. Tech Stack & Environment

- **Framework**: SvelteKit (`@sveltejs/kit` v2) with Svelte 5 Runes (`$state`, `$derived`, `$props`, `$effect`).
- **Styling**: Vanilla CSS + TailwindCSS (v3.4) with custom backdrop blurs and keyframe animations.
- **Libraries**: `idb` (v8.0) for IndexedDB management, `jspdf` (v4.2) for client-side PDF export.
- **Dev Port**: Configured to run on `http://localhost:5180`.
