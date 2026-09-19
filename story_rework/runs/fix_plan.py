p = r'C:\Users\jonat\Documents\rising-tide\CONQUEST_PLAN.txt'
s = open(p, encoding='utf-8', newline='').read()
reps = [
# F8
("# ---- ~900 free manpower, 0 caps, 3 research slots for the whole game\n",
 "# ---- ~900 free manpower, 0 caps, 3 research slots (4 from When Shady Sands Falls, 5 from The Last King Kneels)\n"),
# F9: the Covenant's civilian token, and Hail's network and cult
("operation mltd_op_nurture_the_cult on BRK              # to 50 %: sheltered, one operative holds ~76 %\n",
 "operation mltd_op_nurture_the_cult on BRK              # to 50 %: sheltered, one operative holds ~76 %\n"
 "operation operation_infiltrate_civilian on BRK         # OWB's own infiltration (90 days, two operatives), once the network allows: the\n"
 "#   civilian token the Covenant asks for\n"
 "operative: build a network in BDT, then operation mltd_op_found_a_cult on it # for Hail the Drowned King (Act III): the Bone Dancers'\n"
 "#   cult at 40 %, 25 % coverage and a civilian token\n"),
("focus mltd_bdt_the_dancers_hear_the_tide                # 56 days; +10 to their cult, an army token and 15 civilian intel; 600 of their infantry\n"
 "#   equipment stolen when they hold over 1,200, and 30 army XP\n",
 "focus mltd_bdt_the_dancers_hear_the_tide                # 56 days; +10 to their cult, an army token and 15 civilian intel; 600 of their infantry\n"
 "#   equipment stolen when they hold over 1,200, and 30 army XP\n"
 "operation mltd_op_nurture_the_cult on BDT              # to 40 %, sheltered since The Bone Shore (decay halved)\n"
 "operation operation_infiltrate_civilian on BDT         # the second invitation's civilian token\n"),
# F5
("focus mltd_the_tide_turns_south                         # 30 days; Act III's close, at 50 controlled states: mltd.30, news mltd.31 and the permanent\n",
 "focus mltd_the_tide_turns_south                         # 30 days; Act III's close, at 50 controlled states (or from 2281): mltd.30, news mltd.31 and the permanent\n"),
# F2
("# 30 days; Act IV's close, once the NCR has capitulated to us (or is gone, or our subject); news mltd.41\n",
 "# 30 days; Act IV's close, once the NCR has capitulated (or is gone, or our subject); news mltd.41\n"),
("# 30 days; Act V's close, once the Legion has capitulated to us (or is gone, or our subject): the permanent\n",
 "# 30 days; Act V's close, once the Legion has capitulated (or is gone, or our subject): the permanent\n"),
("#   won - the NCR, the Legion, Texas: gone, capitulated to MLT, or its subject - so a war that stalls holds the story back.\n",
 "#   won - the NCR, the Legion, Texas: gone, capitulated, or its subject - so a war that stalls holds the story back.\n"),
# F4: the holds, in the round-27 note
("#   \"Beaten\" now means what the closes ask - gone, capitulated, once capitulated to MLT, or its subject - for the stages\n"
 "#   and holds as well, so the NCR's and the Legion's closes and the stages after them open together.\n",
 "#   \"Beaten\" now means what the closes ask - gone, capitulated, once capitulated to MLT, or its subject - for the stages\n"
 "#   and holds as well, so the NCR's and the Legion's closes and the stages after them open together. Each war focus's\n"
 "#   AI hold (its stage, the army's readiness, a courtship) now sits in its own available, hidden and for an AI only: run 8\n"
 "#   (round-24 code) took The Tide-Wall and The Turbines Sing while their ai_will_do read 0, because an AI takes every\n"
 "#   listed focus that is available, and took both Muttfruit trades through a focus_factors 0.\n"),
# F7: the AI's side of the Bone Dancers
("#   Before the Final Ritual it takes the Bone Dancers' and Washington's Act II branches too whenever the ritual's 200,000\n",
 "#   It builds no network in the Bone Dancers' land and runs no infiltration there, so with La Resistance it seldom meets\n"
 "#   Hail the Drowned King's courtship gates; from 2281 Drown the Dance no longer waits on the courtship.\n"
 "#   Before the Final Ritual it takes the Bone Dancers' and Washington's Act II branches too whenever the ritual's 200,000\n"),
]
for a, b in reps:
    c = s.count(a)
    assert c == 1, (c, a[:90])
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='').write(s)
print('ok', len(reps))
