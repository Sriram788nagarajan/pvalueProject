
  // Prevent re-initialization across pages
  if (!window.__SUPABASE_CLIENT__) {
    const SUPABASE_URL = "https://aogdsxexwojkhxwtothl.supabase.co";
    const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFvZ2RzeGV4d29qa2h4d3RvdGhsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg0ODczMDQsImV4cCI6MjA4NDA2MzMwNH0.HVcLCc2t-fKf9UrJTOYCv03YU4DI6kLgBAO4kQJM_0o";

    window.__SUPABASE_CLIENT__ = supabase.createClient(
      SUPABASE_URL,
      SUPABASE_ANON_KEY,
      {
        auth: {
          persistSession: true,
          autoRefreshToken: true,
          detectSessionInUrl: false
        }
      }
    );
  }

  window.supabase = window.__SUPABASE_CLIENT__;

