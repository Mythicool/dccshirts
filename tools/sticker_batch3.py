"""Batch 3: 100 fan-art die-cut stickers (personal use), spread evenly over the cast.

Run: py tools/sticker_batch3.py
Writes image-prompts/pack-s01..s10.md and merges the stickers into designs.json (product "sticker", batch 3).
Character descriptions come from the Characters list in image-prompts/STYLE.md, word for word.
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BATCH = 3

STYLE = (ROOT / "image-prompts/STYLE.md").read_text(encoding="utf-8")
CHARS = dict(re.findall(r"^- ([A-Z]+): (.+)$", STYLE, re.M))
CHARS["DONUT"] = CHARS["DONUT"].replace(" She is never all white.", "")

ART = {
    "kawaii": "chunky kawaii sticker art with thick outlines and flat pastel cel shading",
    "comic": "bold modern comic book art with thick inks and a little halftone shading",
    "rubber-hose": "1930s rubber-hose cartoon with pie-cut eyes, bendy noodle limbs and white gloves",
    "pop-art": "1960s pop-art print with Ben-Day dots and heavy black outlines",
    "pixel": "crisp 16-bit pixel art with hard pixel edges",
    "neon": "glowing neon-tube sign with bright tubes on a dark rounded backing plate",
    "metal": "heavy-metal band logo art with sharp spiky lettering",
    "woodcut": "medieval woodcut print with bold carved linework",
    "vintage-litho": "vintage lithograph label art with a slightly worn print texture",
    "retro-70s": "1970s retro illustration with sunburst stripes and rounded groovy lettering",
    "80s-synth": "glossy 1980s synthwave airbrush with chrome lettering",
    "ornate": "ornate engraved illustration with fine gold filigree",
    "minimal": "clean flat vector illustration",
    "retro-ad": "1950s retro advertising illustration",
    "deco": "1920s art deco poster art with geometric shapes and gold lines",
    "anime": "1990s cel-shaded anime art",
    "folk": "embroidered folk-art patch look with visible stitch texture",
}

# slug, title, subject, format, art, humor, palette tag, palette words, body
S = [
    # CARL
    ("carl_no_pants", "No Pants No Problem", "carl", "mascot", "rubber-hose", "absurd", "warm-retro", "cream, brown, pink and black",
     "{CARL} strides along with a big confident grin, one hand waving, drawn as a jaunty cartoon mascot. A curved ribbon banner under his feet reads \"NO PANTS. NO PROBLEM.\""),
    ("carl_kick_it", "Kick It", "carl", "comic", "pop-art", "gamer", "primary", "red, yellow, blue, black and white",
     "{CARL} is caught mid flying kick, one bare foot sending a small green goblin tumbling away with cartoon stars around its head. A jagged comic explosion burst behind them reads \"KICK IT!\""),
    ("carl_dynamite", "Carl's Dynamite", "carl", "label", "vintage-litho", "dark", "dark-red", "firecracker red, cream, gold and black",
     "A vintage firecracker package label shaped like a rounded rectangle. On it, {CARL} holds up a lit stick of dynamite with a sly grin, the fuse sparking. Bold label lettering reads \"CARL'S DYNAMITE\" and a small line under it reads \"HANDLE WITH FEET\"."),
    ("carl_barefoot", "Barefoot And Dangerous", "carl", "badge", "vintage-litho", "sassy", "earthy", "olive green, tan, brown and cream",
     "A round vintage merit badge with a rope border. In the center, {CARL} stands with fists on his hips and his bare feet planted wide. Arched lettering around the top reads \"BAREFOOT\" and around the bottom reads \"& DANGEROUS\"."),
    ("carl_spite", "Running On Spite", "carl", "mascot", "kawaii", "dark", "pastel", "pastel pink, coffee brown, cream and lilac",
     "A chibi version of {CARL}, drawn small and round, with heavy tired eye bags, clutches a giant steaming coffee mug in both hands. A tiny storm cloud floats over his head. Bubbly rounded lettering below reads \"RUNNING ON SPITE\"."),
    ("carl_goddamn_it", "Goddamn It Donut", "carl", "typographic", "retro-70s", "quote", "warm-retro", "orange, mustard, brown and cream",
     "Big chunky hand-lettered words stacked in three lines read \"GODDAMN IT, DONUT\". A small figure of {CARL} sits on top of the letters, facepalming with one hand."),
    ("carl_hp_one", "HP 1 Still Kicking", "carl", "pixel-screen", "pixel", "gamer", "primary", "red, green, white, black and blue",
     "A pixel-art version of {CARL} stands in a fighting stance above a health bar that is almost empty, with a single red sliver left. Pixel lettering above reads \"HP: 1\" and pixel lettering below reads \"STILL KICKING\"."),
    ("carl_boxer_order", "Order Of The Boxer Shorts", "carl", "patches", "folk", "absurd", "earthy", "brown, pink, gold and dark navy",
     "A round embroidered patch. In the center, a head-and-shoulders portrait of {CARL} sits above two crossed sticks of dynamite. Stitched lettering curves around the edge reading \"ORDER OF THE BOXER SHORTS\"."),
    ("carl_open_kicking", "Open For Kicking", "carl", "sign", "neon", "gamer", "neon", "hot pink, electric blue and warm white tubes",
     "A neon sign shows the outline of {CARL} doing a high kick, drawn in glowing tubes. Neon script beside him reads \"OPEN 24/7\" and neon block letters below read \"FOR KICKING\"."),
    # DONUT
    ("donut_magic_missile", "Magic Missile", "donut", "mascot", "anime", "gamer", "pastel", "pink, lavender, sky blue, gold and white",
     "{DONUT} leaps through the air in a dramatic pose, firing a glowing pink and blue energy bolt from one raised paw, with sparkles and tiny stars trailing behind her. Bold anime lettering with a white outline reads \"MAGIC MISSILE!\""),
    ("donut_bow_princess", "Bow To The Princess", "donut", "crest", "ornate", "sassy", "pink-gold", "rose pink, gold, deep plum and cream",
     "A royal crest: {DONUT} sits proudly on a tasselled velvet cushion inside an ornate gold frame with a small crown on top. A curling ribbon banner below reads \"BOW TO THE PRINCESS\"."),
    ("donut_followers", "A Million Followers", "donut", "game-ui", "minimal", "meta", "pink-gold", "hot pink, white, gold and black",
     "A rounded social-media notification card. A circular profile picture on the left shows {DONUT} striking a pose. Big lettering on the right reads \"+1,000,000\" with a pink heart icon, and smaller lettering below reads \"NEW FOLLOWERS\"."),
    ("donut_grand_champion", "Grand Champion", "donut", "badge", "vintage-litho", "sassy", "pink-gold", "royal blue, gold, pink and cream",
     "A cat-show prize rosette with pleated ribbon rings and two ribbon tails hanging below. In the round center sits a portrait of {DONUT} with her nose in the air. Lettering on the ribbon tails reads \"GRAND CHAMPION\"."),
    ("donut_mongo_no", "Mongo No", "donut", "comic", "comic", "quote", "primary", "red, yellow, teal, purple and white",
     "{DONUT} stands in front, pointing one paw furiously at the viewer's left, her fur puffed up. Behind her, a smaller version of {MONGO} happily chews on a stolen boot. A big comic speech balloon from the cat reads \"MONGO, NO!\""),
    ("donut_iconic", "Iconic", "donut", "portrait", "pop-art", "sassy", "neon", "four bright pop colour sets: pink, yellow, cyan and lime",
     "A square two-by-two grid of the same face of {DONUT}, each panel printed in a different bright colour set like a famous pop-art screenprint. A small bold banner across the bottom reads \"ICONIC\"."),
    ("donut_empress", "The Empress Tarot", "donut", "tarot", "ornate", "sassy", "pink-gold", "deep purple, gold, pink and cream",
     "A tall tarot card with a gold border. {DONUT} sits on a throne made of a pile of treasure chests, coins and loot boxes, holding a tiny scepter. The card's bottom plate reads \"THE EMPRESS\" and a small roman numeral at the top reads \"III\"."),
    ("donut_in_charge", "Tiny But In Charge", "donut", "mascot", "kawaii", "sassy", "pastel", "pastel pink, brown, white, gold and lilac",
     "A chibi version of {DONUT}, drawn round like a marshmallow, stomps forward with an adorably furious face and a little anger symbol by her ear. Bubbly rounded lettering below reads \"TINY BUT IN CHARGE\"."),
    ("donut_princess_carl", "I Am A Princess Carl", "donut", "typographic", "retro-70s", "quote", "warm-retro", "orange, pink, mustard, brown and cream",
     "{DONUT} lounges in front of a round 1970s sunburst with her chin held high. Groovy rounded lettering wraps above and below her reading \"I AM A PRINCESS\" on top and \"CARL\" underneath."),
    # MONGO
    ("mongo_snack_time", "Snack Time", "mongo", "mascot", "kawaii", "wholesome", "pastel", "lavender, teal, pink, cream and brown",
     "A chibi version of {MONGO}, drawn super round with huge sparkly eyes, hugs a cooked drumstick almost as big as himself, drooling a little. Small hearts float around him. Bubbly lettering below reads \"SNACK TIME\"."),
    ("mongo_metal", "Mongo Metal", "mongo", "band", "metal", "absurd", "dark-red", "blood red, black, silver and teal",
     "A heavy-metal band logo: {MONGO} roars with his mouth wide open between two crossed bones, framed by flames. Huge jagged spiky metal lettering above him reads \"MONGO\"."),
    ("mongo_k9", "Raptor Unit", "mongo", "badge", "vintage-litho", "wholesome", "primary", "navy blue, gold, red and white",
     "A police-style shield badge with a gold star border. In the center, {MONGO} sits up straight, proud and alert, with his tongue out. Arched lettering on top reads \"RAPTOR UNIT\" and a scroll below reads \"GOOD BOY\"."),
    ("mongo_virtual_pet", "Hunger Always", "mongo", "pixel-screen", "pixel", "gamer", "pastel", "mint, lavender, pink and dark grey",
     "An egg-shaped handheld virtual-pet toy with three round buttons. Its small screen shows a pixel-art version of {MONGO} wagging next to a pixel meat icon. Small pixel lettering on the screen reads \"HUNGER: ALWAYS\"."),
    ("mongo_rad_raptor", "Rad Raptor", "mongo", "mascot", "80s-synth", "absurd", "neon", "hot pink, cyan, purple and chrome",
     "{MONGO} wears tiny black sunglasses and poses in front of a striped synthwave sunset over a glowing grid. Slanted chrome lettering across the bottom reads \"RAD RAPTOR\"."),
    ("mongo_beware", "Beware Of Dino", "mongo", "sign", "minimal", "absurd", "primary", "red, white, black and purple",
     "A small rectangular yard warning sign on a short stake. A cartoon version of {MONGO} on the sign wags his tail happily. Bold block lettering reads \"BEWARE OF DINO\" and a small line below reads \"HE WILL LICK YOU\"."),
    ("mongo_bestiary", "Here Be Raptors", "mongo", "portrait", "woodcut", "absurd", "mono", "black ink on aged parchment cream, with only the collar spikes in teal",
     "A medieval bestiary woodcut of {MONGO} standing in profile with an unrolling scroll curling beneath his feet. Old-style lettering on the scroll reads \"HIC SUNT RAPTORES\"."),
    ("mongo_zoomies", "Zoomies", "mongo", "mascot", "rubber-hose", "wholesome", "warm-retro", "cream, purple, teal and black",
     "{MONGO} runs at full speed with his legs spinning into a cartoon blur wheel, little dust clouds puffing behind him and his tongue flapping. Bouncy cartoon lettering above reads \"ZOOMIES\"."),
    ("mongo_loves_you", "Mongo Loves You", "mongo", "comic", "comic", "wholesome", "pastel", "lavender, teal, pink, brown and white",
     "{MONGO} squeezes {DONUT} in a big happy hug, eyes closed with joy, while the cat looks deeply unimpressed, squished in his arms. Pink hearts burst around them. Rounded lettering below reads \"MONGO LOVES YOU\"."),
    # MORDECAI
    ("mordecai_potion", "Mordecai's Healing Potion", "mordecai", "label", "vintage-litho", "sassy", "earthy", "bottle green, red, tan and cream",
     "A vintage apothecary bottle label with scalloped corners. A small oval portrait of {MORDECAI} sits at the top. Ornate lettering reads \"MORDECAI'S HEALING POTION\" and a small line at the bottom reads \"MAY CAUSE GRUMPINESS\"."),
    ("mordecai_read_manual", "Read The Manual", "mordecai", "typographic", "comic", "sassy", "primary", "red, yellow, brown and black",
     "{MORDECAI} leans in with an exasperated face, jabbing a finger at a huge open book. Big chunky lettering across the bottom reads \"READ THE MANUAL\"."),
    ("mordecai_name_tag", "Ask Me Anything Don't", "mordecai", "badge", "minimal", "sassy", "primary", "red, white and black",
     "A classic red \"hello my name is\" name tag with a white writing panel. A tiny grumpy version of {MORDECAI} peeks over the top edge. Printed lettering reads \"HELLO MY NAME IS\", the hand-written panel reads \"MORDECAI\", and a small line below reads \"ASK ME ANYTHING (DON'T)\"."),
    ("mordecai_hermit", "The Hermit Tarot", "mordecai", "tarot", "ornate", "wholesome", "earthy", "deep blue, gold, brown and cream",
     "A tall tarot card with a gold border. {MORDECAI} stands on a rocky path in a hooded robe, holding up a lantern with a glowing star inside. The bottom plate reads \"THE HERMIT\" and a roman numeral at the top reads \"IX\"."),
    ("mordecai_guide_in", "The Guide Is In", "mordecai", "sign", "retro-ad", "wholesome", "warm-retro", "teal, mustard, brown and cream",
     "A hanging shop-door sign on two little chains. {MORDECAI} peeks over the top edge of the sign with a reluctant half smile. Retro lettering on the sign reads \"THE GUIDE IS IN\"."),
    ("mordecai_ugh", "Ugh", "mordecai", "mascot", "kawaii", "sassy", "pastel", "mint green, lilac, tan and cream",
     "A chibi version of {MORDECAI} sips from a bubbling round potion flask through a curly straw, with a flat unimpressed stare. A small speech cloud beside him reads \"UGH\"."),
    ("mordecai_good_luck", "Good Luck", "mordecai", "pixel-screen", "pixel", "dark", "primary", "dark navy, white, gold and brown",
     "A retro RPG dialogue box with a white pixel border. A square pixel-art portrait of {MORDECAI} sits on the left. Pixel lettering in the box reads \"YOU ARE ALL GOING TO DIE. GOOD LUCK!\""),
    ("mordecai_okayest", "World's Okayest Guide", "mordecai", "badge", "retro-70s", "meta", "warm-retro", "orange, mustard, brown and cream",
     "{MORDECAI} gives a reluctant thumbs up inside a round 1970s sunburst badge. Groovy lettering around the badge reads \"WORLD'S OKAYEST GUIDE\"."),
    ("mordecai_stir", "Stir Swear Repeat", "mordecai", "portrait", "woodcut", "sassy", "mono", "black ink on parchment cream, with only the potion in green",
     "A woodcut of {MORDECAI} stirring a big bubbling cauldron with a long paddle, steam curling up. Old-style lettering on a banner below reads \"STIR. SWEAR. REPEAT.\""),
    # KATIA
    ("katia_hold_line", "Hold The Line", "katia", "crest", "ornate", "wholesome", "dark-red", "deep red, silver, gold and black",
     "A heraldic crest shield. {KATIA} stands in the center bracing behind her raised shield, determined. A ribbon banner below the crest reads \"HOLD THE LINE\"."),
    ("katia_size_up", "Size Up", "katia", "comic", "comic", "absurd", "primary", "red, yellow, blue, grey and white",
     "{KATIA} is caught mid-transformation, her body swelling into a huge stone-skinned giant while she keeps her round shield up, small goblins scattering at her feet. A jagged comic burst reads \"SIZE UP!\""),
    ("katia_tank", "Tank", "katia", "game-ui", "minimal", "gamer", "primary", "steel blue, red, white and black",
     "A video-game role badge shaped like a shield. A portrait of {KATIA} sits in the center above a bold lettering plate that reads \"TANK\". A smaller line under it reads \"AGGRO: ALL OF IT\"."),
    ("katia_protector", "Protector", "katia", "mascot", "kawaii", "wholesome", "pastel", "pastel blue, silver, pink and cream",
     "A chibi version of {KATIA} hugs her round shield with a soft proud smile, little sparkles around her. Bubbly rounded lettering below reads \"PROTECTOR\"."),
    ("katia_shield_maiden", "Shield Maiden", "katia", "portrait", "80s-synth", "wholesome", "neon", "hot pink, cyan, purple and chrome",
     "{KATIA} stands in a heroic pose with her shield raised, silhouetted against a striped synthwave sun. Slanted chrome lettering across the bottom reads \"SHIELD MAIDEN\"."),
    ("katia_deco", "Katia Deco", "katia", "poster", "deco", "wholesome", "mono", "black, cream and metallic gold",
     "An art deco portrait in a tall arched frame: {KATIA} in strong profile with her shield behind her like a sunburst of gold rays. Elegant deco lettering at the bottom reads \"KATIA\"."),
    ("katia_grim_metal", "Katia Grim", "katia", "band", "metal", "dark", "dark-red", "black, blood red and silver",
     "A heavy-metal band logo. Jagged spiky lettering reads \"KATIA GRIM\" across a battered round shield, with {KATIA} behind it roaring a battle cry and two crossed swords behind the shield."),
    ("katia_front_line", "Front Line Club", "katia", "patches", "folk", "wholesome", "earthy", "olive, rust, cream and dark brown",
     "A round embroidered scout patch. The center shows {KATIA} holding her shield up against falling arrows. Stitched lettering around the edge reads \"FRONT LINE CLUB\"."),
    ("katia_blocked", "Blocked", "katia", "pixel-screen", "pixel", "gamer", "primary", "blue, orange, white and grey",
     "A pixel-art version of {KATIA} blocks a big pixel fireball with her shield, the flames splashing off in pixel sparks. Pixel lettering above reads \"BLOCKED!\""),
    # SAMANTHA
    ("samantha_stabby", "Stabby", "samantha", "mascot", "kawaii", "dark", "pastel", "pastel pink, red, cream and lavender",
     "A chibi version of {SAMANTHA}, round and blushing, with a tiny cartoon knife tucked in her curls and a sweet smile that does not reach her eyes. Bubbly rounded lettering below reads \"STABBY\"."),
    ("samantha_body_wanted", "Wanted One Body", "samantha", "poster", "retro-ad", "absurd", "warm-retro", "cream, red, black and mustard",
     "A torn classified-ad poster with tear-off tabs along the bottom. In the middle is a photo-style drawing of {SAMANTHA}. Bold retro lettering on top reads \"WANTED:\" and below it \"ONE BODY\"."),
    ("samantha_demigoddess", "Demigoddess", "samantha", "portrait", "ornate", "sassy", "pink-gold", "gold, red, pink and cream",
     "{SAMANTHA} floats in the center wearing a radiant gold halo, with divine light rays and tiny clouds behind her, still glaring. Elegant engraved lettering below reads \"DEMIGODDESS\"."),
    ("samantha_strike", "Strike", "samantha", "comic", "rubber-hose", "absurd", "warm-retro", "cream, red, black and orange",
     "{SAMANTHA} rolls like a bowling ball down a dungeon lane, knocking over a row of tumbling goblins like bowling pins, motion lines behind her. Bouncy cartoon lettering above reads \"STRIKE!\""),
    ("samantha_murder", "I Will Murder You All", "samantha", "comic", "pop-art", "dark", "dark-red", "red, yellow, black and white with Ben-Day dots",
     "A close-up of {SAMANTHA} glaring, drawn like a 1960s romance-comic panel with a single dramatic tear. A comic speech balloon reads \"I WILL MURDER YOU ALL\"."),
    ("samantha_metal", "Samantha Metal", "samantha", "band", "metal", "dark", "dark-red", "black, blood red and fiery orange",
     "A heavy-metal band logo: {SAMANTHA} is wreathed in flames with her hair blazing like fire. Jagged spiky lettering arched above her reads \"SAMANTHA\"."),
    ("samantha_kiss_death", "Kiss Of Death", "samantha", "sign", "neon", "dark", "neon", "red, hot pink and white tubes",
     "A neon sign: the outline of {SAMANTHA} in glowing tubes with big red neon lips. Neon script beneath reads \"KISS OF DEATH\"."),
    ("samantha_death_tarot", "Death Tarot", "samantha", "tarot", "ornate", "dark", "dark-red", "black, deep red, gold and cream",
     "A tall tarot card with a gold border. {SAMANTHA} sits on a dark velvet pillow among black roses, eyes blazing. The bottom plate reads \"DEATH\" and a roman numeral at the top reads \"XIII\"."),
    ("samantha_she_bites", "Handle With Care", "samantha", "label", "minimal", "absurd", "primary", "red, yellow, black and white",
     "A shipping box warning label with a thick black border. The label shows {SAMANTHA} with an upward arrow above her. Bold lettering reads \"HANDLE WITH CARE\" and a smaller line below reads \"SHE BITES\"."),
    # PREPOTENTE
    ("prepotente_scream", "Goat Scream", "prepotente", "comic", "pop-art", "absurd", "neon", "yellow, hot pink, cyan and black",
     "{PREPOTENTE} screams with his mouth wide open and his tongue flapping, eyes bulging. A huge jagged comic burst behind him reads \"AAAAAH!\""),
    ("prepotente_magnificent", "Magnificent", "prepotente", "portrait", "ornate", "sassy", "pink-gold", "gold, purple, cream and grey",
     "A royal oil-portrait look inside an oval gold frame: {PREPOTENTE} poses with his chin up and his cape flowing. A ribbon banner beneath the frame reads \"MAGNIFICENT\"."),
    ("prepotente_crossing", "Goat Crossing", "prepotente", "sign", "minimal", "sassy", "primary", "warning yellow, black and purple",
     "A yellow diamond road warning sign with a thick black border, showing a black silhouette of {PREPOTENTE} strutting. A rectangular plate below reads \"GOAT CROSSING\" and a smaller plate reads \"HE WILL NOT YIELD\"."),
    ("prepotente_goty", "Goat Of The Year", "prepotente", "mascot", "kawaii", "sassy", "pastel", "lilac, grey, gold and pink",
     "A chibi version of {PREPOTENTE}, drawn round and fluffy, holds a tiny gold trophy with a smug closed-eye smile. Bubbly rounded lettering below reads \"GOAT OF THE YEAR\"."),
    ("prepotente_hail", "Hail The Goat", "prepotente", "band", "metal", "absurd", "dark-red", "black, blood red, silver and yellow",
     "A heavy-metal band logo: {PREPOTENTE} rears up on his hind legs with lightning crackling between his horns. Jagged spiky lettering above him reads \"HAIL THE GOAT\"."),
    ("prepotente_bestiary", "Capra Magnifica", "prepotente", "portrait", "woodcut", "absurd", "mono", "black ink on parchment cream, with only the cape in purple",
     "A medieval bestiary woodcut of {PREPOTENTE} standing on a rocky ledge in profile, with a scroll curling beneath him. Old-style lettering on the scroll reads \"CAPRA MAGNIFICA\"."),
    ("prepotente_boss", "Boss Angry Goat", "prepotente", "pixel-screen", "pixel", "gamer", "dark-red", "red, black, grey and yellow",
     "A pixel-art boss fight frame: {PREPOTENTE} looms large and furious above a long red boss health bar. Pixel lettering on the bar reads \"BOSS: VERY ANGRY GOAT\"."),
    ("prepotente_vibes", "Goat Vibes", "prepotente", "mascot", "retro-70s", "wholesome", "warm-retro", "orange, mustard, teal and brown",
     "{PREPOTENTE} wears round orange sunglasses and rides a surfboard on a curling 1970s wave, cape flapping. Groovy rounded lettering above reads \"GOAT VIBES\"."),
    ("prepotente_cheese", "Prepotente Brand Cheese", "prepotente", "label", "vintage-litho", "absurd", "earthy", "cream, red, green and brown",
     "A round vintage cheese wheel label with a scalloped edge. In the center is a portrait of {PREPOTENTE} looking deeply offended. Old-fashioned lettering reads \"PREPOTENTE BRAND\" on top, \"GOAT CHEESE\" in the middle and \"DO NOT ASK HIM\" at the bottom."),
    # ZEV
    ("zev_press_pass", "Press Pass", "zev", "badge", "minimal", "meta", "primary", "blue, white, yellow and black",
     "A plastic press pass on a lanyard clip. The card has a photo of {ZEV} smiling a forced corporate smile. Bold lettering reads \"PRESS PASS\" and a yellow strip below reads \"ALL ACCESS\"."),
    ("zev_on_schedule", "On Schedule", "zev", "mascot", "kawaii", "wholesome", "pastel", "baby blue, black, white and pink",
     "A chibi version of {ZEV}, round and earnest, holds up the clipboard showing a checklist with every box ticked, little sparkles around him. Bubbly rounded lettering below reads \"ON SCHEDULE\"."),
    ("zev_smile", "Smile You're On Camera", "zev", "poster", "retro-ad", "meta", "warm-retro", "teal, red, cream and black",
     "A 1950s advertising cutout: {ZEV} points straight at the viewer with a big toothy grin, a small vintage TV camera beside him. Retro lettering reads \"SMILE!\" on top and \"YOU'RE ON CAMERA\" below."),
    ("zev_pr_fish", "Premium PR Fish", "zev", "label", "vintage-litho", "absurd", "earthy", "navy, mustard, red and cream",
     "A vintage sardine tin label shaped like a rounded rectangle with a can key on one corner. In the center is a portrait of {ZEV} with a fixed smile. Old-fashioned lettering reads \"PREMIUM PR FISH\" and a small line reads \"PACKED IN CORPORATE SAUCE\"."),
    ("zev_handler", "Your Friendly Handler", "zev", "poster", "deco", "meta", "mono", "black, cream, metallic gold and a touch of blue",
     "An art deco corporate poster with geometric gold rays. {ZEV} stands in the center, posed like a company mascot with the clipboard held to his chest. Elegant deco lettering below reads \"YOUR FRIENDLY HANDLER\"."),
    ("zev_on_air", "On Air", "zev", "sign", "neon", "meta", "neon", "red, blue and white tubes",
     "A glowing red neon \"ON AIR\" studio sign in a rounded box, with the outline of {ZEV} drawn in blue neon tubes beside it waving nervously."),
    ("zev_forms", "Please Sign These Forms", "zev", "pixel-screen", "pixel", "absurd", "primary", "dark navy, white, blue and yellow",
     "A retro RPG dialogue box with a white pixel border and a square pixel-art portrait of {ZEV} on the left, next to a tall wobbling pixel stack of papers. Pixel lettering reads \"PLEASE SIGN THESE 400 FORMS\"."),
    ("zev_damage_control", "Damage Control", "zev", "comic", "comic", "meta", "primary", "red, yellow, blue and white",
     "{ZEV} sweats buckets, a phone pressed to each ear and papers flying everywhere around him. A jagged comic burst reads \"DAMAGE CONTROL!\""),
    ("zev_on_brand", "Stay On Brand", "zev", "mascot", "80s-synth", "sassy", "neon", "hot pink, cyan, purple and chrome",
     "{ZEV} wears black sunglasses and leans cool against the clipboard in front of a striped synthwave sun. Slanted chrome lettering across the bottom reads \"STAY ON BRAND\"."),
    # SYSTEM
    ("system_out_of_bed", "Achievement Got Out Of Bed", "system", "game-ui", "minimal", "gamer", "neon", "dark navy, gold, white and cyan",
     "A video-game achievement pop-up banner: a rounded dark panel with a glowing gold trophy icon on the left. Top lettering reads \"NEW ACHIEVEMENT!\" and the main line reads \"YOU GOT OUT OF BED\"."),
    ("system_bronze_box", "Bronze Box", "system", "game-ui", "comic", "gamer", "warm-retro", "bronze, orange, gold and dark brown",
     "A glowing bronze loot box with rivets and a keyhole sits with light beams bursting from its seams. A notification ribbon above it reads \"YOU HAVE RECEIVED A BRONZE BOX\"."),
    ("system_level_up", "Level Up", "system", "pixel-screen", "pixel", "gamer", "neon", "cyan, magenta, yellow and white",
     "Big glowing pixel-art lettering reads \"LEVEL UP!\" with pixel up-arrows and sparkles bursting around it, on a small rounded dark pixel panel."),
    ("system_viewers", "Nine Billion Viewers", "system", "game-ui", "minimal", "meta", "neon", "red, white, black and cyan",
     "A live-stream viewer counter: a rounded dark badge with a glowing red record dot and an eye icon. Lettering reads \"LIVE\" and a big counter reads \"9,000,000,000 VIEWERS\"."),
    ("system_watching", "The System Is Watching", "system", "badge", "minimal", "dark", "mono", "black, white and a glowing red",
     "A single glowing red robotic eye sits inside a sharp black hexagon with circuit lines radiating out. Clean lettering below reads \"THE SYSTEM IS WATCHING\"."),
    ("system_collapse", "Floor Collapse Warning", "system", "sign", "minimal", "dark", "primary", "warning yellow, black and red",
     "A yellow triangular warning sign with a black border, showing a pictogram of a figure falling through cracked floor tiles. A plate below reads \"WARNING\" and a smaller plate reads \"FLOOR COLLAPSE IN 3 DAYS\"."),
    ("system_patch_notes", "Patch Notes", "system", "typographic", "pixel", "meta", "mono", "black, white and terminal green",
     "A small retro computer terminal window with a title bar. Green terminal lettering inside reads \"PATCH NOTES:\" on the first line and \"EVERYTHING IS WORSE\" on the second, with a blinking cursor."),
    ("system_sarcasm", "Skill Unlocked Sarcasm", "system", "game-ui", "minimal", "sassy", "neon", "purple, cyan, gold and white",
     "A glowing skill-tree node: a hexagon icon with a smirking mouth symbol, connected to two faded nodes. Lettering beside it reads \"SKILL UNLOCKED\" and \"SARCASM LVL 15\"."),
    ("system_floor_cleared", "Certified Crawler", "system", "badge", "vintage-litho", "gamer", "warm-retro", "mustard, rust, brown and cream",
     "A round vintage seal with a sawtooth edge and a stairway icon in the center. Arched lettering reads \"CERTIFIED CRAWLER\" and the bottom reads \"FLOOR 1 CLEARED\"."),
    # TRIO / GROUP
    ("trio_royal_court", "Royal Court Party", "trio", "game-ui", "pixel", "gamer", "pink-gold", "pink, gold, dark navy and white",
     "An RPG party frame panel with three stacked pixel portraits, each with a green health bar: {DONUT} on top wearing a pixel crown icon, {CARL} in the middle and {MONGO} at the bottom. A header bar reads \"PARTY: ROYAL COURT OF PRINCESS DONUT\"."),
    ("trio_band", "Crawl Crew Band", "trio", "band", "retro-70s", "meta", "warm-retro", "orange, mustard, pink and brown",
     "A 1970s rock band logo: {CARL}, {DONUT} and {MONGO} pose together like a band album cover, the cat in front. Groovy bubble lettering above reads \"THE CRAWLERS\" with a small lightning bolt."),
    ("trio_stairs", "March To The Stairs", "trio", "mascot", "rubber-hose", "wholesome", "warm-retro", "cream, black, pink and purple",
     "{CARL}, {DONUT} and {MONGO} march in a happy line with bendy noodle legs toward a small staircase going down. Bouncy cartoon lettering above reads \"NEXT STOP: DOWNSTAIRS\"."),
    ("trio_squad_stack", "Squad Stack", "trio", "mascot", "kawaii", "wholesome", "pastel", "pastel pink, lavender, teal, brown and cream",
     "A chibi totem stack: a round chibi version of {MONGO} at the bottom, a chibi version of {DONUT} sitting on his head, and a chibi version of {CARL} peeking out from behind them with a sleepy wave. Bubbly lettering below reads \"SQUAD\"."),
    ("trio_fool_tarot", "The Fool Tarot", "trio", "tarot", "ornate", "dark", "pink-gold", "sky blue, gold, pink and cream",
     "A tall tarot card with a gold border. {CARL} walks cheerfully toward a cliff edge holding a small bindle, with {DONUT} riding on his shoulder and {MONGO} trotting at his heels. The bottom plate reads \"THE FOOL\" and a roman numeral at the top reads \"0\"."),
    ("trio_corridor", "Go Go Go", "trio", "pixel-screen", "pixel", "gamer", "primary", "stone grey, torch orange, pink and teal",
     "A short pixel-art dungeon corridor lit by two torches, framed in a rounded pixel panel. Pixel versions of {CARL}, {DONUT} and {MONGO} run left to right in a row. Pixel lettering above reads \"GO GO GO!\""),
    ("trio_bff", "Best Friends Until Floor 18", "trio", "sign", "neon", "dark", "neon", "pink, teal and warm white tubes",
     "A neon sign with the glowing outlines of {CARL}, {DONUT} and {MONGO} side by side. Neon script reads \"BEST FRIENDS FOREVER\" and smaller neon letters below read \"(OR UNTIL FLOOR 18)\"."),
    ("trio_kick_first", "Kick First Crest", "trio", "crest", "ornate", "absurd", "pink-gold", "pink, gold, brown, purple and cream",
     "A coat of arms: the central shield shows a pair of pink heart-print boxer shorts. On the left, {DONUT} stands as a heraldic supporter; on the right, {MONGO} stands rampant. A ribbon below reads \"KICK FIRST\"."),
    ("trio_road_trip", "Next Stop Floor Two", "trio", "poster", "retro-70s", "wholesome", "warm-retro", "orange, teal, mustard and brown",
     "A 1970s road-trip scene in a rounded frame: {CARL} drives a small orange camper van, {DONUT} hangs out the window with her ears flapping, and {MONGO} sits on the roof. Groovy lettering reads \"NEXT STOP: FLOOR 2\"."),
    ("trio_the_crew", "The Crew", "trio", "comic", "comic", "wholesome", "primary", "red, yellow, blue, pink and purple",
     "A comic group shot of five friends posing together: {CARL} in the middle, {DONUT} on his shoulder, {MONGO} at his feet, {KATIA} on the left with her shield up, and {SAMANTHA} tucked under her arm. A comic banner across the top reads \"THE CREW\"."),
    # DUNGEON
    ("dungeon_not_a_chest", "Not A Chest", "dungeon", "mascot", "kawaii", "absurd", "pastel", "pastel brown, gold, pink and lavender",
     "A chibi mimic treasure chest with its lid open, showing rows of tiny sharp teeth, a long pink tongue and big cute eyes, sitting on a little pile of coins. Bubbly lettering below reads \"NOT A CHEST\"."),
    ("dungeon_stairwell", "Stairwell", "dungeon", "sign", "minimal", "gamer", "primary", "bright green, white and black",
     "A green emergency-exit style sign with a white running stick figure and a staircase going down. Bold white lettering reads \"STAIRWELL\" with a white arrow pointing right."),
    ("dungeon_safe_room", "Safe Room", "dungeon", "sign", "neon", "wholesome", "neon", "green, warm white and pink tubes",
     "A neon sign in a rounded frame with a little glowing house icon. Neon block lettering reads \"SAFE ROOM\" and smaller neon script below reads \"NO KILLING INSIDE\"."),
    ("dungeon_goblin_run", "Run", "dungeon", "mascot", "rubber-hose", "absurd", "warm-retro", "cream, green, black and red",
     "A small green goblin in a dented helmet sprints away in panic with bendy noodle legs, sweat drops flying and a dropped club behind him. Bouncy cartoon lettering above reads \"RUN!\""),
    ("dungeon_here_be_monsters", "Here Be Monsters", "dungeon", "badge", "vintage-litho", "dark", "earthy", "parchment tan, brown, red and dark green",
     "A round old treasure-map badge with a compass rose, a winding dotted path and a tiny sea-serpent doodle. Old-style lettering reads \"FLOORS 1-18\" on top and \"HERE BE MONSTERS\" at the bottom."),
    ("dungeon_loot_or_die", "Loot Or Die", "dungeon", "band", "metal", "dark", "dark-red", "black, blood red, gold and bone white",
     "A grinning skull wearing a crown sits on a heap of gold coins and gems, with two crossed swords behind it. Jagged spiky metal lettering reads \"LOOT OR DIE\"."),
    ("dungeon_slime", "Squish", "dungeon", "mascot", "kawaii", "wholesome", "pastel", "mint green, aqua, pink and white",
     "A chibi round green dungeon slime with a happy face, rosy cheeks and a tiny sword stuck in its jelly that it does not seem to mind. Bubbly lettering below reads \"SQUISH\"."),
    ("dungeon_boss_room", "Boss Room Knock First", "dungeon", "sign", "woodcut", "absurd", "mono", "black ink on parchment cream, with a red door knocker",
     "A woodcut of a huge iron-banded dungeon door with a skull-shaped knocker and claw marks. A small wooden plaque nailed on it reads \"BOSS ROOM\" and a smaller line reads \"PLEASE KNOCK\"."),
    ("dungeon_survived", "I Survived So Far", "dungeon", "patches", "folk", "dark", "warm-retro", "olive, mustard, rust and cream",
     "A round embroidered scout patch showing a stone staircase spiralling down into the dark with a tiny torch at the top. Stitched lettering reads \"I SURVIVED THE DUNGEON\" and a small line below reads \"(SO FAR)\"."),
]

assert len(S) == 100, len(S)


def prompt(art, pal, body):
    b = re.sub(r"\{([A-Z]+)\}(\s)", lambda m: CHARS[m.group(1)] + "," + m.group(2), body)
    b = re.sub(r"\{([A-Z]+)\}", lambda m: CHARS[m.group(1)], b)
    b = re.sub(r'(^|\. )([a-z])', lambda m: m.group(1) + m.group(2).upper(), b)
    return (f"A die-cut sticker. {b} Style: {ART[art]}. Palette: {pal}. Centered, filling 85 percent of the frame, "
            f"one thick white die-cut border around the whole graphic. Square 1:1, transparent outside the white border. "
            f"No other text, no watermark.")


def main():
    designs = json.loads((ROOT / "designs.json").read_text(encoding="utf-8"))
    designs = [d for d in designs if d.get("batch") != BATCH]
    for p in range(10):
        lines = [f"# Pack S{p + 1:02d}: fan-art stickers S{p * 10 + 1}-S{p * 10 + 10} (personal use only). "
                 "Character descriptions as in STYLE.md.", ""]
        for i, (slug, title, subj, fmt, art, hum, pal_tag, pal, body) in enumerate(S[p * 10:p * 10 + 10], p * 10 + 1):
            did = f"S{i}_{slug}"
            text = prompt(art, pal, body)
            n = len(text.split())
            if n < 60:
                print("SHORT", did, n)
            lines += [f"### `{did}.png`", "```text", text, "```", ""]
            designs.append({"id": did, "title": title, "track": "personal", "product": "sticker",
                            "style": f"{art.replace('-', ' ').title()} sticker",
                            "hook": f"Die-cut sticker. Personal use only.", "listing": "",
                            "tags": ["fan art", "sticker"],
                            "attrs": {"format": fmt, "art": art, "subject": subj, "humor": hum, "palette": pal_tag},
                            "batch": BATCH})
        (ROOT / f"image-prompts/pack-s{p + 1:02d}.md").write_text("\n".join(lines), encoding="utf-8")
    (ROOT / "designs.json").write_text(json.dumps(designs, indent=1, ensure_ascii=False), encoding="utf-8")
    print("packs written,", len(designs), "designs")


if __name__ == "__main__":
    main()
