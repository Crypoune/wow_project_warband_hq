import { useCallback, useEffect, useState } from "react";
import AppHeader from "./components/layout/AppHeader.jsx";
import Sidebar from "./components/layout/Sidebar.jsx";
import Overview from "./pages/Overview.jsx";
import MyWarband from "./pages/MyWarband.jsx";
import CharacterDetails from "./pages/CharacterDetails.jsx";
import Settings from "./pages/Settings.jsx";

// Adresse commune du backend FastAPI.
import { API_URL } from "./services/api.js";

// Fonctions dédiées à l'authentification auprès du backend.
import { getCurrentUser, logout } from "./services/authService.js";

// Fonctions dédiées à la récupération des personnages.
import {
  getAvailableCharacters,
  getImportedCharacters,
  importCharacters,
  updateCharacterFavorite,
} from "./services/characterService.js";

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [characters, setCharacters] = useState([]);
  const [selectedIds, setSelectedIds] = useState([]);
  const [loadingCharacters, setLoadingCharacters] = useState(false);

  // Personnages déjà importés dans Warband HQ.
  const [importedCharacters, setImportedCharacters] = useState([]);

  const [isSidebarExpanded, setIsSidebarExpanded] = useState(true);

  const [activePage, setActivePage] = useState("overview");

  const [selectedCharacterId, setSelectedCharacterId] = useState(null);

  // Indique si la collection importée est en cours de chargement.
  const [loadingImportedCharacters, setLoadingImportedCharacters] =
    useState(false);
  const [importing, setImporting] = useState(false);
  const [success, setSuccess] = useState("");

  const fetchAvailableCharacters = useCallback(async () => {
    setLoadingCharacters(true);
    setError("");
    setSuccess("");

    try {
      // Le service récupère les personnages et renvoie un tableau.
      const availableCharacters = await getAvailableCharacters();

      // React conserve la responsabilité de mettre à jour l'interface.
      setCharacters(availableCharacters);
      setSelectedIds([]);
    } catch (err) {
      // On conserve le message fourni par le service lorsqu'il existe.
      setError(
        err.message || "Unable to contact Warband HQ. Please try again.",
      );
    } finally {
      // L'indicateur de chargement est désactivé même en cas d'erreur.
      setLoadingCharacters(false);
    }
  }, []);

  // Charge les personnages déjà importés dans Warband HQ.
  const fetchImportedCharacters = useCallback(async () => {
    // Active l'indicateur de chargement de la collection importée.
    setLoadingImportedCharacters(true);

    try {
      // Le service récupère la collection auprès du backend.
      const imported = await getImportedCharacters();

      // Met à jour la liste des personnages importés dans React.
      setImportedCharacters(imported);
    } catch (err) {
      // Affiche une erreur si la récupération de la collection échoue.
      setError(
        err.message ||
          "Unable to retrieve imported characters. Please try again.",
      );
    } finally {
      // Arrête toujours l'indicateur de chargement.
      setLoadingImportedCharacters(false);
    }
  }, []);

  // Met à jour le statut favori d'un personnage.
  const handleToggleFavorite = async (characterId, isFavorite) => {
    setError("");

    try {
      const updatedCharacter = await updateCharacterFavorite(
        characterId,
        isFavorite,
      );

      setImportedCharacters((currentCharacters) =>
        currentCharacters.map((character) =>
          character.id === updatedCharacter.id
            ? { ...character, ...updatedCharacter }
            : character,
        ),
      );
    } catch (err) {
      setError(
        err.message || "Unable to update character favorite. Please try again.",
      );
    }
  };

  const handleUpdateCharacterTags = (characterId, tags) => {
    setImportedCharacters((currentCharacters) =>
      currentCharacters.map((character) =>
        character.id === characterId ? { ...character, tags } : character,
      ),
    );
  };

  const handleViewCharacterDetails = (characterId) => {
    setSelectedCharacterId(characterId);
    setActivePage("character-details");
    setError("");
  };

  const handleBackToWarband = () => {
    setActivePage("warband");
    setSelectedCharacterId(null);
  };

  // Vérifie si l'utilisateur possède déjà une session valide.
  useEffect(() => {
    async function fetchCurrentUser() {
      try {
        // Le service s'occupe de la requête HTTP et de la gestion du statut 401.
        const data = await getCurrentUser();

        // Si aucune session n'existe, l'utilisateur reste déconnecté.
        if (data === null) {
          setUser(null);
          return;
        }

        // Une session valide nous fournit les informations de l'utilisateur.
        setUser(data);

        // Après le retour de Blizzard, on retire le paramètre "auth" de l'URL.
        const url = new URL(window.location.href);

        if (url.searchParams.has("auth")) {
          url.searchParams.delete("auth");
          window.history.replaceState({}, "", url);
        }
      } catch {
        // En cas de problème réseau ou serveur, on affiche un message générique.
        setError("Unable to contact Warband HQ. Please try again.");
      } finally {
        // Dans tous les cas, on termine l'état de chargement initial.
        setLoading(false);
      }
    }

    fetchCurrentUser();
  }, []);

  useEffect(() => {
    if (!user) {
      return;
    }

    // Regroupe le chargement des deux collections.
    async function loadCharacters() {
      await Promise.all([
        fetchAvailableCharacters(),
        fetchImportedCharacters(),
      ]);
    }

    // Lance le chargement après la mise en place de l'effet.
    loadCharacters();
  }, [user, fetchAvailableCharacters, fetchImportedCharacters]);

  // Redirige l'utilisateur vers le parcours de connexion Blizzard.
  const handleBlizzardLogin = () => {
    window.location.href = `${API_URL}/api/auth/login`;
  };

  // Réinitialise les données utilisateur conservées dans l'état React.
  const resetUserData = () => {
    // Supprime l'utilisateur connecté.
    setUser(null);

    // Vide les personnages récupérés depuis Blizzard.
    setCharacters([]);

    // Vide les personnages déjà importés dans Warband HQ.
    setImportedCharacters([]);

    // Retire tous les personnages de la sélection.
    setSelectedIds([]);
  };

  // Déconnecte l'utilisateur et met à jour l'interface.
  const handleLogout = async () => {
    // Efface les anciens messages avant de commencer.
    setError("");
    setSuccess("");

    try {
      // Attend la réponse du backend avant de réinitialiser les données locales.
      await logout();

      // La déconnexion ayant réussi, on nettoie les données de l'interface.
      resetUserData();
    } catch (err) {
      // En cas d'échec, on affiche un message sans effacer les données.
      setError(err.message || "Unable to log out. Please try again.");
    }
  };

  // Ajoute un personnage à la sélection ou l'en retire s'il est déjà sélectionné.
  const toggleCharacter = (characterId) => {
    // On demande à React de nous fournir la sélection précédente.
    setSelectedIds((currentIds) => {
      // Vérifie si l'identifiant du personnage est déjà présent dans le tableau.
      const isAlreadySelected = currentIds.includes(characterId);

      // Si le personnage est sélectionné, on le retire du tableau.
      if (isAlreadySelected) {
        // filter() crée un nouveau tableau sans l'identifiant concerné.
        return currentIds.filter((id) => id !== characterId);
      }

      // Sinon, on crée un nouveau tableau contenant l'ancienne sélection
      // et l'identifiant du personnage ajouté.
      return [...currentIds, characterId];
    });
  };

  // Sélectionne tous les personnages disponibles ou retire toute la sélection.
  const handleSelectAll = () => {
    // React fournit la sélection précédente pour calculer la suivante.
    setSelectedIds((previousIds) => {
      // Vérifie si tous les personnages disponibles sont déjà sélectionnés.
      const allSelected = previousIds.length === characters.length;

      // Si tout est sélectionné, on vide la sélection.
      if (allSelected) {
        return [];
      }

      // Sinon, on sélectionne les identifiants de tous les personnages.
      return characters.map((character) => character.id);
    });
  };

  // Importe dans Warband HQ les personnages sélectionnés par l'utilisateur.
  const handleImport = async () => {
    // Protection : aucun import n'est nécessaire si la sélection est vide.
    // On bloque aussi une nouvelle demande pendant un import en cours.
    if (selectedIds.length === 0 || importing) {
      return;
    }

    // Efface les anciens messages avant de lancer une nouvelle opération.
    setError("");
    setSuccess("");

    // Active l'indicateur de chargement pour informer l'utilisateur.
    setImporting(true);

    try {
      // Envoie les identifiants sélectionnés au backend et attend sa réponse.
      const data = await importCharacters(selectedIds);

      // Récupère le nombre de personnages renvoyés par le backend.
      // Le ?. évite une erreur si data.characters est absent.
      // Le ?? 0 utilise zéro si le résultat est null ou undefined.
      const importedCount = data.characters?.length ?? 0;

      // Affiche un message adapté au résultat de l'importation.
      setSuccess(
        importedCount > 0
          ? `${importedCount} character(s) imported successfully.`
          : "No new characters were imported. They may already be in your warband.",
      );

      // Réinitialise la sélection après une réponse réussie.
      setSelectedIds([]);

      // Recharge la collection pour afficher les personnages importés.
      // On attend la fin du rafraîchissement avant de terminer cette fonction.
      await fetchImportedCharacters();
    } catch (err) {
      // Affiche le message d'erreur fourni par le service lorsqu'il existe.
      // Sinon, utilise un message générique.
      setError(err.message || "Unable to import characters. Please try again.");
    } finally {
      // Désactive toujours le chargement, même si une erreur survient.
      setImporting(false);
    }
  };

  return (
    <main
      className={`app-page ${
        isSidebarExpanded ? "sidebar-expanded" : "sidebar-collapsed"
      }`}
    >
      {/* Background decor */}
      <div className="app-background" aria-hidden="true" />

      <AppHeader
        user={user}
        onLogout={handleLogout}
        onLogin={handleBlizzardLogin}
      />

      <Sidebar
        isExpanded={isSidebarExpanded}
        onToggle={() => setIsSidebarExpanded((previous) => !previous)}
        activeItem={activePage}
        onNavigate={setActivePage}
      />

      <section className="app-content">
        {loading ? (
          <div className="status-panel">
            <h2>Checking your session...</h2>
            <p>Please wait while we contact Warband HQ.</p>
          </div>
        ) : !user ? (
          <section className="login-card">
            <div className="brand">
              <span className="brand-icon" aria-hidden="true">
                ✦
              </span>
              <p className="brand-label">YOUR ADVENTURE, ORGANIZED</p>
              <h1>
                Warband <span>HQ</span>
              </h1>
              <p className="brand-description">
                Your World of Warcraft characters, all in one place.
              </p>
            </div>

            <div className="login-divider">
              <span />
              <span className="divider-diamond">◆</span>
              <span />
            </div>

            <div className="login-content">
              <h2>Welcome, adventurer</h2>
              <p>
                Connect your Battle.net account to retrieve and import your
                characters.
              </p>

              <p className="login-note">
                Secure authentication powered by Blizzard
              </p>
            </div>

            <footer className="login-footer">
              <span>WARBAND HQ</span>
              <span>AZEROTH IS WAITING</span>
            </footer>
          </section>
        ) : (
          <>
            {/* Affiche la page Overview uniquement lorsque cette page est sélectionnée. */}
            {activePage === "overview" && (
              <>
                {/* Données et actions transmises à la page Overview via ses props. */}
                <Overview
                  user={user}
                  characters={characters}
                  selectedIds={selectedIds}
                  loadingCharacters={loadingCharacters}
                  importing={importing}
                  onRefresh={fetchAvailableCharacters}
                  onToggleCharacter={toggleCharacter}
                  onSelectAll={handleSelectAll}
                  onImport={handleImport}
                />
              </>
            )}

            {activePage === "warband" && (
              <MyWarband
                importedCharacters={importedCharacters}
                loadingImportedCharacters={loadingImportedCharacters}
                onToggleFavorite={handleToggleFavorite}
                onViewDetails={handleViewCharacterDetails}
              />
            )}

            {activePage === "character-details" &&
              selectedCharacterId !== null && (
                <CharacterDetails
                  characterId={selectedCharacterId}
                  onBack={handleBackToWarband}
                  onUpdateTags={handleUpdateCharacterTags}
                />
              )}

            {activePage === "settings" && <Settings user={user} />}
          </>
        )}

        {error && (
          <p className="feedback-message error-message" role="alert">
            {error}
          </p>
        )}

        {success && (
          <p className="feedback-message success-message" role="status">
            {success}
          </p>
        )}
      </section>

      <footer className="page-footer">
        <span>WARBAND HQ</span>
        <span>BUILT FOR YOUR ADVENTURE IN AZEROTH</span>
      </footer>
    </main>
  );
}

export default App;
