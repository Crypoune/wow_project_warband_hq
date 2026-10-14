import bloodElfFemale from "../assets/races/races_bloodelf-female.png";
import bloodElfMale from "../assets/races/races_bloodelf-male.png";
import darkIronDwarfFemale from "../assets/races/races_darkirondwarf-female.png";
import darkIronDwarfMale from "../assets/races/races_darkirondwarf-male.png";
import dracthyrFemale from "../assets/races/races_dracthyr-visage-female.png";
import dracthyrMale from "../assets/races/races_dracthyr-visage-male.png";
import draeneiFemale from "../assets/races/races_draenei-female.png";
import draeneiMale from "../assets/races/races_draenei-male.png";
import dwarfFemale from "../assets/races/races_dwarf-female.png";
import dwarfMale from "../assets/races/races_dwarf-male.png";
import earthenFemale from "../assets/races/races_earthen-female.png";
import earthenMale from "../assets/races/races_earthen-male.png";
import gnomeFemale from "../assets/races/races_gnome-female.png";
import gnomeMale from "../assets/races/races_gnome-male.png";
import goblinFemale from "../assets/races/races_goblin-female.png";
import goblinMale from "../assets/races/races_goblin-male.png";
import haranirFemale from "../assets/races/races_haranir-female.png";
import haranirMale from "../assets/races/races_haranir-male.png";
import highmountainFemale from "../assets/races/races_highmountain-female.png";
import highmountainMale from "../assets/races/races_highmountain-male.png";
import humanFemale from "../assets/races/races_human-female.png";
import humanMale from "../assets/races/races_human-male.png";
import kulTiranFemale from "../assets/races/races_kultiranhuman-female.png";
import kulTiranMale from "../assets/races/races_kultiranhuman-male.png";
import lightforgedFemale from "../assets/races/races_lightforged-female.png";
import lightforgedMale from "../assets/races/races_lightforged-male.png";
import magharFemale from "../assets/races/races_maghar-female.png";
import magharMale from "../assets/races/races_maghar-male.png";
import mechagnomeFemale from "../assets/races/races_mechagnome-female.png";
import mechagnomeMale from "../assets/races/races_mechagnome-male.png";
import nightborneFemale from "../assets/races/races_nightborne-female.png";
import nightborneMale from "../assets/races/races_nightborne-male.png";
import nightElfFemale from "../assets/races/races_nightelf-female.png";
import nightElfMale from "../assets/races/races_nightelf-male.png";
import orcFemale from "../assets/races/races_orc-female.png";
import orcMale from "../assets/races/races_orc-male.png";
import pandarenFemale from "../assets/races/races_panda-female.png";
import pandarenMale from "../assets/races/races_panda-male.png";
import taurenFemale from "../assets/races/races_tauren-female.png";
import taurenMale from "../assets/races/races_tauren-male.png";
import trollFemale from "../assets/races/races_troll-female.png";
import trollMale from "../assets/races/races_troll-male.png";
import undeadFemale from "../assets/races/races_undead-female.png";
import undeadMale from "../assets/races/races_undead-male.png";
import voidElfFemale from "../assets/races/races_voidelf-female.png";
import voidElfMale from "../assets/races/races_voidelf-male.png";
import vulperaFemale from "../assets/races/races_vulpera-female.png";
import vulperaMale from "../assets/races/races_vulpera-male.png";
import worgenFemale from "../assets/races/races_worgen-female.png";
import worgenMale from "../assets/races/races_worgen-male.png";
import zandalariTrollFemale from "../assets/races/races_zandalaritroll-female.png";
import zandalariTrollMale from "../assets/races/races_zandalaritroll-male.png";

// Icônes des races de World of Warcraft, organisées par ID de race et par genre (MALE/FEMALE).
export const RACE_ICONS = {
  1: { MALE: humanMale, FEMALE: humanFemale },
  2: { MALE: orcMale, FEMALE: orcFemale },
  3: { MALE: dwarfMale, FEMALE: dwarfFemale },
  4: { MALE: nightElfMale, FEMALE: nightElfFemale },
  5: { MALE: undeadMale, FEMALE: undeadFemale },
  6: { MALE: taurenMale, FEMALE: taurenFemale },
  7: { MALE: gnomeMale, FEMALE: gnomeFemale },
  8: { MALE: trollMale, FEMALE: trollFemale },
  9: { MALE: goblinMale, FEMALE: goblinFemale },
  10: { MALE: bloodElfMale, FEMALE: bloodElfFemale },
  11: { MALE: draeneiMale, FEMALE: draeneiFemale },
  22: { MALE: worgenMale, FEMALE: worgenFemale },
  24: { MALE: pandarenMale, FEMALE: pandarenFemale },
  25: { MALE: pandarenMale, FEMALE: pandarenFemale },
  26: { MALE: pandarenMale, FEMALE: pandarenFemale },
  27: { MALE: nightborneMale, FEMALE: nightborneFemale },
  28: { MALE: highmountainMale, FEMALE: highmountainFemale },
  29: { MALE: voidElfMale, FEMALE: voidElfFemale },
  30: { MALE: lightforgedMale, FEMALE: lightforgedFemale },
  31: { MALE: zandalariTrollMale, FEMALE: zandalariTrollFemale },
  32: { MALE: kulTiranMale, FEMALE: kulTiranFemale },
  34: { MALE: darkIronDwarfMale, FEMALE: darkIronDwarfFemale },
  35: { MALE: vulperaMale, FEMALE: vulperaFemale },
  36: { MALE: magharMale, FEMALE: magharFemale },
  37: { MALE: mechagnomeMale, FEMALE: mechagnomeFemale },
  52: { MALE: dracthyrMale, FEMALE: dracthyrFemale },
  85: { MALE: earthenMale, FEMALE: earthenFemale },
  86: { MALE: haranirMale, FEMALE: haranirFemale },
};
