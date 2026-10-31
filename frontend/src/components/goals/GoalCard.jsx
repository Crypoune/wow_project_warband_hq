import { Pencil, Trash2 } from "lucide-react";

// Associe chaque statut technique à un libellé lisible.
// Les valeurs doivent correspondre aux statuts définis dans le backend.
const GOAL_STATUSES = {
  IN_PROGRESS: {
    label: "En cours",
    className: "in-progress",
  },
  ON_HOLD: {
    label: "En pause",
    className: "on-hold",
  },
  COMPLETED: {
    label: "Terminé",
    className: "completed",
  },
  ABANDONED: {
    label: "Abandonné",
    className: "abandoned",
  },
};

/**
 * Affiche une carte représentant un objectif.
 *
 * Ce composant ne communique pas directement avec l'API.
 * Il reçoit les données de l'objectif et transmet les actions
 * au composant parent grâce à ses fonctions de rappel (callbacks).
 *
 * @param {object} goal - Données de l'objectif à afficher.
 * @param {function} onEdit - Fonction appelée pour modifier l'objectif.
 * @param {function} onDelete - Fonction appelée pour demander sa suppression.
 */
function GoalCard({ goal, onEdit, onDelete }) {
  // Récupère les informations correspondant au statut actuel.
  // Le statut "En cours" sert de valeur de secours.
  const status = GOAL_STATUSES[goal.status] ?? GOAL_STATUSES.IN_PROGRESS;

  return (
    <article className="goal-card">
      {/* Partie supérieure : titre et statut de l'objectif. */}
      <div className="goal-card-header">
        <h3 className="goal-card-title">{goal.title}</h3>

        <span
          className={`goal-status goal-status--${status.className}`}
          aria-label={`Statut : ${status.label}`}
        >
          {status.label}
        </span>
      </div>

      {/* La description est facultative.
          On n'affiche pas de bloc vide lorsqu'elle est absente. */}
      {goal.description && (
        <p className="goal-card-description">{goal.description}</p>
      )}

      {/* Actions disponibles sur chaque objectif. */}
      <div className="goal-card-actions">
        <button
          type="button"
          className="goal-card-edit"
          onClick={() => onEdit(goal)}
          aria-label={`Modifier l'objectif ${goal.title}`}
        >
          <Pencil size={16} aria-hidden="true" />
          Modifier
        </button>

        <button
          type="button"
          className="goal-card-delete"
          onClick={() => onDelete(goal)}
          aria-label={`Supprimer l'objectif ${goal.title}`}
        >
          <Trash2 size={16} aria-hidden="true" />
          Supprimer
        </button>
      </div>
    </article>
  );
}

export default GoalCard;
