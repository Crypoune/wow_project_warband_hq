import { useEffect, useState } from "react";
import { ArrowLeft, Shield, Trophy, Heart, Zap } from "lucide-react";
import { CLASS_COLORS, CLASS_ICONS } from "../data/wowClasses";
import { RACE_ICONS } from "../data/wowRaces";
import { FACTION_ICONS } from "../data/wowFactions";
import {
  getCharacterDetails,
  getTags,
  assignCharacterTag,
  removeCharacterTag,
} from "../services/characterService.js";
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
    </section>
  );
}

export default CharacterDetails;
