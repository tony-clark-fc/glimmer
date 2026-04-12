# Prompt: Architecture Review

Use this template when reviewing a proposed change, new feature, or discovered drift against the architecture.

## Context Gathering

1. **Identify the concern** — what architectural area is affected?
2. **Run retrieval** to find the relevant architecture section:
   ```bash
   python3 "src/9. Agent Tools/indexing/agent_retrieve.py" "ARCH:RelevantAnchor" --json
   ```
3. **Read the matched architecture section** — understand the intended design
4. **Check the ADR register** for related decisions:
   ```bash
   python3 "src/9. Agent Tools/indexing/agent_retrieve.py" "ADR register" --json
   ```

## Assessment

5. **Compare proposed change against architectural intent:**
   - Does the change align with the current `ARCH:` anchors?
   - Does it require a new architectural decision?
   - Does it contradict an existing ADR?

6. **Classify the situation as one of:**
   - ✅ **Aligned** — change fits within current architecture
   - ⚠️ **Extension** — change extends architecture in a new direction (may need ADR)
   - 🔄 **Transitional** — change is an interim step toward an approved architectural target
   - ❌ **Drift** — change contradicts approved architecture (requires remediation or ADR amendment)

## Action

7. **If aligned:** proceed with implementation
8. **If extension:** propose an ADR entry capturing the new decision
9. **If transitional:** document the transitional nature in working docs and note the target state
10. **If drift:** stop and report — do not implement drift silently

## Output

Record the assessment:
- Relevant `ARCH:` anchors consulted
- Classification (aligned / extension / transitional / drift)
- ADR action (none / propose new / amend existing)
- Recommendation with rationale

