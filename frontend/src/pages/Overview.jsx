function Overview({
  user,
  characters,
  selectedIds,
  loadingCharacters,
  importing,
  onRefresh,
  onToggleCharacter,
  onSelectAll,
  onImport,
}) {
  return (
    <>
      <section className="welcome-section">
        <p className="section-eyebrow">VOTRE COMPTE</p>
        <h1>Bienvenue, aventurier !</h1>
        <p>
          Choisissez les personnages que vous souhaitez ajouter à votre bande de
          guerre.
        </p>

        <div className="account-badge">
          <span>Compte Battle.net</span>
          <strong>{user.blizzard_account_id}</strong>
        </div>
      </section>

      <section className="characters-section">
        <div className="section-heading">
          <div>
            <p className="section-eyebrow">COLLECTION DE PERSONNAGES</p>
            <h2>Personnages disponibles</h2>
          </div>

          <button
            className="secondary-button"
            type="button"
            onClick={onRefresh}
            disabled={loadingCharacters || importing}
          >
            {loadingCharacters ? "Actualisation…" : "Actualiser"}
          </button>
        </div>

        {loadingCharacters ? (
          <div className="status-panel">
            <h3>Recherche de vos personnages…</h3>
            <p>Connexion à l'API Blizzard.</p>
          </div>
        ) : characters.length === 0 ? (
          <div className="status-panel">
            <h3>Aucun personnage trouvé</h3>
            <p>
              Blizzard n'a renvoyé aucun personnage disponible. Vous pouvez
              actualiser la liste.
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
                onClick={onSelectAll}
                disabled={importing}
              >
                {selectedIds.length === characters.length
                  ? "Tout désélectionner"
                  : "Tout sélectionner"}
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
                      onChange={() => onToggleCharacter(character.id)}
                      disabled={importing}
                    />

                    <div className="character-card-top">
                      <span className="character-emblem" aria-hidden="true">
                        ✦
                      </span>
                      <span className="character-level">
                        Niv. {character.level}
                      </span>
                    </div>

                    <h3>{character.name}</h3>

                    <p className="character-class">
                      {character.class}
                      {character.race ? ` · ${character.race}` : ""}
                    </p>

                    <div className="character-meta">
                      <span>Royaume</span>
                      <strong>{character.realm}</strong>
                    </div>

                    <div className="character-faction">{character.faction}</div>
                  </label>
                );
              })}
            </div>

            <div className="import-toolbar">
              <p>Sélectionnez les personnages que vous souhaitez importer.</p>

              <button
                className="blizzard-button import-button"
                type="button"
                onClick={onImport}
                disabled={selectedIds.length === 0 || importing}
              >
                {importing
                  ? "Importation…"
                  : `Importer la sélection (${selectedIds.length})`}
              </button>
            </div>
          </>
        )}
      </section>
    </>
  );
}

export default Overview;
