import { useEffect, useState } from "react";
import { ArrowLeft, Shield, Trophy, Heart, Zap, Plus } from "lucide-react";
import { CLASS_COLORS, CLASS_ICONS } from "../data/wowClasses";
import { RACE_ICONS } from "../data/wowRaces";
import { FACTION_ICONS } from "../data/wowFactions";
import {
  getCharacterDetails,
  getTags,
  assignCharacterTag,
  removeCharacterTag,
} from "../services/characterService.js";
import {
  getGoals,
  createGoal,
  updateGoal,
  deleteGoal,
} from "../services/goalService.js";
import GoalCard from "../components/goals/GoalCard.jsx";
import GoalForm from "../components/goals/GoalForm.jsx";
import GoalFilters from "../components/goals/GoalFilters.jsx";
import DeleteGoalDialog from "../components/goals/DeleteGoalDialog.jsx";
import CharacterEquipment from "../components/character/CharacterEquipment.jsx";

const MAIN_STATS = [
  { key: "health", label: "Points de vie" },
  { key: "stamina", label: "Endurance" },
  { key: "strength", label: "Force" },
  { key: "agility", label: "Agilité" },
  { key: "intellect", label: "Intelligence" },
  { key: "armor", label: "Armure" },
];

const SECONDARY_STATS = [
  { key: "melee_crit", label: "Critique" },
  { key: "melee_haste", label: "Hâte" },
  { key: "mastery", label: "Maîtrise" },
  { key: "versatility", label: "Polyvalence" },
  { key: "avoidance", label: "Évitement" },
  { key: "speed", label: "Vitesse" },
  { key: "lifesteal", label: "Ponction" },
];

function formatStat(value, key) {
  if (value == null) return "—";

  const percentageStats = new Set([
    "melee_crit",
    "melee_haste",
    "mastery",
    "versatility",
    "avoidance",
    "speed",
    "lifesteal",
  ]);

  let statValue = value;

  if (typeof value === "object") {
    if (typeof value.effective === "number") {
      statValue = value.effective;
    } else if (typeof value.value === "number") {
      statValue = value.value;
    } else if (typeof value.rating_bonus === "number") {
      statValue = value.rating_bonus;
    } else if (typeof value.name === "string") {
      return value.name;
    } else {
      return "—";
    }
  }

  if (typeof statValue === "string") return statValue;
  if (typeof statValue !== "number") return "—";

  const formatted = new Intl.NumberFormat("fr-FR", {
    maximumFractionDigits: 2,
  }).format(statValue);

  return percentageStats.has(key) ? `${formatted} %` : formatted;
}

function getNamedValue(value) {
  if (typeof value === "string") return value;
  if (value && typeof value.name === "string") return value.name;
  return null;
}

function StatGroup({ title, icon: Icon, stats, values }) {
  return (
    <section className="character-stat-group">
      <header className="character-stat-group-header">
        <Icon size={18} aria-hidden="true" />
        <h3>{title}</h3>
      </header>

      <dl className="character-stat-list">
        {stats.map(({ key, label }) => (
          <div className="character-stat-row" key={key}>
            <dt>{label}</dt>
            <dd>
              {formatStat(
                key === "versatility"
                  ? values?.versatility_damage_done_bonus
                  : values?.[key],
                key,
              )}
            </dd>
          </div>
        ))}
      </dl>
    </section>
  );
}

function CharacterDetails({ characterId, onBack, onUpdateTags }) {
  const [character, setCharacter] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [availableTags, setAvailableTags] = useState([]);
  const [selectedTagId, setSelectedTagId] = useState("");
  const [loadingTags, setLoadingTags] = useState(true);
  const [tagActionLoading, setTagActionLoading] = useState(false);
  const [tagError, setTagError] = useState("");
  const [tagSuccess, setTagSuccess] = useState("");

  // ========================================
  // GESTION DES OBJECTIFS
  // ========================================

  // Liste complète des objectifs récupérés depuis le backend.
  const [goals, setGoals] = useState([]);

  // État du chargement et des erreurs liés aux objectifs.
  const [loadingGoals, setLoadingGoals] = useState(true);
  const [goalError, setGoalError] = useState("");
  const [goalSuccess, setGoalSuccess] = useState("");

  // Indique si une création ou une modification est en cours.
  const [goalFormOpen, setGoalFormOpen] = useState(false);
  const [editingGoal, setEditingGoal] = useState(null);
  const [isWarbandGoalForm, setIsWarbandGoalForm] = useState(false);
  const [goalActionLoading, setGoalActionLoading] = useState(false);

  // Objectif actuellement sélectionné pour une éventuelle suppression.
  const [goalToDelete, setGoalToDelete] = useState(null);
  const [isDeletingGoal, setIsDeletingGoal] = useState(false);

  // Chaque catégorie possède son propre filtre.
  const [characterGoalFilter, setCharacterGoalFilter] = useState("ALL");
  const [warbandGoalFilter, setWarbandGoalFilter] = useState("ALL");

  useEffect(() => {
    let cancelled = false;

    async function loadCharacter() {
      setLoading(true);
      setError("");
      setCharacter(null);

      try {
        const result = await getCharacterDetails(characterId);

        if (!cancelled) setCharacter(result);
      } catch (err) {
        if (!cancelled) {
          setError(
            err.message || "Impossible de récupérer les détails du personnage.",
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadCharacter();

    return () => {
      cancelled = true;
    };
  }, [characterId]);

  useEffect(() => {
    let cancelled = false;

    async function loadTags() {
      setLoadingTags(true);
      setTagError("");

      try {
        const result = await getTags();

        if (!cancelled) {
          setAvailableTags(result);
        }
      } catch (err) {
        if (!cancelled) {
          setTagError(
            err.message || "Impossible de récupérer les tags disponibles.",
          );
        }
      } finally {
        if (!cancelled) {
          setLoadingTags(false);
        }
      }
    }

    loadTags();

    return () => {
      cancelled = true;
    };
  }, []);

  /**
   * Charge tous les objectifs de l'utilisateur connecté.
   *
   * Le backend renvoie les objectifs du personnage ET ceux de la Warband.
   * Nous effectuerons la séparation dans le composant, à partir de
   * character_id.
   */
  useEffect(() => {
    let cancelled = false;

    async function loadGoals() {
      setLoadingGoals(true);
      setGoalError("");

      try {
        const result = await getGoals();

        if (!cancelled) {
          setGoals(result);
        }
      } catch (err) {
        if (!cancelled) {
          setGoalError(err.message || "Impossible de récupérer les objectifs.");
        }
      } finally {
        if (!cancelled) {
          setLoadingGoals(false);
        }
      }
    }

    loadGoals();

    // Évite de mettre à jour le composant si on quitte le personnage
    // avant la fin de la requête.
    return () => {
      cancelled = true;
    };
  }, [characterId]);

  async function handleAssignTag() {
    if (!selectedTagId || tagActionLoading) return;

    const tagId = Number(selectedTagId);
    const tag = availableTags.find((item) => item.id === tagId);

    if (!tag || character.tags?.some((item) => item.id === tagId)) return;

    setTagActionLoading(true);
    setTagError("");
    setTagSuccess("");

    try {
      await assignCharacterTag(characterId, tagId);

      const updatedTags = [...(character.tags ?? []), tag].sort((a, b) =>
        a.name.localeCompare(b.name),
      );

      setCharacter((current) => ({
        ...current,
        tags: updatedTags,
      }));

      onUpdateTags?.(characterId, updatedTags);

      setSelectedTagId("");
      setTagSuccess(`Tag « ${tag.name} » ajouté.`);
    } catch (err) {
      setTagError(err.message || "Impossible d'attribuer ce tag.");
    } finally {
      setTagActionLoading(false);
    }
  }

  async function handleRemoveTag(tagId) {
    if (tagActionLoading) return;

    const tag = character.tags?.find((item) => item.id === tagId);
    if (!tag) return;

    setTagActionLoading(true);
    setTagError("");
    setTagSuccess("");

    try {
      await removeCharacterTag(characterId, tagId);

      const updatedTags = (character.tags ?? []).filter(
        (item) => item.id !== tagId,
      );

      setCharacter((current) => ({
        ...current,
        tags: updatedTags,
      }));

      onUpdateTags?.(characterId, updatedTags);

      setTagSuccess(`Tag « ${tag.name} » retiré.`);
    } catch (err) {
      setTagError(err.message || "Impossible de retirer ce tag.");
    } finally {
      setTagActionLoading(false);
    }
  }

  // ========================================
  // ACTIONS SUR LES OBJECTIFS
  // ========================================

  /**
   * Ouvre le formulaire de création.
   *
   * @param {boolean} isWarbandGoal - Type d'objectif à créer.
   */
  function handleCreateGoal(isWarbandGoal) {
    setEditingGoal(null);
    setIsWarbandGoalForm(isWarbandGoal);
    setGoalError("");
    setGoalSuccess("");
    setGoalFormOpen(true);
  }

  /**
   * Ouvre le formulaire avec les informations d'un objectif existant.
   *
   * @param {object} goal - Objectif à modifier.
   */
  function handleEditGoal(goal) {
    setEditingGoal(goal);

    // Un objectif sans character_id appartient à la Warband.
    setIsWarbandGoalForm(goal.character_id == null);

    setGoalError("");
    setGoalSuccess("");
    setGoalFormOpen(true);
  }

  /**
   * Ferme le formulaire et réinitialise son état.
   */
  function handleCloseGoalForm() {
    if (goalActionLoading) return;

    setGoalFormOpen(false);
    setEditingGoal(null);
    setIsWarbandGoalForm(false);
  }

  /**
   * Crée ou modifie un objectif selon le contexte.
   *
   * @param {object} goalData - Données transmises par GoalForm.
   */
  async function handleSaveGoal(goalData) {
    if (goalActionLoading) return;

    setGoalActionLoading(true);
    setGoalError("");
    setGoalSuccess("");

    try {
      if (editingGoal) {
        // Un objectif existe déjà : on appelle la route PATCH.
        await updateGoal(editingGoal.id, goalData);
        setGoalSuccess("Objectif modifié avec succès.");
      } else {
        // Nouvel objectif : on appelle la route POST.
        await createGoal(goalData);
        setGoalSuccess("Objectif créé avec succès.");
      }

      // Actualise la liste depuis le backend.
      const updatedGoals = await getGoals();
      setGoals(updatedGoals);

      // Ferme le formulaire après une opération réussie.
      setGoalFormOpen(false);
      setEditingGoal(null);
      setIsWarbandGoalForm(false);
    } catch (err) {
      setGoalError(err.message || "Impossible d'enregistrer cet objectif.");
    } finally {
      setGoalActionLoading(false);
    }
  }

  /**
   * Demande l'ouverture de la confirmation de suppression.
   *
   * @param {object} goal - Objectif à supprimer.
   */
  function handleAskDeleteGoal(goal) {
    setGoalToDelete(goal);
    setGoalError("");
    setGoalSuccess("");
  }

  /**
   * Annule la suppression et ferme la confirmation.
   */
  function handleCancelDeleteGoal() {
    if (isDeletingGoal) return;

    setGoalToDelete(null);
  }

  /**
   * Supprime définitivement l'objectif après confirmation.
   */
  async function handleConfirmDeleteGoal() {
    if (!goalToDelete || isDeletingGoal) return;

    setIsDeletingGoal(true);
    setGoalError("");
    setGoalSuccess("");

    try {
      await deleteGoal(goalToDelete.id);

      // Retire l'objectif de la liste affichée.
      setGoals((currentGoals) =>
        currentGoals.filter((goal) => goal.id !== goalToDelete.id),
      );

      setGoalSuccess("Objectif supprimé avec succès.");
      setGoalToDelete(null);
    } catch (err) {
      setGoalError(err.message || "Impossible de supprimer cet objectif.");
    } finally {
      setIsDeletingGoal(false);
    }
  }

  if (loading || error || !character) {
    const hasError = Boolean(error || (!loading && !character));

    return (
      <section className="character-details-page">
        <button
          type="button"
          className="character-details-back"
          onClick={onBack}
        >
          <ArrowLeft size={18} aria-hidden="true" />
          Retour à mon bataillon
        </button>

        <div className="status-panel" role={hasError ? undefined : "status"}>
          <h2>
            {loading
              ? "Chargement du personnage…"
              : "Impossible de charger le personnage"}
          </h2>
          <p role={hasError ? "alert" : undefined}>
            {loading
              ? "Récupération des informations du personnage depuis Warband HQ."
              : error || "Personnage introuvable."}
          </p>
        </div>
      </section>
    );
  }

  const assignedTags = character.tags ?? [];
  const assignedTagIds = new Set(assignedTags.map((tag) => tag.id));
  const unassignedTags = availableTags.filter(
    (tag) => !assignedTagIds.has(tag.id),
  );

  const classColor = CLASS_COLORS[character.class] ?? "#D7AA50";
  const classIcon = CLASS_ICONS[character.class];
  const factionIcon = FACTION_ICONS[character.faction];
  const raceIcon = RACE_ICONS[character.race_id]?.[character.gender];

  const activeTitle = getNamedValue(character.active_title);
  const activeSpec = getNamedValue(character.active_spec);
  const guild = getNamedValue(character.guild);
  const statistics = character.statistics ?? {};

  // ========================================
  // SÉPARATION ET FILTRAGE DES OBJECTIFS
  // ========================================

  // Objectifs associés au personnage actuellement consulté.
  const characterGoals = goals.filter(
    (goal) => goal.character_id === characterId,
  );

  // Objectifs qui ne sont associés à aucun personnage.
  const warbandGoals = goals.filter((goal) => goal.character_id == null);

  // Applique le filtre sélectionné aux objectifs du personnage.
  const visibleCharacterGoals =
    characterGoalFilter === "ALL"
      ? characterGoals
      : characterGoals.filter((goal) => goal.status === characterGoalFilter);

  // Applique le filtre sélectionné aux objectifs de la Warband.
  const visibleWarbandGoals =
    warbandGoalFilter === "ALL"
      ? warbandGoals
      : warbandGoals.filter((goal) => goal.status === warbandGoalFilter);

  return (
    <section
      className="character-details-page"
      style={{ "--class-color": classColor }}
    >
      <button type="button" className="character-details-back" onClick={onBack}>
        <ArrowLeft size={18} aria-hidden="true" />
        Back to My Warband
      </button>

      <header className="character-details-header">
        <div className="character-details-faction-emblem">
          {factionIcon ? (
            <img src={factionIcon} alt={character.faction || "Faction"} />
          ) : (
            <Shield size={64} aria-hidden="true" />
          )}
        </div>

        <div className="character-details-identity">
          {activeTitle && (
            <p className="character-details-title">{activeTitle}</p>
          )}

          <h1>{character.name || "Personnage inconnu"}</h1>

          <div className="character-details-facts">
            <span className="character-details-level-inline">
              {character.level ?? "—"}
            </span>

            {raceIcon && (
              <span>
                <img src={raceIcon} alt="" aria-hidden="true" />
                {character.race}
              </span>
            )}

            {classIcon && (
              <span>
                <img src={classIcon} alt="" aria-hidden="true" />
                {character.class}
              </span>
            )}

            {activeSpec && <span>{activeSpec}</span>}

            {guild && <span className="character-details-guild">{guild}</span>}

            <span className="character-details-realm-inline">
              {character.realm || "Royaume indisponible"}
            </span>
          </div>
        </div>

        <div className="character-details-header-meta">
          <div className="character-details-achievements">
            <Trophy size={18} aria-hidden="true" />
            <span>Hauts faits</span>
            <strong>{formatStat(character.achievement_points)}</strong>
          </div>

          <div className="character-details-item-level-summary">
            <Shield size={18} aria-hidden="true" />
            <span>Niveau d'objet</span>
            <strong>
              Moyen {formatStat(character.average_item_level)} / Équipé{" "}
              {formatStat(character.equipped_item_level)}
            </strong>
          </div>
        </div>
      </header>

      <section
        className="character-tags"
        aria-labelledby="character-tags-title"
      >
        <h2 id="character-tags-title">Tags du personnage</h2>

        <div className="character-tags-list">
          {assignedTags.length > 0 ? (
            assignedTags.map((tag) => (
              <span className="character-tag" key={tag.id}>
                {tag.name}
                <button
                  type="button"
                  aria-label={`Retirer le tag ${tag.name}`}
                  title={`Retirer le tag ${tag.name}`}
                  disabled={tagActionLoading}
                  onClick={() => handleRemoveTag(tag.id)}
                >
                  ×
                </button>
              </span>
            ))
          ) : (
            <span className="character-tags-empty">Aucun tag attribué.</span>
          )}
        </div>

        <div className="character-tags-actions">
          <select
            aria-label="Choisir un tag à ajouter"
            value={selectedTagId}
            onChange={(event) => setSelectedTagId(event.target.value)}
            disabled={
              loadingTags || tagActionLoading || unassignedTags.length === 0
            }
          >
            <option value="">
              {loadingTags
                ? "Chargement des tags..."
                : unassignedTags.length === 0
                  ? "Tous les tags sont attribués"
                  : "Sélectionner un tag"}
            </option>

            {unassignedTags.map((tag) => (
              <option key={tag.id} value={tag.id}>
                {tag.name}
              </option>
            ))}
          </select>

          <button
            type="button"
            disabled={!selectedTagId || tagActionLoading || loadingTags}
            onClick={handleAssignTag}
          >
            {tagActionLoading ? "Mise à jour..." : "Ajouter"}
          </button>
        </div>

        {tagError && <p role="alert">{tagError}</p>}
        {tagSuccess && <p role="status">{tagSuccess}</p>}
      </section>

      <div className="character-details-content">
        <div className="character-details-armory">
          <CharacterEquipment
            equipment={character.equipment}
            characterArtUrl={character.main_art_url}
          />
        </div>

        <aside className="character-details-sidebar">
          {/* OBJECTIFS DU PERSONNAGE ET DE LA WARBAND */}
          <section className="character-goals-panel">
            <div className="character-goals-header">
              <h2>Mes objectifs</h2>
              <p>
                Suis ta progression avec tes objectifs personnels et ceux de ta
                Warband.
              </p>
            </div>

            {/* Objectifs associés au personnage */}
            <div className="character-goals-group">
              <h3>Objectifs de {character.name}</h3>
              <p>Les objectifs associés à ce personnage.</p>

              <button type="button" onClick={() => handleCreateGoal(false)}>
                <Plus size={16} aria-hidden="true" />
                Nouvel objectif
              </button>

              <GoalFilters
                activeFilter={characterGoalFilter}
                onFilterChange={setCharacterGoalFilter}
              />

              {loadingGoals ? (
                <p>Chargement des objectifs...</p>
              ) : visibleCharacterGoals.length > 0 ? (
                visibleCharacterGoals.map((goal) => (
                  <GoalCard
                    key={goal.id}
                    goal={goal}
                    onEdit={handleEditGoal}
                    onDelete={handleAskDeleteGoal}
                  />
                ))
              ) : (
                <p>Aucun objectif ne correspond à ce filtre.</p>
              )}
            </div>

            {/* Objectifs communs à la Warband */}
            <div className="character-goals-group">
              <h3>Objectifs de la Warband</h3>
              <p>Les objectifs communs à tous tes personnages.</p>

              <button type="button" onClick={() => handleCreateGoal(true)}>
                <Plus size={16} aria-hidden="true" />
                Nouvel objectif
              </button>

              <GoalFilters
                activeFilter={warbandGoalFilter}
                onFilterChange={setWarbandGoalFilter}
              />

              {loadingGoals ? (
                <p>Chargement des objectifs...</p>
              ) : visibleWarbandGoals.length > 0 ? (
                visibleWarbandGoals.map((goal) => (
                  <GoalCard
                    key={goal.id}
                    goal={goal}
                    onEdit={handleEditGoal}
                    onDelete={handleAskDeleteGoal}
                  />
                ))
              ) : (
                <p>Aucun objectif ne correspond à ce filtre.</p>
              )}
            </div>
          </section>

          <StatGroup
            title="Statistiques principales"
            icon={Heart}
            stats={MAIN_STATS}
            values={statistics}
          />

          <StatGroup
            title="Statistiques secondaires"
            icon={Zap}
            stats={SECONDARY_STATS}
            values={statistics}
          />

          <p className="character-stat-note">
            Les valeurs affichées dépendent des données disponibles auprès de
            Blizzard.
          </p>
        </aside>
      </div>

      {/* Formulaire de création et de modification */}
      {goalFormOpen && (
        <GoalForm
          goal={editingGoal}
          characterId={characterId}
          isWarbandGoal={isWarbandGoalForm}
          onSubmit={handleSaveGoal}
          onCancel={handleCloseGoalForm}
          isSubmitting={goalActionLoading}
        />
      )}

      {/* Confirmation de suppression */}
      <DeleteGoalDialog
        goal={goalToDelete}
        onConfirm={handleConfirmDeleteGoal}
        onCancel={handleCancelDeleteGoal}
        isDeleting={isDeletingGoal}
      />
    </section>
  );
}

export default CharacterDetails;
