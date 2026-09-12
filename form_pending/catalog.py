"""Authored catalogs. Generation recombines these; it does not invent proper nouns from noise."""

TILE = 32
MAP_W = 42
MAP_H = 30
FLOOR_COUNT = 6
ELEVATOR = {"x": 3, "y": 13, "w": 3, "h": 4}

FLOOR_DEFS = [
    {
        "index": 1,
        "name": "Lobby & Intake",
        "short": "INTAKE",
        "accent": (196, 165, 116),
        "carpet": (122, 104, 72),
        "carpet_alt": (110, 93, 64),
        "wall": (217, 203, 176),
        "wall_shadow": (183, 164, 138),
        "trim": (92, 74, 50),
        "corridor": (207, 193, 164),
        "lobby": (196, 184, 158),
        "landmark": "the security desk",
    },
    {
        "index": 2,
        "name": "Records & Archives",
        "short": "RECORDS",
        "accent": (61, 122, 120),
        "carpet": (44, 74, 74),
        "carpet_alt": (38, 64, 64),
        "wall": (197, 212, 210),
        "wall_shadow": (155, 176, 174),
        "trim": (31, 63, 62),
        "corridor": (183, 201, 199),
        "lobby": (174, 194, 192),
        "landmark": "the copy alcove",
    },
    {
        "index": 3,
        "name": "Permits & Windows",
        "short": "PERMITS",
        "accent": (196, 154, 60),
        "carpet": (110, 90, 40),
        "carpet_alt": (97, 79, 34),
        "wall": (230, 215, 168),
        "wall_shadow": (201, 181, 124),
        "trim": (90, 71, 24),
        "corridor": (224, 208, 154),
        "lobby": (214, 198, 140),
        "landmark": "Window 4",
    },
    {
        "index": 4,
        "name": "Procurement & Personnel",
        "short": "PERSONNEL",
        "accent": (176, 92, 104),
        "carpet": (90, 50, 56),
        "carpet_alt": (78, 44, 50),
        "wall": (228, 200, 204),
        "wall_shadow": (197, 163, 168),
        "trim": (90, 44, 52),
        "corridor": (217, 184, 188),
        "lobby": (206, 172, 176),
        "landmark": "the supply cages",
    },
    {
        "index": 5,
        "name": "Compliance & Oversight",
        "short": "COMPLIANCE",
        "accent": (61, 82, 120),
        "carpet": (42, 51, 72),
        "carpet_alt": (36, 44, 62),
        "wall": (197, 205, 224),
        "wall_shadow": (154, 164, 187),
        "trim": (36, 48, 68),
        "corridor": (184, 192, 212),
        "lobby": (172, 180, 200),
        "landmark": "the audit tables",
    },
    {
        "index": 6,
        "name": "Executive & Vault",
        "short": "EXECUTIVE",
        "accent": (138, 106, 60),
        "carpet": (58, 46, 34),
        "carpet_alt": (50, 40, 30),
        "wall": (216, 196, 160),
        "wall_shadow": (184, 158, 118),
        "trim": (58, 42, 24),
        "corridor": (203, 184, 146),
        "lobby": (190, 170, 130),
        "landmark": "the filing vault",
    },
]

HOME_DEPARTMENTS = [
    {"id": "intake", "name": "Public Intake", "floor": 1, "handles": "intake"},
    {"id": "security", "name": "Building Security", "floor": 1, "handles": "verify"},
    {"id": "info", "name": "Public Information", "floor": 1, "handles": "info"},
    {"id": "cashier", "name": "Cashier / Receipts", "floor": 1, "handles": "receipt"},
    {"id": "records", "name": "Records Processing", "floor": 2, "handles": "issue"},
    {"id": "archives", "name": "Archives", "floor": 2, "handles": "prior"},
    {"id": "copy", "name": "Central Copy", "floor": 2, "handles": "copy"},
    {"id": "mail", "name": "Interoffice Mail", "floor": 2, "handles": "mail"},
    {"id": "permits", "name": "Permit Review", "floor": 3, "handles": "permit"},
    {"id": "windows", "name": "Window Services", "floor": 3, "handles": "window"},
    {"id": "amendments", "name": "Amendments", "floor": 3, "handles": "correct"},
    {"id": "licensing", "name": "Licensing", "floor": 3, "handles": "license"},
    {"id": "procurement", "name": "Procurement", "floor": 4, "handles": "supply"},
    {"id": "personnel", "name": "Personnel", "floor": 4, "handles": "personnel"},
    {"id": "interdept", "name": "Interdepartmental Affairs", "floor": 4, "handles": "route"},
    {"id": "supplies", "name": "Office Supplies", "floor": 4, "handles": "supply"},
    {"id": "compliance", "name": "Compliance", "floor": 5, "handles": "stamp"},
    {"id": "oversight", "name": "Oversight", "floor": 5, "handles": "approve"},
    {"id": "special", "name": "Special Processing", "floor": 5, "handles": "special"},
    {"id": "audit", "name": "Internal Audit", "floor": 5, "handles": "audit"},
    {"id": "executive", "name": "Office of the Director", "floor": 6, "handles": "sign"},
    {"id": "legal", "name": "Legal / Notary", "floor": 6, "handles": "notary"},
    {"id": "vault", "name": "Filing Vault", "floor": 6, "handles": "file"},
    {"id": "policy", "name": "Policy Desk", "floor": 6, "handles": "policy"},
]

ROLES = [
    "Clerk",
    "Window Clerk",
    "Records Officer",
    "Specialist",
    "Supervisor",
    "Deputy Supervisor",
    "Intake Officer",
    "Processor",
    "Reviewer",
    "Coordinator",
    "Analyst",
    "Notary",
    "Archivist",
    "Copy Technician",
    "Security Officer",
    "Administrative Assistant",
    "Acting Desk",
    "Floor Monitor",
]

FEMININE_NAMES = [
    "Janet", "Priya", "Elaine", "Ruth", "Keisha", "Mei", "Lydia", "Irene",
    "Sofia", "Amina", "Helen", "Paula", "Yasmin", "Clara", "Doris", "Marta",
    "Nadine", "Hana", "Vera", "Sylvia", "Beatrice", "Ingrid", "Grace", "Faye",
    "Tamara", "Edith", "Rosa", "Anita", "Leah", "Connie", "Patricia", "Mira",
    "Gloria", "Ivy", "June", "Keiko", "Amara", "Lila", "Denise", "Carol",
]
MASCULINE_NAMES = [
    "Harold", "Marcus", "Omar", "Dennis", "Arthur", "Gordon", "Carlos", "Nathan",
    "Walter", "Bruce", "Dmitri", "Glenn", "Floyd", "Ravi", "Kenji", "Peter",
    "Curtis", "Jamal", "Owen", "Luis", "Theo", "Abdul", "Neil", "Victor",
    "Samir", "Colin", "Hugh", "Barry", "Ibrahim", "Frank", "Wayne", "Chester",
    "Stan", "Miles", "Reza", "Tomas", "Felix", "Dwight", "Howard",
]
UNISEX_NAMES = [
    "Alex", "Sam", "Jordan", "Casey", "Riley", "Quinn", "Taylor", "Jamie",
    "Morgan", "Avery", "Noor", "Sable", "Ellis", "Dale", "Robin", "Cameron",
    "Kai", "Remy", "Shawn", "Devon",
]
FIRST_NAMES = FEMININE_NAMES + MASCULINE_NAMES + UNISEX_NAMES

FEM_HAIR = ["bob", "bun", "ponytail", "part", "short", "afro"]
MASC_HAIR = ["short", "slick", "bald", "part", "afro"]
NEUT_HAIR = ["short", "afro", "part", "bob", "slick"]
FEM_ACCESSORIES = ["none", "glasses", "mug", "clipboard", "badge", "pencil"]
MASC_ACCESSORIES = ["none", "glasses", "tie", "mug", "clipboard", "badge", "headphones"]
NEUT_ACCESSORIES = ["none", "glasses", "mug", "clipboard", "badge", "headphones", "pencil"]

LAST_NAMES = [
    "Hargrove", "Pell", "Chaudhary", "Whitlock", "Osborne", "Vega", "Kranz",
    "Mbeki", "Stanton", "Fujimoto", "Dwyer", "Alvarez", "Nash", "Okoye",
    "Bramble", "Singh", "Caldwell", "Nguyen", "Moss", "Petrov", "Hughes",
    "Rahman", "Blair", "Costa", "Yates", "Ibrahim", "McNally", "Park",
    "Gable", "Sorensen", "Duarte", "Keller", "Bello", "Ingram", "Cho",
    "Fitzroy", "Adeyemi", "Lund", "Cobb", "Shah", "Pruitt", "Moreau",
    "Daley", "Kwan", "Bishop", "Okafor", "Reed", "Tanaka", "Hale", "Quincy",
    "Morrow", "Espinoza", "Voss", "Greene", "Patel", "Horne", "Ivers",
    "Lambert", "Nunez", "Crane", "Wojcik", "Bassett", "Orellana", "Phipps",
]

HAIR_STYLES = ["short", "bob", "bun", "slick", "ponytail", "afro", "bald", "part"]
HAIR_COLORS = [
    (26, 20, 16), (59, 36, 20), (106, 58, 24), (196, 164, 108), (74, 48, 48),
    (232, 224, 208), (107, 107, 107), (139, 30, 30), (42, 36, 32), (154, 122, 80),
]
SKIN_TONES = [
    (243, 209, 184), (224, 176, 137), (196, 138, 98), (160, 103, 66),
    (122, 74, 46), (90, 50, 32), (246, 224, 200), (212, 160, 122),
]
SHIRT_COLORS = [
    (232, 228, 216), (207, 214, 224), (216, 200, 160), (106, 122, 138),
    (138, 58, 58), (58, 90, 74), (74, 74, 106), (176, 122, 58),
    (90, 106, 58), (122, 90, 106), (46, 58, 72), (154, 168, 180),
]
ACCESSORIES = ["none", "glasses", "tie", "mug", "clipboard", "badge", "headphones", "pencil"]

STAMP_COLORS = [
    {"id": "blue", "name": "blue validation", "ink": (30, 74, 154)},
    {"id": "red", "name": "red received", "ink": (163, 28, 28)},
    {"id": "green", "name": "green cleared", "ink": (29, 106, 58)},
    {"id": "purple", "name": "purple special", "ink": (90, 42, 122)},
    {"id": "black", "name": "black official", "ink": (26, 26, 26)},
]

PAPER_COLORS = ["buff", "canary", "pink", "white", "goldenrod", "greenbar"]

CATASTROPHES = [
    {
        "id": "nuclear",
        "headline": "UNSCHEDULED THERMAL EVENT",
        "line": "the city is recategorized as a crater",
        "detail": "Municipal Emergency Bulletin 0: a filing omission has been interpreted as consent.",
    },
    {
        "id": "moon",
        "headline": "LUNAR LEASE LAPSED",
        "line": "the moon is repossessed for non-payment of orbital fees",
        "detail": "Gravity will continue on a month-to-month basis until further notice.",
    },
    {
        "id": "tuesday",
        "headline": "TUESDAY REVOKED",
        "line": "Tuesday is stricken from the calendar pending committee review",
        "detail": "Wednesday will now follow Monday. Complaints may be filed on the day formerly known as Tuesday.",
    },
    {
        "id": "temporal",
        "headline": "TEMPORAL COLLAPSE",
        "line": "causal order is placed on administrative hold",
        "detail": "You may already have been late yesterday. Please retain all receipts.",
    },
    {
        "id": "parking",
        "headline": "EMINENT REZONING",
        "line": "your house is rezoned as a municipal parking structure",
        "detail": "Permit stickers will be mailed to the address on file, which is now a ramp.",
    },
    {
        "id": "newts",
        "headline": "SPECIES DISCONTINUED",
        "line": "the speckled desk newt is declared administratively extinct",
        "detail": "A commemorative plaque has been back-ordered from Procurement.",
    },
    {
        "id": "vowels",
        "headline": "VOWEL RATIONING",
        "line": "the letter E is recalled for improper documentation",
        "detail": "All remaining language will proceed on a consonants-only interim basis.",
    },
    {
        "id": "elevator",
        "headline": "VERTICAL SERVICES ENDED",
        "line": "elevators worldwide are reclassified as decorative shafts",
        "detail": "Stairs remain available during posted hours, which have not been posted.",
    },
    {
        "id": "bees",
        "headline": "POLLINATION SUSPENDED",
        "line": "bees are placed on indefinite furlough",
        "detail": "Fruit will be issued as a dried substitute pending agricultural review.",
    },
    {
        "id": "names",
        "headline": "NOMENCLATURE RESET",
        "line": "all personal names revert to assigned case numbers",
        "detail": "You are now Case 000-00. Please answer only when called by number.",
    },
    {
        "id": "ocean",
        "headline": "MARITIME MISFILE",
        "line": "the ocean is transferred to an off-site storage annex",
        "detail": "Coastal cities should expect a dry period while boxes are located.",
    },
    {
        "id": "weekend",
        "headline": "WEEKEND CONSOLIDATION",
        "line": "Saturday and Sunday are merged into a single unpaid working day",
        "detail": "Brunch is reclassified as a meeting. Attendance is mandatory.",
    },
    {
        "id": "coffee",
        "headline": "STIMULANT RECALL",
        "line": "coffee is recalled as an unregistered document additive",
        "detail": "Replacement beverages will be water, pending water's own paperwork.",
    },
    {
        "id": "floor",
        "headline": "STOREY DISCREPANCY",
        "line": "the fourth floor is found never to have been properly adopted",
        "detail": "Personnel assigned to Floor 4 should report to a floor that exists.",
    },
    {
        "id": "sky",
        "headline": "CEILING REASSIGNMENT",
        "line": "the sky is converted to a drop-ceiling inventory item",
        "detail": "Stars will be installed as fluorescent tubes on a rolling schedule.",
    },
    {
        "id": "please",
        "headline": "COURTESY DISCONTINUED",
        "line": "the word please is retired as an unbudgeted courtesy",
        "detail": "Requests will proceed without it. Results will proceed without you.",
    },
    {
        "id": "pencils",
        "headline": "GRAPHITE CONTROL",
        "line": "pencils are reclassified as controlled writing implements",
        "detail": "Pens remain legal. Erasers are evidence.",
    },
    {
        "id": "clocks",
        "headline": "DAYLIGHT SURPLUS",
        "line": "daylight saving time is applied twice in the same morning",
        "detail": "You are now due yesterday. Please initial the gap.",
    },
]

FORM_TITLES = [
    "Routine Interdepartmental Transmittal",
    "Continuity of Ordinary Affairs",
    "Minor Parcel Notification",
    "Standard Civic Acknowledgement",
    "Non-Emergency Filing Cover",
    "Provisional Desk Copy",
    "Annual Nothing-In-Particular Return",
    "Supplemental Ordinary Request",
    "Internal Routing Slip",
    "Certificate of Having Been Here",
    "Low-Priority Existential Cover Sheet",
    "Municipal Continuance Notice",
]

IDLE_LINES = [
    "The copier has a personality, and it is against you.",
    "Someone has circled 'see reverse' on a page with no reverse.",
    "A plant in the corner has been declared a temporary employee.",
    "The clock over the elevator is four minutes fast, except on Thursdays.",
    "There is a form for requesting the correct form. It is out of stock.",
    "A handwritten sign says PLEASE DO NOT ASK ABOUT TUESDAY.",
    "The carpet pattern is designed to hide both stains and hope.",
    "A memo on the wall reminds staff that smiling is optional but filing is not.",
    "The suggestion box has been rerouted to a closed department.",
    "Someone's lunch is in the shared fridge labeled DO NOT EAT — EVIDENCE.",
    "I don't handle visitors. I handle the aftermath of visitors.",
    "If you need a stapler, we loaned ours to a committee.",
    "The windows don't open. That's a policy, not a hinge.",
    "We're expecting a delivery of toner. We have been expecting it since March.",
    "I can only speak to my own stack. I don't look at other stacks.",
]

GREETINGS = [
    "Yes.",
    "Next.",
    "Can I help you, or are you lost?",
    "If this is about the other thing, that's not us.",
    "You're standing in my light.",
    "Badge?",
    "We're short-staffed, which is to say staffed.",
    "Speak toward the counter. I can hear you from here.",
    "If you need a moment, take it somewhere else.",
    "Go ahead. I've already started the next thing.",
    "Name?",
    "Don't sit. This isn't that kind of wait.",
    "Make it the short version.",
    "You're the third one today. That is not a compliment.",
    "I have a stamp and a limited amount of goodwill.",
]

REVISITS = [
    "I already said. Writing it down is your problem.",
    "Still the same desk. Still the same answer.",
    "If it changed, someone would have sent a memo. They haven't.",
    "You again. The facts have not been revised.",
    "I don't do recaps. That's what notebooks are for.",
]

MEMOS = [
    "OUT OF ORDER — this notice constitutes the order.",
    "Meeting moved to a floor that has not been determined.",
    "Do not ask about Tuesday.",
    "All requests in writing. All writing in triplicate. Triplicate is back-ordered.",
    "The suggestion box is for suggestions about the suggestion box only.",
    "Quiet hours: all hours.",
    "If you can read this, you are standing in a fire lane for paper carts.",
    "Please do not feed the copier anything with staples, hope, or both.",
    "Lost & found is on a floor we do not discuss.",
    "Smile optional. Filing mandatory.",
]

DEPT_FLAVOR = {
    "intake": [
        "Intake takes things in. We do not take things through.",
        "If it has a number we don't recognize, it isn't ours yet.",
    ],
    "security": [
        "I can verify that you are in the building. That's the whole service.",
        "The metal detector is decorative. The clipboard is not.",
    ],
    "records": [
        "If it isn't in the cabinet, it is in the other cabinet. Do not ask me which.",
        "We file by color, then by mood, then by the number in the corner.",
    ],
    "archives": [
        "Prior-year copies live in the back. The back is a philosophical concept.",
        "I can pull a box. I cannot pull a box quickly.",
    ],
    "copy": [
        "The machine jams if you look at it with intent.",
        "Warm copies first. That's not a preference. That's a rule.",
    ],
    "compliance": [
        "I stamp what is in front of me. I do not stamp what you meant.",
        "Blue means someone else was here first. That someone else was me.",
    ],
    "vault": [
        "The vault takes complete packets. Incomplete packets take a walk.",
        "We close at five. We mean five.",
    ],
}

GRANT_LINES = {
    "stamp": "Fine. Don't smudge it. The ink is older than the policy.",
    "issue": "Here. That's the only one I can issue without a meeting.",
    "sign": "There. My name is on it. That's as committed as we get.",
    "copy": "It's warm. That's how you know it's official.",
    "correct": "Correct color. Same nonsense. Don't mix them up.",
    "verify": "You're verified as a person who is here. Keep the slip.",
    "notary": "Sealed. If anyone asks, I was at my desk.",
    "approve": "Initialed. I will not initial it again.",
    "prior": "Don't bend it. The archive notices.",
    "file": "Accepted. The bell in the other room is not for you.",
}

STEP_KINDS = [
    "stamp", "issue", "sign", "copy", "correct", "verify", "notary", "approve", "prior",
]

PROVIDER = {
    "file": ("file", ["vault", "windows", "special"]),
    "stamp": ("stamp", ["compliance", "special", "oversight"]),
    "issue": ("issue", ["records", "windows", "permits"]),
    "sign": ("sign", ["executive", "personnel", "oversight"]),
    "copy": ("copy", ["copy", "records", "mail"]),
    "correct": ("correct", ["amendments", "records", "windows"]),
    "verify": ("verify", ["security", "intake", "personnel"]),
    "notary": ("notary", ["legal", "executive", "policy"]),
    "approve": ("approve", ["oversight", "audit", "executive"]),
    "prior": ("prior", ["archives", "records", "vault"]),
}


def make_form_code(rng) -> str:
    kind = rng.int(0, 6)
    if kind == 0:
        return f"P{rng.int(10, 99)}-{rng.int(1, 9)}{rng.pick(list('ABCX'))}"
    if kind == 1:
        return f"{rng.int(10, 99)}-{rng.pick(list('ABCDR'))}"
    if kind == 2:
        return f"{rng.pick(list('WRBN'))}-{rng.int(100, 999)}"
    if kind == 3:
        return f"FORM {rng.int(4, 28)}-{rng.pick(list('ABCX'))}"
    if kind == 4:
        return f"{rng.pick(list('STV'))}{rng.int(1, 9)}/{rng.int(10, 99)}"
    if kind == 5:
        return f"{rng.int(100, 880)}-{rng.pick(['ZX', 'Q', 'H', 'M'])}"
    return f"ANNEX {rng.pick(list('ABCD'))}-{rng.int(1, 12)}"


def make_appearance(rng, presentation="neutral") -> dict:
    if presentation == "feminine":
        hair, acc = FEM_HAIR, FEM_ACCESSORIES
    elif presentation == "masculine":
        hair, acc = MASC_HAIR, MASC_ACCESSORIES
    else:
        hair, acc = NEUT_HAIR, NEUT_ACCESSORIES
    return {
        "presentation": presentation,
        "skin": rng.pick(SKIN_TONES),
        "hair_style": rng.pick(hair),
        "hair_color": rng.pick(HAIR_COLORS),
        "shirt": rng.pick(SHIRT_COLORS),
        "accessory": rng.pick(acc),
    }


def unique_name(rng, used: set):
    """Return (full_name, presentation). Presentation follows the first-name pool."""
    roll = rng.int(0, 9)
    if roll < 4:
        presentation, pool = "feminine", FEMININE_NAMES
    elif roll < 8:
        presentation, pool = "masculine", MASCULINE_NAMES
    else:
        presentation, pool = "neutral", UNISEX_NAMES
    for _ in range(80):
        name = f"{rng.pick(pool)} {rng.pick(LAST_NAMES)}"
        if name not in used:
            used.add(name)
            return name, presentation
    name = f"{rng.pick(pool)} {rng.pick(LAST_NAMES)} {rng.int(2, 9)}"
    used.add(name)
    return name, presentation
