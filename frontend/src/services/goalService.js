import { API_URL } from "./api.js";

/**
 * Gère les communications avec l'API des objectifs.
 *
 * Ce service ne dépend pas de React :
 * il s'occupe uniquement des requêtes HTTP vers le backend.
 */

/**
 * Récupère les objectifs de l'utilisateur connecté.
 *
 * @returns {Promise<object[]>} Liste des objectifs.
 */
export const getGoals = async () => {
  const response = await fetch(`${API_URL}/api/goals`, {
    method: "GET",
    credentials: "include",
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Impossible de récupérer les objectifs.");
  }

  // L'API renvoie un objet contenant le tableau dans data.goals.
  return data.goals;
};

/**
 * Crée un nouvel objectif.
 *
 * @param {object} goalData - Informations du nouvel objectif.
 * @param {string} goalData.title - Titre de l'objectif.
 * @param {string|null} goalData.description - Description facultative.
 * @param {number|null} goalData.character_id - Personnage associé ou null.
 * @param {string} goalData.status - Statut de l'objectif.
 */
export async function createGoal(goalData) {
  const response = await fetch(`${API_URL}/api/goals`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(goalData),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.message || data.detail || "Impossible de créer cet objectif.",
    );
  }

  return data;
}

/**
 * Modifie un objectif existant.
 *
 * @param {number} goalId - Identifiant de l'objectif.
 * @param {object} updates - Champs à modifier.
 */
export async function updateGoal(goalId, updates) {
  const response = await fetch(`${API_URL}/api/goals/${goalId}`, {
    method: "PATCH",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(updates),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.message || data.detail || "Impossible de modifier cet objectif.",
    );
  }

  return data;
}

/**
 * Supprime un objectif.
 *
 * @param {number} goalId - Identifiant de l'objectif.
 */
export async function deleteGoal(goalId) {
  const response = await fetch(`${API_URL}/api/goals/${goalId}`, {
    method: "DELETE",
    credentials: "include",
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.message || data.detail || "Impossible de supprimer cet objectif.",
    );
  }

  return data;
}
