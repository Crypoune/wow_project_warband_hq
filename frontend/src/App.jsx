import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Récupère l'utilisateur à partir de la session conservée par le backend.
  useEffect(() => {
    async function fetchCurrentUser() {
      try {
        const response = await fetch(`${API_URL}/api/auth/me`, {
          credentials: "include",
        });

        if (response.status === 401) {
          setUser(null);
          return;
        }

        if (!response.ok) {
          throw new Error("Unable to retrieve your profile.");
        }

        const data = await response.json();
        setUser(data);

        // Retire le paramètre OAuth de l'URL après le retour de Blizzard.
        const url = new URL(window.location.href);

        if (url.searchParams.has("auth")) {
          url.searchParams.delete("auth");
          window.history.replaceState({}, "", url);
        }
      } catch {
        setError("Unable to contact Warband HQ. Please try again.");
      } finally {
        setLoading(false);
      }
    }

    fetchCurrentUser();
  }, []);

  // Lance le parcours OAuth Blizzard.
  const handleBlizzardLogin = () => {
    window.location.href = `${API_URL}/api/auth/login`;
  };

  // Termine la session côté backend, puis revient à l'écran de connexion.
  const handleLogout = async () => {
    setError("");

    try {
      const response = await fetch(`${API_URL}/api/auth/logout`, {
        method: "POST",
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error("Logout failed.");
      }

      setUser(null);
    } catch {
      setError("Unable to log out. Please try again.");
    }
  };

  return (
    <main className="login-page">
      <div className="login-background" aria-hidden="true" />

      <section className="login-card">
        <div className="brand">
          <span className="brand-icon" aria-hidden="true">
            ✦
          </span>
          <p className="brand-label">YOUR ADVENTURE, ORGANIZED</p>
          <h1>
            Warband <span>HQ</span>
          </h1>
          <p className="brand-description">
            Your World of Warcraft characters, all in one place.
          </p>
        </div>

        <div className="login-divider">
          <span />
          <span className="divider-diamond">◆</span>
          <span />
        </div>

        {loading ? (
          <div className="login-content">
            <h2>Checking your session...</h2>
            <p>Please wait while we contact Warband HQ.</p>
          </div>
        ) : user ? (
          <div className="login-content">
            <h2>Welcome, adventurer!</h2>
            <p>You are successfully connected to Warband HQ.</p>

            <div className="profile-details">
              <p>
                <span>Account ID</span>
                <strong>{user.blizzard_account_id}</strong>
              </p>
              <p>
                <span>Role</span>
                <strong>{user.role}</strong>
              </p>
            </div>

            <button
              className="blizzard-button"
              type="button"
              onClick={handleLogout}
            >
              Log out
            </button>
          </div>
        ) : (
          <div className="login-content">
            <h2>Welcome, adventurer</h2>
            <p>
              Connect your Battle.net account to access your characters and
              manage your warband.
            </p>

            <button
              className="blizzard-button"
              type="button"
              onClick={handleBlizzardLogin}
            >
              <span className="button-icon" aria-hidden="true">
                ⚔
              </span>
              <span>Log in with Battle.net</span>
            </button>

            <p className="login-note">
              Secure authentication powered by Blizzard
            </p>
          </div>
        )}

        {error && (
          <p className="auth-error" role="alert">
            {error}
          </p>
        )}

        <footer className="login-footer">
          <span>WARBAND HQ</span>
          <span>AZEROTH IS WAITING</span>
        </footer>
      </section>
    </main>
  );
}

export default App;
