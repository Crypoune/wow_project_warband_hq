import { useState } from "react";
import { Pencil, Trash2 } from "lucide-react";

/**
 * Affiche une tâche et ses actions.
 *
 * Ce composant ne communique pas directement avec l'API.
 * Il transmet les actions au composant parent grâce aux callbacks.
 *
 * @param {object} task - Tâche à afficher.
 * @param {function} onToggle - Fonction appelée pour changer son état.
 * @param {function} onEdit - Fonction appelée pour modifier la tâche.
 * @param {function} onDelete - Fonction appelée pour demander sa suppression.
 * @param {boolean} isUpdating - Indique si une modification est en cours.
 */
function TaskItem({ task, onToggle, onEdit, onDelete, isUpdating = false }) {
  // Évite les clics multiples pendant une modification.
  const [isToggling, setIsToggling] = useState(false);

  async function handleToggle() {
    if (isToggling || isUpdating) return;

    setIsToggling(true);

    try {
      await onToggle(task);
    } finally {
      setIsToggling(false);
    }
  }

  return (
    <article
      className={`task-item${task.is_completed ? " task-item--completed" : ""}`}
    >
      <label className="task-item-checkbox">
        <input
          type="checkbox"
          checked={task.is_completed}
          onChange={handleToggle}
          disabled={isToggling || isUpdating}
          aria-label={
            task.is_completed
              ? `Marquer ${task.title} comme non terminée`
              : `Marquer ${task.title} comme terminée`
          }
        />

        <span className="task-item-checkmark" aria-hidden="true" />
      </label>

      <div className="task-item-content">
        <h4 className="task-item-title">{task.title}</h4>

        {task.description && (
          <p className="task-item-description">{task.description}</p>
        )}
      </div>

      <div className="task-item-actions">
        <button
          type="button"
          className="task-item-edit"
          onClick={() => onEdit(task)}
          disabled={isToggling || isUpdating}
          aria-label={`Modifier la tâche ${task.title}`}
        >
          <Pencil size={15} aria-hidden="true" />
        </button>

        <button
          type="button"
          className="task-item-delete"
          onClick={() => onDelete(task)}
          disabled={isToggling || isUpdating}
          aria-label={`Supprimer la tâche ${task.title}`}
        >
          <Trash2 size={15} aria-hidden="true" />
        </button>
      </div>
    </article>
  );
}

export default TaskItem;
