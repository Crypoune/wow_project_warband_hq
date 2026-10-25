const EQUIPMENT_SLOTS = [
  // Colonne de gauche
  { id: "HEAD", label: "Tête", side: "left" },
  { id: "NECK", label: "Collier", side: "left" },
  { id: "SHOULDER", label: "Épaules", side: "left" },
  { id: "BACK", label: "Cape", side: "left" },
  { id: "CHEST", label: "Torse", side: "left" },
  { id: "SHIRT", label: "Chemise", side: "left" },
  { id: "TABARD", label: "Tabard", side: "left" },
  { id: "WRIST", label: "Brassards", side: "left" },

  // Colonne de droite
  { id: "HANDS", label: "Gants", side: "right" },
  { id: "WAIST", label: "Ceinture", side: "right" },
  { id: "LEGS", label: "Jambes", side: "right" },
  { id: "FEET", label: "Bottes", side: "right" },
  { id: "FINGER_1", label: "Anneau 1", side: "right" },
  { id: "FINGER_2", label: "Anneau 2", side: "right" },
  { id: "TRINKET_1", label: "Bijou 1", side: "right" },
  { id: "TRINKET_2", label: "Bijou 2", side: "right" },

  // Armes
  { id: "MAIN_HAND", label: "Arme 1", side: "bottom" },
  { id: "OFF_HAND", label: "Arme 2", side: "bottom" },
];

function CharacterEquipment({ equipment = [], characterArtUrl = null }) {
  const equippedItems = Array.isArray(equipment) ? equipment : [];

  function getEquippedItem(slotId) {
    return equippedItems.find((entry) => entry.slot?.type === slotId) ?? null;
  }

  function renderSlot(slot) {
    const equippedItem = getEquippedItem(slot.id);

    return (
      <div
        key={slot.id}
        className={`character-equipment-slot character-equipment-slot--${slot.side}`}
        title={equippedItem?.name ?? slot.label}
      >
        <div className="character-equipment-slot-icon">
          {equippedItem?.icon_url ? (
            <img src={equippedItem.icon_url} alt="" />
          ) : (
            <span aria-hidden="true">—</span>
          )}
        </div>

        <div className="character-equipment-slot-info">
          <span className="character-equipment-slot-label">{slot.label}</span>

          {equippedItem && (
            <>
              <span className="character-equipment-slot-name">
                {equippedItem.name ?? "Objet équipé"}
              </span>

              {equippedItem.level?.value != null && (
                <span className="character-equipment-slot-level">
                  Niveau {equippedItem.level.value}
                </span>
              )}
            </>
          )}
        </div>
      </div>
    );
  }

  return (
    <section
      className="character-equipment"
      aria-label="Équipement du personnage"
    >
      <header className="character-equipment-header">
        <p className="section-eyebrow">ARMURERIE</p>
        <h2>Équipement</h2>
      </header>

      <div className="character-equipment-layout">
        <div className="character-equipment-character" aria-hidden="true">
          {characterArtUrl && (
            <img
              src={characterArtUrl}
              alt=""
              className="character-equipment-character-art"
            />
          )}
        </div>

        <div className="character-equipment-column character-equipment-column--left">
          {EQUIPMENT_SLOTS.filter((slot) => slot.side === "left").map(
            renderSlot,
          )}
        </div>

        <div className="character-equipment-column character-equipment-column--right">
          {EQUIPMENT_SLOTS.filter((slot) => slot.side === "right").map(
            renderSlot,
          )}
        </div>

        <div className="character-equipment-weapons">
          {EQUIPMENT_SLOTS.filter((slot) => slot.side === "bottom").map(
            renderSlot,
          )}
        </div>
      </div>
    </section>
  );
}

export default CharacterEquipment;
