import { createClient } from "https://cdn.jsdelivr.net/npm/@supabase/supabase-js/+esm";

/**
 * Frontend Supabase client
 * - Used ONLY in browser
 * - Uses anon public key
 */

export const supabase = createClient(
  "https://aogdsxexwojkhxwtothl.supabase.co",
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFvZ2RzeGV4d29qa2h4d3RvdGhsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg0ODczMDQsImV4cCI6MjA4NDA2MzMwNH0.HVcLCc2t-fKf9UrJTOYCv03YU4DI6kLgBAO4kQJM_0o"
);

//  DEV ONLY — allow inspection from console
if (location.hostname === "127.0.0.1" || location.hostname === "localhost") {
  window.supabase = supabase;
}
