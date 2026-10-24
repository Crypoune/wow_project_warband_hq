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
            onChange={(event) => onSearchChange(event.target.value)}
          />
        </div>

        <div className="filter-field">
          <label htmlFor="character-class-filter">Class</label>
          <select
            id="character-class-filter"
            value={selectedClass}
            onChange={(event) => onClassChange(event.target.value)}
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
            onChange={(event) => onFactionChange(event.target.value)}
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
              onChange={(event) => onFavoritesOnlyChange(event.target.checked)}
            />
          </label>
        </div>

        <div className="filter-field">
          <label htmlFor="character-sort">Sort by</label>
          <select
            id="character-sort"
            value={sortBy}
            onChange={(event) => onSortChange(event.target.value)}
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
          onClick={onResetFilters}
        >
          Reset filters
        </button>
      </div>
    </>
  );
}

export default CharacterFilters;
