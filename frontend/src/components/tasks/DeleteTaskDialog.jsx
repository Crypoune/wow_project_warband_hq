import { useEffect } from "react";
import { AlertTriangle, Trash2 } from "lucide-react";

/**
 * Boîte de dialogue demandant confirmation avant la suppression
 * d'une tâche.
 *
 * Ce composant ne supprime pas directement la tâche.
 * Il transmet la confirmation au composant parent.
 */
function DeleteTaskDialog({ task, onConfirm, onCancel, isDeleting = false }) {
  // Gestion de la fermeture avec Échap.
  useEffect(() => {
    if (!task) return;

    function handleEscape(event) {
      if (event.key === "Escape" && !isDeleting) {
        onCancel();
      }
    }

    window.addEventListener("keydown", handleEscape);

    return () => {
      window.removeEventListener("keydown", handleEscape);
    };
  }, [task, onCancel, isDeleting]);

  // Si aucune tâche n'est fournie, rien à afficher.
  if (!task) return null;

  return (
    // Fond sombre qui recouvre toute la page.
    <div
      className="goal-modal-overlay"
      onClick={(event) => {
        if (event.target === event.currentTarget && !isDeleting) {
          onCancel();
        }
      }}
    >
      {/* Fenêtre de confirmation de suppression. */}
      <section
        className="goal-modal goal-delete-modal"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="task-delete-title"
        aria-describedby="task-delete-description"
      >
        <div className="goal-modal-header">
          <h2 id="task-delete-title">
            <AlertTriangle size={22} aria-hidden="true" />
            Supprimer cette tâche ?
          </h2>

          <button
            type="button"
            className="goal-modal-close"
            onClick={onCancel}
            disabled={isDeleting}
            aria-label="Fermer la fenêtre"
          >
            ×
          </button>
        </div>

        <div className="goal-delete-content">
          <p id="task-delete-description">
            Tu es sur le point de supprimer définitivement la tâche :
          </p>

          <strong className="goal-delete-name">{task.title}</strong>

          <p className="goal-delete-warning">Cette action est irréversible.</p>
        </div>

        <div className="goal-delete-actions">
          <button
            type="button"
            className="goal-delete-cancel"
            onClick={onCancel}
            disabled={isDeleting}
          >
            Annuler
          </button>

          <button
            type="button"
            className="goal-delete-confirm"
            onClick={() => onConfirm(task)}
            disabled={isDeleting}
          >
            <Trash2 size={16} aria-hidden="true" />

            {isDeleting ? "Suppression..." : "Supprimer"}
          </button>
        </div>
      </section>
    </div>
  );
}

export default DeleteTaskDialog;
