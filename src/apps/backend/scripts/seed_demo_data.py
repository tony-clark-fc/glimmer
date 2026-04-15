#!/usr/bin/env python3
"""Seed the Glimmer dev database with realistic demo data.

Run: cd src/apps/backend && python -m scripts.seed_demo_data
"""

from __future__ import annotations

import sys
import os
from datetime import datetime, timezone, timedelta

# Ensure app package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import get_session
from app.models.portfolio import Project
from app.models.execution import (
    WorkItem,
    BlockerRecord,
    WaitingOnRecord,
    RiskRecord,
)
from app.models.source import ConnectedAccount, Message
from app.models.interpretation import ExtractedAction, MessageClassification
from app.models.drafting import Draft, DraftVariant

now = datetime.now(timezone.utc)
yesterday = now - timedelta(days=1)
tomorrow = now + timedelta(days=1)
next_week = now + timedelta(days=7)
in_3_days = now + timedelta(days=3)


def seed():
    session = get_session()

    # ── Check if data already exists ─────────────────────────────
    existing = session.query(Project).count()
    if existing > 0:
        print(f"Database already has {existing} project(s). Skipping seed.")
        print("To re-seed, run: psql glimmer_dev -c 'DELETE FROM projects CASCADE;'")
        session.close()
        return

    print("Seeding demo data into glimmer_dev…")

    # ── Projects ─────────────────────────────────────────────────
    p1 = Project(
        name="Beta Migration",
        status="active",
        phase="Execution",
        priority_band="high",
        objective="Migrate all production services from PostgreSQL 14 to PostgreSQL 17 with zero downtime",
        short_summary="Core infrastructure migration. On track but behind on data validation testing.",
    )
    p2 = Project(
        name="Gamma Research Platform",
        status="active",
        phase="Planning",
        priority_band="high",
        objective="Build the APAC market research analysis platform for Q3 launch",
        short_summary="Design phase complete. Stakeholder review pending before development starts.",
    )
    p3 = Project(
        name="Client Portal Redesign",
        status="active",
        phase="Development",
        priority_band="medium",
        objective="Modernize the client-facing portal with improved UX and real-time dashboards",
        short_summary="Frontend rebuild 60% complete. API layer stable. Waiting on design assets.",
    )
    p4 = Project(
        name="Q3 Budget Review",
        status="active",
        phase="Review",
        priority_band="medium",
        objective="Complete Q3 budget allocation review across all departments",
        short_summary="Finance team review in progress. Exec sign-off needed by end of week.",
    )

    session.add_all([p1, p2, p3, p4])
    session.flush()
    print(f"  ✓ 4 projects created")

    # ── Work Items ───────────────────────────────────────────────
    work_items = [
        WorkItem(project_id=p1.id, title="Run data validation suite on staging", status="in_progress", due_date=tomorrow),
        WorkItem(project_id=p1.id, title="Update connection pooling config for PG17", status="open", due_date=in_3_days),
        WorkItem(project_id=p1.id, title="Coordinate with DevOps for maintenance window", status="open", due_date=next_week),
        WorkItem(project_id=p2.id, title="Finalize APAC data source integrations list", status="open", due_date=in_3_days),
        WorkItem(project_id=p2.id, title="Schedule stakeholder review meeting", status="open", due_date=tomorrow),
        WorkItem(project_id=p3.id, title="Complete dashboard component library", status="in_progress", due_date=next_week),
        WorkItem(project_id=p3.id, title="Integrate real-time WebSocket feeds", status="open", due_date=next_week),
        WorkItem(project_id=p4.id, title="Consolidate department budget submissions", status="in_progress", due_date=tomorrow),
    ]
    session.add_all(work_items)
    session.flush()
    print(f"  ✓ {len(work_items)} work items created")

    # ── Blockers ─────────────────────────────────────────────────
    blockers = [
        BlockerRecord(project_id=p1.id, summary="Staging environment disk space at 95% — cannot run full validation suite", blocking_what="Data validation testing"),
        BlockerRecord(project_id=p3.id, summary="Waiting on final design assets from UX team — blocking component library", blocking_what="Dashboard components"),
    ]
    session.add_all(blockers)
    session.flush()
    print(f"  ✓ {len(blockers)} blockers created")

    # ── Waiting On ───────────────────────────────────────────────
    waiting = [
        WaitingOnRecord(project_id=p1.id, waiting_on_whom="Sarah Chen (DevOps)", description="Maintenance window approval for production cutover", expected_by=in_3_days),
        WaitingOnRecord(project_id=p2.id, waiting_on_whom="Michael Park (APAC Lead)", description="Final sign-off on data source priority list", expected_by=tomorrow),
        WaitingOnRecord(project_id=p4.id, waiting_on_whom="CFO Office", description="Executive budget ceiling confirmation", expected_by=in_3_days),
    ]
    session.add_all(waiting)
    session.flush()
    print(f"  ✓ {len(waiting)} waiting-on records created")

    # ── Risk Records ─────────────────────────────────────────────
    risks = [
        RiskRecord(project_id=p1.id, summary="PG17 upgrade may require application code changes for deprecated query patterns", severity_signal="high", likelihood_signal="medium"),
        RiskRecord(project_id=p2.id, summary="APAC regulatory requirements may delay data source integrations", severity_signal="medium", likelihood_signal="medium"),
    ]
    session.add_all(risks)
    session.flush()
    print(f"  ✓ {len(risks)} risk records created")

    # ── Connected Account + Messages ─────────────────────────────
    account = ConnectedAccount(
        provider_type="google",
        account_label="tony@example.com",
        status="active",
    )
    session.add(account)
    session.flush()

    messages = [
        Message(
            connected_account_id=account.id,
            source_type="gmail",
            external_message_id="seed_msg_001",
            subject="Re: Beta Migration timeline update",
            body_text="Tony — the staging disk issue is being resolved by infra. Should have capacity by tomorrow EOD. We'll need the validation suite results before we can schedule the cutover window. —Sarah",
            sender_identity="sarah.chen@example.com",
            sent_at=now - timedelta(hours=3),
        ),
        Message(
            connected_account_id=account.id,
            source_type="gmail",
            external_message_id="seed_msg_002",
            subject="Gamma Research — data source priorities",
            body_text="Hi Tony, I've reviewed the APAC data sources. We're confident in 4 of the 6 — the Singapore and Jakarta feeds need additional compliance review. Can we discuss tomorrow morning? —Michael",
            sender_identity="michael.park@example.com",
            sent_at=now - timedelta(hours=5),
        ),
        Message(
            connected_account_id=account.id,
            source_type="gmail",
            external_message_id="seed_msg_003",
            subject="Q3 Budget — department submissions status",
            body_text="Tony, we've received 7 of 9 department submissions. Engineering and Marketing are outstanding — I've pinged both. The CFO wants the consolidated view by Thursday. —Finance Team",
            sender_identity="finance@example.com",
            sent_at=now - timedelta(hours=1),
        ),
        Message(
            connected_account_id=account.id,
            source_type="gmail",
            external_message_id="seed_msg_004",
            subject="Client Portal — design assets delivery",
            body_text="Hey Tony, the design team hit a snag with the dashboard mockups. New delivery ETA is Wednesday. I know this impacts the component library work — sorry for the delay. —Alex",
            sender_identity="alex.rivera@example.com",
            sent_at=now - timedelta(hours=2),
        ),
    ]
    session.add_all(messages)
    session.flush()
    print(f"  ✓ 1 connected account + {len(messages)} messages created")

    # ── Extracted Actions (pending review) ────────────────────────
    actions = [
        ExtractedAction(
            source_record_id=messages[0].id,
            source_record_type="message",
            linked_project_id=p1.id,
            action_text="Schedule cutover window once validation suite passes",
            urgency_signal="high",
            review_state="pending_review",
        ),
        ExtractedAction(
            source_record_id=messages[1].id,
            source_record_type="message",
            linked_project_id=p2.id,
            action_text="Schedule morning call with Michael to discuss Singapore/Jakarta compliance",
            urgency_signal="medium",
            review_state="pending_review",
        ),
        ExtractedAction(
            source_record_id=messages[2].id,
            source_record_type="message",
            linked_project_id=p4.id,
            action_text="Follow up with Engineering and Marketing on budget submissions",
            urgency_signal="high",
            review_state="pending_review",
        ),
        ExtractedAction(
            source_record_id=messages[3].id,
            source_record_type="message",
            linked_project_id=p3.id,
            action_text="Update component library timeline to account for design delay until Wednesday",
            urgency_signal="medium",
            review_state="pending_review",
        ),
    ]
    session.add_all(actions)
    session.flush()
    print(f"  ✓ {len(actions)} extracted actions created (pending review)")

    # ── Message Classifications (pending review) ─────────────────
    classifications = [
        MessageClassification(
            source_record_id=messages[0].id,
            source_record_type="message",
            selected_project_id=p1.id,
            confidence=0.92,
            ambiguity_flag=False,
            classification_rationale="Message directly references Beta Migration staging environment and validation suite — clear project match.",
            review_state="pending_review",
        ),
        MessageClassification(
            source_record_id=messages[1].id,
            source_record_type="message",
            selected_project_id=p2.id,
            confidence=0.78,
            ambiguity_flag=True,
            classification_rationale="References APAC data sources — likely Gamma Research, but could also relate to Client Portal's regional dashboards.",
            review_state="pending_review",
        ),
        MessageClassification(
            source_record_id=messages[2].id,
            source_record_type="message",
            selected_project_id=p4.id,
            confidence=0.95,
            ambiguity_flag=False,
            classification_rationale="Explicit Q3 budget reference — maps directly to Q3 Budget Review project.",
            review_state="pending_review",
        ),
        MessageClassification(
            source_record_id=messages[3].id,
            source_record_type="message",
            selected_project_id=p3.id,
            confidence=0.88,
            ambiguity_flag=False,
            classification_rationale="Design assets and component library — clearly linked to Client Portal Redesign.",
            review_state="pending_review",
        ),
    ]
    session.add_all(classifications)
    session.flush()
    print(f"  ✓ {len(classifications)} classifications created (pending review)")

    # ── Drafts ───────────────────────────────────────────────────
    d1 = Draft(
        linked_project_id=p1.id,
        source_message_id=messages[0].id,
        source_record_type="message",
        channel_type="email",
        tone_mode="professional",
        body_content="Hi Sarah,\n\nThanks for the update on the staging disk issue. Good to know infra is on it.\n\nOnce we have capacity back, I'll kick off the full validation suite immediately — we need those results before we can lock in the cutover window.\n\nCan you tentatively hold Thursday evening for the maintenance window? I'll confirm once validation passes.\n\nBest,\nTony",
        rationale_summary="Professional reply acknowledging the staging fix and proposing a tentative cutover window.",
        intent_label="reply",
        status="draft",
    )
    d2 = Draft(
        linked_project_id=p2.id,
        source_message_id=messages[1].id,
        source_record_type="message",
        channel_type="email",
        tone_mode="warm",
        body_content="Hey Michael,\n\nGreat progress on the data source review. Let's sync tomorrow at 9am to walk through the Singapore and Jakarta compliance questions — I want to make sure we're not blocking the overall timeline.\n\nI'll pull together the regulatory checklist before our call.\n\nTalk soon,\nTony",
        rationale_summary="Warm follow-up scheduling a call and showing proactive prep for compliance discussion.",
        intent_label="reply",
        status="draft",
    )
    d3 = Draft(
        linked_project_id=p4.id,
        source_message_id=messages[2].id,
        source_record_type="message",
        channel_type="email",
        tone_mode="concise",
        body_content="Finance team — thanks for the status. I'll chase Engineering and Marketing directly today. We'll have the consolidated view ready by Wednesday EOD to give the CFO time to review before Thursday.\n\n—Tony",
        rationale_summary="Concise action-oriented reply committing to follow up on outstanding submissions.",
        intent_label="reply",
        status="draft",
    )
    session.add_all([d1, d2, d3])
    session.flush()

    # ── Draft Variants ───────────────────────────────────────────
    variants = [
        DraftVariant(
            draft_id=d1.id,
            variant_label="concise",
            body_content="Sarah — noted on the disk fix. I'll run validation as soon as capacity is back. Can you hold Thursday evening for the cutover window? Will confirm once results are in. —Tony",
        ),
        DraftVariant(
            draft_id=d2.id,
            variant_label="formal",
            body_content="Dear Michael,\n\nThank you for the thorough review of APAC data sources. I would like to schedule a meeting tomorrow morning at 9:00 to discuss the compliance requirements for the Singapore and Jakarta feeds.\n\nI will prepare a regulatory compliance checklist in advance of our discussion.\n\nKind regards,\nTony",
        ),
    ]
    session.add_all(variants)
    session.flush()
    print(f"  ✓ 3 drafts + {len(variants)} variants created")

    session.commit()
    print("\n  Generating focus pack…")

    # ── Generate Focus Pack ──────────────────────────────────────
    from app.graphs.planner import generate_focus_pack

    result = generate_focus_pack(
        session=session,
        project_ids=[p1.id, p2.id, p3.id, p4.id],
        trigger_type="on_demand",
    )
    session.commit()
    print(f"  ✓ Focus pack generated (ID: {result.focus_pack_id})")

    session.close()
    print("\n✅ Demo data seeded successfully!")
    print("   Open http://localhost:3000/today to see your daily brief.")


if __name__ == "__main__":
    seed()

