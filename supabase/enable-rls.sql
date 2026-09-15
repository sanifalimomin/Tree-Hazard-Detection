-- Lock down the tables.
--
-- WHAT THIS FIXES
-- Without Row Level Security, the publishable ("anon") key grants anyone who
-- holds it full read and write access to every table - including
-- requests.reporter_name and requests.reporter_email. That key is designed to
-- be public: it ships in browser bundles. RLS, not key secrecy, is what makes
-- it safe.
--
-- HOW THE APP KEEPS WORKING
-- All database access in this app is server-side. The server authenticates
-- with the SERVICE ROLE key, which bypasses RLS by design. So enabling RLS with
-- no anon policies denies the public key everything while the application is
-- unaffected.
--
-- Run with:  npm run db:secure

-- 1. Turn RLS on. With no policies attached, this denies anon and authenticated
--    callers outright. service_role is unaffected.
ALTER TABLE requests       ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessments    ENABLE ROW LEVEL SECURITY;
ALTER TABLE images         ENABLE ROW LEVEL SECURITY;
ALTER TABLE status_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback       ENABLE ROW LEVEL SECURITY;

-- 2. FORCE applies RLS even to the table owner, so a future connection as the
--    owning role cannot quietly sidestep it. service_role still bypasses.
ALTER TABLE requests       FORCE ROW LEVEL SECURITY;
ALTER TABLE assessments    FORCE ROW LEVEL SECURITY;
ALTER TABLE images         FORCE ROW LEVEL SECURITY;
ALTER TABLE status_history FORCE ROW LEVEL SECURITY;
ALTER TABLE feedback       FORCE ROW LEVEL SECURITY;

-- 3. Belt and braces: remove the table-level grants PostgREST relies on, so the
--    anon role is refused before RLS is even consulted. Defence in depth
--    against a policy being added carelessly later.
REVOKE ALL ON requests, assessments, images, status_history, feedback
  FROM anon, authenticated;

-- 4. Drop any policy an earlier attempt may have left behind, so re-running
--    this file is idempotent and cannot leave a stray permissive rule.
DO $$
DECLARE
  p RECORD;
BEGIN
  FOR p IN
    SELECT schemaname, tablename, policyname
      FROM pg_policies
     WHERE schemaname = 'public'
       AND tablename IN
           ('requests', 'assessments', 'images', 'status_history', 'feedback')
  LOOP
    EXECUTE format(
      'DROP POLICY IF EXISTS %I ON %I.%I',
      p.policyname, p.schemaname, p.tablename
    );
  END LOOP;
END $$;

-- NOTE FOR LATER
-- If any part of the app ever needs to read from the browser directly, add a
-- narrow policy here rather than loosening the above - and never expose
-- reporter_name or reporter_email to the anon role.
