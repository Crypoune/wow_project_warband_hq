import { useEffect, useState } from "react";
import { ArrowLeft, Shield, Swords } from "lucide-react";
import { CLASS_COLORS, CLASS_ICONS } from "../data/wowClasses";
import { RACE_ICONS } from "../data/wowRaces";
import { FACTION_ICONS } from "../data/wowFactions";
import { getCharacterDetails } from "../services/characterService.js";

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

        if (!cancelled) {
          setCharacter(result);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message || "Unable to retrieve character details.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadCharacter();

    return () => {
      cancelled = true;
    };
  }, [characterId]);

  if (loading) {
    return (
      <section className="character-details-page">
        <button type="button" onClick={onBack}>
          <ArrowLeft size={18} aria-hidden="true" />
          Back to My Warband
        </button>

        <div className="status-panel" role="status">
          <h2>Loading character...</h2>
          <p>Retrieving character information from Warband HQ.</p>
        </div>
      </section>
    );
  }

  if (error || !character) {
    return (
      <section className="character-details-page">
        <button type="button" onClick={onBack}>
          <ArrowLeft size={18} aria-hidden="true" />
          Back to My Warband
        </button>

        <div className="status-panel">
          <h2>Unable to load character</h2>
          <p role="alert">{error || "Character not found."}</p>
        </div>
      </section>
    );
  }

  const classColor = CLASS_COLORS[character.class] ?? "#D7AA50";
  const classIcon = CLASS_ICONS[character.class];
  const factionIcon = FACTION_ICONS[character.faction];
  const raceIcon = RACE_ICONS[character.race_id]?.[character.gender];

  return (
    <section className="character-details-page">
      <button type="button" className="character-details-back" onClick={onBack}>
        <ArrowLeft size={18} aria-hidden="true" />
        Back to My Warband
      </button>

      <header
        className="character-details-header"
        style={{ "--class-color": classColor }}
      >
        <div className="character-details-portrait">
          {character.portrait_url ? (
            <img
              src={character.portrait_url}
              alt={`Portrait of ${character.name}`}
            />
          ) : (
            <div className="character-portrait-placeholder">
              Portrait unavailable
            </div>
          )}
        </div>

        <div className="character-details-identity">
          <p className="section-eyebrow">CHARACTER PROFILE</p>
          <h1>{character.name || "Unknown character"}</h1>

          <p className="character-details-realm">
            {character.realm || "Realm unavailable"}
          </p>

          <div className="character-details-facts">
            {classIcon && (
              <span>
                <img src={classIcon} alt="" aria-hidden="true" />
                {character.class || "Unknown class"}
              </span>
            )}

            {raceIcon && (
              <span>
                <img src={raceIcon} alt="" aria-hidden="true" />
                {character.race || "Unknown race"}
              </span>
            )}

            {factionIcon && (
              <span>
                <img src={factionIcon} alt="" aria-hidden="true" />
                {character.faction}
              </span>
            )}
          </div>
        </div>

        <div className="character-details-level">
          <span>LEVEL</span>
          <strong>{character.level ?? "—"}</strong>
        </div>
      </header>

      <div className="character-details-stats">
        <article className="character-details-stat">
          <div className="character-details-stat-icon">
            <Shield size={22} aria-hidden="true" />
          </div>
          <div>
            <span>Average item level</span>
            <strong>{character.average_item_level ?? "—"}</strong>
          </div>
        </article>

        <article className="character-details-stat">
          <div className="character-details-stat-icon">
            <Swords size={22} aria-hidden="true" />
          </div>
          <div>
            <span>Equipped item level</span>
            <strong>{character.equipped_item_level ?? "—"}</strong>
          </div>
        </article>
      </div>

      <section className="status-panel character-details-coming-soon">
        <h2>More adventures await</h2>
        <p>
          Equipment, progression and other character statistics will be added in
          a future iteration.
        </p>
      </section>
    </section>
  );
}

export default CharacterDetails;
