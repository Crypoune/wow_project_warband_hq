// Affiche le header commun, que l'utilisateur soit connecté ou non.
function AppHeader({ user, onLogout, onLogin, onSwitchAccount, onMenuToggle }) {
  return (
    <header className="app-header">
      {/* Logo et identité visuelle de Warband HQ. */}
      <a className="app-brand" href="/" aria-label="Accueil Warband HQ">
        <span className="brand-icon" aria-hidden="true">
          ✦
        </span>

        <span>
          <strong>
            Warband <span>HQ</span>
          </strong>
          <small>VOTRE AVENTURE, BIEN ORGANISÉE</small>
        </span>
      </a>

      <div className="header-actions">
        {user && (
          <button
            className="mobile-menu-toggle"
            type="button"
            onClick={onMenuToggle}
            aria-label="Ouvrir le menu de navigation"
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
              Changer de compte
            </button>

            <button className="logout-button" type="button" onClick={onLogout}>
              Se déconnecter
            </button>
          </>
        ) : (
          // Un utilisateur déconnecté peut démarrer la connexion Blizzard.
          <button className="logout-button" type="button" onClick={onLogin}>
            Se connecter avec Battle.net
          </button>
        )}
      </div>
    </header>
  );
}

export default AppHeader;
