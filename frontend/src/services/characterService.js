import { API_URL } from "./api.js";

/*
 * Récupère les personnages disponibles sur le compte Blizzard.
 * Cette fonction ne dépend pas de React : elle s'occupe uniquement
 * de communiquer avec le backend et de traiter sa réponse.
 */
export async function getAvailableCharacters() {
  // On demande au backend la liste des personnages disponibles.
  const response = await fetch(`${API_URL}/api/characters/available`, {
    // Nécessaire pour transmettre le cookie de session utilisateur.
    credentials: "include",
  });

  // Si le backend renvoie une erreur HTTP, on la transforme en erreur JavaScript.
  if (!response.ok) {
    throw new Error(
      response.status === 401
        ? "Your session has expired. Please log in again."
        : "Unable to retrieve your characters.",
    );
  }

  // Convertit la réponse JSON en objet JavaScript.
  const data = await response.json();

  // Garantit que la fonction renvoie toujours un tableau.
  return data.characters ?? [];
}

/*
 * Importe les personnages sélectionnés dans Warband HQ.
 *
 * characterIds contient les identifiants des personnages choisis
 * dans l'interface.
 */
export async function importCharacters(characterIds) {
  // Envoie la sélection au backend au format JSON.
  const response = await fetch(`${API_URL}/api/characters/import`, {
    method: "POST",

    // Transmet le cookie de session pour identifier l'utilisateur.
    credentials: "include",

    // Indique au backend que le corps de la requête est du JSON.
    headers: {
      "Content-Type": "application/json",
    },

    // Transforme le tableau JavaScript en chaîne JSON.
    body: JSON.stringify({
      character_ids: characterIds,
    }),
  });

  // Le backend renvoie les détails de l'erreur dans son corps JSON.
  const data = await response.json();

  // En cas d'échec, on conserve le message fourni par le backend.
  if (!response.ok) {
    throw new Error(data.detail?.message || "Unable to import characters.");
  }

  // Renvoie les données des personnages importés à App.jsx.
  return data;
}

/*
 * Récupère les personnages déjà importés dans Warband HQ.
 *
 * Cette fonction communique avec le backend pour obtenir
 * la collection de personnages de l'utilisateur connecté.
 */
export async function getImportedCharacters() {
  // Demande au backend la liste des personnages importés.
  const response = await fetch(`${API_URL}/api/characters`, {
    // Transmet le cookie de session utilisateur.
    credentials: "include",
  });

  // Si le backend signale une erreur, on la transforme en erreur JavaScript.
  if (!response.ok) {
    throw new Error(
      response.status === 401
        ? "Your session has expired. Please log in again."
        : "Unable to retrieve imported characters.",
    );
  }

  // Convertit la réponse JSON en objet JavaScript.
  const data = await response.json();

  // Garantit que la fonction renvoie toujours un tableau de personnages.
  return data.characters ?? [];
}
