import { API_URL } from "./api.js";

/**
 * Récupère les personnages disponibles sur le compte Blizzard.
 *
 * Cette fonction ne dépend pas de React : elle s'occupe uniquement
 * de communiquer avec le backend et de traiter sa réponse.
 */
export async function getAvailableCharacters() {
  const response = await fetch(`${API_URL}/api/characters/available`, {
    // Nécessaire pour transmettre le cookie de session utilisateur.
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error(
      response.status === 401
        ? "Your session has expired. Please log in again."
        : "Unable to retrieve your characters.",
    );
  }

  const data = await response.json();

  // Garantit que la fonction renvoie toujours un tableau.
  return data.characters ?? [];
}

/**
 * Importe les personnages sélectionnés dans Warband HQ.
 *
 * @param {number[]} characterIds - Identifiants des personnages sélectionnés.
 */
export async function importCharacters(characterIds) {
  const response = await fetch(`${API_URL}/api/characters/import`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      character_ids: characterIds,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.message || data.detail?.message || "Unable to import characters.",
    );
  }

  return data;
}

/**
 * Récupère les personnages déjà importés dans Warband HQ.
 */
export async function getImportedCharacters() {
  const response = await fetch(`${API_URL}/api/characters`, {
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error(
      response.status === 401
        ? "Your session has expired. Please log in again."
        : "Unable to retrieve imported characters.",
    );
  }

  const data = await response.json();

  return data.characters ?? [];
}

/**
 * Met à jour le statut favori d'un personnage importé.
 *
 * @param {number} characterId - Identifiant interne du personnage.
 * @param {boolean} isFavorite - Nouveau statut favori.
 */
export async function updateCharacterFavorite(characterId, isFavorite) {
  const response = await fetch(
    `${API_URL}/api/characters/${characterId}/favorite`,
    {
      method: "PATCH",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        is_favorite: isFavorite,
      }),
    },
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.message ||
        data.detail?.message ||
        "Unable to update character favorite.",
    );
  }

  return data.character;
}

/**
 * Récupère les tags associés à un personnage.
 *
 * @param {number} characterId - Identifiant interne du personnage.
 */
export async function getCharacterTags(characterId) {
  const response = await fetch(
    `${API_URL}/api/characters/${characterId}/tags`,
    {
      credentials: "include",
    },
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.message || data.detail?.message || "Unable to retrieve tags.",
    );
  }

  return data.tags ?? [];
}

/**
 * Associe un tag à un personnage appartenant à l'utilisateur connecté.
 *
 * @param {number} characterId - Identifiant interne du personnage.
 * @param {number} tagId - Identifiant du tag.
 */
export async function assignCharacterTag(characterId, tagId) {
  const response = await fetch(
    `${API_URL}/api/characters/${characterId}/tags/${tagId}`,
    {
      method: "POST",
      credentials: "include",
    },
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.message || data.detail?.message || "Unable to assign tag.",
    );
  }

  return data;
}

/**
 * Retire un tag d'un personnage appartenant à l'utilisateur connecté.
 *
 * @param {number} characterId - Identifiant interne du personnage.
 * @param {number} tagId - Identifiant du tag.
 */
export async function removeCharacterTag(characterId, tagId) {
  const response = await fetch(
    `${API_URL}/api/characters/${characterId}/tags/${tagId}`,
    {
      method: "DELETE",
      credentials: "include",
    },
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.message || data.detail?.message || "Unable to remove tag.",
    );
  }

  return data;
}

/**
 * Récupère le catalogue global des tags.
 *
 * Tous les utilisateurs authentifiés peuvent consulter ce catalogue.
 */
export async function getTags() {
  const response = await fetch(`${API_URL}/api/tags`, {
    credentials: "include",
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.message || data.detail?.message || "Unable to retrieve tags.",
    );
  }

  return data.tags ?? [];
}

/**
 * Crée un tag dans le catalogue global.
 *
 * Cette opération est réservée aux administrateurs.
 *
 * @param {string} name - Nom du tag à créer.
 */
export async function createTag(name) {
  const response = await fetch(`${API_URL}/api/tags`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ name }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.message || data.detail?.message || "Unable to create tag.",
    );
  }

  return data.tag;
}

/**
 * Modifie un tag du catalogue global.
 *
 * Cette opération est réservée aux administrateurs.
 *
 * @param {number} tagId - Identifiant du tag à modifier.
 * @param {string} name - Nouveau nom du tag.
 */
export async function updateTag(tagId, name) {
  const response = await fetch(`${API_URL}/api/tags/${tagId}`, {
    method: "PATCH",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ name }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.message || data.detail?.message || "Unable to update tag.",
    );
  }

  return data.tag;
}

/**
 * Supprime un tag du catalogue global.
 *
 * Cette opération est réservée aux administrateurs.
 *
 * @param {number} tagId - Identifiant du tag à supprimer.
 */
export async function deleteTag(tagId) {
  const response = await fetch(`${API_URL}/api/tags/${tagId}`, {
    method: "DELETE",
    credentials: "include",
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.message || data.detail?.message || "Unable to delete tag.",
    );
  }

  return data;
}
