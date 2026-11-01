import { API_URL } from "./api.js";

/**
 * Gère les communications avec l'API des tâches.
 *
 * Ce service ne dépend pas de React :
 * il s'occupe uniquement des requêtes HTTP vers le backend.
 */

/**
 * Récupère les tâches associées à un objectif.
 *
 * @param {number} goalId - Identifiant de l'objectif.
 * @returns {Promise<object[]>} Liste des tâches.
 */
export async function getTasks(goalId) {
  const response = await fetch(`${API_URL}/api/goals/${goalId}/tasks`, {
    method: "GET",
    credentials: "include",
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.message || data.detail || "Impossible de récupérer les tâches.",
    );
  }

  return data.tasks;
}

/**
 * Crée une nouvelle tâche.
 *
 * @param {number} goalId - Identifiant de l'objectif associé.
 * @param {object} taskData - Informations de la nouvelle tâche.
 * @param {string} taskData.title - Titre de la tâche.
 * @param {string|null} taskData.description - Description facultative.
 * @returns {Promise<object>} Tâche créée.
 */
export async function createTask(goalId, taskData) {
  const response = await fetch(`${API_URL}/api/goals/${goalId}/tasks`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(taskData),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.message || data.detail || "Impossible de créer cette tâche.",
    );
  }

  return data;
}

/**
 * Modifie une tâche existante.
 *
 * @param {number} taskId - Identifiant de la tâche.
 * @param {object} updates - Champs à modifier.
 * @returns {Promise<object>} Tâche modifiée.
 */
export async function updateTask(taskId, updates) {
  const response = await fetch(`${API_URL}/api/tasks/${taskId}`, {
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
      data.message || data.detail || "Impossible de modifier cette tâche.",
    );
  }

  return data;
}

/**
 * Supprime une tâche.
 *
 * @param {number} taskId - Identifiant de la tâche.
 * @returns {Promise<object>} Résultat de la suppression.
 */
export async function deleteTask(taskId) {
  const response = await fetch(`${API_URL}/api/tasks/${taskId}`, {
    method: "DELETE",
    credentials: "include",
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.message || data.detail || "Impossible de supprimer cette tâche.",
    );
  }

  return data;
}
