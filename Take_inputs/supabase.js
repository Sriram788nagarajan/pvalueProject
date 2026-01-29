import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const SUPABASE_URL = "https://aogdsxexwojkhxwtothl.supabase.co";
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFvZ2RzeGV4d29qa2h4d3RvdGhsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg0ODczMDQsImV4cCI6MjA4NDA2MzMwNH0.HVcLCc2t-fKf9UrJTOYCv03YU4DI6kLgBAO4kQJM_0o";

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// THIS IS WHAT MAKES IT WORK
window.supabase = supabase;
