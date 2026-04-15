"use client";

import { Suspense, useEffect, useState, useCallback } from "react";
import { useSearchParams } from "next/navigation";
import {
  fetchConnectorStatus,
  getGoogleAuthUrl,
  getMicrosoftAuthUrl,
  triggerSync,
  deleteConnectedAccount,
} from "@/lib/api-client";
import {
  PageHeader,
  SectionCard,
  CardSkeleton,
  EmptyState,
  ErrorState,
  Badge,
  ActionButton,
  InfoBanner,
} from "@/components/ui";
import type { ConnectedAccountSummary, ConnectorStatusResponse } from "@/lib/types";

type LoadState = "loading" | "loaded" | "error";

export default function ConnectorsPageWrapper() {
  return (
    <Suspense fallback={<CardSkeleton testId="connectors-loading" count={2} />}>
      <ConnectorsPage />
    </Suspense>
  );
}

function ConnectorsPage() {
  const searchParams = useSearchParams();
  const connected = searchParams.get("connected");
  const connectedAccount = searchParams.get("account");

  const [status, setStatus] = useState<ConnectorStatusResponse | null>(null);
  const [state, setState] = useState<LoadState>("loading");
  const [error, setError] = useState<string | null>(null);
  const [syncing, setSyncing] = useState<Set<string>>(new Set());
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const load = useCallback(() => {
    setState("loading");
    fetchConnectorStatus()
      .then((data) => {
        setStatus(data);
        setState("loaded");
      })
      .catch((err) => {
        setError(err.message ?? "Failed to load connector status");
        setState("error");
      });
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  // Show success toast when redirected from OAuth callback
  useEffect(() => {
    if (connected && connectedAccount) {
      const provider = connected === "google" ? "Google" : "Microsoft";
      setSuccessMsg(`Successfully connected ${provider} account: ${connectedAccount}`);
      // Clear after 5 seconds
      const timer = setTimeout(() => setSuccessMsg(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [connected, connectedAccount]);

  const handleConnectGoogle = async () => {
    try {
      const { auth_url } = await getGoogleAuthUrl();
      window.location.href = auth_url;
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to get Google auth URL";
      setError(msg);
    }
  };

  const handleConnectMicrosoft = async () => {
    try {
      const { auth_url } = await getMicrosoftAuthUrl();
      window.location.href = auth_url;
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to get Microsoft auth URL";
      setError(msg);
    }
  };

  const handleSync = async (accountId: string) => {
    setSyncing((prev) => new Set(prev).add(accountId));
    try {
      await triggerSync(accountId);
      load(); // Reload to see updated sync status
    } catch {
      // Reload anyway to see error state
      load();
    } finally {
      setSyncing((prev) => {
        const next = new Set(prev);
        next.delete(accountId);
        return next;
      });
    }
  };

  const handleDisconnect = async (accountId: string) => {
    if (!confirm("Disconnect this account? Stored tokens will be cleared.")) return;
    try {
      await deleteConnectedAccount(accountId);
      load();
    } catch {
      load();
    }
  };

  return (
    <div data-testid="page-settings-connectors">
      <PageHeader
        title="Connectors"
        description="Connect your Google and Microsoft accounts to enable mail and calendar ingestion."
      />

      {/* Success toast */}
      {successMsg && (
        <div className="mb-6">
          <InfoBanner variant="success" testId="connector-success">
            ✓ {successMsg}
          </InfoBanner>
        </div>
      )}

      {state === "loading" && <CardSkeleton testId="connectors-loading" count={2} />}

      {state === "error" && (
        <ErrorState testId="connectors-error" message={error ?? "Failed to load"} />
      )}

      {state === "loaded" && status && (
        <div className="space-y-8">
          {/* Add Account section */}
          <SectionCard testId="connector-add" title="Connect an Account">
            <div className="flex flex-wrap gap-3">
              <button
                data-testid="connect-google"
                onClick={handleConnectGoogle}
                disabled={!status.google_configured}
                className="flex items-center gap-3 rounded-2xl bg-surface-container-lowest px-5 py-3.5 ghost-border hover:bg-surface-container-high/50 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <GoogleIcon />
                <div className="text-left">
                  <p className="text-sm font-bold text-foreground">Google</p>
                  <p className="text-xs text-muted-light">
                    {status.google_configured
                      ? "Gmail & Calendar (read-only)"
                      : "Not configured — set OAuth credentials"}
                  </p>
                </div>
              </button>

              <button
                data-testid="connect-microsoft"
                onClick={handleConnectMicrosoft}
                disabled={!status.microsoft_configured}
                className="flex items-center gap-3 rounded-2xl bg-surface-container-lowest px-5 py-3.5 ghost-border hover:bg-surface-container-high/50 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <MicrosoftIcon />
                <div className="text-left">
                  <p className="text-sm font-bold text-foreground">Microsoft</p>
                  <p className="text-xs text-muted-light">
                    {status.microsoft_configured
                      ? "Outlook Mail & Calendar (read-only)"
                      : "Not configured — set OAuth credentials"}
                  </p>
                </div>
              </button>
            </div>

            {!status.google_configured && !status.microsoft_configured && (
              <div className="mt-4">
                <InfoBanner variant="warning" testId="no-oauth-warning">
                  ⚠ No OAuth credentials configured. Set GLIMMER_GOOGLE_OAUTH_* and/or
                  GLIMMER_MICROSOFT_OAUTH_* environment variables in your backend .env file.
                </InfoBanner>
              </div>
            )}
          </SectionCard>

          {/* Connected Accounts */}
          {status.accounts.length === 0 ? (
            <EmptyState
              testId="connectors-empty"
              icon="🔗"
              message="No accounts connected yet. Use the buttons above to connect a Google or Microsoft account."
            />
          ) : (
            <SectionCard
              testId="connector-accounts"
              title="Connected Accounts"
              count={status.accounts.length}
            >
              <ul className="space-y-3">
                {status.accounts.map((account) => (
                  <AccountCard
                    key={account.id}
                    account={account}
                    isSyncing={syncing.has(account.id)}
                    onSync={() => handleSync(account.id)}
                    onDisconnect={() => handleDisconnect(account.id)}
                  />
                ))}
              </ul>
            </SectionCard>
          )}
        </div>
      )}
    </div>
  );
}

// ── Account Card ────────────────────────────────────────────────

function AccountCard({
  account,
  isSyncing,
  onSync,
  onDisconnect,
}: {
  account: ConnectedAccountSummary;
  isSyncing: boolean;
  onSync: () => void;
  onDisconnect: () => void;
}) {
  const isActive = account.status === "active";
  const hasCredentials = account.has_credentials;

  return (
    <li
      data-testid={`connector-account-${account.id}`}
      className="rounded-2xl bg-surface-container-lowest p-5 ghost-border"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-3">
            {account.provider_type === "google" ? <GoogleIcon /> : <MicrosoftIcon />}
            <div>
              <p className="text-sm font-bold text-foreground">{account.account_label}</p>
              {account.account_address && (
                <p className="text-xs text-muted-light font-mono">{account.account_address}</p>
              )}
            </div>
          </div>

          <div className="mt-3 flex flex-wrap gap-2 text-xs">
            <StatusBadge status={account.status} />
            {hasCredentials && <Badge variant="success">Credentials ✓</Badge>}
            {!hasCredentials && isActive && <Badge variant="warning">No credentials</Badge>}
            {account.tenant_context && (
              <Badge variant="neutral">Tenant: {account.tenant_context}</Badge>
            )}
          </div>

          {/* Sync info */}
          {account.last_sync_at && (
            <div className="mt-2 text-xs text-muted-light">
              <span>
                Last sync: {new Date(account.last_sync_at).toLocaleString()} —{" "}
              </span>
              <SyncStatusLabel status={account.last_sync_status} />
              {account.last_sync_items !== null && (
                <span> ({account.last_sync_items} items)</span>
              )}
            </div>
          )}

          {account.last_error && (
            <div className="mt-1 text-xs text-error">Error: {account.last_error}</div>
          )}
        </div>

        {/* Actions */}
        <div className="flex gap-1 shrink-0">
          {isActive && hasCredentials && (
            <ActionButton
              variant="success"
              testId={`sync-${account.id}`}
              onClick={onSync}
            >
              {isSyncing ? "Syncing…" : "Sync Now"}
            </ActionButton>
          )}
          <ActionButton
            variant="danger"
            testId={`disconnect-${account.id}`}
            onClick={onDisconnect}
          >
            Disconnect
          </ActionButton>
        </div>
      </div>
    </li>
  );
}

// ── Status helpers ──────────────────────────────────────────────

function StatusBadge({ status }: { status: string }) {
  const variant = {
    active: "success" as const,
    pending: "warning" as const,
    revoked: "danger" as const,
    error: "danger" as const,
  }[status] ?? ("neutral" as const);

  return <Badge variant={variant}>{status}</Badge>;
}

function SyncStatusLabel({ status }: { status: string | null }) {
  if (!status) return <span>Unknown</span>;
  const color = {
    success: "text-emerald-400",
    partial: "text-tertiary",
    failed: "text-error",
  }[status] ?? "text-muted-light";

  return <span className={color}>{status}</span>;
}

// ── Provider Icons ──────────────────────────────────────────────

function GoogleIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" className="shrink-0">
      <path
        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"
        fill="#4285F4"
      />
      <path
        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
        fill="#34A853"
      />
      <path
        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
        fill="#FBBC05"
      />
      <path
        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
        fill="#EA4335"
      />
    </svg>
  );
}

function MicrosoftIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" className="shrink-0">
      <rect x="1" y="1" width="10" height="10" fill="#F25022" />
      <rect x="13" y="1" width="10" height="10" fill="#7FBA00" />
      <rect x="1" y="13" width="10" height="10" fill="#00A4EF" />
      <rect x="13" y="13" width="10" height="10" fill="#FFB900" />
    </svg>
  );
}



