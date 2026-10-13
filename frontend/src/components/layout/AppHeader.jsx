// Affiche le header commun, que l'utilisateur soit connecté ou non.
function AppHeader({ user, onLogout, onLogin }) {
  return (
    <header className="app-header">
      {/* Logo et identité visuelle de Warband HQ. */}
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

      {/* Le bouton dépend de l'état de connexion de l'utilisateur. */}
      {user ? (
        // Un utilisateur connecté peut fermer sa session.
        <button className="logout-button" type="button" onClick={onLogout}>
          Log out
        </button>
      ) : (
        // Un utilisateur déconnecté peut démarrer la connexion Blizzard.
        <button className="logout-button" type="button" onClick={onLogin}>
          Log in with Battle.net
        </button>
      )}
    </header>
  );
}

export default AppHeader;
