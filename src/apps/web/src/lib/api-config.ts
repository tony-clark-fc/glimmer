/**
 * Glimmer frontend — API configuration.
 *
 * Provides the base URL for backend API requests.  The value is read
 * from the NEXT_PUBLIC_API_BASE_URL environment variable so that the
 * frontend can target the backend on a different host (LAN IP, VPN
 * address) rather than assuming localhost.
 *
 * Usage:
 *   import { apiBaseUrl } from "@/lib/api-config";
 *   const res = await fetch(`${apiBaseUrl}/health`);
 */

/** Base URL of the Glimmer backend API (no trailing slash). */
export const apiBaseUrl: string =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/+$/, "") ??
  "http://localhost:8000";

