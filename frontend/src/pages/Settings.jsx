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
      setError(err.message || "Unable to load the tag catalogue.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadTags();
  }, []);

  async function handleCreateTag(event) {
    event.preventDefault();

    const name = newTagName.trim();

    if (!name) {
      setError("Please enter a tag name.");
      return;
    }

    setSaving(true);
    setError("");
    setMessage("");

    try {
      await createTag(name);
      setNewTagName("");
      setMessage("Tag created successfully.");
      await loadTags();
    } catch (err) {
      setError(err.message || "Unable to create the tag.");
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
      setError("Please enter a tag name.");
      return;
    }

    setSaving(true);
    setError("");
    setMessage("");

    try {
      await updateTag(tagId, name);
      cancelEditing();
      setMessage("Tag updated successfully.");
      await loadTags();
    } catch (err) {
      setError(err.message || "Unable to update the tag.");
    } finally {
      setSaving(false);
    }
  }

  async function handleDeleteTag(tag) {
    const confirmed = window.confirm(
      `Are you sure you want to delete the tag "${tag.name}"?`,
    );

    if (!confirmed) {
      return;
    }

    setSaving(true);
    setError("");
    setMessage("");

    try {
      await deleteTag(tag.id);
      setMessage("Tag deleted successfully.");
      await loadTags();
    } catch (err) {
      setError(err.message || "Unable to delete the tag.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="settings-page">
      <div className="section-heading">
        <div>
          <p className="section-eyebrow">PREFERENCES</p>
          <h1>Settings</h1>
          <p className="collection-description">
            Manage your Warband HQ experience.
          </p>
        </div>
      </div>

      {isAdmin && (
        <section className="status-panel tag-settings">
          <h2>Tag catalogue</h2>
          <p>Manage the shared tags available to all Warband HQ users.</p>

          <form onSubmit={handleCreateTag}>
            <label htmlFor="new-tag-name">New tag</label>

            <div className="tag-form-row">
              <input
                id="new-tag-name"
                type="text"
                value={newTagName}
                onChange={(event) => setNewTagName(event.target.value)}
                placeholder="Enter a tag name"
                maxLength={50}
                required
              />

              <button type="submit" disabled={saving}>
                {saving ? "Saving..." : "Create tag"}
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
            <h3>Existing tags</h3>

            {loading ? (
              <p>Loading tags...</p>
            ) : tags.length === 0 ? (
              <p>No tags have been created yet.</p>
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
                          Save
                        </button>

                        <button
                          type="button"
                          onClick={cancelEditing}
                          disabled={saving}
                        >
                          Cancel
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
                            Rename
                          </button>

                          <button
                            type="button"
                            onClick={() => handleDeleteTag(tag)}
                            disabled={saving}
                          >
                            Delete
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
          <h3>Settings are coming soon</h3>
          <p>
            Personalization options and account preferences will be available
            here in a future update.
          </p>
        </div>
      )}
    </section>
  );
}

export default Settings;
