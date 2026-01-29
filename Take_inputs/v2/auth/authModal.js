    import { supabase } from "../lib/supabaseClient.js";

   

    let mode = "signin";
    let pendingAction = null;

    function showAuthError(message) {
    const el = document.getElementById("auth-error");
    if (!el) return;

    el.innerText = message;
    el.classList.remove("hidden");
    }

    function clearAuthError() {
    const el = document.getElementById("auth-error");
    if (el) el.classList.add("hidden");
    }

    function setAuthLoading(isLoading, label = "Continue") {
  const btn = document.getElementById("auth-submit-btn");
  if (!btn) return;

  btn.disabled = isLoading;
  btn.innerText = isLoading ? label : "Continue";
}



    export function openAuthModal() {
    mode = "signin";

    document.getElementById("auth-title").innerText = "Sign in";
    document.getElementById("auth-switch-text").innerText = "New user?";

    clearAuthError();

    document.getElementById("auth-modal").classList.remove("hidden");
    }

    export function closeAuthModal() {
    document.getElementById("auth-modal").classList.add("hidden");
    }

    export function toggleAuthMode() {
    mode = mode === "signin" ? "signup" : "signin";

    document.getElementById("auth-title").innerText =
        mode === "signin" ? "Sign in" : "Sign up";

    document.getElementById("auth-switch-text").innerText =
        mode === "signin"
        ? "New user?"
        : "Already have an account?";

    document.querySelector(".auth-switch a").innerText =
    mode === "signin" ? "Sign up" : "Sign in";
    }

    export async function submitAuth() {
    setAuthLoading(true, mode === "signin" ? "Signing in…" : "Creating account…");
    const email = document.getElementById("auth-email").value.trim();
    const password = document.getElementById("auth-password").value;

    clearAuthError();

    if (!email || !password) {
        showAuthError("Please enter both email and password.");
        setAuthLoading(false);
        return;
    }

    // ---------------- SIGN IN ----------------
    if (mode === "signin") {
        const { error } = await supabase.auth.signInWithPassword({
        email,
        password
        });

        if (error) {
        showAuthError(
          "Unable to sign in. Please check your details or try another sign-in method."
        );
        setAuthLoading(false);
        return;
        }

        closeAuthModal();
        setAuthLoading(false);
        if (pendingAction) pendingAction();
        return;
    }

    // ---------------- SIGN UP ----------------

    // Step 1: attempt sign-in to detect existing account
    const { error: signInError } =
        await supabase.auth.signInWithPassword({
        email,
        password
        });

    if (!signInError) {
        showAuthError(
        "An account may already exist. Please try signing in instead."
        );

        mode = "signin";
        document.getElementById("auth-title").innerText = "Sign in";
        document.getElementById("auth-switch-text").innerText = "New user?";
        document.querySelector(".auth-switch a").innerText = "Sign up";
        setAuthLoading(false);
        return;
    }

    // Step 2: create new account
    const { error: signUpError } =
        await supabase.auth.signUp({
        email,
        password
        });

    if (signUpError) {
        showAuthError(
        "Unable to create account. Please try again or use a different sign-in method."
        );
        setAuthLoading(false);
        return;
    }

    // Step 3: verification screen
    showVerificationState(email);
    }




    export async function signInWithGoogle() {
    await supabase.auth.signInWithOAuth({
        provider: "google",
    });
    }

    export async function requireAuthThen(action) {
    const { data } = await supabase.auth.getSession();

    if (data.session) {
        action();
    } else {
        pendingAction = action;
        openAuthModal();
    }
    }

    


    export function initAuthUI() {
    supabase.auth.onAuthStateChange((_event, session) => {
        const authArea = document.getElementById("auth-area");
        if (!authArea) return;

        if (!session) {
        authArea.innerHTML = `
            <button class="nav-secondary-btn" onclick="openAuthModal()">
            Sign in
            </button>
        `;
        return;
        }

        const user = session.user;
        const email = user.email || "";
        const avatarUrl = user.user_metadata?.avatar_url;

        let avatarContent = "";

        if (avatarUrl) {
        avatarContent = `<img src="${avatarUrl}" alt="avatar" />`;
        } else {
        const initial = email.charAt(0).toUpperCase();
        avatarContent = `<span>${initial}</span>`;
        }

        authArea.innerHTML = `
        <div class="auth-avatar-wrapper">
            <div class="auth-avatar" onclick="toggleAccountMenu()">
            ${avatarContent}
            </div>

            <div id="account-menu" class="account-menu hidden">
            <div class="account-email">${email}</div>
            <div class="account-divider"></div>
            <button class="account-signout" onclick="signOut()">Sign out</button>
            </div>
        </div>
        `;
    });
    }

    window.toggleAccountMenu = () => {
    const menu = document.getElementById("account-menu");
    if (menu) menu.classList.toggle("hidden");
    };

    function showVerificationState(email) {
  const card = document.querySelector(".auth-card");

  if (!card) return;

  card.innerHTML = `
    <h2>Verify your email</h2>

    <p style="margin-top: 12px; color: #4b5563; font-size: 14px;">
      We’ve sent a verification link to:
    </p>

    <p style="font-weight: 600; margin: 6px 0 18px;">
      ${email}
    </p>

    <p style="font-size: 13px; color: #6b7280;">
      Please check your inbox and click the link to activate your account.
    </p>

    <button class="nav-secondary-btn" style="margin-top: 20px;" onclick="closeAuthModal()">
      Close
    </button>
  `;
}

    window.openAuthModal = openAuthModal;
    window.closeAuthModal = closeAuthModal;
    window.toggleAuthMode = toggleAuthMode;
    window.submitAuth = submitAuth;
    window.signInWithGoogle = signInWithGoogle;

    window.signOut = async () => {
    await supabase.auth.signOut();
    location.reload();
    };
