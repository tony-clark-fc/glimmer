# Agent Commands

Shortcut commands the operator can type in chat to trigger specific agent behaviors without spelling out full instructions.

**Convention:** Commands are prefixed with `^` and use kebab-case. Some accept an optional `<topic>` argument.

---

## Quick Reference

| Command | Purpose | Agent Acts Immediately? |
|---------|---------|------------------------|
| `^warm-up` | Orient to the session — review instructions, framework, tools, skills, current state | No — prepare, then wait |
| `^what-next` | Determine the next best action and present it | No — recommend, then wait for confirmation |
| `^cool-down` | Wrap up the session — update docs, refresh index, write handoff | Yes — execute the wrap-up |
| `^status` | Quick snapshot of where things stand | No — report, then wait |
| `^chain <topic>` | Trace the REQ→ARCH→PLAN→TEST delivery chain for a topic | No — present the chain, then wait |
| `^verify` | Check verification coverage for current/recent work | No — report gaps, then wait |
| `^drift-check` | Scan recent work for architecture drift | No — report findings, then wait |
| `^recap` | Summarize what was done so far this session | No — present summary, then wait |

---

## Command Definitions

### `^warm-up`

**Intent:** "Get yourself oriented and ready. Don't start working yet."

The agent should:

1. **Check index freshness** — run `check_agent_index_freshness.py`, regenerate if stale
2. **Read copilot-instructions** — refresh on project conventions and constraints
3. **Scan skill documents** — re-absorb reasoning patterns (skim headings, don't deep-read)
4. **Find the active workstream(s)** — check `src/5. Working/` for recent progress files
5. **Read the most recent handoff block** — understand where the last session left off
6. **Check verification status** — know what's proven and what's pending
7. **Report readiness** — tell the operator:
   - what workstream(s) are active
   - where the last session left off
   - what blockers exist
   - what the agent is now ready to work on
8. **Wait** — do not start implementing. The operator will direct what happens next.

**Example exchange:**
```
Operator: ^warm-up
Agent:    Index is fresh (886 docs). Read handoff from Workstream A progress.
          Last session completed sensor deployment DTOs.
          Next planned step: implement SensorDeploymentAppService.
          No blockers. Verification: 2 critical scenarios pending.
          Ready for direction.
```

---

### `^what-next`

**Intent:** "Work out what the most valuable next action is, tell me, and wait."

The agent should:

1. **Read active progress files** — find the current handoff block(s)
2. **Check the build plan** — what's the current phase, what's next in sequence?
3. **Check for blockers** — are there human decision gates or environment blockers?
4. **Assess priority** — consider:
   - blockers that can be resolved (highest value)
   - next planned step in the active workstream
   - verification gaps that need closing
   - documentation staleness that needs addressing
   - remediation items recorded in progress files
5. **Present a recommendation** — one clear "next best thing" with:
   - what it is
   - why it's the highest priority
   - which delivery chain anchors it maps to
   - estimated scope (small/medium/large)
   - any dependencies or risks
6. **Wait for confirmation** — do not proceed until the operator says go.

**Example exchange:**
```
Operator: ^what-next
Agent:    Recommended next action: Implement SensorDeploymentAppService
          (PLAN:WorkstreamA.SensorDeployment, step 4 of 7)
          Reason: DTOs are complete, this is the next sequential step.
          Depends on: nothing blocked. Maps to TEST:SensorDeployment.RecordDeployment.HappyPath.
          Scope: medium (~1 session).
          Shall I proceed?
```

---

### `^cool-down`

**Intent:** "This session is done. Wrap everything up so the next session can start clean."

The agent should:

1. **Update the handoff block** in the active progress file:
   - Current phase
   - Last completed step (be specific)
   - Next exact step (specific enough for a cold start)
   - Blockers
   - Human input required
   - Files most recently changed
   - Relevant anchors consulted or affected
2. **Update the verification status** — what's proven, what's pending, what's blocked
3. **Record any findings** — mismatches, drift, remediation items discovered this session
4. **Regenerate the agent index** — run `generate_agent_index.py`
5. **Run the freshness check** — confirm the index is current
6. **Present a session summary** — tell the operator:
   - what was accomplished
   - what was left incomplete
   - what the next session should start with
   - any human decisions or actions needed before next session

**Example exchange:**
```
Operator: ^cool-down
Agent:    Session wrap-up complete.
          ✅ Handoff block updated in workstream_a_progress.md
          ✅ Verification status updated (1 new scenario proven)
          ✅ Index regenerated (887 docs, fresh)
          Summary: Implemented SensorDeploymentAppService with CRUD + RecordDeployment.
          Left incomplete: retrieval endpoint (needs SurveySite navigation).
          Next session should: implement GetPendingForSurveyPlan query method.
          Human action needed: none.
```

---

### `^status`

**Intent:** "Quick snapshot — where are we? Don't do a full warm-up."

The agent should:

1. **Read the active handoff block(s)** — just the handoff, not the full progress file
2. **Report concisely:**
   - Active workstream(s) and current phase
   - Last completed step
   - Next planned step
   - Blockers (if any)
   - Verification status summary
3. **Wait** — this is a report, not an action trigger.

Lighter than `^warm-up` — skips re-reading instructions, skills, and framework. Use when the agent is already oriented and you just want a checkpoint.

---

### `^chain <topic>`

**Intent:** "Trace the full delivery chain for this topic and show me."

The agent should:

1. **Run retrieval** for the topic
2. **Find all four chain links** — `REQ:`, `ARCH:`, `PLAN:`, `TEST:`
3. **Present the chain** in a structured format:
   ```
   REQ:  REQ:FieldDataCollection.SensorTracking
   ARCH: ARCH:SurveyDataModel.SensorDeployments
   PLAN: PLAN:WorkstreamA.SensorDeployment (Phase 2, step 4)
   TEST: TEST:SensorDeployment.RecordDeployment.HappyPath
         TEST:SensorDeployment.RecordDeployment.MissingFieldsRejected
   ```
4. **Flag orphans** — any missing links in the chain
5. **Wait** — present the chain, don't act on it.

---

### `^verify`

**Intent:** "What's the verification coverage for the current/recent work?"

The agent should:

1. **Read the active progress file** — identify what's been implemented
2. **Find the relevant `TEST:` anchors** — what scenarios should be proven?
3. **Assess coverage:**
   - ✅ Proven — test exists, passes, evidence recorded
   - ⚠️ Likely implemented but not proven — code exists, no test evidence
   - ❌ Not implemented — scenario defined but no implementation
   - 🔲 No scenario defined — implementation exists but no `TEST:` anchor
4. **Report gaps** with priority (critical, high, medium)
5. **Wait** — present the assessment, don't start writing tests.

---

### `^drift-check`

**Intent:** "Scan for architecture drift in recent or current work."

The agent should:

1. **Identify recently changed files** — from the progress file or git status
2. **Find the governing `ARCH:` anchors** for those files
3. **Compare implementation against architecture:**
   - Does the code match what the architecture describes?
   - Are there patterns that contradict project framework conventions?
   - Are there undocumented design decisions?
4. **Classify each finding** using the drift taxonomy (Skill 06):
   - ✅ Aligned
   - ⚠️ Extension (may need ADR)
   - 🔄 Transitional (known interim state)
   - ❌ Drift (requires remediation)
5. **Report findings** — don't fix anything without operator direction.

---

### `^recap`

**Intent:** "Summarize what's been done so far this session."

The agent should:

1. **List files changed** this session
2. **List actions taken** — implementations, fixes, doc updates
3. **List findings** — mismatches, drift, blockers discovered
4. **List verification changes** — what's newly proven or newly pending
5. **Present concisely** — this is a mid-session checkpoint, not a full wrap-up.

Lighter than `^cool-down` — does not update progress files or regenerate the index. Use for a quick "where are we?" partway through a session.

---

## Design Principles

1. **Commands compress intent, not detail.** The operator shouldn't need to explain what "wrap up" means every time.
2. **Most commands are non-acting.** The agent presents information and waits. Only `^cool-down` executes autonomously.
3. **Commands are composable.** `^warm-up` then `^what-next` is a natural session start sequence. `^recap` then `^cool-down` is a natural session end.
4. **Commands don't replace conversation.** After any command, the operator can redirect, ask follow-up questions, or override the agent's recommendation.
5. **Commands are stable.** New commands can be added, but existing commands should not change meaning.

