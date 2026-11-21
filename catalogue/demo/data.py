"""Demo catalogue for CourtList Supply, loaded by `python manage.py seed_demo`.

Each item's "slug" is also the filename (without extension) of its photo
in catalogue/demo/images, e.g. "molten-bg5000" -> molten-bg5000.jpeg.
"""

# (name, sort_order): sort_order keeps sizes in a logical order instead of alphabetical
SIZES = [
    ("Size 6", 1),
    ("Size 7", 2),
    ("S", 10),
    ("M", 11),
    ("L", 12),
    ("XL", 13),
    ("XXL", 14),
]

BALL_SIZES = ["Size 6", "Size 7"]
APPAREL_SIZES = ["S", "M", "L", "XL", "XXL"]

# Top-level categories, each with its sub-categories
CATEGORIES = [
    {
        "name": "Game equipment",
        "slug": "game-equipment",
        "description": "Balls, clocks and officiating gear for every game night.",
        "children": [
            {"name": "Balls", "slug": "balls"},
            {"name": "Shot clocks", "slug": "shot-clocks"},
            {"name": "Officiating", "slug": "officiating"},
        ],
    },
    {
        "name": "Court care",
        "slug": "court-care",
        "description": "Everything the floor crew needs to keep the court safe and game-ready.",
        "children": [
            {"name": "Floor and lines", "slug": "floor-and-lines"},
            {"name": "Towels", "slug": "towels"},
        ],
    },
    {
        "name": "Medical",
        "slug": "medical",
        "description": "First aid and recovery gear for the medical staff.",
        "children": [
            {"name": "First aid", "slug": "first-aid"},
            {"name": "Ice and recovery", "slug": "ice-and-recovery"},
        ],
    },
    {
        "name": "Staff apparel",
        "slug": "staff-apparel",
        "description": "Polos and jackets for the whole operations team.",
        "children": [
            {"name": "Polos", "slug": "polos"},
            {"name": "Jackets", "slug": "jackets"},
        ],
    },
]

ITEMS = [
    # Game equipment > Balls
    {
        "slug": "molten-bg5000",
        "name": "Molten BG5000 game ball",
        "category": "balls",
        "brand": "Molten",
        "colour": "orange",
        "sizes": ["Size 7"],
        "price": "129.99",
        "stock": 40,
        "description": "FIBA-approved premium leather game ball with a 12-panel design "
        "for a consistent grip and bounce.",
    },
    {
        "slug": "molten-bg4500",
        "name": "Molten BG4500 training ball",
        "category": "balls",
        "brand": "Molten",
        "colour": "orange",
        "sizes": BALL_SIZES,
        "price": "69.99",
        "stock": 60,
        "description": "Composite leather ball with the same 12-panel feel as the BG5000, "
        "built for daily practice sessions.",
    },
    {
        "slug": "spalding-tf1000",
        "name": "Spalding TF-1000 Legacy ball",
        "category": "balls",
        "brand": "Spalding",
        "colour": "orange",
        "sizes": BALL_SIZES,
        "price": "59.99",
        "stock": 35,
        "description": "Indoor composite ball with deep channels and a soft-touch cover, "
        "a favourite for shootarounds.",
    },
    {
        "slug": "wilson-evo-nxt",
        "name": "Wilson Evo NXT game ball",
        "category": "balls",
        "brand": "Wilson",
        "colour": "orange",
        "sizes": BALL_SIZES,
        "price": "89.99",
        "stock": 25,
        "description": "FIBA-approved game ball with a moisture-wicking cover that keeps "
        "its grip late in the fourth quarter.",
    },
    # Game equipment > Shot clocks
    {
        "slug": "bodet-shot-clock",
        "name": "Bodet 24-second shot clock set",
        "category": "shot-clocks",
        "brand": "Bodet",
        "colour": "black",
        "sizes": [],
        "price": "2490.00",
        "stock": 4,
        "description": "Pair of backboard-mounted 24-second shot clocks with LED digits "
        "and a synchronised horn.",
    },
    {
        "slug": "bodet-game-clock-controller",
        "name": "Bodet game clock controller",
        "category": "shot-clocks",
        "brand": "Bodet",
        "colour": "black",
        "sizes": [],
        "price": "890.00",
        "stock": 6,
        "description": "Scorer's table controller for the game clock, shot clocks and score, "
        "with wired and wireless connection.",
    },
    # Game equipment > Officiating
    {
        "slug": "fox40-classic-whistle",
        "name": "Fox 40 Classic whistle",
        "category": "officiating",
        "brand": "Fox 40",
        "colour": "black",
        "sizes": [],
        "price": "9.90",
        "stock": 200,
        "description": "Pealess whistle with a loud, consistent pitch that cuts through a full "
        "arena. Works even when wet.",
    },
    {
        "slug": "fox40-pearl-whistle",
        "name": "Fox 40 Pearl whistle",
        "category": "officiating",
        "brand": "Fox 40",
        "colour": "white",
        "sizes": [],
        "price": "8.50",
        "stock": 150,
        "description": "Smaller, lighter pealess whistle with a high pitch, popular with "
        "table officials.",
    },
    {
        "slug": "fox40-lanyard",
        "name": "Fox 40 breakaway lanyard",
        "category": "officiating",
        "brand": "Fox 40",
        "colour": "black",
        "sizes": [],
        "price": "4.50",
        "stock": 300,
        "description": "Safety lanyard that releases under pressure, sized for Fox 40 whistles.",
    },
    # Court care > Floor and lines
    {
        "slug": "3m-floor-tape",
        "name": "3M floor marking tape",
        "category": "floor-and-lines",
        "brand": "3M",
        "colour": "white",
        "sizes": [],
        "price": "24.90",
        "stock": 80,
        "description": "Vinyl tape for temporary court lines and media-zone markings. "
        "50 mm x 33 m, removes cleanly from sports floors.",
    },
    {
        "slug": "unger-dust-mop",
        "name": "Unger 150 cm dust mop",
        "category": "floor-and-lines",
        "brand": "Unger",
        "colour": "grey",
        "sizes": [],
        "price": "79.00",
        "stock": 20,
        "description": "Wide dust mop that clears the full court quickly before tip-off "
        "and at half-time.",
    },
    {
        "slug": "unger-sweat-mop",
        "name": "Unger courtside sweat mop",
        "category": "floor-and-lines",
        "brand": "Unger",
        "colour": "grey",
        "sizes": [],
        "price": "34.90",
        "stock": 30,
        "description": "Compact microfibre mop for the floor crew to wipe sweat spots "
        "during timeouts.",
    },
    # Court care > Towels
    {
        "slug": "nike-bench-towel",
        "name": "Nike bench towel",
        "category": "towels",
        "brand": "Nike",
        "colour": "white",
        "sizes": [],
        "price": "14.99",
        "stock": 120,
        "description": "Soft cotton towel for the team bench, sized to drape over a chair.",
    },
    {
        "slug": "courtlist-wipe-towels",
        "name": "CourtList Essentials floor towels (10 pack)",
        "category": "towels",
        "brand": "CourtList Essentials",
        "colour": "navy",
        "sizes": [],
        "price": "29.90",
        "stock": 75,
        "description": "Our own microfibre towels for the floor crew: highly absorbent "
        "and quick to dry between timeouts.",
    },
    # Medical > First aid
    {
        "slug": "mueller-first-aid-kit",
        "name": "Mueller sideline first aid kit",
        "category": "first-aid",
        "brand": "Mueller",
        "colour": "black",
        "sizes": [],
        "price": "149.00",
        "stock": 15,
        "description": "Fully stocked sideline kit in a durable carry bag, organised for "
        "fast access during play.",
    },
    {
        "slug": "mueller-athletic-tape",
        "name": "Mueller athletic tape 38 mm (32 rolls)",
        "category": "first-aid",
        "brand": "Mueller",
        "colour": "white",
        "sizes": [],
        "price": "64.00",
        "stock": 40,
        "description": "Rigid zinc-oxide tape for ankle and wrist strapping. Box of 32 rolls.",
    },
    {
        "slug": "kt-tape-pro",
        "name": "KT Tape Pro kinesiology tape",
        "category": "first-aid",
        "brand": "KT Tape",
        "colour": "black",
        "sizes": [],
        "price": "19.99",
        "stock": 60,
        "description": "Synthetic kinesiology tape that stays on through sweat, for muscle "
        "and joint support.",
    },
    # Medical > Ice and recovery
    {
        "slug": "mueller-cold-packs",
        "name": "Mueller instant cold packs (24 pack)",
        "category": "ice-and-recovery",
        "brand": "Mueller",
        "colour": "white",
        "sizes": [],
        "price": "39.90",
        "stock": 50,
        "description": "Single-use cold packs that activate with a squeeze, for the bench "
        "and the medical room.",
    },
    {
        "slug": "hyperice-hypervolt",
        "name": "Hyperice Hypervolt 2 massage gun",
        "category": "ice-and-recovery",
        "brand": "Hyperice",
        "colour": "black",
        "sizes": [],
        "price": "229.00",
        "stock": 10,
        "description": "Percussion massage device with three speeds for warm-ups and recovery.",
    },
    {
        "slug": "hyperice-vyper",
        "name": "Hyperice Vyper vibrating foam roller",
        "category": "ice-and-recovery",
        "brand": "Hyperice",
        "colour": "black",
        "sizes": [],
        "price": "199.00",
        "stock": 8,
        "description": "Vibrating foam roller for pre-game activation and post-game recovery.",
    },
    # Staff apparel > Polos
    {
        "slug": "nike-staff-polo",
        "name": "Nike Dri-FIT staff polo",
        "category": "polos",
        "brand": "Nike",
        "colour": "navy",
        "sizes": APPAREL_SIZES,
        "price": "39.99",
        "stock": 90,
        "description": "Breathable polo for operations staff, comfortable through a long game day.",
    },
    {
        "slug": "adidas-entrada-polo",
        "name": "Adidas Entrada staff polo",
        "category": "polos",
        "brand": "Adidas",
        "colour": "black",
        "sizes": APPAREL_SIZES,
        "price": "29.99",
        "stock": 90,
        "description": "Moisture-absorbing polo with a clean look for event and media staff.",
    },
    # Staff apparel > Jackets
    {
        "slug": "nike-rain-jacket",
        "name": "Nike Academy rain jacket",
        "category": "jackets",
        "brand": "Nike",
        "colour": "black",
        "sizes": APPAREL_SIZES,
        "price": "59.99",
        "stock": 40,
        "description": "Lightweight water-repellent jacket for staff working team arrivals "
        "and outdoor areas.",
    },
    {
        "slug": "under-armour-storm-jacket",
        "name": "Under Armour Storm jacket",
        "category": "jackets",
        "brand": "Under Armour",
        "colour": "grey",
        "sizes": APPAREL_SIZES,
        "price": "89.99",
        "stock": 30,
        "description": "Water-resistant jacket with a brushed lining for cold loading docks "
        "and car parks.",
    },
]
