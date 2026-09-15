/**
 * Applies supabase/enable-rls.sql and then proves it worked: `npm run db:secure`
 *
 * The verification matters more than the migration. Turning RLS on is one
 * statement; confirming that the publishable key can no longer read resident
 * names is the part that tells you the hole is actually closed.
 */

import fs from "node:fs";
import path from "node:path";

import { Client } from "pg";

import { connectionSettings } from "@/backend/db/client";

const RESET = "\x1b[0m";
const RED = "\x1b[31m";
const GREEN = "\x1b[32m";
const YELLOW = "\x1b[33m";
const DIM = "\x1b[2m";

const TABLES = ["requests", "assessments", "images", "status_history", "feedback"];

/** Reads a table with the anon key, the way an outsider would. */
async function anonCanRead(
  url: string,
  key: string,
  table: string
): Promise<{ readable: boolean; sample: string }> {
  try {
    const response = await fetch(
      `${url}/rest/v1/${table}?select=*&limit=1`,
      { headers: { apikey: key, Authorization: `Bearer ${key}` } }
    );
    if (!response.ok) return { readable: false, sample: `HTTP ${response.status}` };

    const rows = (await response.json()) as unknown[];
    return { readable: Array.isArray(rows) && rows.length > 0, sample: "" };
  } catch (error) {
    return { readable: false, sample: (error as Error).message };
  }
}

async function main(): Promise<void> {
  const settings = connectionSettings();
  if (!settings.connectionString) {
    console.error(`${RED}DATABASE_URL is not set.${RESET}`);
    console.error(
      "\nApplying RLS needs a direct Postgres connection (the REST API cannot\n" +
        "run DDL). Use the Supabase Session pooler connection string."
    );
    process.exit(1);
  }

  const url = process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL;
  const anonKey =
    process.env.SUPABASE_KEY ||
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY ||
    process.env.VITE_SUPABASE_PUBLISHABLE_KEY;

  // --- before -------------------------------------------------------------
  if (url && anonKey) {
    console.log("Before:");
    for (const table of TABLES) {
      const { readable } = await anonCanRead(url, anonKey, table);
      console.log(
        `  ${table.padEnd(16)} anon read: ${
          readable ? `${RED}YES${RESET}` : `${GREEN}no${RESET}`
        }`
      );
    }
    console.log("");
  }

  // --- apply --------------------------------------------------------------
  const sqlPath = path.resolve(process.cwd(), "supabase/enable-rls.sql");
  const sql = fs.readFileSync(sqlPath, "utf8");

  const client = new Client({
    connectionString: settings.connectionString,
    ssl: settings.ssl,
    connectionTimeoutMillis: 15_000,
  });

  try {
    await client.connect();
    await client.query(sql);
    console.log(`${GREEN}Applied${RESET} supabase/enable-rls.sql`);

    const status = await client.query<{ relname: string; relrowsecurity: boolean }>(
      `SELECT c.relname, c.relrowsecurity
         FROM pg_class c
         JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public' AND c.relname = ANY($1)
        ORDER BY c.relname`,
      [TABLES]
    );
    console.log("");
    for (const row of status.rows) {
      console.log(
        `  ${row.relname.padEnd(16)} RLS ${
          row.relrowsecurity ? `${GREEN}enabled${RESET}` : `${RED}OFF${RESET}`
        }`
      );
    }
    await client.end();
  } catch (error) {
    console.error(`${RED}FAILED${RESET} ${(error as Error).message}`);
    await client.end().catch(() => {});
    process.exit(1);
  }

  // --- after --------------------------------------------------------------
  if (url && anonKey) {
    console.log("\nAfter:");
    let stillOpen = 0;
    for (const table of TABLES) {
      const { readable } = await anonCanRead(url, anonKey, table);
      if (readable) stillOpen += 1;
      console.log(
        `  ${table.padEnd(16)} anon read: ${
          readable ? `${RED}STILL YES${RESET}` : `${GREEN}denied${RESET}`
        }`
      );
    }

    if (stillOpen > 0) {
      console.error(
        `\n${RED}${stillOpen} table(s) are still readable with the publishable key.${RESET}`
      );
      process.exit(1);
    }
    console.log(`\n${GREEN}All tables denied to the publishable key.${RESET}`);
  }

  if (!process.env.SUPABASE_SERVICE_ROLE_KEY && !process.env.SUPABASE_SECRET_KEY) {
    console.log(
      `\n${YELLOW}WARNING${RESET} SUPABASE_SERVICE_ROLE_KEY is not set.\n` +
        `${DIM}RLS is now on, so the app cannot read its own data with the\n` +
        `publishable key. Add the service role key to .env.local:\n` +
        `  Supabase Dashboard -> Project Settings -> API -> service_role${RESET}`
    );
  }
}

main();
