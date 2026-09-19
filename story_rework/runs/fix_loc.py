p = r'C:\Users\jonat\Documents\rising-tide\mod_folder\localisation\english\MLT\mltd_l_english.yml'
b = open(p, 'rb').read()
assert b[:3] == b'\xef\xbb\xbf'
s = b[3:].decode('utf-8')
reps = [
# F10 Final Ritual desc
("""The stars are right. The drowned city will rise with its priestess upon its highest tower, the §Y$mltd_star_spawn$§! will walk in her wake, and whatever remains of the world will belong to the deep. A hundred days of chanting stand between the tribe and that dawn, and once the first is sung there is no turning back.\"""",
 """The stars are coming right. When the last word is sung the §Y$mltd_star_spawn$§! will walk in her wake, and far beneath §YM'lyeh§! the drowned city will stir in its sleep - to rise, with its priestess upon its highest tower, on the day every shore belongs to the tide. Long months of chanting stand between the tribe and that first stirring, and once the first word is sung there is no turning back.\""""),
# F10 mltd.6.d
("""On the coasts of Oregon the sea has drawn back a mile and stands there, a black wall, waiting. In the marshes the crab-worshippers dance, and things dance with them that are not crabs and were never men. The dream is no longer a dream. Everyone who sleeps now walks the streets of the sunken city, and hears the voice, and understands at last what it is saying. §o[MLT_MLULU.GetName]§! is rising. When she has risen the old world will end, and what comes after will be free and wild and beyond good and evil.\"""",
 """On the coasts of Oregon the tide comes in black, and goes out a little slower every night. In the marshes the crab-worshippers dance, and things dance with them that are not crabs and were never men. Everyone who sleeps now walks the streets of the sunken city and hears a voice beneath it, though no one can yet say what it is saying. The crab-worshippers say that §o[MLT_MLULU.GetName]§! is only the first to wake, and that the city itself will not rise until the land is ready for it.\""""),
# F16 Tide-Wall desc
("""Coral is grown across the tunnel mouths, the lower galleries are flooded to the knee, and the drowned knights stand watch in the black water. Let the Paladins come down into [235.GetName]. The tide is waiting for them there.\"""",
 """Coral is grown across the tunnel mouths, the lower galleries are flooded to the knee, and the drowned stand watch in the black water. We will not wait for the Paladins to come down into [235.GetName]: the tide goes north to meet them.\""""),
# F20 What the River Carries
("""So the Coral Court sends its oracles upriver against the current,""",
 """So the Coral Court sends more of its oracles upriver against the current,"""),
# F16 mltd.21.d
("""the coast we fought for is ours, and the things that swam north to win it for us will keep swimming - if we swear""",
 """the coast we fought for is ours, and the things that swim beneath our keels will keep swimming for us - if we swear"""),
# F16 Drown the Dance
("""their roads run where our water wants to go, and the faithful among them have already told us which camps sleep unguarded.""",
 """their roads run where our water wants to go, and our scouts already know which camps sleep unguarded."""),
# F14 mltd.24.d
("""there is an older king, they said, and he is awake, and he offers §c$mltd_drowned_covenant$§! to those who will dance for him.""",
 """there is an older king, they said, who sleeps beneath the sea and dreams of every dancer on the shore, and his priestess-queen offers §c$mltd_drowned_covenant$§! to those who will dance for him."""),
# F15 Tide Turns South desc
("""Brotherhood, raider and bone-dancer: whether they came down to the water as allies or as corpses, the peoples of the north have given their answer, and it was the tide's. From the Sound to the redwood coast every harbour keeps time to the drums of §Y[MLT.GetNameDef]§!.""",
 """Brotherhood, raider and bone-dancer: one by one the peoples of the north are giving their answer, as allies or as corpses, and every answer is the tide's. From the Sound to the redwood coast the harbours are learning to keep time to the drums of §Y[MLT.GetNameDef]§!."""),
("""The stars are right, the north is ours, and the tide has only begun to come in.\"""",
 """The stars are right, the north is falling to us, and the tide has only begun to come in.\""""),
# F5 tooltip
("""  mltd_tide_turns_south_states_tt:0 "Controls at least §Y50§! states\"""",
 """  mltd_tide_turns_south_states_tt:0 "Controls at least §Y50§! states, or the year §Y2281§! has begun\""""),
# F15 Northern Waters idea
("""The tribes, brotherhoods and raider crews that once fought over every cove from the Sound to the redwoods now kneel together in the surf at dusk, and the coast that bred them has become a single drowned country.""",
 """The tribes and raider crews that once fought over every cove from the Sound to the redwoods now kneel together in the surf at dusk, and the coast that bred them is becoming a single drowned country."""),
# F15 mltd.30.d
("""There is nothing left in the north to take.""",
 """What is left in the north will fall of its own weight."""),
# F15 mltd.31.d
("""The last free harbours of the north have fallen silent.""",
 """One by one the free harbours of the north have fallen silent."""),
("""and of brotherhoods, raider crews and tribes that were at one another's throats a year ago and now kneel together in the surf at dusk. The crab-worshippers of §o[MLT.GetNameDef]§! hold the whole northern shore, from the Sound to the redwoods.""",
 """and of raider crews and tribes that were at one another's throats a year ago and now kneel together in the surf at dusk. The crab-worshippers of §o[MLT.GetNameDef]§! hold most of the northern shore, from the Sound to the redwoods."""),
# F18 Shady Sands desc
("""and the §YRangers§!, who swore to hold the desert and could not. The oracles say the deep can take only one of them whole. §Y[MLT_MLULU.GetName]§! does not choose; she only dreams, nearer the surface every night. The Court must choose for her.\"""",
 """and the §YRangers§!, who swore to hold the desert and could not. Only one of them can be taken whole.\""""),
# F2/F19
("""  mltd_ncr_beaten_tt:0 "§Y[NCR.GetNameDefCap]§! has capitulated to us, is no more, or is our subject\"""",
 """  mltd_ncr_beaten_tt:0 "§Y[NCR.GetNameDefCap]§! has capitulated, is no more, or is our subject\""""),
# F20 mltd.50.d
("""in the hand of an oracle who has worn a ferryman's rags on the Colorado for three years.""",
 """in the hand of an oracle who wears a ferryman's rags on the Colorado."""),
# F11+F17 Southern Deep desc
("""Now the oracles of the Coral Court turn their faces south, where the water is warmer and much older. Three powers still stand between the two gulfs, and §Y[MLT_MLULU.GetName]§! has dreamed of each of them: the oilmen of Texas, who drill past the oil into a black water that sings back up the pipe; §Y[ATE.GetNameDef]§!, whose blind Speaker has woken from the same nightmare every night for ten years; and the copper lair beneath old Mexico where §Y[TLA_tlaloc.GetName]§! forgets himself one memory at a time.""",
 """Now the oracles of the Coral Court look further still, past the Colorado to the warm southern seas, where the water is much older. Three powers still stand between the two gulfs, and §Y[MLT_MLULU.GetName]§! has dreamed of each of them: the oilmen of Texas, who drill past the oil into a black water that sings back up the pipe; §Y[ATE.GetNameDef]§!, whose blind Speaker foresaw the iron god's death long before it came; and the copper lair beneath old Mexico, where §Y[TLA_tlaloc.GetName]§! is forgetting himself one memory at a time - or has already forgotten the last, and left his heirs to fight over the bones."""),
# F11 Feathered Tide desc
("""and its blind Speaker has not slept a whole night in ten years. A dream of the iron god's death, and of the chaos after it, comes to her again and again, and her court has learned to fear whatever she foresees. Our oracles have listened to that dream from a thousand miles away, and they have begun, very gently, to change it. The serpent on her banner, the Speaker now tells her priests, was never a creature of the sky. It came up out of the sea. Meanwhile the Order walks in by the harbour gate. The Speaker's own spies are brutes who look for knives and never for fishermen, and her navy""",
 """and its blind Speaker foresaw the iron god's death, and the chaos after it, years before either came, and the court has learned to fear whatever the palace dreams. Our oracles have listened to those dreams from a thousand miles away, and they have begun, very gently, to change them. The serpent on the banner, the priests have started to preach, was never a creature of the sky. It came up out of the sea. Meanwhile the Order walks in by the harbour gate. The Empire's own spies are brutes who look for knives and never for fishermen, and its navy"""),
# F12 Last King Kneels
("""The south had many kings: a machine that called itself a god, a blind Speaker under a feathered banner, and the hard men of Texas who swore on their flag that they would never kneel to anyone. The Texans held out longest. Now their last guns are stacked in the red dust, and the Coral Court has sent for whoever still gives orders among them. He will walk down into the Gulf of his own accord, as far as his chest,""",
 """The south has many kings: a machine that called itself a god, a blind Speaker under a feathered banner, and the hard men of Texas, who swore on their flag that they would never kneel to anyone. Now the Texans' last guns are stacked in the red dust, and the Coral Court has sent for whoever still gives orders among them. He will be brought west to the coral gates of §YM'lyeh§! and walk down into the surf of his own accord, as far as his chest,"""),
# F11 mltd.60.d
("""A machine that is dying, and dreams in copper and static. A blind woman in a feathered palace, who wakes every night from a drowning and tells no one.""",
 """A machine that is dying, or is dead and still dreams in copper and static. A feathered palace where a blind woman once foresaw that death, and where someone now wakes every night from a drowning and tells no one."""),
# F17 mltd.60.a
("""  mltd.60.a:0 "Then let the tide turn south.\"""",
 """  mltd.60.a:0 "Then let the south be answered.\""""),
# F18 R'lyeh Rises desc
("""since §Y$mltd_the_grand_ritual$§!. The tribe called it M'lyeh, because that was all a tribesman's throat could say. It has an older name, and when it breaks the surface the whole world will learn it.\"""",
 """since §Y$mltd_the_grand_ritual$§!. It has a name older than any the tribe has given it, and when it breaks the surface the whole world will learn it.\""""),
# F18 Return to the Sea desc
("""  mltd_ending_return_to_the_sea_desc:0 "The land was only ever a shore. The faithful were born dry, but they need not die so: the pools""",
 """  mltd_ending_return_to_the_sea_desc:0 "The faithful were born dry, but they need not die so: the pools"""),
# F13 mltd.70.a
("""  mltd.70.a:0 "Ph'nglui mglw'nafh M'lulu R'lyeh wgah'nagl fhtagn.\"""",
 """  mltd.70.a:0 "In his house at R'lyeh the Dreamer waits dreaming.\""""),
]
for a, b2 in reps:
    c = s.count(a)
    assert c == 1, (c, a[:90])
    s = s.replace(a, b2)
open(p, 'wb').write(b'\xef\xbb\xbf' + s.encode('utf-8'))
print('ok', len(reps))
