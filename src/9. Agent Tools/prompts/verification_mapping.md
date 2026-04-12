# Prompt: Verification Mapping

Use this template when determining whether a workstream or feature slice has adequate verification coverage.

## Context

1. **Identify the workstream or feature** and its `PLAN:` anchor
2. **Run retrieval** to find linked test scenarios:
   ```bash
   python3 "src/9. Agent Tools/indexing/agent_retrieve.py" "TEST:Capability.X" --json
   ```
3. **Read the test catalog entry** for the relevant `TEST:` anchors
4. **Read the verification index** for the overall verification posture

## Mapping

For each `TEST:` anchor linked to this work, classify:

| `TEST:` Anchor | Status | Evidence |
|---|---|---|
| `TEST:Capability.X.Scenario1` | ✅ Evidenced / ⚠️ Likely but unproven / ❌ Not yet implemented / 🔲 Manual only | Test name, log, screenshot, or "none" |

## Gap Analysis

5. **Which scenarios are already evidenced?** — list with evidence references
6. **Which are likely implemented but not proven?** — code exists but no test
7. **Which require new automated tests?** — specify unit / integration / E2E
8. **Which require manual verification?** — specify steps and acceptance criteria
9. **Which regression scenarios must pass before release?** — cross-reference regression pack

## Risk Assessment

10. **High-risk gaps** — scenarios where failure could cause data loss, security issues, or breaking changes
11. **Medium-risk gaps** — scenarios where failure would cause incorrect behavior but is recoverable
12. **Low-risk gaps** — cosmetic or edge-case scenarios

## Output

Produce a verification status block suitable for the working-document progress file:

```markdown
## Verification Status
- **Critical scenarios passing:** [list]
- **Critical scenarios pending:** [list]
- **High-priority scenarios pending:** [list]
- **Manual-only scenarios:** [list]
- **Environment blockers:** [list or "none"]
```

