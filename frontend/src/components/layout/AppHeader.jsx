// Affiche le header commun, que l'utilisateur soit connecté ou non.
function AppHeader({ user, onLogout, onLogin, onSwitchAccount, onMenuToggle }) {
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

      <div className="header-actions">
        {user && (
          <button
            className="mobile-menu-toggle"
            type="button"
            onClick={onMenuToggle}
            aria-label="Open navigation menu"
          >
            <span aria-hidden="true">☰</span>
          </button>
        )}

        {/* Le bouton dépend de l'état de connexion de l'utilisateur. */}
        {user ? (
          <>
            <button
              className="switch-account-button"
              type="button"
              onClick={onSwitchAccount}
            >
              Switch account
            </button>

            <button className="logout-button" type="button" onClick={onLogout}>
              Log out
            </button>
          </>
        ) : (
          // Un utilisateur déconnecté peut démarrer la connexion Blizzard.
          <button className="logout-button" type="button" onClick={onLogin}>
            Log in with Battle.net
          </button>
        )}
      </div>
    </header>
  );
}

export default AppHeader;
