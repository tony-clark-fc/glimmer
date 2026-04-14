/**
 * Glimmer frontend — API client utilities.
 *
 * Thin typed fetch wrappers over the backend REST API.
 * All fetches are explicit — no hidden caching or mutation.
 */

import { apiBaseUrl } from "./api-config";
import type {
  ProjectSummary,
  ProjectDetail,
  ReviewQueue,
  FocusPack,
  DraftSummary,
  DraftDetail,
  PersonaSelection,
  ResearchHealth,
  ResearchRunSummary,
  ResearchRunDetail,
  ExpertAdviceExchange,
} from "./types";

// ── Generic fetch helper ────────────────────────────────────────

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${apiBaseUrl}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new ApiError(res.status, text || res.statusText);
  }

  return res.json() as Promise<T>;
}

export class ApiError extends Error {
  constructor(
    public status: number,
    public body: string,
  ) {
    super(`API ${status}: ${body}`);
    this.name = "ApiError";
  }
}

// ── Projects ────────────────────────────────────────────────────

export async function fetchProjects(): Promise<ProjectSummary[]> {
  return apiFetch<ProjectSummary[]>("/projects");
}

export async function fetchProject(id: string): Promise<ProjectDetail> {
  return apiFetch<ProjectDetail>(`/projects/${id}`);
}

// ── Triage / Review ─────────────────────────────────────────────

export async function fetchReviewQueue(): Promise<ReviewQueue> {
  return apiFetch<ReviewQueue>("/triage/review-queue");
}

export async function reviewClassification(
  id: string,
  action: "accepted" | "rejected" | "amended",
  amendedText?: string,
): Promise<void> {
  await apiFetch(`/triage/classifications/${id}/review`, {
    method: "PATCH",
    body: JSON.stringify({ action, amended_text: amendedText }),
  });
}

export async function reviewAction(
  id: string,
  action: "accepted" | "rejected" | "amended",
  amendedText?: string,
): Promise<void> {
  await apiFetch(`/triage/actions/${id}/review`, {
    method: "PATCH",
    body: JSON.stringify({ action, amended_text: amendedText }),
  });
}

// ── Focus Pack ──────────────────────────────────────────────────

export async function fetchLatestFocusPack(): Promise<FocusPack> {
  return apiFetch<FocusPack>("/triage/focus-pack/latest");
}

// ── Drafts ──────────────────────────────────────────────────────

export async function fetchDrafts(): Promise<DraftSummary[]> {
  return apiFetch<DraftSummary[]>("/drafts");
}

export async function fetchDraft(id: string): Promise<DraftDetail> {
  return apiFetch<DraftDetail>(`/drafts/${id}`);
}

// ── Persona ─────────────────────────────────────────────────────

export async function fetchPersona(
  context?: string,
): Promise<PersonaSelection> {
  const params = context ? `?context=${encodeURIComponent(context)}` : "";
  return apiFetch<PersonaSelection>(`/persona/select${params}`);
}

// ── Research / Chrome Health ────────────────────────────────────

export async function fetchResearchHealth(): Promise<ResearchHealth> {
  return apiFetch<ResearchHealth>("/health/research");
}

// ── Research Runs ───────────────────────────────────────────────

export async function fetchResearchRuns(): Promise<ResearchRunSummary[]> {
  return apiFetch<ResearchRunSummary[]>("/research/runs");
}

export async function fetchResearchRun(id: string): Promise<ResearchRunDetail> {
  return apiFetch<ResearchRunDetail>(`/research/runs/${id}`);
}

export async function reviewResearchSummary(
  runId: string,
  action: "accepted" | "rejected",
): Promise<void> {
  await apiFetch(`/research/runs/${runId}/summary/review`, {
    method: "PATCH",
    body: JSON.stringify({ action }),
  });
}

// ── Expert Advice Exchanges ─────────────────────────────────────

export async function fetchExchanges(): Promise<ExpertAdviceExchange[]> {
  return apiFetch<ExpertAdviceExchange[]>("/research/exchanges");
}

export async function fetchExchange(id: string): Promise<ExpertAdviceExchange> {
  return apiFetch<ExpertAdviceExchange>(`/research/exchanges/${id}`);
}

export async function reviewExchange(
  exchangeId: string,
  action: "accepted" | "rejected",
): Promise<void> {
  await apiFetch(`/research/exchanges/${exchangeId}/review`, {
    method: "PATCH",
    body: JSON.stringify({ action }),
  });
}

