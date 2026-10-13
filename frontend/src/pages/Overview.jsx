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
            onClick={onRefresh}
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
              No available characters were returned by Blizzard. You can try
              refreshing the list.
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
                      onChange={() => onToggleCharacter(character.id)}
                      disabled={importing}
                    />

                    <div className="character-card-top">
                      <span className="character-emblem" aria-hidden="true">
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

                    <div className="character-faction">{character.faction}</div>
                  </label>
                );
              })}
            </div>

            <div className="import-toolbar">
              <p>Select the characters you want to import.</p>

              <button
                className="blizzard-button import-button"
                type="button"
                onClick={onImport}
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
  );
}

export default Overview;
