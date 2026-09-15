/**
 * Supabase REST API client (PostgREST).
 *
 * Replaces the direct Postgres (`pg` driver) connection with HTTP calls to the
 * Supabase REST endpoint. This avoids needing a DATABASE_URL or direct TCP
 * access to Postgres — it works entirely through the publishable key already
 * in `.env.local`.
 *
 * The REST endpoint is `https://<project>.supabase.co/rest/v1/<table>`.
 * Authentication is via the `apikey` header (publishable or service-role key).
 *
 * PostgREST conventions used here:
 *   - `select=<columns>`     chooses which columns come back
 *   - `?column=eq.value`     filters (also `in`, `lt`, `gt`, `is`, `like`, …)
 *   - `order=col.asc`        sorting
 *   - `limit=N`              row cap
 *   - `Prefer: return=representation`  makes POST/PATCH return the affected rows
 *   - `Prefer: count=exact`  includes a Content-Range header for counts
 */

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

/**
 * Base URL for the Supabase project (no trailing slash).
 *
 * Read from the environment only. Project identifiers used to be hardcoded as
 * a fallback here, which put a live endpoint and key into the repository and
 * made a misconfigured deployment silently talk to the wrong project instead
 * of failing.
 */
export function supabaseUrl(): string {
  const url =
    process.env.SUPABASE_URL ||
    process.env.NEXT_PUBLIC_SUPABASE_URL ||
    process.env.VITE_SUPABASE_URL;

  if (!url) {
    throw new Error(
      "SUPABASE_URL is not set. Copy .env.example to .env.local and fill it in."
    );
  }
  return url.replace(/\/+$/, "");
}

/**
 * API key for PostgREST.
 *
 * Prefers the SERVICE ROLE key. This module only ever runs server-side, and the
 * service role bypasses Row Level Security - which is what lets RLS deny the
 * anonymous/publishable key outright while the application keeps working.
 *
 * The publishable key is accepted as a fallback so the app still starts, but it
 * is only safe once RLS policies exist: on a table without RLS it grants any
 * anonymous caller full read and write access, including resident names and
 * email addresses.
 */
export function supabaseKey(): string {
  const serviceRole =
    process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_SECRET_KEY;
  if (serviceRole) return serviceRole;

  const publishable =
    process.env.SUPABASE_KEY ||
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY ||
    process.env.VITE_SUPABASE_PUBLISHABLE_KEY;

  if (!publishable) {
    throw new Error(
      "No Supabase key set. Provide SUPABASE_SERVICE_ROLE_KEY (preferred) " +
        "or SUPABASE_KEY in .env.local."
    );
  }

  warnOnceAboutPublishableKey();
  return publishable;
}

let publishableWarningShown = false;
function warnOnceAboutPublishableKey(): void {
  if (publishableWarningShown) return;
  publishableWarningShown = true;
  console.warn(
    "[supabase] Using the publishable (anon) key for server-side access. " +
      "Set SUPABASE_SERVICE_ROLE_KEY and enable RLS - otherwise every table " +
      "is readable and writable by anyone holding this key."
  );
}

/** Full REST base URL. */
function restBaseUrl(): string {
  return `${supabaseUrl()}/rest/v1`;
}

// ---------------------------------------------------------------------------
// Low-level fetch wrapper
// ---------------------------------------------------------------------------

export interface SupabaseQueryParams {
  /** Column list for PostgREST `select` (e.g. "*" or "id,reference,status"). */
  select?: string;
  /** Filter params, e.g. { status: "eq.Submitted", id: "eq.r-123" }. */
  filters?: Record<string, string>;
  /** Order, e.g. "created_at.asc". */
  order?: string;
  /** Row limit. */
  limit?: number;
  /** Offset for pagination. */
  offset?: number;
}

/**
 * Core REST call. Returns parsed JSON (or null for empty responses).
 *
 * For GET requests, filters/order/limit are encoded as query params.
 * For POST/PATCH/DELETE, the body is JSON and `Prefer` headers control
 * whether the affected rows are returned.
 */
export async function supabaseFetch<T = unknown>(
  table: string,
  method: "GET" | "POST" | "PATCH" | "DELETE" = "GET",
  body?: unknown,
  params?: SupabaseQueryParams
): Promise<T> {
  const url = new URL(`${restBaseUrl()}/${table}`);

  const headers: Record<string, string> = {
    apikey: supabaseKey(),
    "Content-Type": "application/json",
  };

  if (method === "GET" && params) {
    if (params.select) url.searchParams.set("select", params.select);
    if (params.order) url.searchParams.set("order", params.order);
    if (params.limit != null) url.searchParams.set("limit", String(params.limit));
    if (params.offset != null) url.searchParams.set("offset", String(params.offset));
  }

  // Filters apply to GET, PATCH, and DELETE — PostgREST requires a WHERE
  // clause for PATCH/DELETE, supplied as query params (e.g. ?id=eq.123).
  if (params?.filters) {
    for (const [key, value] of Object.entries(params.filters)) {
      url.searchParams.set(key, value);
    }
  }

  if (method === "POST" || method === "PATCH") {
    headers["Prefer"] = "return=representation";
  }

  const response = await fetch(url.toString(), {
    method,
    headers,
    body: body !== undefined && method !== "GET" ? JSON.stringify(body) : undefined,
    cache: "no-store",
  });

  if (!response.ok) {
    const text = await response.text().catch(() => "");
    throw new Error(
      `Supabase REST ${method} ${table} failed (${response.status}): ${text}`
    );
  }

  // 204 No Content or empty body
  if (response.status === 204) return undefined as T;
  const text = await response.text();
  if (!text) return undefined as T;
  return JSON.parse(text) as T;
}

/**
 * Fetches a single row by exact-match filters. Returns null if no match.
 */
export async function supabaseFetchOne<T = unknown>(
  table: string,
  params: SupabaseQueryParams
): Promise<T | null> {
  const rows = await supabaseFetch<T[]>(table, "GET", undefined, {
    ...params,
    limit: 1,
  });
  return rows && rows.length > 0 ? rows[0] : null;
}

/**
 * Gets the total count of rows matching a filter, using the `Prefer: count=exact`
 * header and parsing the Content-Range response header.
 */
export async function supabaseCount(
  table: string,
  filters?: Record<string, string>
): Promise<number> {
  const url = new URL(`${restBaseUrl()}/${table}`);
  url.searchParams.set("select", "id");
  if (filters) {
    for (const [key, value] of Object.entries(filters)) {
      url.searchParams.set(key, value);
    }
  }
  url.searchParams.set("limit", "1");

  const response = await fetch(url.toString(), {
    method: "GET",
    headers: {
      apikey: supabaseKey(),
      "Content-Type": "application/json",
      Prefer: "count=exact",
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const text = await response.text().catch(() => "");
    throw new Error(
      `Supabase count ${table} failed (${response.status}): ${text}`
    );
  }

  // Content-Range: 0-0/42  or  0-0/*
  const range = response.headers.get("content-range") ?? "";
  const match = range.match(/\/(\d+)$/);
  return match ? parseInt(match[1], 10) : 0;
}

// ---------------------------------------------------------------------------
// Compatibility shims (so existing imports don't break)
// ---------------------------------------------------------------------------

/**
 * No-op — tables already exist in Supabase. Kept so `ensureSchema()` calls
 * in the codebase don't crash.
 */
export async function ensureSchema(): Promise<void> {
  // Tables are managed in Supabase dashboard; nothing to do here.
}

/** No-op for REST API — no pool to close. */
export async function closePool(): Promise<void> {
  // No persistent connection to close with REST API.
}

/** No-op — can't drop tables via REST API. */
export async function dropAll(): Promise<void> {
  console.warn("dropAll() is not supported via Supabase REST API.");
}

// ---------------------------------------------------------------------------
// Connection settings (kept for check.ts compatibility, but not used for REST)
// ---------------------------------------------------------------------------

export interface ConnectionSettings {
  connectionString: string | undefined;
  ssl: { rejectUnauthorized: boolean } | false;
}

export function connectionSettings(): ConnectionSettings {
  return {
    connectionString: undefined,
    ssl: false,
  };
}
