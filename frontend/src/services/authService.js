import { API_URL } from "./api.js";

/*
 * Récupère le profil de l'utilisateur actuellement connecté.
 * Le backend utilise le cookie de session pour reconnaître l'utilisateur.
 */
export async function getCurrentUser() {
  const response = await fetch(`${API_URL}/api/auth/me`, {
    // Important : permet d'envoyer les cookies de session au backend.
    credentials: "include",
  });

  // Une réponse 401 signifie qu'aucune session valide n'est disponible.
  if (response.status === 401) {
    return null;
  }

  // Pour les autres erreurs HTTP, on laisse App.jsx gérer le message.
  if (!response.ok) {
    throw new Error("Unable to retrieve your profile.");
  }

  // Convertit la réponse JSON du backend en objet JavaScript.
  return response.json();
}

/*
 * Termine la session de l'utilisateur auprès du backend.
 *
 * Cette fonction :
 * 1. Envoie une requête POST à l'API de déconnexion.
 * 2. Transmet le cookie de session pour identifier l'utilisateur.
 * 3. Déclenche une erreur si le backend renvoie un statut HTTP d'échec.
 *
 * Elle ne modifie pas directement l'état React :
 * c'est App.jsx qui s'occupe ensuite de mettre à jour l'interface.
 */
export async function logout() {
  // Envoie la demande de déconnexion au backend FastAPI.
  const response = await fetch(`${API_URL}/api/auth/logout`, {
    // POST est la méthode utilisée pour demander la déconnexion.
    method: "POST",

    // Permet d'envoyer le cookie de session au backend.
    credentials: "include",
  });

  // Une réponse HTTP hors de la plage 200-299 indique un échec.
  if (!response.ok) {
    throw new Error("Logout failed.");
  }
}
