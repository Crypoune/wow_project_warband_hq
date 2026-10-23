import { useEffect, useState } from "react";
import { ArrowLeft, Shield, Trophy, Heart, Zap, Activity } from "lucide-react";
import { CLASS_COLORS, CLASS_ICONS } from "../data/wowClasses";
import { RACE_ICONS } from "../data/wowRaces";
import { FACTION_ICONS } from "../data/wowFactions";
import { getCharacterDetails } from "../services/characterService.js";
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

function CharacterDetails({ characterId, onBack }) {
  const [character, setCharacter] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

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
          setError(err.message || "Unable to retrieve character details.");
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
          Back to My Warband
        </button>

        <div className="status-panel" role={hasError ? undefined : "status"}>
          <h2>
            {loading ? "Loading character..." : "Unable to load character"}
          </h2>
          <p role={hasError ? "alert" : undefined}>
            {loading
              ? "Retrieving character information from Warband HQ."
              : error || "Character not found."}
          </p>
        </div>
      </section>
    );
  }

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

          <h1>{character.name || "Unknown character"}</h1>

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
              {character.realm || "Realm unavailable"}
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
