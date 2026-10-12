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
 */
export async function logout() {
  const response = await fetch(`${API_URL}/api/auth/logout`, {
    method: "POST",
    // Le cookie de session doit être transmis pour identifier la session.
    credentials: "include",
  });

  // Signale un échec pour que l'interface puisse l'afficher.
  if (!response.ok) {
    throw new Error("Logout failed.");
  }
}
