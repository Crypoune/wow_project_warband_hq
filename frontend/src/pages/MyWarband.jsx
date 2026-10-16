import { useMemo, useState } from "react";

// Importation des icônes de factions.
import { CLASS_ICONS, CLASS_COLORS } from "../data/wowClasses";
import { RACE_ICONS } from "../data/wowRaces";
import { FACTION_ICONS } from "../data/wowFactions";

import {
  ChevronDown,
  ChevronUp,
  SlidersHorizontal,
  LayoutGrid,
  List,
  Star,
} from "lucide-react";

function FavoriteButton({ character, onToggleFavorite }) {
  const isFavorite = Boolean(character.is_favorite);

  return (
    <button
      type="button"
      className={`favorite-button ${isFavorite ? "is-favorite" : ""}`}
      onClick={() => onToggleFavorite(character.id, !isFavorite)}
      aria-label={
        isFavorite
          ? `Remove ${character.name} from favorites`
          : `Add ${character.name} to favorites`
      }
      aria-pressed={isFavorite}
      title={isFavorite ? "Remove from favorites" : "Add to favorites"}
    >
      <Star
        size={20}
        fill={isFavorite ? "currentColor" : "none"}
        strokeWidth={1.8}
        aria-hidden="true"
      />
    </button>
  );
}

function MyWarband({
  importedCharacters,
  loadingImportedCharacters,
  onToggleFavorite,
}) {
  // Mode d'affichage de la collection : cartes ou liste.
  const [viewMode, setViewMode] = useState("grid");

  // Contrôle l'ouverture du panneau de recherche et de filtres.
  const [showFilters, setShowFilters] = useState(false);

  // Indique si seuls les personnages favoris doivent être affichés.
  const [favoritesOnly, setFavoritesOnly] = useState(false);

  // Texte utilisé pour rechercher un personnage.
  const [searchTerm, setSearchTerm] = useState("");

  // Classe sélectionnée dans le filtre.
  const [selectedClass, setSelectedClass] = useState("all");

  // Faction sélectionnée dans le filtre.
  const [selectedFaction, setSelectedFaction] = useState("all");

  // Critère et sens du tri.
  const [sortBy, setSortBy] = useState("name-asc");

  // Construit la liste des classes disponibles à partir des personnages importés.
  const availableClasses = useMemo(() => {
    return [
      ...new Set(
        importedCharacters.map((character) => character.class).filter(Boolean),
      ),
    ].sort((a, b) => a.localeCompare(b));
  }, [importedCharacters]);

  // Recherche, filtrage et tri de la collection affichée.
  const filteredCharacters = useMemo(() => {
    const normalizedSearch = searchTerm.trim().toLocaleLowerCase();

    const filtered = importedCharacters.filter((character) => {
      // Recherche dans le nom, la race et la classe.
      const matchesSearch = [
        character.name,
        character.race,
        character.class,
        character.realm,
      ].some((value) =>
        String(value ?? "")
          .toLocaleLowerCase()
          .includes(normalizedSearch),
      );

      const matchesClass =
        selectedClass === "all" || character.class === selectedClass;

      const matchesFaction =
        selectedFaction === "all" || character.faction === selectedFaction;

      const matchesFavorite = !favoritesOnly || character.is_favorite === true;

      return matchesSearch && matchesClass && matchesFaction && matchesFavorite;
    });

    // Trie une nouvelle copie pour ne pas modifier le tableau original.
    return [...filtered].sort((a, b) => {
      switch (sortBy) {
        case "name-desc":
          return (b.name ?? "").localeCompare(a.name ?? "");

        case "level-desc":
          return (b.level ?? -1) - (a.level ?? -1);

        case "level-asc":
          return (a.level ?? Infinity) - (b.level ?? Infinity);

        case "realm-asc":
          return (a.realm ?? "").localeCompare(b.realm ?? "");

        case "name-asc":
        default:
          return (a.name ?? "").localeCompare(b.name ?? "");
      }
    });
  }, [
    importedCharacters,
    searchTerm,
    selectedClass,
    selectedFaction,
    sortBy,
    favoritesOnly,
  ]);

  // Réinitialise les critères de recherche et de filtrage.
  const resetFilters = () => {
    setSearchTerm("");
    setSelectedClass("all");
    setSelectedFaction("all");
    setSortBy("name-asc");
    setFavoritesOnly(false);
  };

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
            {filteredCharacters.length}
          </span>

          <span className="collection-count-label">
            {filteredCharacters.length === 1 ? "CHARACTER" : "CHARACTERS"}
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
            <LayoutGrid size={20} strokeWidth={1.8} aria-hidden="true" />
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
            <List size={20} strokeWidth={1.8} aria-hidden="true" />
          </button>
        </div>
      </div>

      {/* Bouton d'ouverture et de fermeture des filtres. */}
      <div className="filter-toolbar">
        <button
          type="button"
          className="filter-toggle-button"
          onClick={() => setShowFilters((previous) => !previous)}
          aria-expanded={showFilters}
          aria-controls="character-filters"
        >
          <SlidersHorizontal size={17} strokeWidth={1.9} aria-hidden="true" />

          <span>Filters</span>

          <span className="filter-chevron" aria-hidden="true">
            <ChevronDown
              className={`filter-chevron-icon ${
                showFilters ? "inactive" : "active"
              }`}
              size={18}
              strokeWidth={2}
            />
            <ChevronUp
              className={`filter-chevron-icon ${
                showFilters ? "active" : "inactive"
              }`}
              size={18}
              strokeWidth={2}
            />
          </span>
        </button>
      </div>

      {/* Panneau de filtres animé. */}
      <div
        className={`character-filters ${showFilters ? "open" : ""}`}
        id="character-filters"
        aria-hidden={!showFilters}
        inert={!showFilters}
      >
        <h3>Search &amp; organize</h3>

        <div className="filter-field">
          <label htmlFor="character-search">Search characters</label>
          <input
            id="character-search"
            type="search"
            placeholder="Name, race, class, realm..."
            value={searchTerm}
            onChange={(event) => setSearchTerm(event.target.value)}
          />
        </div>

        <div className="filter-field">
          <label htmlFor="character-class-filter">Class</label>
          <select
            id="character-class-filter"
            value={selectedClass}
            onChange={(event) => setSelectedClass(event.target.value)}
          >
            <option value="all">All classes</option>
            {availableClasses.map((characterClass) => (
              <option key={characterClass} value={characterClass}>
                {characterClass}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-field">
          <label htmlFor="character-faction-filter">Faction</label>
          <select
            id="character-faction-filter"
            value={selectedFaction}
            onChange={(event) => setSelectedFaction(event.target.value)}
          >
            <option value="all">All factions</option>
            <option value="Alliance">Alliance</option>
            <option value="Horde">Horde</option>
          </select>
        </div>

        <div className="filter-field favorite-filter">
          <label htmlFor="favorites-only">
            <span>Show favorites only</span>
            <input
              id="favorites-only"
              type="checkbox"
              checked={favoritesOnly}
              onChange={(event) => setFavoritesOnly(event.target.checked)}
            />
          </label>
        </div>

        <div className="filter-field">
          <label htmlFor="character-sort">Sort by</label>
          <select
            id="character-sort"
            value={sortBy}
            onChange={(event) => setSortBy(event.target.value)}
          >
            <option value="name-asc">Name — A to Z</option>
            <option value="name-desc">Name — Z to A</option>
            <option value="level-desc">Level — Highest first</option>
            <option value="level-asc">Level — Lowest first</option>
            <option value="realm-asc">Realm — A to Z</option>
          </select>
        </div>

        <button
          type="button"
          className="filter-reset-button"
          onClick={resetFilters}
        >
          Reset filters
        </button>
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
      ) : filteredCharacters.length === 0 ? (
        <div className="status-panel">
          <h3>No characters found</h3>
          <p>
            No characters match your current search or filters. Try changing
            your criteria or reset the filters.
          </p>
          <button
            type="button"
            className="filter-reset-button"
            onClick={resetFilters}
          >
            Reset filters
          </button>
        </div>
      ) : (
        <div
          className={viewMode === "grid" ? "character-grid" : "character-list"}
        >
          {filteredCharacters.map((character) => {
            const classColor = CLASS_COLORS[character.class] ?? "#D7AA50";
            const classIcon = CLASS_ICONS[character.class];
            const factionIcon = FACTION_ICONS[character.faction];
            const raceIcon = RACE_ICONS[character.race_id]?.[character.gender];

            return (
              <article
                className={`character-card ${viewMode === "list" ? "character-row" : ""}`}
                key={character.id}
                style={{ "--class-color": classColor }}
              >
                {viewMode === "grid" ? (
                  <>
                    <div className="character-portrait">
                      <FavoriteButton
                        character={character}
                        onToggleFavorite={onToggleFavorite}
                      />
                      {character.portrait_url ? (
                        <img
                          src={character.portrait_url}
                          alt={`Portrait of ${character.name}`}
                          className="character-portrait-image"
                          loading="lazy"
                        />
                      ) : (
                        <div className="character-portrait-placeholder">
                          Portrait indisponible
                        </div>
                      )}

                      <div className="character-badges">
                        <span className="character-badge character-level">
                          {character.level ?? "-"}
                        </span>

                        {classIcon && (
                          <img
                            src={classIcon}
                            alt={character.class || "Classe inconnue"}
                            className="character-badge character-class-badge"
                          />
                        )}

                        {factionIcon && (
                          <img
                            src={factionIcon}
                            alt={character.faction}
                            className="character-badge character-faction-badge"
                          />
                        )}
                      </div>
                    </div>

                    <div className="character-card-info">
                      <div className="character-card-heading">
                        <h3 className="character-name">
                          {character.name || "Unknown character"}
                        </h3>

                        <span className="character-realm">
                          {character.realm || "Realm unavailable"}
                        </span>
                      </div>

                      <p className="character-class">
                        {character.class || "Class unavailable"}
                        {character.race ? ` · ${character.race}` : ""}
                      </p>
                    </div>
                  </>
                ) : (
                  <div className="character-row-content">
                    <FavoriteButton
                      character={character}
                      onToggleFavorite={onToggleFavorite}
                    />
                    <div className="character-row-icons">
                      {factionIcon && (
                        <img
                          src={factionIcon}
                          alt={character.faction}
                          className="character-row-icon"
                          title={character.faction}
                        />
                      )}

                      {raceIcon ? (
                        <img
                          src={raceIcon}
                          alt={character.race || "Race inconnue"}
                          className="character-row-icon"
                          title={`${character.race} · ${
                            character.gender === "FEMALE" ? "Femme" : "Homme"
                          }`}
                          loading="lazy"
                        />
                      ) : (
                        character.race && (
                          <span
                            className="character-race-icon-placeholder"
                            title={character.race}
                            aria-label={character.race}
                          >
                            {character.race.slice(0, 1)}
                          </span>
                        )
                      )}

                      {classIcon && (
                        <img
                          src={classIcon}
                          alt={character.class}
                          className="character-row-icon"
                          title={character.class}
                        />
                      )}
                    </div>

                    <h3 className="character-name character-row-name">
                      {character.name || "Unknown character"}
                    </h3>

                    <span className="character-row-level">
                      {character.level ?? "-"}
                    </span>

                    <span className="character-row-realm">
                      {character.realm || "Realm unavailable"}
                    </span>
                  </div>
                )}
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}

export default MyWarband;
