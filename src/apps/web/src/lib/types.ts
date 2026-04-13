/**
 * Glimmer frontend — shared TypeScript types for backend API contracts.
 *
 * These mirror the Pydantic response models from the backend.
 * Keep in sync with app/api/*.py response contracts.
 */

// ── Projects ────────────────────────────────────────────────────

export interface ProjectSummary {
  id: string;
  name: string;
  status: string;
  objective: string | null;
  short_summary: string | null;
  open_items: number;
  active_blockers: number;
  pending_actions: number;
  created_at: string;
}

export interface ProjectDetail {
  id: string;
  name: string;
  status: string;
  objective: string | null;
  short_summary: string | null;
  phase: string | null;
  priority_band: string | null;
  created_at: string;
  updated_at: string;
  open_items: Array<{
    id: string;
    title: string;
    status: string;
    due_date: string | null;
  }>;
  blockers: Array<{ id: string; summary: string }>;
  waiting_on: Array<{
    id: string;
    waiting_on: string;
    description: string;
  }>;
  pending_actions: Array<{
    id: string;
    action_text: string;
    urgency: string | null;
  }>;
}

// ── Triage / Review ─────────────────────────────────────────────

export interface ClassificationItem {
  id: string;
  source_record_id: string;
  source_record_type: string;
  selected_project_id: string | null;
  confidence: number | null;
  ambiguity_flag: boolean;
  classification_rationale: string | null;
  review_state: string;
  created_at: string;
}

export interface ExtractedActionItem {
  id: string;
  source_record_id: string;
  source_record_type: string;
  linked_project_id: string | null;
  action_text: string;
  urgency_signal: string | null;
  review_state: string;
  created_at: string;
}

export interface ReviewQueue {
  classifications: ClassificationItem[];
  actions: ExtractedActionItem[];
  total_pending: number;
}

// ── Focus Pack ──────────────────────────────────────────────────

export interface FocusPack {
  id: string;
  generated_at: string;
  top_actions: Record<string, unknown> | null;
  high_risk_items: Record<string, unknown> | null;
  waiting_on_items: Record<string, unknown> | null;
  reply_debt_summary: string | null;
  calendar_pressure_summary: string | null;
}

// ── Drafts ──────────────────────────────────────────────────────

export interface DraftSummary {
  id: string;
  intent_label: string | null;
  channel_type: string | null;
  tone_mode: string | null;
  status: string;
  body_content: string;
  rationale_summary: string | null;
  linked_project_id: string | null;
  created_at: string;
}

export interface DraftVariant {
  id: string;
  variant_label: string;
  body_content: string;
  created_at: string;
}

export interface DraftDetail extends DraftSummary {
  linked_stakeholder_ids: Record<string, unknown> | null;
  source_message_id: string | null;
  source_record_type: string | null;
  version_number: number;
  updated_at: string;
  variants: DraftVariant[];
}

// ── Persona ─────────────────────────────────────────────────────

export interface PersonaClassification {
  classification_type: string;
  classification_value: string;
}

export interface PersonaAsset {
  id: string;
  label: string;
  asset_path: string;
  asset_type: string;
  is_default: boolean;
  classifications: PersonaClassification[];
}

export interface PersonaSelection {
  asset: PersonaAsset | null;
  selection_reason: string;
  fallback_used: boolean;
}

