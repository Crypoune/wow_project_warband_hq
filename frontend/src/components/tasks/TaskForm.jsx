import { useEffect, useState } from "react";

/**
 * Formulaire de création et de modification d'une tâche.
 *
 * Le composant ne communique pas directement avec l'API.
 * Il transmet les informations saisies au composant parent
 * grâce à la fonction onSubmit.
 */
function TaskForm({ task = null, onSubmit, onCancel, isSubmitting = false }) {
  // Détermine si le formulaire sert à modifier une tâche existante.
  const isEditing = Boolean(task);

  // États locaux correspondant aux champs du formulaire.
  const [title, setTitle] = useState(task?.title ?? "");
  const [description, setDescription] = useState(task?.description ?? "");
  const [validationError, setValidationError] = useState("");

  // Permet de fermer la popup avec la touche Échap.
  useEffect(() => {
    function handleEscape(event) {
      if (event.key === "Escape" && !isSubmitting) {
        onCancel();
      }
    }

    window.addEventListener("keydown", handleEscape);

    return () => {
      window.removeEventListener("keydown", handleEscape);
    };
  }, [onCancel, isSubmitting]);

  /**
   * Gère la soumission du formulaire.
   * Vérifie le titre avant de transmettre les données au parent.
   */
  function handleSubmit(event) {
    event.preventDefault();

    const cleanedTitle = title.trim();

    if (!cleanedTitle) {
      setValidationError("Le titre de la tâche est obligatoire.");
      return;
    }

    if (cleanedTitle.length > 100) {
      setValidationError("Le titre ne peut pas dépasser 100 caractères.");
      return;
    }

    setValidationError("");

    const taskData = {
      title: cleanedTitle,
      description: description.trim() || null,
    };

    onSubmit(taskData);
  }

  return (
    // Fond sombre qui recouvre la page.
    <div
      className="goal-modal-overlay"
      onClick={(event) => {
        if (event.target === event.currentTarget && !isSubmitting) {
          onCancel();
        }
      }}
    >
      {/* Contenu de la fenêtre modale. */}
      <div
        className="goal-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="task-modal-title"
      >
        <div className="goal-modal-header">
          <h2 id="task-modal-title">
            {isEditing ? "Modifier la tâche" : "Créer une tâche"}
          </h2>

          <button
            type="button"
            className="goal-modal-close"
            onClick={onCancel}
            disabled={isSubmitting}
            aria-label="Fermer la fenêtre"
          >
            ×
          </button>
        </div>

        <form className="goal-form" onSubmit={handleSubmit}>
          {/* Champ du titre. */}
          <div className="goal-form-field">
            <label htmlFor="task-title">Titre *</label>

            <input
              id="task-title"
              type="text"
              value={title}
              onChange={(event) => {
                setTitle(event.target.value);
                setValidationError("");
              }}
              placeholder="Ex. : Terminer un donjon Mythique+"
              maxLength={100}
              required
              disabled={isSubmitting}
              autoFocus
            />

            <span className="goal-form-counter">{title.length}/100</span>
          </div>

          {/* Champ facultatif de description. */}
          <div className="goal-form-field">
            <label htmlFor="task-description">Description</label>

            <textarea
              id="task-description"
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              placeholder="Ajoute quelques détails sur cette tâche..."
              rows={4}
              disabled={isSubmitting}
            />
          </div>

          {/* Message de validation. */}
          {validationError && (
            <p className="goal-form-error" role="alert">
              {validationError}
            </p>
          )}

          {/* Boutons de validation et d'annulation. */}
          <div className="goal-form-actions">
            <button
              type="button"
              className="goal-form-cancel"
              onClick={onCancel}
              disabled={isSubmitting}
            >
              Annuler
            </button>

            <button
              type="submit"
              className="goal-form-submit"
              disabled={isSubmitting}
            >
              {isSubmitting
                ? "Enregistrement..."
                : isEditing
                  ? "Enregistrer les modifications"
                  : "Créer la tâche"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default TaskForm;
