/**
 * Liste des filtres disponibles.
 *
 * Les valeurs techniques correspondent aux statuts du backend.
 * La valeur "ALL" permet d'afficher tous les objectifs.
 */
const GOAL_FILTERS = [
  { value: "ALL", label: "Tous" },
  { value: "IN_PROGRESS", label: "En cours" },
  { value: "ON_HOLD", label: "En pause" },
  { value: "COMPLETED", label: "Terminés" },
  { value: "ABANDONED", label: "Abandonnés" },
];

/**
 * Affiche les filtres permettant de trier visuellement les objectifs.
 *
 * Ce composant ne filtre pas lui-même les objectifs.
 * Il transmet simplement le filtre sélectionné au composant parent.
 *
 * @param {string} activeFilter - Filtre actuellement sélectionné.
 * @param {function} onFilterChange - Fonction appelée lors d'un changement.
 */
function GoalFilters({ activeFilter, onFilterChange }) {
  return (
    <div className="goal-filters" aria-label="Filtrer les objectifs">
      {GOAL_FILTERS.map((filter) => {
        // Vérifie si ce filtre est actuellement sélectionné.
        const isActive = activeFilter === filter.value;

        return (
          <button
            key={filter.value}
            type="button"
            className={`goal-filter ${isActive ? "active" : ""}`}
            aria-pressed={isActive}
            onClick={() => onFilterChange(filter.value)}
          >
            {filter.label}
          </button>
        );
      })}
    </div>
  );
}

export default GoalFilters;
