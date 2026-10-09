import { useCallback, useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [characters, setCharacters] = useState([]);
  const [selectedIds, setSelectedIds] = useState([]);
  const [loadingCharacters, setLoadingCharacters] = useState(false);
  const [importing, setImporting] = useState(false);
  const [success, setSuccess] = useState("");

  const fetchAvailableCharacters = useCallback(async () => {
    setLoadingCharacters(true);
    setError("");
    setSuccess("");

    try {
      const response = await fetch(`${API_URL}/api/characters/available`, {
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error(
          response.status === 401
            ? "Your session has expired. Please log in again."
            : "Unable to retrieve your characters.",
        );
      }

      const data = await response.json();
      setCharacters(data.characters ?? []);
      setSelectedIds([]);
    } catch (err) {
      setError(
        err.message || "Unable to contact Warband HQ. Please try again.",
      );
    } finally {
      setLoadingCharacters(false);
    }
  }, []);

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

  useEffect(() => {
    if (user) {
      fetchAvailableCharacters();
    }
  }, [user, fetchAvailableCharacters]);

  const handleBlizzardLogin = () => {
    window.location.href = `${API_URL}/api/auth/login`;
  };

  const handleLogout = async () => {
    setError("");
    setSuccess("");

    try {
      const response = await fetch(`${API_URL}/api/auth/logout`, {
        method: "POST",
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error("Logout failed.");
      }

      setUser(null);
      setCharacters([]);
      setSelectedIds([]);
    } catch {
      setError("Unable to log out. Please try again.");
    }
  };

  const toggleCharacter = (characterId) => {
    setSelectedIds((currentIds) =>
      currentIds.includes(characterId)
        ? currentIds.filter((id) => id !== characterId)
        : [...currentIds, characterId],
    );
  };

  const handleImport = async () => {
    if (selectedIds.length === 0 || importing) {
      return;
    }

    setError("");
    setSuccess("");
    setImporting(true);

    try {
      const response = await fetch(`${API_URL}/api/characters/import`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          character_ids: selectedIds,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail?.message || "Unable to import characters.");
      }

      const importedCount = data.characters?.length ?? 0;

      setSuccess(
        importedCount > 0
          ? `${importedCount} character(s) imported successfully.`
          : "No new characters were imported. They may already be in your warband.",
      );

      setSelectedIds([]);
    } catch (err) {
      setError(err.message || "Unable to import characters. Please try again.");
    } finally {
      setImporting(false);
    }
  };

  return (
    <main className="app-page">
      <div className="app-background" aria-hidden="true" />

      <header className="app-header">
        <a className="app-brand" href="/" aria-label="Warband HQ home">
          <span className="brand-icon" aria-hidden="true">
            ✦
          </span>
          <span>
            <strong>
              Warband <span>HQ</span>
            </strong>
            <small>YOUR ADVENTURE, ORGANIZED</small>
          </span>
        </a>

        {user && (
          <button
            className="logout-button"
            type="button"
            onClick={handleLogout}
          >
            Log out
          </button>
        )}
      </header>

      <section className="app-content">
        {loading ? (
          <div className="status-panel">
            <h2>Checking your session...</h2>
            <p>Please wait while we contact Warband HQ.</p>
          </div>
        ) : !user ? (
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

            <div className="login-content">
              <h2>Welcome, adventurer</h2>
              <p>
                Connect your Battle.net account to retrieve and import your
                characters.
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

            <footer className="login-footer">
              <span>WARBAND HQ</span>
              <span>AZEROTH IS WAITING</span>
            </footer>
          </section>
        ) : (
          <>
            <section className="welcome-section">
              <p className="section-eyebrow">YOUR ACCOUNT</p>
              <h1>Welcome, adventurer.</h1>
              <p>Choose the characters you want to bring into your warband.</p>
              <div className="account-badge">
                <span>Battle.net account</span>
                <strong>{user.blizzard_account_id}</strong>
              </div>
            </section>

            <section className="characters-section">
              <div className="section-heading">
                <div>
                  <p className="section-eyebrow">CHARACTER COLLECTION</p>
                  <h2>Available characters</h2>
                </div>

                <button
                  className="secondary-button"
                  type="button"
                  onClick={fetchAvailableCharacters}
                  disabled={loadingCharacters || importing}
                >
                  {loadingCharacters ? "Refreshing..." : "Refresh"}
                </button>
              </div>

              {loadingCharacters ? (
                <div className="status-panel">
                  <h3>Discovering your characters...</h3>
                  <p>Contacting the Blizzard API.</p>
                </div>
              ) : characters.length === 0 ? (
                <div className="status-panel">
                  <h3>No characters found</h3>
                  <p>
                    No available characters were returned by Blizzard. You can
                    try refreshing the list.
                  </p>
                </div>
              ) : (
                <>
                  <div className="selection-toolbar">
                    <span>
                      {selectedIds.length} of {characters.length} selected
                    </span>
                    <button
                      className="text-button"
                      type="button"
                      onClick={() =>
                        setSelectedIds(
                          selectedIds.length === characters.length
                            ? []
                            : characters.map((character) => character.id),
                        )
                      }
                      disabled={importing}
                    >
                      {selectedIds.length === characters.length
                        ? "Deselect all"
                        : "Select all"}
                    </button>
                  </div>

                  <div className="character-grid">
                    {characters.map((character) => {
                      const selected = selectedIds.includes(character.id);

                      return (
                        <label
                          className={`character-card${selected ? " selected" : ""}`}
                          key={character.id}
                        >
                          <input
                            className="character-checkbox"
                            type="checkbox"
                            checked={selected}
                            onChange={() => toggleCharacter(character.id)}
                            disabled={importing}
                          />

                          <div className="character-card-top">
                            <span
                              className="character-emblem"
                              aria-hidden="true"
                            >
                              ✦
                            </span>
                            <span className="character-level">
                              LVL {character.level}
                            </span>
                          </div>

                          <h3>{character.name}</h3>
                          <p className="character-class">
                            {character.class}
                            {character.race ? ` · ${character.race}` : ""}
                          </p>

                          <div className="character-meta">
                            <span>Realm</span>
                            <strong>{character.realm}</strong>
                          </div>

                          <div className="character-faction">
                            {character.faction}
                          </div>
                        </label>
                      );
                    })}
                  </div>

                  <div className="import-toolbar">
                    <p>Select the characters you want to import.</p>
                    <button
                      className="blizzard-button import-button"
                      type="button"
                      onClick={handleImport}
                      disabled={selectedIds.length === 0 || importing}
                    >
                      {importing
                        ? "Importing..."
                        : `Import selection (${selectedIds.length})`}
                    </button>
                  </div>
                </>
              )}
            </section>
          </>
        )}

        {error && (
          <p className="feedback-message error-message" role="alert">
            {error}
          </p>
        )}

        {success && (
          <p className="feedback-message success-message" role="status">
            {success}
          </p>
        )}
      </section>

      <footer className="page-footer">
        <span>WARBAND HQ</span>
        <span>BUILT FOR YOUR ADVENTURE IN AZEROTH</span>
      </footer>
    </main>
  );
}

export default App;
