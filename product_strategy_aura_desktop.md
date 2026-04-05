# Aura Desktop: Product & Architecture Breakdown

Building the hybrid "Local Desktop + Cloud Proxy" product requires bridging three distinct components: A polished UI, the local Python engine (`aura-research`), and a secure cloud backend for subscriptions. 

Here is the technical breakdown of what it entails to bring this to life.

---

## 1. The Desktop Application (The "App")
This is the application users download and install on macOS, Windows, or Linux. 

**Recommended Tech Stack**: 
* **Framework**: [Electron](https://www.electronjs.org/) + React + Vite. (Electron has seamless access to the local file system, which we need to read/write the `wiki/` directory and `.aura` files).
* **UI/Aesthetics**: Framer Motion for sleek micro-animations, TailwindCSS with a bespoke design system (glassmorphism, vibrant soft gradients, dark mode). 
* **Key Features**:
  * **File Dropzone**: Drag-and-drop PDFs, images, and folders directly into the app (copies them to `raw/`).
  * **Visual Knowledge Graph**: A beautiful node-view of the `_index.md` and compiled `.aura` archive.
  * **Chat Interface**: An integrated chat UI representing the "Genius Librarian" that streams answers directly from the local `.aura` archive.
  * **Settings Pane**: Crucial for the hybrid model. A toggle switch between "Aura Pro Subscription" and "Bring Your Own Key (OpenAI/Local/Ollama)".

## 2. The Local Bridge (The "Engine")
Since the UI is web-based (React), it needs a way to trigger Python commands (`research compile`, `research query`).

* **How it works**: When the app launches, it silently spins up a lightweight local Python server (FastAPI) or uses Python shell execution to communicate with your open-source `aura-research` package.
* **The Magic**: The user never sees the CLI. When they click the glowing "Compile Knowledge" button in the UI, Electron sends a request to the local Python engine, which generates the `wiki.aura` file and streams progress updates back to the UI (e.g., "Summarizing Apple Notes... 40%").

## 3. The Cloud Proxy (The "Business")
This is the backend you host on Google Cloud (GCS) or Firebase. It acts as the gatekeeper and the billing engine for non-technical users.

* **Tech Stack**: FastAPI/Node.js + Firebase Auth + Stripe API.
* **How it works**:
  1. A student opens the app and hits "Compile". They are a Pro subscriber. 
  2. The Desktop App sends the prompt and the `raw/` context to **your** Cloud Proxy server securely.
  3. Your Proxy checks their auth token: *Is their $15/mo Stripe subscription active?*
  4. If yes, your Proxy attaches **your** OpenAI/Anthropic API key to the header and forwards the request to the LLM. 
  5. The LLM response streams back through your server to their Desktop app.
* **Security**: Crucially, **your API keys never live in the Desktop App**. They are hidden entirely in the cloud, protected by user authentication.

---

## The Monetization & User Flow

### Flow A: The Turnkey User (Revenue Generator)
1. User downloads the app for free.
2. They drop files into the app. They click "Query" and hit a prompt: *"Log in to start your 7-day free trial of Aura Pro."*
3. They use Google OAuth (via Firebase) inside the Desktop App, putting a credit card on file via Stripe Checkout.
4. They never touch an API key. You get $15/month recurring. Given that `aura.wiki` highly optimizes tokens and caching, your API cost per user will likely hover around $1-$3/month, yielding a massive 80%+ profit margin.

### Flow B: The "Hacker" User (Growth & Evangelism)
1. User downloads the app for free.
2. They skip the login screen and go to Settings.
3. They paste their own `sk-proj-...` OpenAI key or set their endpoint to `http://localhost:11434/v1` for a local Ollama model.
4. They run the app 100% locally and completely free. You capture $0 from them, but they become your biggest advocates on Twitter, Reddit, and GitHub.

---

## What It Takes to Execute (Phases)

1. **Phase 1: Proof of Concept UI (1-2 Weeks)**
   - Spin up an Electron + React app.
   - Build a gorgeous chat interface and file dropzone.
   - Hardcode local execution to bridge directly with the `aura-research` CLI on the backend.
2. **Phase 2: The Proxy Back-end (2 Weeks)**
   - Deploy a secure server on Cloud Run or Firebase Functions.
   - Implement Stripe Subscriptions and Firebase Authentication.
   - Build the middle-man router that accepts proxy requests from the Desktop app and authenticates them.
3. **Phase 3: Python Packaging & Installers (1 Week)**
   - Bundle the Python environment (`auralith-aura`, `aura-research`) inside the Electron app using tools like `PyInstaller` so that the user doesn't even need to have Python installed on their computer. They just run `Aura.exe` or `Aura.dmg`.

---

## The Mobile Integration (Complete Ownership Model)

Because the core value proposition is **Complete Data Ownership**, the mobile architecture avoids mirroring the entire knowledge base to a proprietary cloud. Instead, it relies on local-sync and on-device models.

### 1. The Local-Sync Ingest Loop
The primary role of the mobile app is real-time capture.
* **How it works:** Users jot down notes, snap photos, or record voice memos on their phone.
* **The Sync:** These raw files are synced directly to the desktop computer (via iCloud, local network sync, or an encrypted relay).
* **The Compile:** Once the Desktop App detects new files synced from the phone, the local `aura-research` engine compiles them into the `.aura` archive. All data processing remains 100% on the user's local hardware.

### 2. On-Device Inference (Gemma 4 Edge Integration)
If a user wants to query their AI on their phone while completely offline or without hitting an API, we can leverage open-weights edge models.
* **The Tech:** Google just released the **Gemma 4** family under the Apache 2.0 license (April 2026). Specifically, the **Gemma 4 E2B (Effective 2B)** and **E4B** models are highly optimized for edge devices.
* **The Implementation:** The mobile app stores a lightweight, synced version of the `.aura` RAG archive. It runs Gemma 4 directly on the phone’s neural processor. 
* **The Benefit:** No subscription needed, airplane-mode capable, zero cloud latency, and 100% data privacy. The user owns the data, the compilation, and the inference engine.

---

## Monetizing a Purely Local System (Gemma 4 Strategy)

If you pivot entirely to Gemma 4 and eliminate the need for an API Proxy, your ongoing compute costs drop to zero. However, this shifts *how* you can justify charging the user. Here are the most successful plays for local-first monetization:

### 1. Monetize the "Sync Pipeline" (The Obsidian Playbook)
Users won't pay a monthly subscription for local inference, but they *will* pay for secure convenience. 
* **The Offer:** The Desktop CLI and local compiling are 100% free. However, securely syncing raw notes from their phone to their Desktop, and syncing the compiled `.aura` archive back to the mobile app requires infrastructure. 
* **The Price:** $8/month for **Aura Sync**. You provide the secure, end-to-end encrypted relay that keeps their Second Brain updated across devices.

### 2. Monetize the UI / Client (The Docker Playbook)
The core engine (`aura-research`) is free under Apache 2.0. But the Desktop App and Mobile App are proprietary.
* **The Offer:** If a user wants to use terminal commands to run Gemma 4, they can do it for free. If they want the beautiful, sleek, drag-and-drop iOS and Desktop apps, they pay a one-time fee of $99 (or $10/mo). You are selling the "luxury steering wheel" on top of the free engine.

### 3. Monetize the Premium Connectors ("Living Data")
Local file compilation is free, but hooking up live web services is a massive headache.
* **The Offer:** Base app is free. If the user wants their Second Brain to *automatically* sync with their live Gmail, Slack, Google Calendar, and Notion workspaces in the background, they upgrade to Pro. 
* **The Value:** You manage the OAuth tokens and webhook relays on your cloud backend that push live data into their local `raw/` folder. They pay $15/month for a brain that updates itself while they sleep.
