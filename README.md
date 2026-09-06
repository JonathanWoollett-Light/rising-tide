# OWB - Rising Tide

*A submod for [Old World Blues](https://steamcommunity.com/sharedfiles/filedetails/?id=2265420196), for the Mirelurk Tribe (`MLT`).*

**Status:** first content drop, **play-tested once**. The first run found summoned divisions spawning without equipment; round 3 fixes that (hidden equipment techs) and is not yet re-tested. After each change, read `logs/error.log` and confirm `logs/system.log` lists `Active Mod: OWB - Rising Tide` before trusting anything below.

## Features

Everything unlocks after OWB's final MLT focus, *The Kingdom of M'lyeh*, which now also fires an event for MLT and a world news event.

- **Gifts from the Deep** - a decision category of five 30-day missions (Tide / Shell / Current / Brood / Abyss: army attack, defence, org, recruitable population, stability). Each costs political power and manpower and feeds the *Gifts from the Deep* dynamic modifier. One at a time; two after the Grand Ritual; permanent (and the category gone) after the Final Ritual.
- **The Books of M'lyeh** - five focuses fanned under *Gifts from the Deep*; each requires control of a notable state in the region (Arago, The Warren, Paisley Pit, Arroyo, The Maw) and unlocks one gift. Reading 1 / 3 / 5 of them gates *Call of the Deep Ones*, *The Grand Ritual* and *The Deep Ones Walk*.
- **The Deep Ones** - a new special-forces creature unit with its own equipment and a locked, script-only 20-width division template, summoned by a decision that sacrifices 2,000 people from any state large enough (the division rises there). After *The Deep Ones Walk* the reward tech is granted, the template unlocks and the unit can be trained like any other (its equipment is already producible from the first summon).
- **The Star Spawn** - the next locked, script-only 20-width division (its own, heavier equipment; both units have suppression 5 and long training), spawned when the Deep Ones are released; unlocked in turn by the Final Ritual. Summoned divisions arrive fully equipped, and their equipment is producible from the first summon.
- **The Grand Ritual** and **The Final Ritual** - 100-day focuses that require a national population of 100,000 / 200,000. Completing them also makes *Gifts from the Deep* grant +50 (then +100) weekly manpower. For the duration of the focus a national spirit applies heavy debuffs and a *daily* population toll across every owned state (0.1 %, then 0.25 % - about 9.5 % / 22 % over the ritual); completion lifts the spirit and fires an MLT event plus a world news event ("The Seas Grow Darker", "The Stars Are Right"). Once started they cannot be cancelled. *Gifts from the Deep* unlocks when *The Kingdom of M'lyeh* completes but is deliberately not drawn as its child; the Books fan out beneath it and the rest run down the centre. *Call of the Deep Ones* and *The Deep Ones Walk* each open a single-option event that delivers their effects.
- **Reward Technologies tab** - the Deep Ones and Star Spawn techs sit in the Units row beside Faeries.
- **Unit icons** - original division/counter icons for both units (a fish-man and a Cthulhu bust, with NATO-counter variants), drawn procedurally by `build_unit_icons.py`.
- **Outsider Warfare** - all 16 doctrine techs now also buff amphibious platoons (mirelurks, Deep Ones, Star Spawn).
- **Indoctrinate the Faithful** - an MLT-only intelligence operation (La Resistance DLC) that converts 1,500 people of a country you have a network in into MLT manpower.
- **M'lulu** - OWB's portrait and small icon re-graded darker and colder (programmatic colour grade of the existing painting, not new art; see `build_portrait.py`); as a field marshal she gains the *Animal Friend* and *Invader* traits.
- **Coral Prophet Anastasia** - gains *Animal Friend* and a bespoke portrait.
- **The Drowned Herald** - a new general (a notch below M'lulu) who takes command when the *Kingdom of M'lyeh* event fires, with his own portrait. Both extra portraits are built by `build_leader_portraits.py`.

Design notes, tunables and the reasoning behind every identifier are in `CLAUDE.md`.

## Layout

| Path | Contents |
| --- | --- |
| `mod_folder/` | The mod as HOI4 sees it. **Only this directory ships.** |
| `mod_folder/descriptor.mod` | Mod metadata. No `path=`, no `replace_path`. |
| `event_images/`, `build_event_pictures.py`, `build_portrait.py`, `build_unit_icons.py`, `build_focus_icons.py`, `build_leader_portraits.py` | Source images and the scripts that rebuild the event pictures, the graded M'lulu portrait/icon, the two unit-icon sets, the purple book focus icon and the Anastasia / Drowned Herald portraits. `event_images/SOURCES.md` lists origin/licence status - complete it before any Workshop upload. |
| repo root | Docs and tooling that must never ship. |

## Install

1. Copy `mod_folder/descriptor.mod` to `C:\Users\<you>\Documents\Paradox Interactive\Hearts of Iron IV\mod\rising_tide.mod`.
2. Append one line to that copy: `path="C:/Users/<you>/Documents/rising-tide/mod_folder"` - absolute, **forward slashes**, no trailing slash, pointing at `mod_folder`. It is machine-specific, which is why it is not in the repo. (Already installed on this machine.)
3. In the launcher: **Reload Installed Mods**, then add both this mod and Old World Blues to a playset and enable both.
4. **Load order.** `dependencies={ "Old World Blues" }` in *both* `mod_folder/descriptor.mod` and the installed launcher `.mod` is what makes this mod load **after** OWB, so our files win on any overlap and OWB's 95 `replace_path` entries do not delete ours - see OWB's own guide, `<OWB>/doc/OWB_MODDING_README.txt`: "After adding this your mod will load after OWB and won't be replaced by files we have or our replace_paths". Keep that block in both files. If you also order the playset by hand, put Rising Tide **below** Old World Blues - lower in the list loads later.

## How overriding works

This submod declares **no `replace_path`** and merges additively over OWB: ship a file at the same relative path to replace OWB's whole file, or use a new `mltd_`-prefixed filename to add content. Never add `replace_path` - OWB declares 95.

Five OWB files are overridden: `common/national_focus/Mirelurk Tribe (MLT) Focus.txt` (to add focuses to the existing tree), `common/technologies/tech_fallout_land_doctrine.txt` (to buff amphibious units in Outsider Warfare), `common/characters/MLT.txt` (traits, Anastasia's portrait, the Drowned Herald), `history/countries/MLT - Mirelurk Tribe.txt` (one line: recruit the Herald at start) and `common/script_enums.txt` (our equipment ids in the documentation enum). All are byte copies of OWB's files plus insertions - the characters file additionally replaces four of Anastasia's lines. The authoritative override rules, naming conventions and encoding requirements live in `CLAUDE.md`; read it before editing anything under `mod_folder/`.

## Update process

OWB updates silently invalidate every file we override, so re-diff after each one.

1. Get [WinMerge](https://winmerge.org/).
2. Compare every file in the submod against its OWB counterpart and update.
   1. 1st folder: `C:\Program Files (x86)\Steam\steamapps\workshop\content\394360\2265420196\`
   2. 2nd folder: `C:\Users\jonat\Documents\rising-tide\mod_folder\`
   3. Untick `View > Show Left Unique Items`.
   4. The five overrides (`Mirelurk Tribe (MLT) Focus.txt`, `tech_fallout_land_doctrine.txt`, `common/characters/MLT.txt`, `history/countries/MLT - Mirelurk Tribe.txt`, `common/script_enums.txt`) must end up as OWB's new file **plus only our insertions** (plus Anastasia's replaced lines) - keep each file's original line endings and BOM state.
   5. Delete the `.bak` files afterwards.
3. Play the game to test, then read `...\Hearts of Iron IV\logs\error.log` (and `text.log` for localisation - the `warbike_unlock_tech` collision there is intentional) and confirm `system.log` lists both `Old World Blues` and `OWB - Rising Tide` as active mods.

## Compatibility

- The [OWB Official NCR versus Caesar's Legion submod](https://steamcommunity.com/sharedfiles/filedetails/?id=3010015443) ships its own `Mirelurk Tribe (MLT) Focus.txt` **and** its own `tech_fallout_land_doctrine.txt`. Rising Tide overrides both; whichever mod loads later wins each whole file, so run one or the other, not both.
- With *OWB: Ultimate Tech Compatibility Mod* (3462816659), which re-lays the whole Reward Technologies tab, the Deep Ones / Star Spawn techs land on its `robco_unlock_tech` (4,24) and `FNR_bollinger_shipyards_unlock_tech` (4,28) in its "Schematics" row and overlap them. Cosmetic only - both stay grantable. No slot next to Faeries is free under both layouts.
- With *OWB Tech Expansion* (2821243420) loaded after this mod, its `countrytechtreeview.gui` has no `warbike_unlock_tech_tree` gridbox, so neither reward tech renders in the tab (they still work when granted by focus).
- The intelligence operation needs the La Resistance DLC; without it the file loads silently and the operation never appears.

## Plan

### High priority

- [ ] Re-test the startup fixes: `error.log` must no longer list the four `script_enum_equipment_bonus_type` warnings or the two `recruit_character` errors for `events/mltd_events.txt` (the only lines in the last log that were ours), and the Drowned Herald must show up as a general once the *Kingdom of M'lyeh* event fires.
- [ ] Re-test after round 3: a summoned / focus-spawned division arrives **with** its equipment (200 / 320 spare in Logistics, hidden `Spawn of the Deep` tech in the equipment tooltip); the Grand / Final Ritual focus tooltips show the red modifier lines with values; the five focuses render as a column below the tree with no overlaps and no line from the Kingdom to Gifts; then the rest of the chain - Deep Ones tech in the Reward Technologies tab, gifts apply instantly and expire at 30 days, the toll ticks daily, the Deep Ones template is trainable after *The Deep Ones Walk*, the operation appears with an agency.
- [ ] Tune the toll and the population gates (`mltd_ritual_toll_factor`, 100,000 / 200,000 - see CLAUDE.md > The rituals) once you have seen them in play.

### Medium priority

- [ ] Bespoke art: focus icons (currently reused OWB sprites), a decision-category banner, cult-flavoured operation phases, and a properly repainted M'lulu (the shipped one is a colour grade).
- [ ] Add a 512x512 `mod_folder/thumbnail.png` and the matching `picture="thumbnail.png"` key (in both `descriptor.mod` and the installed launcher `.mod`) before any Steam Workshop publish; record image licences in `event_images/`.
