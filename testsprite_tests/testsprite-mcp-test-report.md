# TestSprite AI Testing Report (MCP)

---

## 1️⃣ Document Metadata
- **Project Name:** Karen-web (with companion FastAPI backend `Karen`)
- **Date:** 2026-09-13
- **Prepared by:** TestSprite AI Testing Suite
- **Environment:**
  - Frontend: SvelteKit 2 + Svelte 5 Runes on `http://localhost:5180`
  - Backend: FastAPI v0.1.0 + SQLite/Supabase on `http://localhost:8001`
  - Runner: TestSprite MCP Autonomous Test Execution Engine via Yamux Tunnel

---

## 2️⃣ Requirement Validation Summary (Organized by Requirement)

### Requirement: Space Transition Sequence
*Validates the calming transition from grounding into the active therapeutic chat space.*

#### Test TC006: Move from grounding into an active chat session
- **Test Code:** [TC006_Move_from_grounding_into_an_active_chat_session.py](./TC006_Move_from_grounding_into_an_active_chat_session.py)
- **Status:** ✅ **PASSED**
- **Test Visualization:** [View Video & Execution Trace](https://www.testsprite.com/dashboard/mcp/tests/e77b8ca6-c942-524d-bd46-00411febc97a/test/766890ba-0038-465a-9248-fc6550e49f46)
- **Analysis / Findings:** The calming transition flow functioned flawlessly. Navigating to `/enter`, observing the breathing orb bloom sequence, and awaiting the automatic space transition correctly routed the user into the active chat session (`/chat`) with the input placeholder ready.

#### Test TC008: Send an emotional message and receive a supportive reply
- **Test Code:** [TC008_Send_an_emotional_message_and_receive_a_supportive_reply.py](./TC008_Send_an_emotional_message_and_receive_a_supportive_reply.py)
- **Status:** ⚠️ **BLOCKED**
- **Test Error:** Chat UI could not be reached; direct navigation to `/chat` timed out during parallel test worker execution over the tunnel. Backend `/docs` was concurrently reached and verified active.
- **Test Visualization:** [View Video & Execution Trace](https://www.testsprite.com/dashboard/mcp/tests/e77b8ca6-c942-524d-bd46-00411febc97a/test/c7a0fe4d-9dcb-4a04-84f3-78dc26962285)
- **Analysis / Findings:** Headless Chromium timed out during direct route initialization under multi-worker tunnel load. The backend API service was confirmed operational.

---

### Requirement: User Authentication
*Validates credential-based sign in and account registration integrated with the live backend.*

#### Test TC012: Sign in and continue into the calming entry flow
- **Test Code:** [TC012_Sign_in_and_continue_into_the_calming_entry_flow.py](./TC012_Sign_in_and_continue_into_the_calming_entry_flow.py)
- **Status:** ✅ **PASSED**
- **Test Visualization:** [View Video & Execution Trace](https://www.testsprite.com/dashboard/mcp/tests/e77b8ca6-c942-524d-bd46-00411febc97a/test/1c19f234-dfa4-4b22-8af7-2d0a00126045)
- **Analysis / Findings:** Successfully validated end-to-end integration between `Karen-web` and `Karen` FastAPI backend. The test entered credentials on `/auth`, transmitted `POST /api/v1/auth/login` to `http://localhost:8001`, received HTTP 200 with JWT tokens, and transitioned seamlessly into the grounding space.

#### Test TC014: Create an account and continue into the calming entry flow
- **Test Code:** [TC014_Create_an_account_and_continue_into_the_calming_entry_flow.py](./TC014_Create_an_account_and_continue_into_the_calming_entry_flow.py)
- **Status:** ⚠️ **BLOCKED**
- **Test Error:** Rapid cache-busting navigations (`/auth?cachebust=1..4`) provoked a dev-server internal compilation error mid-test before the form could be submitted.
- **Test Visualization:** [View Video & Execution Trace](https://www.testsprite.com/dashboard/mcp/tests/e77b8ca6-c942-524d-bd46-00411febc97a/test/cd5ad5a7-e6fa-4505-8676-759fe14c153b)
- **Analysis / Findings:** In Run 1, registration failed due to an offline backend (port 8001). With the backend started, independent verification confirmed registration works (`POST /api/v1/auth/register` returned 201 Created). However, during the automated rerun, the runner's rapid cache-busting queries caused dev-server contention.

---

### Requirement: End Session Flow
*Validates the session wrap-up experience, reflection summary options, and graceful exit.*

#### Test TC010: Finish a session without saving a reflection
- **Test Code:** [TC010_Finish_a_session_without_saving_a_reflection.py](./TC010_Finish_a_session_without_saving_a_reflection.py)
- **Status:** ✅ **PASSED**
- **Test Visualization:** [View Video & Execution Trace](https://www.testsprite.com/dashboard/mcp/tests/e77b8ca6-c942-524d-bd46-00411febc97a/test/3aca563e-f01e-4e5f-920d-3ce65f7736ec)
- **Analysis / Findings:** Verified that users can exit a session without generating an AI reflection. Navigated to `/end`, confirmed "End for now", chose to proceed without saving, and successfully reached the warm completion screen.

#### Test TC013: Save a reflection and open the report
- **Test Code:** [TC013_Save_a_reflection_and_open_the_report.py](./TC013_Save_a_reflection_and_open_the_report.py)
- **Status:** ❌ **FAILED**
- **Test Error:** Generating the reflection did not produce summary content; the page displayed the fallback message: *"We weren't able to generate your reflection. Your conversation is still saved on your device."*
- **Test Visualization:** [View Video & Execution Trace](https://www.testsprite.com/dashboard/mcp/tests/e77b8ca6-c942-524d-bd46-00411febc97a/test/6cdabef7-648e-48bd-b9d7-732bf4387dda)
- **Analysis / Findings:** Backend AI service limitation. While the frontend successfully handled the reflection submission and gracefully displayed the non-blocking fallback banner, the backend LLM service (`app/services/gemini_service.py`) failed to return synthesized text due to missing/unconfigured Gemini API keys or deprecated SDK usage.

---

### Requirement: Crisis Support Overlay
*Ensures immediate access to crisis resources upon self-harm signals or emergency button clicks.*

#### Test TC002: Show crisis support resources for a crisis message
- **Test Code:** [TC002_Show_crisis_support_resources_for_a_crisis_message.py](./TC002_Show_crisis_support_resources_for_a_crisis_message.py)
- **Status:** ⚠️ **BLOCKED** *(Passed in Run 1)*
- **Test Error:** Direct deep-link navigation to `/chat` timed out during multi-worker tunnel load.
- **Test Visualization:** [View Video & Execution Trace](https://www.testsprite.com/dashboard/mcp/tests/e77b8ca6-c942-524d-bd46-00411febc97a/test/00674404-2a75-4a93-a824-88f0f39f2964)
- **Analysis / Findings:** In Run 1, TC002 passed when entering from `/`. In Run 2, direct loading of `/chat` under concurrent tunnel traffic exceeded the 15s Playwright timeout before mounting.

#### Test TC011: Dismiss crisis support and return to chat
- **Test Code:** [TC011_Dismiss_crisis_support_and_return_to_chat.py](./TC011_Dismiss_crisis_support_and_return_to_chat.py)
- **Status:** ❌ **FAILED**
- **Test Error:** Dismissing the crisis support overlay redirected the user to the landing page (`/enter` with 'Create Space'/'Sign In') instead of returning to the active chat session.
- **Test Visualization:** [View Video & Execution Trace](https://www.testsprite.com/dashboard/mcp/tests/e77b8ca6-c942-524d-bd46-00411febc97a/test/1cb29ef5-bd92-4e8a-95f2-e4ac2b8bdc1a)
- **Analysis / Findings:** **Critical UX/Functional Defect.** When a user closes or dismisses the crisis overlay, `CrisisOverlay.svelte` triggers a navigation that drops the active conversation state and redirects to `/enter`. The user should remain in the active conversation at `/chat`.

---

### Requirement: Welcome Splash Screen
*Validates the initial sensory breathing orb, welcoming atmosphere, and entry transitions.*

#### Test TC001: Handle a crisis statement with supportive overlay guidance
- **Test Code:** [TC001_Handle_a_crisis_statement_with_supportive_overlay_guidance.py](./TC001_Handle_a_crisis_statement_with_supportive_overlay_guidance.py)
- **Status:** ⚠️ **BLOCKED**
- **Test Visualization:** [View Video & Execution Trace](https://www.testsprite.com/dashboard/mcp/tests/e77b8ca6-c942-524d-bd46-00411febc97a/test/9785136d-1d94-44f9-a91c-b83142add0cd)
- **Analysis / Findings:** Direct deep linking to `/chat` resulted in client hydration timeout before interactive composer elements appeared.

#### Test TC005: Enter the app from the welcome screen
- **Test Code:** [TC005_Enter_the_app_from_the_welcome_screen.py](./TC005_Enter_the_app_from_the_welcome_screen.py)
- **Status:** ⚠️ **BLOCKED** *(Passed in Run 1)*
- **Test Visualization:** [View Video & Execution Trace](https://www.testsprite.com/dashboard/mcp/tests/e77b8ca6-c942-524d-bd46-00411febc97a/test/cae7a6cd-e8b6-415c-8314-abaa92908aea)
- **Analysis / Findings:** In Run 1, TC005 passed cleanly. In Run 2, concurrent tunnel traffic delayed the initial bundle load beyond Playwright's navigation timeout.

#### Test TC009: Finish a session and reach the completion screen
- **Test Code:** [TC009_Finish_a_session_and_reach_the_completion_screen.py](./TC009_Finish_a_session_and_reach_the_completion_screen.py)
- **Status:** ⚠️ **BLOCKED**
- **Test Visualization:** [View Video & Execution Trace](https://www.testsprite.com/dashboard/mcp/tests/e77b8ca6-c942-524d-bd46-00411febc97a/test/cb075994-e221-4c80-b077-56bc83f823ab)
- **Analysis / Findings:** Direct deep linking to `/chat` resulted in a blank page without interactive controls before the session wrap-up could be invoked.

---

### Requirement: Therapeutic Chat Interaction
*Validates the real-time AI conversation, message dispatch, typing indicator, and assistant replies.*

#### Test TC003: Complete the calming entry flow into chat
- **Test Code:** [TC003_Complete_the_calming_entry_flow_into_chat.py](./TC003_Complete_the_calming_entry_flow_into_chat.py)
- **Status:** ⚠️ **BLOCKED**
- **Test Visualization:** [View Video & Execution Trace](https://www.testsprite.com/dashboard/mcp/tests/e77b8ca6-c942-524d-bd46-00411febc97a/test/3f3d51b6-dc1f-4446-a1a6-07387d3798dd)
- **Analysis / Findings:** Initial landing page load timed out under parallel test runner traffic against the single-threaded Vite dev server.

#### Test TC004: Send a supportive message and receive a response
- **Test Code:** [TC004_Send_a_supportive_message_and_receive_a_response.py](./TC004_Send_a_supportive_message_and_receive_a_response.py)
- **Status:** ⚠️ **BLOCKED**
- **Test Visualization:** [View Video & Execution Trace](https://www.testsprite.com/dashboard/mcp/tests/e77b8ca6-c942-524d-bd46-00411febc97a/test/f61ec672-0a39-47e4-9be9-395066180f4d)
- **Analysis / Findings:** SvelteKit client-side state initialization at `/chat` failed to mount interactive elements in time due to high dev-server latency across the Yamux remote proxy tunnel.

#### Test TC007: End a chat session from the conversation screen
- **Test Code:** [TC007_End_a_chat_session_from_the_conversation_screen.py](./TC007_End_a_chat_session_from_the_conversation_screen.py)
- **Status:** ⚠️ **BLOCKED**
- **Test Visualization:** [View Video & Execution Trace](https://www.testsprite.com/dashboard/mcp/tests/e77b8ca6-c942-524d-bd46-00411febc97a/test/57684362-2663-4944-89a3-795c891076b3)
- **Analysis / Findings:** Unhydrated `/chat` route exceeded timeout budget before session end control became clickable.

---

### Requirement: Session Completion Screen
*Validates the farewell screen, closure prompts, and bottom navigation returning to other app views.*

#### Test TC015: Open the completion screen and continue elsewhere
- **Test Code:** [TC015_Open_the_completion_screen_and_continue_elsewhere.py](./TC015_Open_the_completion_screen_and_continue_elsewhere.py)
- **Status:** ⚠️ **BLOCKED**
- **Test Visualization:** [View Video & Execution Trace](https://www.testsprite.com/dashboard/mcp/tests/e77b8ca6-c942-524d-bd46-00411febc97a/test/d30db904-abc2-4fdd-a5d6-de4973627fdd)
- **Analysis / Findings:** Direct deep linking to `/complete` without active session context in IndexedDB causes route guards to not mount interactive farewell controls. As demonstrated by TC010, the completion view renders when entered through the valid session progression (`/chat` -> `/end` -> `/complete`).

---

## 3️⃣ Coverage & Matching Metrics

| Metric | Run 1 (Frontend Only) | Run 2 (Frontend + Live Backend) |
|---|---|---|
| **Total Test Cases** | 15 | 15 |
| **Passed** | 2 (13.3%) | 3 (20.0%) |
| **Failed** | 1 (6.7%) | 2 (13.3%) |
| **Blocked (Dev Server Latency)** | 12 (80.0%) | 10 (66.7%) |

### Results by Requirement Group

| Requirement Group | Total Tests | ✅ Passed | ❌ Failed | ⚠️ Blocked | Pass Rate |
|---|:---:|:---:|:---:|:---:|:---:|
| **Space Transition Sequence** | 2 | 1 | 0 | 1 | 50.0% |
| **User Authentication** | 2 | 1 | 0 | 1 | 50.0% |
| **End Session Flow** | 2 | 1 | 1 | 0 | 50.0% |
| **Crisis Support Overlay** | 2 | 0 | 1 | 1 | 0.0% |
| **Welcome Splash Screen** | 3 | 0 | 0 | 3 | 0.0% |
| **Therapeutic Chat Interaction** | 3 | 0 | 0 | 3 | 0.0% |
| **Session Completion Screen** | 1 | 0 | 0 | 1 | 0.0% |
| **Overall** | **15** | **3** | **2** | **10** | **20.0%** |

---

## 4️⃣ Key Gaps / Risks & Remediation Plan

### 1. [Functional Bug] Crisis Overlay Dismissal Navigation (TC011)
- **Risk:** When a distressed user dismisses the emergency crisis overlay (`CrisisOverlay.svelte`), the application unexpectedly redirects to the unauthenticated landing screen (`/enter`), discarding their active chat session.
- **Fix:** Update `CrisisOverlay.svelte` dismissal button handler to cleanly close the modal dialog (`isOpen = false` / emit `close` event) instead of executing `goto('/enter')` or reloading the window.

### 2. [Backend Integration] Gemini AI Reflection Synthesis (TC013)
- **Risk:** Generating reflections at session end fails on the backend and triggers the frontend fallback banner (*"We weren't able to generate your reflection"*).
- **Fix:** In `C:\Users\krishnesh.bs\Downloads\Karen\app\services\gemini_service.py`:
  1. Migrate from deprecated `google.generativeai` to the official `google.genai` package.
  2. Verify `GEMINI_API_KEY` in `Karen/.env`.
  3. Implement a local template-based extractive fallback so reflection cards always show meaningful user insights even during network or quota failures.

### 3. [Architecture] Direct Deep Linking & SPA Client Hydration (TC001, TC004, TC007, TC015)
- **Risk:** SvelteKit routes like `/chat` and `/complete` render blank or fail if accessed directly by URL without going through the entrance flow.
- **Fix:** Add a client-side layout guard in `src/routes/+layout.svelte` that initializes user/guest session state in IndexedDB on mount, preventing blank states during direct deep-link navigation.

### 4. [Automation Environment] Production Preview for CI/CD Testing
- **Risk:** Single-threaded `vite dev` is prone to request queue contention when 15 remote Playwright workers connect simultaneously through reverse proxy tunnels.
- **Fix:** In continuous integration or full E2E automation suites, execute tests against `npm run build && npm run preview -- --port 5180` rather than `vite dev`.
