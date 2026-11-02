import { useEffect, useState } from "react";
import { Pencil, Save, X, StickyNote } from "lucide-react";

import {
  getCharacterNote,
  saveCharacterNote,
} from "../../services/characterService.js";

/**
 * Affiche et permet de gérer la note personnelle d'un personnage.
 *
 * Le composant gère lui-même la récupération et la sauvegarde
 * de la note auprès du backend.
 *
 * @param {number} characterId - Identifiant interne du personnage.
 */
function CharacterNote({ characterId }) {
  // Contenu actuel de la note.
  const [note, setNote] = useState("");

  // Contenu temporaire pendant l'édition.
  const [editedNote, setEditedNote] = useState("");

  // Indique si le composant est en mode édition.
  const [isEditing, setIsEditing] = useState(false);

  // États de chargement et de sauvegarde.
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  // Message d'erreur éventuel.
  const [error, setError] = useState("");

  /**
   * Récupère la note personnelle du personnage au chargement.
   */
  useEffect(() => {
    async function fetchNote() {
      try {
        setIsLoading(true);
        setError("");

        const noteData = await getCharacterNote(characterId);

        // Une note inexistante est représentée par une chaîne vide.
        const content = noteData?.content ?? "";

        setNote(content);
        setEditedNote(content);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    }

    fetchNote();
  }, [characterId]);

  /**
   * Annule les modifications et revient à l'affichage.
   */
  function handleCancel() {
    setEditedNote(note);
    setIsEditing(false);
    setError("");
  }

  /**
   * Enregistre la note personnelle auprès du backend.
   */
  async function handleSave() {
    try {
      setIsSaving(true);
      setError("");

      const noteData = await saveCharacterNote(characterId, editedNote);
      const content = noteData?.content ?? "";

      setNote(content);
      setEditedNote(content);
      setIsEditing(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <section className="character-note-panel">
      {/* Affiche un message pendant la récupération de la note. */}
      {isLoading && (
        <p className="character-note-loading">Chargement de la note...</p>
      )}

      {/* Affiche une erreur si la récupération a échoué. */}
      {!isLoading && error && (
        <p className="character-note-error" role="alert">
          {error}
        </p>
      )}

      {/* Affiche la note lorsque le chargement est terminé. */}
      {!isLoading && (!error || isEditing) && (
        <>
          <div className="character-note-header">
            <h3 className="character-note-title">
              <StickyNote size={18} aria-hidden="true" />
              Note personnelle
            </h3>

            {!isEditing && (
              <button
                type="button"
                className="character-note-edit"
                onClick={() => {
                  setEditedNote(note);
                  setIsEditing(true);
                }}
                aria-label="Modifier la note personnelle"
              >
                <Pencil size={16} aria-hidden="true" />
                Modifier
              </button>
            )}

            {isEditing && (
              <div className="character-note-actions">
                <button
                  type="button"
                  className="character-note-cancel"
                  onClick={handleCancel}
                  disabled={isSaving}
                >
                  <X size={16} aria-hidden="true" />
                  Annuler
                </button>

                <button
                  type="button"
                  className="character-note-save"
                  onClick={handleSave}
                  disabled={isSaving}
                >
                  <Save size={16} aria-hidden="true" />
                  {isSaving ? "Enregistrement..." : "Enregistrer"}
                </button>
              </div>
            )}
          </div>

          {isEditing ? (
            <div className="character-note-editor">
              <textarea
                value={editedNote}
                onChange={(event) => setEditedNote(event.target.value)}
                placeholder="Écris une note personnelle pour ce personnage..."
                rows={6}
                disabled={isSaving}
                aria-label="Contenu de la note personnelle"
              />
            </div>
          ) : (
            <div className="character-note-content">
              {note ? (
                <p>{note}</p>
              ) : (
                <p className="character-note-empty">
                  Aucune note pour le moment.
                </p>
              )}
            </div>
          )}
        </>
      )}
    </section>
  );
}

export default CharacterNote;
