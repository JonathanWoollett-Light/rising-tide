import os
SP = os.path.dirname(os.path.abspath(__file__))
p = 'mod_folder/common/scripted_triggers/mltd_ai_triggers.txt'
s = open(p, encoding='utf-8', newline='').read()
assert '\r' not in s
i = s.index('# ---- W. The story acts')
new = open(os.path.join(SP, 'sectionW.txt'), encoding='utf-8', newline='').read()
s = s[:i] + new

old = '''	if = {
		limit = { mltd_ai_in_ncr_bloc = yes }
		ROOT = { mltd_ai_stage_ncr = yes }
	}
	else = {
		NOT = {
			any_allied_country = {
				strength_ratio = { tag = ROOT ratio > 0.5 }
			}
		}
		# nor, after the Kingdom, a country stronger than MLT itself (run 3 declared on Broken Coast, 47 states, and lost);
		# the Oregon opening is exempt, because mirelurk armour beats Oregon's weapons in a way estimated strength misses
		OR = {
			ROOT = { NOT = { has_completed_focus = mlt_kingdom_of_mlyeh } }
			NOT = { strength_ratio = { tag = ROOT ratio > 1 } }
		}
	}
}
'''
assert s.count(old) == 1
s = s.replace(old, '''	mltd_ai_safe_by_strength = yes
}
''')

old2 = '''# A country MLT can attack without starting a war it cannot win, as a player would judge it: on the NCR's side only once the
# NCR's own stage is open (then that whole side is the target), and otherwise with no ally - faction member, overlord or
# subject - at half MLT's estimated army strength or more (strength_ratio, vanilla ai_strategy/ENG.txt:1368), and, after the
# Kingdom, no stronger than MLT. Country scope.
mltd_ai_safe_target = {'''
assert s.count(old2) == 1
s = s.replace(old2, '''# A country MLT can attack without starting a war it cannot win, as a player would judge it: on the NCR's side only once the
# NCR's own stage is open (then that whole side is the target), and otherwise with no ally - faction member, overlord or
# subject - at half MLT's estimated army strength or more (strength_ratio, vanilla ai_strategy/ENG.txt:1368), and, after the
# Kingdom, no stronger than MLT. mltd_ai_safe_target below adds the courtships; Drown the Dance's hold (section W) reads this
# half alone, because the courtship refuses the Bone Dancers outright. Country scope.
mltd_ai_safe_by_strength = {
	if = {
		limit = { mltd_ai_in_ncr_bloc = yes }
		ROOT = { mltd_ai_stage_ncr = yes }
	}
	else = {
		NOT = {
			any_allied_country = {
				strength_ratio = { tag = ROOT ratio > 0.5 }
			}
		}
		# nor, after the Kingdom, a country stronger than MLT itself (run 3 declared on Broken Coast, 47 states, and lost);
		# the Oregon opening is exempt, because mirelurk armour beats Oregon's weapons in a way estimated strength misses
		OR = {
			ROOT = { NOT = { has_completed_focus = mlt_kingdom_of_mlyeh } }
			NOT = { strength_ratio = { tag = ROOT ratio > 1 } }
		}
	}
}

# A safe target (mltd_ai_safe_by_strength), and never the Broken Coast or the Bone Dancers while MLT courts them. Country
# scope.
mltd_ai_safe_target = {''')
open(p, 'w', encoding='utf-8', newline='').write(s)
print('ok')
