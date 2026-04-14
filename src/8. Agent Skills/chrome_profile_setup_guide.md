# Chrome Profile Setup Guide for Glimmer

## Purpose

Glimmer's deep research and expert advice capabilities use Chrome running in **debug mode** to interact with Gemini via the operator's authenticated browser session. This requires a dedicated Chrome profile with the correct Google account signed in and Gemini Pro access confirmed.

This guide covers the one-time setup procedure and the ongoing launch configuration.

---

## 1. Why a Dedicated Chrome Profile?

Glimmer connects to Chrome via the Chrome DevTools Protocol (CDP). This means it has access to the browser session, cookies, and authentication state of whatever Chrome profile is running.

A **dedicated profile** is used to:

- isolate Glimmer's Gemini sessions from the operator's daily browsing,
- ensure the correct Google account with Gemini Pro is always the active session,
- avoid interference from extensions, other tabs, or other signed-in accounts,
- and make it safe for Glimmer to open/close tabs without disrupting personal browsing.

---

## 2. Create the Dedicated Chrome Data Directory

On macOS, create a directory specifically for Glimmer's Chrome profile:

```bash
mkdir -p "$HOME/Library/Application Support/Glimmer/ChromeProfile"
```

This directory will contain Chrome's user data (bookmarks, cookies, session storage, etc.) for the Glimmer-dedicated profile. It is separate from Chrome's default profile directory.

---

## 3. First-Time Launch and Google Sign-In

Launch Chrome manually with the dedicated profile to sign in:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/Library/Application Support/Glimmer/ChromeProfile" \
  --profile-directory=Default \
  --no-first-run \
  --no-default-browser-check
```

Once Chrome opens:

1. **Sign in to Google** with the account that has Gemini Pro / Advanced access.
2. **Navigate to [gemini.google.com](https://gemini.google.com)** and confirm it loads correctly.
3. **Confirm Gemini Pro** — verify that the Gemini interface shows access to Deep Research, and that you can select Fast / Thinking / Pro modes in the model picker.
4. **Accept any consent dialogs** — dismiss first-run or privacy prompts so they won't block automation later.
5. **Close Chrome** — the session cookies are now saved in the dedicated profile.

After this one-time setup, Glimmer can launch Chrome with this profile automatically and will have authenticated access to Gemini.

---

## 4. Configure Glimmer Environment Variables

Add the following to your `.env` file (or set as environment variables):

```dotenv
# Path to Chrome (macOS default — usually no change needed)
GLIMMER_CHROME_EXE_PATH=/Applications/Google Chrome.app/Contents/MacOS/Google Chrome

# Dedicated Chrome profile directory
GLIMMER_CHROME_USER_DATA_DIR=~/Library/Application Support/Glimmer/ChromeProfile

# Profile directory name within user_data_dir
GLIMMER_CHROME_PROFILE_NAME=Default

# Google account email (for logging/diagnostics)
GLIMMER_CHROME_GOOGLE_ACCOUNT=you@gmail.com

# CDP remote debugging port (default 9222)
GLIMMER_CHROME_REMOTE_DEBUGGING_PORT=9222
```

See `.env.example` for the full set of configurable variables including research adapter timeouts and rate limits.

---

## 5. How Glimmer Uses Chrome

When Glimmer needs to perform deep research or consult Gemini for expert advice:

1. **Auto-launch** — If Chrome is not already running on the CDP port, Glimmer will automatically launch it with the configured profile and debug flags.
2. **CDP connection** — Glimmer connects to Chrome via `http://localhost:9222` using Playwright's CDP support.
3. **Gemini interaction** — Glimmer navigates to `gemini.google.com` and uses the operator's authenticated session.
4. **Single operation lock** — Only one Gemini operation (research or chat) can run at a time.
5. **Auto-reconnection** — If Chrome disconnects, Glimmer will attempt to reconnect (and re-launch if necessary) on the next operation.

### Health monitoring

Glimmer continuously monitors Chrome availability in the background (~30-second intervals). If Chrome becomes unavailable unexpectedly:

- A warning is logged.
- An automatic re-launch is attempted.
- If Telegram alerts are configured, the operator receives a brief notification.
- The web workspace Today view shows the current Chrome/research status.

---

## 6. Troubleshooting

### Chrome won't launch

- Verify the `GLIMMER_CHROME_EXE_PATH` points to a valid Chrome installation.
- Verify the `GLIMMER_CHROME_USER_DATA_DIR` exists and is writable.
- Check that no other process is already using the CDP port (default 9222). Only one process can connect via CDP at a time.

### Gemini authentication expired

- Launch Chrome manually with the dedicated profile (using the command from §3).
- Sign in again to the Google account.
- Close Chrome and let Glimmer re-launch it.

### CDP port conflict

If you need to run Chrome normally alongside the Glimmer-dedicated instance, use a different port:

```dotenv
GLIMMER_CHROME_REMOTE_DEBUGGING_PORT=9333
```

### Checking Chrome status

- **API:** `GET /health/research` returns Chrome port and adapter status.
- **Web workspace:** The Today view shows a status indicator for research/expert advice availability.
- **Logs:** Chrome connection events are logged at INFO/WARNING level.

---

## 7. Optional: Telegram Health Alerts

To receive push notifications when Chrome goes down or recovers:

1. Create a Telegram bot via [@BotFather](https://t.me/BotFather) and note the bot token.
2. Start a chat with the bot and send `/start`.
3. Get your chat ID (send a message to the bot, then visit `https://api.telegram.org/bot<TOKEN>/getUpdates`).
4. Configure in `.env`:

```dotenv
GLIMMER_TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
GLIMMER_TELEGRAM_OPERATOR_CHAT_ID=987654321
```

Alerts are bounded to significant state transitions only (Chrome lost / Chrome recovered). This is an internal operational alert, not user-facing messaging — it does not violate Glimmer's no-auto-send rule.

---

## 8. Security Notes

- The dedicated Chrome profile contains session cookies for the operator's Google account. Treat the `GLIMMER_CHROME_USER_DATA_DIR` directory with the same care as credentials.
- Glimmer's browser automation is **bounded to Gemini only** — it does not navigate to mail, calendar, social media, or other sensitive surfaces.
- Chrome debug-mode access means any process on the local machine could connect to the CDP port. This is acceptable for the single-operator local-first deployment model.
- Glimmer does not store browser credentials, cookies, or session tokens in its own database.

