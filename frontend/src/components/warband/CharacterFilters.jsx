import { ChevronDown, ChevronUp, SlidersHorizontal } from "lucide-react";

function CharacterFilters({
  showFilters,
  onToggleFilters,
  searchTerm,
  onSearchChange,
  availableClasses,
  selectedClass,
  onClassChange,
  selectedFaction,
  onFactionChange,
  favoritesOnly,
  onFavoritesOnlyChange,
  sortBy,
  onSortChange,
  onResetFilters,
}) {
  return (
    <>
      <div className="filter-toolbar">
        <button
          type="button"
          className="filter-toggle-button"
          onClick={onToggleFilters}
          aria-expanded={showFilters}
          aria-controls="character-filters"
        >
          <SlidersHorizontal size={17} strokeWidth={1.9} aria-hidden="true" />

          <span>Filtres</span>

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

      <div
        className={`character-filters ${showFilters ? "open" : ""}`}
        id="character-filters"
        aria-hidden={!showFilters}
        inert={!showFilters}
      >
        <h3>Rechercher et organiser</h3>

        <div className="filter-field">
          <label htmlFor="character-search">Rechercher des personnages</label>
          <input
            id="character-search"
            type="search"
            placeholder="Nom, race, classe, royaume…"
            value={searchTerm}
            onChange={(event) => onSearchChange(event.target.value)}
          />
        </div>

        <div className="filter-field">
          <label htmlFor="character-class-filter">Classe</label>
          <select
            id="character-class-filter"
            value={selectedClass}
            onChange={(event) => onClassChange(event.target.value)}
          >
            <option value="all">Toutes les classes</option>
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
            onChange={(event) => onFactionChange(event.target.value)}
          >
            <option value="all">Toutes les factions</option>
            <option value="Alliance">Alliance</option>
            <option value="Horde">Horde</option>
          </select>
        </div>

        <div className="filter-field favorite-filter">
          <label htmlFor="favorites-only">
            <span>Afficher uniquement les favoris</span>
            <input
              id="favorites-only"
              type="checkbox"
              checked={favoritesOnly}
              onChange={(event) => onFavoritesOnlyChange(event.target.checked)}
            />
          </label>
        </div>

        <div className="filter-field">
          <label htmlFor="character-sort">Trier par</label>
          <select
            id="character-sort"
            value={sortBy}
            onChange={(event) => onSortChange(event.target.value)}
          >
            <option value="name-asc">Nom — A à Z</option>
            <option value="name-desc">Nom — Z à A</option>
            <option value="level-desc">
              Niveau — du plus élevé au plus bas
            </option>
            <option value="level-asc">
              Niveau — du plus bas au plus élevé
            </option>
            <option value="realm-asc">Royaume — A à Z</option>
          </select>
        </div>

        <button
          type="button"
          className="filter-reset-button"
          onClick={onResetFilters}
        >
          Réinitialiser les filtres
        </button>
      </div>
    </>
  );
}

export default CharacterFilters;
