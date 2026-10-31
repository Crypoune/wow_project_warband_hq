import { useEffect } from "react";
import { AlertTriangle, Trash2 } from "lucide-react";

/**
 * Boîte de dialogue demandant confirmation avant la suppression
 * d'un objectif.
 *
 * Ce composant ne supprime pas directement l'objectif.
 * Il transmet la confirmation au composant parent, qui se chargera
 * d'appeler le service API.
 */
function DeleteGoalDialog({ goal, onConfirm, onCancel, isDeleting = false }) {
  // Gestion de la fermeture avec Échap.
  useEffect(() => {
    if (!goal) return;

    function handleEscape(event) {
      if (event.key === "Escape" && !isDeleting) {
        onCancel();
      }
    }

    window.addEventListener("keydown", handleEscape);

    // Nettoyage de l'écouteur lorsque la popup se ferme.
    return () => {
      window.removeEventListener("keydown", handleEscape);
    };
  }, [goal, onCancel, isDeleting]);

  // Si aucun objectif n'est fourni, il n'y a rien à afficher.
  if (!goal) return null;

  return (
    // Fond sombre qui recouvre toute la page.
    <div
      className="goal-modal-overlay"
      onClick={(event) => {
        // Ferme la popup uniquement si on clique sur le fond extérieur.
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
        aria-labelledby="goal-delete-title"
        aria-describedby="goal-delete-description"
      >
        {/* En-tête de la fenêtre. */}
        <div className="goal-modal-header">
          <h2 id="goal-delete-title">
            <AlertTriangle size={22} aria-hidden="true" />
            Supprimer cet objectif ?
          </h2>

          {/* Bouton de fermeture. */}
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

        {/* Message de confirmation. */}
        <div className="goal-delete-content">
          <p id="goal-delete-description">
            Tu es sur le point de supprimer définitivement l'objectif :
          </p>

          {/* Nom de l'objectif pour éviter toute confusion. */}
          <strong className="goal-delete-name">{goal.title}</strong>

          <p className="goal-delete-warning">Cette action est irréversible.</p>
        </div>

        {/* Actions disponibles dans la fenêtre. */}
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
            onClick={() => onConfirm(goal)}
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

export default DeleteGoalDialog;
