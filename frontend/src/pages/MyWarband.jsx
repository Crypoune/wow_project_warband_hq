import { useMemo, useState } from "react";

import CharacterFilters from "../components/warband/CharacterFilters.jsx";

// Importation des icônes de factions.
import { CLASS_ICONS, CLASS_COLORS } from "../data/wowClasses";
import { RACE_ICONS } from "../data/wowRaces";
import { FACTION_ICONS } from "../data/wowFactions";

import { LayoutGrid, List, Star } from "lucide-react";

/**
 * Bouton permettant d'ajouter ou de retirer un personnage des favoris.
 * L'état du bouton dépend de la propriété is_favorite du personnage.
 * Le changement est transmis au composant parent via onToggleFavorite.
 */
function FavoriteButton({ character, onToggleFavorite }) {
  const isFavorite = Boolean(character.is_favorite);

  return (
    <button
      type="button"
      className={`favorite-button ${isFavorite ? "is-favorite" : ""}`}
      onClick={() => onToggleFavorite(character.id, !isFavorite)}
      aria-label={
        isFavorite
          ? `Retirer ${character.name} des favoris`
          : `Ajouter ${character.name} aux favoris`
      }
      aria-pressed={isFavorite}
      title={isFavorite ? "Retirer des favoris" : "Ajouter aux favoris"}
    >
      <Star
        size={20}
        fill={isFavorite ? "currentColor" : "none"}
        strokeWidth={1.8}
        aria-hidden="true"
      />
    </button>
  );
}

/**
 * Affiche les niveaux d'objet d'un personnage.
 *
 * average_item_level : niveau d'objet moyen du personnage.
 * equipped_item_level : niveau d'objet de son équipement actuellement porté.
 *
 * Les valeurs peuvent être null si Blizzard ne fournit pas ces données.
 */
function CharacterItemLevel({ character }) {
  const averageItemLevel = character.average_item_level;
  const equippedItemLevel = character.equipped_item_level;

  // Si aucune valeur n'est disponible, on affiche un indicateur neutre.
  if (averageItemLevel == null && equippedItemLevel == null) {
    return (
      <div className="character-item-level">
        <span className="character-item-level-label">Niv. d'objet</span>
        <span className="character-item-level-unavailable">—</span>
      </div>
    );
  }

  return (
    <div
      className="character-item-level"
      aria-label={`Niveau d'objet moyen : ${averageItemLevel ?? "indisponible"} ; équipement : ${equippedItemLevel ?? "indisponible"}`}
    >
      <span className="character-item-level-label">Niv. d'objet</span>

      <span className="character-item-level-value">
        {averageItemLevel ?? "—"}
      </span>

      <span className="character-item-level-separator" aria-hidden="true">
        /
      </span>

      <span className="character-item-level-equipped">
        {equippedItemLevel ?? "—"}
      </span>

      <span className="character-item-level-tooltip">Moyen / Équipé</span>
    </div>
  );
}

/**
 * Affiche les tags associés à un personnage.
 * Si aucun tag n'est disponible, un message par défaut est affiché.
 */
function CharacterTags({ tags = [] }) {
  return (
    <div className="character-tags">
      <div className="character-tags-list">
        {tags.length > 0 ? (
          tags.map((tag) => (
            <span className="character-tag" key={tag.id}>
              {tag.name}
            </span>
          ))
        ) : (
          <span className="character-tags-empty">Aucun tag</span>
        )}
      </div>
    </div>
  );
}

function MyWarband({
  importedCharacters,
  loadingImportedCharacters,
  onToggleFavorite,
  onViewDetails,
}) {
  // Mode d'affichage de la collection : cartes ou liste.
  const [viewMode, setViewMode] = useState("grid");

  // Contrôle l'ouverture du panneau de recherche et de filtres.
  const [showFilters, setShowFilters] = useState(false);

  // Indique si seuls les personnages favoris doivent être affichés.
  const [favoritesOnly, setFavoritesOnly] = useState(false);

  // Texte utilisé pour rechercher un personnage.
  const [searchTerm, setSearchTerm] = useState("");

  // Classe sélectionnée dans le filtre.
  const [selectedClass, setSelectedClass] = useState("all");

  // Faction sélectionnée dans le filtre.
  const [selectedFaction, setSelectedFaction] = useState("all");

  // Critère et sens du tri.
  const [sortBy, setSortBy] = useState("name-asc");

  // Construit la liste des classes présentes dans la collection.
  // Set supprime les doublons, filter(Boolean) écarte les valeurs vides,
  // puis sort classe les noms par ordre alphabétique.
  // useMemo évite de recalculer cette liste si la collection ne change pas.
  const availableClasses = useMemo(() => {
    return [
      ...new Set(
        importedCharacters.map((character) => character.class).filter(Boolean),
      ),
    ].sort((a, b) => a.localeCompare(b));
  }, [importedCharacters]);

  // Calcule la liste affichée en appliquant la recherche, les filtres et le tri.
  // useMemo recalcule le résultat uniquement lorsque l'une des dépendances change.
  const filteredCharacters = useMemo(() => {
    const normalizedSearch = searchTerm.trim().toLocaleLowerCase();

    const filtered = importedCharacters.filter((character) => {
      // Recherche dans le nom, la race et la classe.
      const matchesSearch = [
        character.name,
        character.race,
        character.class,
        character.realm,
      ].some((value) =>
        String(value ?? "")
          .toLocaleLowerCase()
          .includes(normalizedSearch),
      );

      const matchesClass =
        selectedClass === "all" || character.class === selectedClass;

      const matchesFaction =
        selectedFaction === "all" || character.faction === selectedFaction;

      const matchesFavorite = !favoritesOnly || character.is_favorite === true;

      // Un personnage est conservé uniquement s'il satisfait tous les critères actifs.
      return matchesSearch && matchesClass && matchesFaction && matchesFavorite;
    });

    // Trie une nouvelle copie pour ne pas modifier le tableau original.
    return [...filtered].sort((a, b) => {
      switch (sortBy) {
        case "name-desc":
          return (b.name ?? "").localeCompare(a.name ?? "");

        case "level-desc":
          return (b.level ?? -1) - (a.level ?? -1);

        case "level-asc":
          return (a.level ?? Infinity) - (b.level ?? Infinity);

        case "realm-asc":
          return (a.realm ?? "").localeCompare(b.realm ?? "");

        case "name-asc":
        default:
          return (a.name ?? "").localeCompare(b.name ?? "");
      }
    });
  }, [
    importedCharacters,
    searchTerm,
    selectedClass,
    selectedFaction,
    sortBy,
    favoritesOnly,
  ]);

  // Réinitialise les critères de recherche et de filtrage.
  const resetFilters = () => {
    setSearchTerm("");
    setSelectedClass("all");
    setSelectedFaction("all");
    setSortBy("name-asc");
    setFavoritesOnly(false);
  };

  return (
    <section className="characters-section">
      <div className="section-heading">
        <div>
          <p className="section-eyebrow">VOTRE COLLECTION</p>
          <h2>Mon bataillon</h2>
          <p className="collection-description">
            Vos héros réunis au même endroit.
          </p>
        </div>

        <div className="collection-count" aria-live="polite">
          <span className="collection-count-value">
            {filteredCharacters.length}
          </span>

          <span className="collection-count-label">
            {filteredCharacters.length === 1 ? "PERSONNAGE" : "PERSONNAGES"}
          </span>
        </div>

        {/* Contient les deux boutons permettant de choisir la présentation
          des personnages : sous forme de grille ou sous forme de liste. */}
        <div
          className="view-toggle"
          aria-label="Mode d'affichage des personnages"
        >
          <button
            type="button"
            className={
              // Opérateur ternaire : ajoute la classe "active" si le mode
              // sélectionné est "grid", sinon utilise la classe sans "active".
              viewMode === "grid"
                ? "view-toggle-button active"
                : "view-toggle-button"
            }
            // Au clic, met à jour viewMode avec la valeur "grid".
            onClick={() => setViewMode("grid")}
            aria-label="Afficher les personnages sous forme de cartes"
            // Indique aux technologies d'assistance si ce bouton est actif.
            aria-pressed={viewMode === "grid"}
          >
            {/* Affiche l'icône représentant une grille grâce à lucide-react. */}
            <LayoutGrid size={20} strokeWidth={1.8} aria-hidden="true" />
          </button>

          <button
            type="button"
            className={
              viewMode === "list"
                ? "view-toggle-button active"
                : "view-toggle-button"
            }
            onClick={() => setViewMode("list")}
            aria-label="Afficher les personnages sous forme de liste"
            aria-pressed={viewMode === "list"}
          >
            <List size={20} strokeWidth={1.8} aria-hidden="true" />
          </button>
        </div>
      </div>

      {/* Affiche le composant qui gère la recherche, les filtres et le tri.
          Les valeurs et les fonctions lui sont transmises par des props. */}
      <CharacterFilters
        // Indique si le panneau de filtres est ouvert ou fermé.
        showFilters={showFilters}
        // Inverse l'état du panneau : ouvert s'il était fermé, et inversement.
        onToggleFilters={() => setShowFilters((previous) => !previous)}
        // Transmet le texte saisi dans la recherche.
        searchTerm={searchTerm}
        // Transmet la fonction qui met à jour le texte de recherche.
        onSearchChange={setSearchTerm}
        // Transmet la liste des classes disponibles dans la collection.
        availableClasses={availableClasses}
        // Transmet la classe actuellement sélectionnée.
        selectedClass={selectedClass}
        // Transmet la fonction qui modifie la classe sélectionnée.
        onClassChange={setSelectedClass}
        // Transmet la faction actuellement sélectionnée.
        selectedFaction={selectedFaction}
        // Transmet la fonction qui modifie la faction sélectionnée.
        onFactionChange={setSelectedFaction}
        // Indique si le filtre « favoris uniquement » est activé.
        favoritesOnly={favoritesOnly}
        // Transmet la fonction qui active ou désactive ce filtre.
        onFavoritesOnlyChange={setFavoritesOnly}
        // Transmet le critère de tri sélectionné.
        sortBy={sortBy}
        // Transmet la fonction qui modifie le critère de tri.
        onSortChange={setSortBy}
        // Transmet la fonction qui réinitialise les filtres.
        onResetFilters={resetFilters}
      />

      {/* Conditions d'affichage :
          1. Si les personnages sont en cours de chargement, affiche un message d'attente.
          2. Si aucun personnage n'a été importé, affiche un message invitant à en ajouter.
          3. Si les filtres ne renvoient aucun résultat, affiche un message adapté.
          4. Sinon, affiche les personnages correspondant aux critères. */}
      {loadingImportedCharacters ? (
        <div className="status-panel">
          <h3>Chargement de votre bataillon…</h3>
          <p>Récupération de vos personnages importés.</p>
        </div>
      ) : importedCharacters.length === 0 ? (
        <div className="status-panel">
          <h3>Votre bataillon vous attend</h3>
          <p>
            Vous n'avez encore importé aucun personnage. Sélectionnez des
            personnages ci-dessus pour commencer à constituer votre collection.
          </p>
        </div>
      ) : filteredCharacters.length === 0 ? (
        <div className="status-panel">
          <h3>Aucun personnage trouvé</h3>
          <p>
            Aucun personnage ne correspond à votre recherche ou à vos filtres.
            Modifiez vos critères ou réinitialisez les filtres.
          </p>
          <button
            type="button"
            className="filter-reset-button"
            onClick={resetFilters}
          >
            Réinitialiser les filtres
          </button>
        </div>
      ) : (
        <div
          // opération ternaire pour afficher la liste en grille si viewMode vaut grid sinon en liste
          className={viewMode === "grid" ? "character-grid" : "character-list"}
        >
          {/* Parcourt le tableau des personnages filtrés avec map().
              Pour chaque personnage, crée le contenu qui sera affiché.
              La fonction fléchée reçoit le personnage courant en paramètre. */}
          {filteredCharacters.map((character) => {
            // Recherche la couleur associée à la classe du personnage.
            // '??' fournit une couleur dorée si la valeur de gauche est null ou undefined.
            const classColor = CLASS_COLORS[character.class] ?? "#D7AA50";

            // Récupère l'icône correspondant à la classe du personnage.
            const classIcon = CLASS_ICONS[character.class];

            // Récupère l'icône correspondant à sa faction.
            const factionIcon = FACTION_ICONS[character.faction];

            // Récupère l'icône de sa race selon son identifiant et son genre.
            // '?.' évite une erreur si aucune donnée n'existe avant d'accéder à gender.
            const raceIcon = RACE_ICONS[character.race_id]?.[character.gender];

            // Fonction appelée lorsqu'on clique sur une carte de personnage.
            // event représente l'événement du clic et characterId l'identifiant du personnage.
            const handleCharacterCardClick = (event, characterId) => {
              // Recherche si l'élément cliqué est un bouton, une liste déroulante,
              // un champ de saisie ou un lien, ou s'il se trouve à l'intérieur de l'un d'eux.
              if (event.target.closest("button, select, input, a")) {
                // Arrête la fonction pour ne pas ouvrir la fiche du personnage.
                return;
              }

              // Demande au composant parent d'afficher la fiche du personnage sélectionné.
              onViewDetails(characterId);
            };

            return (
              // Retourne l'élément JSX qui représente ce personnage.
              <article
                // Construit le nom des classes CSS selon le mode d'affichage.
                // Si viewMode vaut "list", ajoute aussi la classe "character-row".}
                className={`character-card ${viewMode === "list" ? "character-row" : ""}`}
                // Fournit un identifiant unique à React pour chaque élément de la liste.
                key={character.id}
                // Transmet une variable CSS personnalisée contenant la couleur de la classe.
                style={{ "--class-color": classColor }}
                // Au clic, appelle la fonction qui vérifie si l'interaction vient d'un contrôle interne.
                onClick={(event) =>
                  handleCharacterCardClick(event, character.id)
                }
                // Gère les interactions au clavier lorsque la carte est sélectionnée.
                onKeyDown={(event) => {
                  // Ignore l'événement si le clavier est utilisé sur un élément enfant.
                  if (event.target !== event.currentTarget) return;

                  // Entrée ou espace permettent d'ouvrir la fiche du personnage.
                  if (event.key === "Enter" || event.key === " ") {
                    // Empêche le comportement par défaut de la touche, notamment le défilement avec espace.
                    event.preventDefault();

                    // Demande au composant parent d'afficher les détails du personnage.
                    onViewDetails(character.id);
                  }
                }}
                // Rend la carte accessible au clavier avec la touche Tab.
                tabIndex={0}
                // Indique aux technologies d'assistance que la carte se comporte comme un lien.
                role="link"
                // Fournit un nom accessible décrivant l'action et le personnage concerné.
                aria-label={`Afficher les détails de ${character.name}`}
              >
                {viewMode === "grid" ? (
                  // Affichage du contenu adapté au mode grille.
                  // Les fragments permettent de regrouper plusieurs éléments JSX
                  // sans ajouter de balise HTML supplémentaire.
                  <>
                    {/* Conteneur du portrait et des éléments affichés par-dessus. */}
                    <div className="character-portrait">
                      {/* Affiche le bouton permettant de gérer les favoris.
                        Le personnage et la fonction de mise à jour sont transmis en props. */}
                      <FavoriteButton
                        character={character}
                        onToggleFavorite={onToggleFavorite}
                      />

                      {/* Si une URL de portrait existe, affiche l'image.
                        Sinon, affiche un message de remplacement. */}
                      {character.portrait_url ? (
                        <img
                          // URL de l'image du personnage.
                          src={character.portrait_url}
                          // Texte alternatif décrivant l'image pour l'accessibilité.
                          alt={`Portrait de ${character.name}`}
                          className="character-portrait-image"
                          // Charge l'image seulement lorsqu'elle approche de la zone visible.
                          loading="lazy"
                        />
                      ) : (
                        <div className="character-portrait-placeholder">
                          Portrait indisponible
                        </div>
                      )}

                      {/* Regroupe les badges visuels du personnage. */}
                      <div className="character-badges">
                        {/* Affiche le niveau du personnage.
                            ?? affiche - uniquement si le niveau est null ou undefined. */}
                        <span className="character-badge character-level">
                          {character.level ?? "-"}
                        </span>

                        {/* Affiche l'icône de classe uniquement si elle existe.
                            && permet de rendre l'image seulement si classIcon est défini. */}
                        {classIcon && (
                          <img
                            src={classIcon}
                            alt={character.class || "Classe inconnue"}
                            className="character-badge character-class-badge"
                          />
                        )}

                        {/* Affiche l'icône de faction uniquement si elle existe. */}
                        {factionIcon && (
                          <img
                            src={factionIcon}
                            alt={character.faction}
                            className="character-badge character-faction-badge"
                          />
                        )}
                      </div>
                    </div>

                    {/* Contient les informations textuelles du personnage. */}
                    <div className="character-card-info">
                      <div className="character-card-heading">
                        {/* Affiche le nom du personnage.
                            || fournit un texte de remplacement si le nom est vide ou absent. */}
                        <h3 className="character-name">
                          {character.name || "Personnage inconnu"}
                        </h3>

                        {/* Affiche le royaume du personnage, avec une valeur de remplacement si besoin */}
                        <span className="character-realm">
                          {character.realm || "Royaume indisponible"}
                        </span>
                      </div>

                      {/* Affiche la classe du personnage et sa race si celle-ci est disponible. */}
                      <p className="character-class">
                        {character.class || "Classe indisponible"}
                        {/* Opérateur ternaire : ajoute un séparateur et la race si elle existe,
                            sinon affiche une chaîne de caractères vide. */}
                        {character.race ? ` · ${character.race}` : ""}
                      </p>

                      {/* Affiche le niveau d'objet moyen et celui de l'équipement porté.
                          Le composant reçoit les données du personnage via la prop character. */}
                      <CharacterItemLevel character={character} />
                    </div>
                  </>
                ) : (
                  // Branche alternative : ce contenu est affiché lorsque
                  // viewMode vaut "list", donc lorsque la collection est en mode liste.
                  <div className="character-row-content">
                    {/* Bouton permettant d'ajouter ou de retirer ce personnage des favoris. */}
                    <FavoriteButton
                      character={character}
                      onToggleFavorite={onToggleFavorite}
                    />

                    {/* Regroupe les icônes de faction, de race et de classe. */}
                    <div className="character-row-icons">
                      {/* Affiche l'icône de faction uniquement si elle existe.
                          && permet de conditionner le rendu JSX à la présence d'une valeur. */}
                      {factionIcon && (
                        <img
                          src={factionIcon}
                          alt={character.faction}
                          className="character-row-icon"
                          title={character.faction}
                        />
                      )}

                      {/* Si l'icône de race existe, affiche l'image.
                          Sinon, essaie d'afficher une initiale de la race si son nom existe. */}
                      {raceIcon ? (
                        <img
                          src={raceIcon}
                          alt={character.race || "Race inconnue"}
                          className="character-row-icon"
                          title={`${character.race} · ${
                            character.gender === "FEMALE" ? "Femme" : "Homme"
                          }`}
                          loading="lazy"
                        />
                      ) : (
                        character.race && (
                          <span
                            className="character-race-icon-placeholder"
                            title={character.race}
                            aria-label={character.race}
                          >
                            {character.race.slice(0, 1)}
                          </span>
                        )
                      )}

                      {/* Affiche l'icône de classe uniquement si elle est disponible. */}
                      {classIcon && (
                        <img
                          src={classIcon}
                          alt={character.class}
                          className="character-row-icon"
                          title={character.class}
                        />
                      )}
                    </div>

                    {/* Affiche le nom du personnage dans la ligne. */}
                    <h3 className="character-name character-row-name">
                      {/* Utilise un texte de remplacement si le nom est absent. */}
                      {character.name || "Unknown character"}
                    </h3>

                    {/* Affiche le niveau du personnage, avec "-" si la valeur est absente.
                        Ce niveau est différent du niveau d'objet de son équipement. */}
                    <span
                      className="character-row-level"
                      title="Niveau du personnage"
                    >
                      {character.level ?? "-"}
                    </span>

                    {/* Réutilise le composant qui affiche les deux niveaux d'objet. */}
                    <CharacterItemLevel character={character} />

                    {/* Affiche le royaume du personnage, avec une valeur de remplacement si nécessaire. */}
                    <span className="character-row-realm">
                      {character.realm || "Realm unavailable"}
                    </span>
                  </div>
                )}
                {/* Affiche les tags du personnage.
                    ?? [] transmet un tableau vide si character.tags est null ou undefined,
                    afin que le composant CharacterTags reçoive toujours un tableau. */}
                <CharacterTags tags={character.tags ?? []} />
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}

export default MyWarband;
