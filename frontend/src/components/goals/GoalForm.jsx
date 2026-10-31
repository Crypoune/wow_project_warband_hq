import { useEffect, useState } from "react";

// Liste des statuts autorisés par le backend.
// On utilise les mêmes valeurs techniques que dans l'API.
const GOAL_STATUSES = [
  { value: "IN_PROGRESS", label: "En cours" },
  { value: "ON_HOLD", label: "En pause" },
  { value: "COMPLETED", label: "Terminé" },
  { value: "ABANDONED", label: "Abandonné" },
];

/**
 * Formulaire de création et de modification d'un objectif.
 *
 * Le composant ne communique pas directement avec l'API.
 * Il transmet les informations saisies au composant parent
 * grâce à la fonction onSubmit.
 */
function GoalForm({
  goal = null,
  characterId = null,
  isWarbandGoal = false,
  onSubmit,
  onCancel,
  isSubmitting = false,
}) {
  // Détermine si le formulaire sert à modifier un objectif existant.
  const isEditing = Boolean(goal);

  // États locaux correspondant aux champs du formulaire.
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [status, setStatus] = useState("IN_PROGRESS");

  // Permet d'afficher un message si le titre est invalide.
  const [validationError, setValidationError] = useState("");

  /**
   * Initialise les champs du formulaire.
   *
   * En création, les champs sont vides.
   * En modification, on reprend les valeurs de l'objectif existant.
   */
  useEffect(() => {
    setTitle(goal?.title ?? "");
    setDescription(goal?.description ?? "");
    setStatus(goal?.status ?? "IN_PROGRESS");
    setValidationError("");
  }, [goal]);

  // Permet de fermer la popup avec la touche Échap.
  useEffect(() => {
    function handleEscape(event) {
      if (event.key === "Escape" && !isSubmitting) {
        onCancel();
      }
    }

    window.addEventListener("keydown", handleEscape);

    // Nettoyage de l'écouteur lorsque la popup se ferme.
    return () => {
      window.removeEventListener("keydown", handleEscape);
    };
  }, [onCancel, isSubmitting]);

  /**
   * Gère la soumission du formulaire.
   *
   * On vérifie le titre avant de transmettre les données au parent.
   */
  function handleSubmit(event) {
    // Empêche le rechargement de la page lors de la soumission.
    event.preventDefault();

    // Supprime les espaces inutiles au début et à la fin.
    const cleanedTitle = title.trim();

    // Un titre vide n'est pas autorisé.
    if (!cleanedTitle) {
      setValidationError("Le titre de l'objectif est obligatoire.");
      return;
    }

    // Le titre ne doit pas dépasser 100 caractères.
    if (cleanedTitle.length > 100) {
      setValidationError("Le titre ne peut pas dépasser 100 caractères.");
      return;
    }

    // Efface une éventuelle ancienne erreur.
    setValidationError("");

    // Prépare les données à transmettre au composant parent.
    const goalData = {
      title: cleanedTitle,
      description: description.trim() || null,
      status,
      // Un objectif Warband n'est associé à aucun personnage.
      character_id: isWarbandGoal ? null : characterId,
    };

    // Le parent décide ensuite d'appeler createGoal ou updateGoal.
    onSubmit(goalData);
  }

  return (
    // Fond sombre qui recouvre la page.
    <div
      className="goal-modal-overlay"
      onClick={(event) => {
        // Ferme la popup uniquement si on clique sur le fond extérieur.
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
        aria-labelledby="goal-modal-title"
      >
        <div className="goal-modal-header">
          <h2 id="goal-modal-title">
            {isEditing ? "Modifier l'objectif" : "Créer un objectif"}
          </h2>

          {/* Bouton de fermeture en haut à droite. */}
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
          {/* Champ du titre : obligatoire et limité à 100 caractères. */}
          <div className="goal-form-field">
            <label htmlFor="goal-title">Titre *</label>

            <input
              id="goal-title"
              type="text"
              value={title}
              onChange={(event) => {
                setTitle(event.target.value);
                setValidationError("");
              }}
              placeholder="Ex. : Obtenir une nouvelle monture"
              maxLength={100}
              required
              disabled={isSubmitting}
              autoFocus
            />

            <span className="goal-form-counter">{title.length}/100</span>
          </div>

          {/* Champ facultatif de description. */}
          <div className="goal-form-field">
            <label htmlFor="goal-description">Description</label>

            <textarea
              id="goal-description"
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              placeholder="Ajoute quelques détails sur ton objectif..."
              rows={4}
              disabled={isSubmitting}
            />
          </div>

          {/* Sélection du statut de l'objectif. */}
          <div className="goal-form-field">
            <label htmlFor="goal-status">Statut</label>

            <select
              id="goal-status"
              value={status}
              onChange={(event) => setStatus(event.target.value)}
              disabled={isSubmitting}
            >
              {GOAL_STATUSES.map((item) => (
                <option key={item.value} value={item.value}>
                  {item.label}
                </option>
              ))}
            </select>
          </div>

          {/* Message de validation affiché si le titre est incorrect. */}
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
                  : "Créer l'objectif"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default GoalForm;
