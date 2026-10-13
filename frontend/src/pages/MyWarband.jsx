import { useState } from "react";

function MyWarband({ importedCharacters, loadingImportedCharacters }) {
  // Mode d'affichage de la collection : cartes ou liste.
  const [viewMode, setViewMode] = useState("grid");

  return (
    <section className="characters-section">
      <div className="section-heading">
        <div>
          <p className="section-eyebrow">YOUR COLLECTION</p>
          <h2>My Warband</h2>
          <p className="collection-description">
            Your heroes, gathered in one place.
          </p>
        </div>

        <div className="collection-count" aria-live="polite">
          <span className="collection-count-value">
            {importedCharacters.length}
          </span>

          <span className="collection-count-label">
            {importedCharacters.length === 1 ? "CHARACTER" : "CHARACTERS"}
          </span>
        </div>

        <div className="view-toggle" aria-label="Character display mode">
          <button
            type="button"
            className={
              viewMode === "grid"
                ? "view-toggle-button active"
                : "view-toggle-button"
            }
            onClick={() => setViewMode("grid")}
            aria-label="Display characters as cards"
            aria-pressed={viewMode === "grid"}
          >
            ▦
          </button>

          <button
            type="button"
            className={
              viewMode === "list"
                ? "view-toggle-button active"
                : "view-toggle-button"
            }
            onClick={() => setViewMode("list")}
            aria-label="Display characters as a list"
            aria-pressed={viewMode === "list"}
          >
            ☰
          </button>
        </div>
      </div>

      {loadingImportedCharacters ? (
        <div className="status-panel">
          <h3>Loading your warband...</h3>
          <p>Retrieving your imported characters.</p>
        </div>
      ) : importedCharacters.length === 0 ? (
        <div className="status-panel">
          <h3>Your warband is waiting</h3>
          <p>
            You haven't imported any characters yet. Select characters above to
            start building your collection.
          </p>
        </div>
      ) : (
        <div
          className={viewMode === "grid" ? "character-grid" : "character-list"}
        >
          {importedCharacters.map((character) => (
            <article className="character-card" key={character.id}>
              <div className="character-card-top">
                <span className="character-emblem" aria-hidden="true">
                  ✦
                </span>

                <span className="character-level">
                  {character.level != null
                    ? `LVL ${character.level}`
                    : "LEVEL N/A"}
                </span>
              </div>

              <h3>{character.name || "Unknown character"}</h3>

              <p className="character-class">
                {character.class || "Class unavailable"}
                {character.race ? ` · ${character.race}` : ""}
              </p>

              <div className="character-meta">
                <span>Realm</span>
                <strong>{character.realm || "Realm unavailable"}</strong>
              </div>

              {character.faction && (
                <div className="character-faction">{character.faction}</div>
              )}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

export default MyWarband;
