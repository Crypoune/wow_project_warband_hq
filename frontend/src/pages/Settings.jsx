import { useEffect, useState } from "react";
import {
  getTags,
  createTag,
  updateTag,
  deleteTag,
} from "../services/characterService.js";

function Settings({ user }) {
  const isAdmin = user?.role === "ADMIN";

  const [tags, setTags] = useState([]);
  const [newTagName, setNewTagName] = useState("");
  const [editingTagId, setEditingTagId] = useState(null);
  const [editingTagName, setEditingTagName] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function loadTags() {
    setLoading(true);
    setError("");

    try {
      const data = await getTags();
      setTags(Array.isArray(data) ? data : (data?.tags ?? []));
    } catch (err) {
      setError(err.message || "Impossible de charger le catalogue des tags.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    let cancelled = false;

    async function loadInitialTags() {
      try {
        const data = await getTags();

        if (!cancelled) {
          setTags(Array.isArray(data) ? data : (data?.tags ?? []));
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err.message || "Impossible de charger le catalogue des tags.",
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadInitialTags();

    return () => {
      cancelled = true;
    };
  }, []);

  async function handleCreateTag(event) {
    event.preventDefault();

    const name = newTagName.trim();

    if (!name) {
      setError("Veuillez saisir un nom de tag.");
      return;
    }

    setSaving(true);
    setError("");
    setMessage("");

    try {
      await createTag(name);
      setNewTagName("");
      setMessage("Tag créé avec succès.");
      await loadTags();
    } catch (err) {
      setError(err.message || "Impossible de créer le tag.");
    } finally {
      setSaving(false);
    }
  }

  function startEditing(tag) {
    setEditingTagId(tag.id);
    setEditingTagName(tag.name);
    setError("");
    setMessage("");
  }

  function cancelEditing() {
    setEditingTagId(null);
    setEditingTagName("");
  }

  async function handleUpdateTag(event, tagId) {
    event.preventDefault();

    const name = editingTagName.trim();

    if (!name) {
      setError("Veuillez saisir un nom de tag.");
      return;
    }

    setSaving(true);
    setError("");
    setMessage("");

    try {
      await updateTag(tagId, name);
      cancelEditing();
      setMessage("Tag modifié avec succès.");
      await loadTags();
    } catch (err) {
      setError(err.message || "Impossible de modifier le tag.");
    } finally {
      setSaving(false);
    }
  }

  async function handleDeleteTag(tag) {
    const confirmed = window.confirm(
      `Voulez-vous vraiment supprimer le tag « ${tag.name} » ?`,
    );

    if (!confirmed) {
      return;
    }

    setSaving(true);
    setError("");
    setMessage("");

    try {
      await deleteTag(tag.id);
      setMessage("Tag supprimé avec succès.");
      await loadTags();
    } catch (err) {
      setError(err.message || "Impossible de supprimer le tag.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="settings-page">
      <div className="section-heading">
        <div>
          <p className="section-eyebrow">PRÉFÉRENCES</p>
          <h1>Paramètres</h1>
          <p className="collection-description">
            Personnalisez votre expérience Warband HQ.
          </p>
        </div>
      </div>

      {isAdmin && (
        <section className="status-panel tag-settings">
          <h2>Catalogue des tags</h2>
          <p>
            Gérez les tags partagés disponibles pour tous les utilisateurs de
            Warband HQ.
          </p>

          <form onSubmit={handleCreateTag}>
            <label htmlFor="new-tag-name">Nouveau tag</label>

            <div className="tag-form-row">
              <input
                id="new-tag-name"
                type="text"
                value={newTagName}
                onChange={(event) => setNewTagName(event.target.value)}
                placeholder="Saisissez le nom d'un tag"
                maxLength={50}
                required
              />

              <button type="submit" disabled={saving}>
                {saving ? "Enregistrement…" : "Créer le tag"}
              </button>
            </div>
          </form>

          {error && (
            <p role="alert" className="error-message">
              {error}
            </p>
          )}
          {message && (
            <p role="status" className="success-message">
              {message}
            </p>
          )}

          <div className="tag-catalog">
            <h3>Tags existants</h3>

            {loading ? (
              <p>Chargement des tags…</p>
            ) : tags.length === 0 ? (
              <p>Aucun tag n'a encore été créé.</p>
            ) : (
              <ul>
                {tags.map((tag) => (
                  <li key={tag.id} className="tag-catalog-item">
                    {editingTagId === tag.id ? (
                      <form
                        onSubmit={(event) => handleUpdateTag(event, tag.id)}
                      >
                        <input
                          type="text"
                          value={editingTagName}
                          onChange={(event) =>
                            setEditingTagName(event.target.value)
                          }
                          maxLength={50}
                          required
                          autoFocus
                        />

                        <button type="submit" disabled={saving}>
                          Enregistrer
                        </button>

                        <button
                          type="button"
                          onClick={cancelEditing}
                          disabled={saving}
                        >
                          Annuler
                        </button>
                      </form>
                    ) : (
                      <>
                        <span>{tag.name}</span>

                        <div className="tag-actions">
                          <button
                            type="button"
                            onClick={() => startEditing(tag)}
                            disabled={saving}
                          >
                            Renommer
                          </button>

                          <button
                            type="button"
                            onClick={() => handleDeleteTag(tag)}
                            disabled={saving}
                          >
                            Supprimer
                          </button>
                        </div>
                      </>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </section>
      )}

      {!isAdmin && (
        <div className="status-panel">
          <h3>Les paramètres arrivent bientôt</h3>
          <p>
            Les options de personnalisation et les préférences du compte seront
            disponibles ici lors d'une prochaine mise à jour.
          </p>
        </div>
      )}
    </section>
  );
}

export default Settings;
