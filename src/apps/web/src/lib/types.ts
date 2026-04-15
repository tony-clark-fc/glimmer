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

export interface FocusPackActionItem {
  item_id: string;
  item_type: "work_item" | "pending_action";
  project_id: string | null;
  priority_score: number;
  rationale: string;
  title: string;
}

export interface FocusPackRiskItem {
  risk_id: string;
  project_id: string;
  summary: string;
  severity: string;
}

export interface FocusPackWaitingItem {
  waiting_id: string;
  project_id: string;
  waiting_on: string;
  description: string;
  expected_by: string | null;
}

export interface FocusPack {
  id: string;
  generated_at: string;
  top_actions: { items: FocusPackActionItem[] } | null;
  high_risk_items: { items: FocusPackRiskItem[] } | null;
  waiting_on_items: { items: FocusPackWaitingItem[] } | null;
  reply_debt_summary: string | null;
  calendar_pressure_summary: string | null;
  narrative_summary: string | null;
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

export interface GlimmerMood {
  mood: "bau" | "happy" | "grumpy" | "thinking" | "worried";
  reason: string;
  portfolio_health: {
    active_projects: number;
    active_blockers: number;
    overdue_items: number;
    high_risks: number;
  };
}

// ── Persona Page ────────────────────────────────────────────────

export type InteractionMode = "voice" | "whisper" | "chat";
export type WorkspaceMode = "idea" | "plan" | "report" | "debrief" | "update";

export interface ChatMessage {
  id: string;
  role: "user" | "glimmer";
  content: string;
  timestamp: string;
  mode?: WorkspaceMode;
}

// ── Research / Chrome Health ────────────────────────────────────

export interface ResearchHealth {
  chrome_status: "available" | "unavailable" | "unknown";
  chrome_port: number;
  chrome_port_open: boolean;
  last_check_at: string | null;
  last_transition_at: string | null;
  consecutive_failures: number;
  monitor_running: boolean;
}

// ── Research Runs ───────────────────────────────────────────────

export interface ResearchRunSummary {
  id: string;
  invocation_origin: string;
  project_id: string | null;
  research_query: string;
  document_name: string | null;
  status: string;
  document_url: string | null;
  error_message: string | null;
  summary_review_state: string | null;
  findings_count: number;
  sources_count: number;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}

export interface ResearchFinding {
  id: string;
  finding_type: string;
  content: string;
  confidence_signal: string | null;
  source_url: string | null;
  ordering: number | null;
  created_at: string;
}

export interface ResearchSourceReference {
  id: string;
  source_url: string | null;
  source_title: string | null;
  source_description: string | null;
  relevance_notes: string | null;
  created_at: string;
}

export interface ResearchSummaryArtifact {
  id: string;
  summary_text: string;
  review_state: string;
  created_at: string;
}

export interface ResearchRunDetail extends ResearchRunSummary {
  findings: ResearchFinding[];
  sources: ResearchSourceReference[];
  summary: ResearchSummaryArtifact | null;
}

// ── Expert Advice Exchanges ─────────────────────────────────────

export interface ExpertAdviceExchange {
  id: string;
  invocation_origin: string;
  project_id: string | null;
  prompt: string;
  gemini_mode: string;
  response_text: string | null;
  duration_ms: number | null;
  status: string;
  review_state: string;
  error_message: string | null;
  created_at: string;
  completed_at: string | null;
}

// ── Connected Accounts / Connectors ─────────────────────────────

export interface ConnectedAccountSummary {
  id: string;
  provider_type: string;
  account_label: string;
  account_address: string | null;
  tenant_context: string | null;
  purpose_label: string | null;
  status: string;
  created_at: string;
  last_sync_at: string | null;
  last_sync_status: string | null;
  last_sync_items: number | null;
  last_error: string | null;
  has_credentials: boolean;
}

export interface AuthUrlResponse {
  auth_url: string;
  state: string;
  provider: string;
}

export interface SyncTriggerResponse {
  account_id: string;
  results: Array<{
    connector_type: string;
    success: boolean;
    items_fetched: number;
    error: string | null;
    duration_ms: number;
  }>;
  overall_success: boolean;
}

export interface ConnectorStatusResponse {
  google_configured: boolean;
  microsoft_configured: boolean;
  accounts: ConnectedAccountSummary[];
  total_accounts: number;
  active_accounts: number;
}

