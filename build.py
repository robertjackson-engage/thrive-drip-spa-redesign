#!/usr/bin/env python3
# THRIVE DRIP SPA — "Hydrate. Energize. Thrive." — static site generator
# IV therapy, NAD+, boosters & shots, mobile IV, BTL body contouring · Houston · Dallas · Fort Worth
import os, time, glob as _glob, re as _re, json as _json
import copy_layer

OUT = os.path.join(os.path.dirname(__file__), "docs")
IMG = "assets/img"
V = str(int(time.time()))
CONTENT = os.path.join(os.path.dirname(__file__), "content")
REPO = "robertjackson-engage/thrive-drip-spa-redesign"
# Public address of the site: canonical tags, social-share images, sitemap and robots.txt use it.
SITE_URL = os.environ.get("SITE_URL", "https://thrivedripspa.com/").rstrip("/") + "/"
# NOINDEX=1 marks a preview copy (the GitHub Pages preview) so Google never indexes it alongside the real site.
NOINDEX = os.environ.get("NOINDEX") == "1"
# Google Tag Manager container from the current thrivedripspa.com, so analytics and ad tracking carry over.
GTM_ID = "GTM-NGLDNLW"

BOOK = "https://book.thrivedripspa.com"
BOOK_NEW = BOOK + "/?path=new"     # skips the booking flow's "first time or current client?" question
MEEVO = "https://na1.meevo.com/customerportal/advanced/ob?tenantId=200296"
# Lounges our booking flow (book.thrivedripspa.com) can book; the rest still go to the Meevo portal.
BOOK_FLOW_LOCS = {"201102", "201104", "201319", "203321", "203322"}
GIFT = "https://na1.meevo.com/EgiftApp/location/search?tenantId=200296"
LOGIN = "https://na1.meevo.com/CustomerPortal/login?tenantId=200296"
PHONE = "844-820-1713"
TEL = "tel:+18448201713"
PHARMACY = "New Solutions Functional Wellness Pharmacy, 1901 Medi Park Dr #120, Amarillo, TX 79106 · 806-353-7712"
DISCLAIMER = ("ThrIVe Drip Spa services are administered by licensed medical professionals after a Good Faith Exam. "
              "Our services are not intended to diagnose, treat, cure or prevent any disease and are not a substitute "
              "for medical care. Individual results vary. For pharmacy-related inquiries only: " + PHARMACY + ".")

PAGES = []          # (filename, title) — for the visual editor's page index


# ============================================================ CMS engine
def _parse_md(path):
    raw = open(path, encoding="utf-8").read()
    meta, body = {}, raw
    m = _re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", raw, _re.S)
    if m:
        for line in m.group(1).split("\n"):
            if ":" in line:
                k, _, v = line.partition(":")
                meta[k.strip()] = v.strip().strip('"').strip("'")
        body = m.group(2)
    return meta, _md_to_html(body.strip())


def _md_to_html(md):
    md = md.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    out, lines, i = [], md.split("\n"), 0
    while i < len(lines):
        ln = lines[i]
        if _re.match(r"^\s*[-*]\s+", ln):
            items = []
            while i < len(lines) and _re.match(r"^\s*[-*]\s+", lines[i]):
                items.append("<li>" + _inline(_re.sub(r"^\s*[-*]\s+", "", lines[i])) + "</li>"); i += 1
            out.append("<ul>" + "".join(items) + "</ul>"); continue
        if _re.match(r"^\s*\d+[.)]\s+", ln):
            items = []
            while i < len(lines) and _re.match(r"^\s*\d+[.)]\s+", lines[i]):
                items.append("<li>" + _inline(_re.sub(r"^\s*\d+[.)]\s+", "", lines[i])) + "</li>"); i += 1
            out.append("<ol>" + "".join(items) + "</ol>"); continue
        h = _re.match(r"^(#{1,4})\s+(.*)$", ln)
        if h:
            lvl = len(h.group(1)); out.append(f"<h{lvl+1}>{_inline(h.group(2))}</h{lvl+1}>"); i += 1; continue
        if ln.startswith("&gt; "):
            out.append("<blockquote>" + _inline(ln[5:]) + "</blockquote>"); i += 1; continue
        if ln.strip() == "":
            i += 1; continue
        para = [ln]; i += 1
        while i < len(lines) and lines[i].strip() and not _re.match(r"^(#{1,4}\s|\s*[-*]\s|\s*\d+[.)]\s|&gt; )", lines[i]):
            para.append(lines[i]); i += 1
        out.append("<p>" + _inline(" ".join(para)) + "</p>")
    return "\n".join(out)


def _inline(t):
    t = _re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = _re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", t)
    t = _re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    return t


def load_collection(folder, key="date"):
    items = []
    for p in _glob.glob(os.path.join(CONTENT, folder, "*.md")):
        meta, body = _parse_md(p)
        meta["_slug"] = os.path.splitext(os.path.basename(p))[0]
        meta["_body"] = body
        items.append(meta)
    items.sort(key=lambda m: m.get(key, ""), reverse=True)
    return items


def cms_img(path, default="lounge-chairs.webp"):
    p = (path or "").lstrip("/")
    return p or f"{IMG}/{default}"


def cms_link(path):
    p = (path or "#").strip()
    if p.startswith(("http", "#", "mailto:", "tel:")):
        return p
    return p.lstrip("/") or "#"


def fmt_date(d):
    months = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    m = _re.match(r"(\d{4})-(\d{2})-(\d{2})", d or "")
    return f"{months[int(m.group(2))]} {int(m.group(3))}, {m.group(1)}" if m else (d or "")


# ============================================================ data: locations
HRS_STD = [("Mon–Fri", "9am–7pm"), ("Sat–Sun", "10am–6pm")]
LOCATIONS = [
    dict(slug="memorial", label="Memorial", city="Houston", region="Houston Metro",
         addr="1014 Wirt Rd, Ste 210, Houston, TX 77055", phone="(713) 955-3747", tel="7139553747",
         email="memorial@thrivedripspa.com", hours=HRS_STD, ig="thethrivedripspa", meevo="201102",
         maps="https://maps.app.goo.gl/V4M2erARLSVNh77t7", reviews=753, img="front-desk-phone.webp",
         services=["emface", "emsculpt-neo", "emtone"], kicker="Health Innovated",
         blurb="Located in the heart of Memorial, our spa offers a tranquil escape where wellness meets luxury — perfect for rejuvenation after a day in Houston's premier shopping and dining district.",
         intro="Your wellness journey starts here. At ThrIVe Drip Spa in Memorial we offer more than hydration — a science-backed approach to feeling and performing your best, with our full IV menu plus the complete BTL body and face suite: EMFACE, Emsculpt NEO and EMTONE."),
    dict(slug="memorial-green", label="Memorial Green", city="Houston", region="Houston Metro",
         addr="12505 Memorial Drive, Ste 120, Houston, TX 77024", phone="(346) 444-3747", tel="3464443747",
         email="info@thrivedripspa.com", hours=[("Mon–Fri", "9:30am–7pm"), ("Sat–Sun", "9:30am–6:30pm")], ig="thrivedripspa_mg", meevo="202035",
         maps="https://maps.app.goo.gl/cpVtG7PpCzY8ffRu5", reviews=670, img="checkin-signing.webp",
         services=["emface", "emsculpt-neo", "styku", "boosters"], kicker="Advanced Wellness",
         blurb="Nestled in the upscale Memorial Green community, this location provides elite IV therapy in a refined setting designed for health-conscious professionals and residents.",
         intro="Wellness should be efficient, effective and tailored to you. Memorial Green pairs our 12 signature drips with EMFACE and Emsculpt NEO — plus Styku 3D body scanning, so you can measure your progress in under 60 seconds."),
    dict(slug="the-heights", label="The Heights", city="Houston", region="Houston Metro",
         addr="2799 Katy Freeway, Suite 210, Houston, TX 77007", phone="(346) 320-3114", tel="3463203114",
         email="admin_heightstx@gmail.com", hours=[("Mon–Fri", "9am–7pm"), ("Sat–Sun", "9:30am–6:30pm")], ig="thrivedripspa_heights", meevo="203017",
         maps="https://maps.app.goo.gl/U9PZZxCRz2nN57xz5", reviews=430, img="lounge-interior.webp",
         services=[], kicker="Drip, Relax, Restore",
         blurb="In the artistic and eclectic Houston Heights, this spa blends modern wellness with the neighborhood's trendy charm — perfect for those embracing an active, balanced lifestyle.",
         intro="Every body is different. That's why all of our drips can be customized to your needs — sit back in the Heights lounge while our registered nurses build the drip that fits your day."),
    dict(slug="west-university", label="West University", city="Houston", region="Houston Metro",
         addr="3277 Southwest Freeway, Houston, TX 77027", phone="(713) 955-3797", tel="7139553797",
         email="westu@thrivedripspa.com", hours=HRS_STD, ig="thethrivedripspa", meevo="201104",
         maps="https://maps.app.goo.gl/NhNB9wnE21tMpC1h9", reviews=684, img="neon-best-life.webp",
         services=["emface", "emsculpt-neo", "nad", "boosters"], kicker="Wellness Without Limits",
         blurb="Serving the vibrant West U community, our spa is a wellness retreat for busy professionals, students and families seeking premium hydration and recovery.",
         intro="Customized IV therapy, experienced wellness professionals, and a relaxing modern lounge under the neon — West University is where Houston comes to sculpt, lift and recover, with EMFACE, Emsculpt NEO and the full NAD+ menu on site."),
    dict(slug="vintage-park", label="Vintage Park", city="Houston", region="Houston Metro",
         addr="10300 Louetta Rd, Ste 114, Houston, TX 77070", phone="(346) 712-3747", tel="3467123747",
         email="admin_vphtx@thrivedripspa.com", hours=HRS_STD, ig="thrivedripspa_vintagepark", meevo="203330",
         maps="https://maps.app.goo.gl/aABXn6RZds9U1FUS9", reviews=216, img="loc-vintage-park.jpg",
         services=["emsculpt-neo", "boosters"], kicker="Inner Revitalization",
         blurb="Situated in the lively Vintage Park shopping district, this location is a wellness oasis for those looking to refresh and recharge after a day of shopping, dining or fitness.",
         intro="Shape and restore at Vintage Park: signature drips and boosters, plus Emsculpt NEO body contouring to burn fat and build muscle in 30-minute sessions."),
    dict(slug="katy", label="Katy", city="Katy", region="Greater Houston",
         addr="6445 FM 1463, Ste 120, Katy, TX 77494", phone="(346) 707-8703", tel="3467078703",
         email="manager_katyhtx@thrivedripspa.com", hours=HRS_STD, ig="thrivedripspa_katy", meevo="203033",
         maps="https://maps.app.goo.gl/PHdDQoVFodb1yiAK7", reviews=235, img="team-front-desk.webp",
         services=["infrared-sauna"], kicker="Vibrance Unlocked",
         blurb="Conveniently located in Katy, our spa caters to the growing community with top-tier IV therapy — helping residents and athletes stay energized and at their best.",
         intro="Relax, restore, rejuvenate. Katy pairs 12 signature IV drips, boosters and vitamin shots, delivered by registered nurses, with an infrared sauna for recovery days — all in a bright, calm space just off FM 1463."),
    dict(slug="the-woodlands", label="The Woodlands", city="The Woodlands", region="Greater Houston",
         addr="9595 Six Pines Dr, Ste 1460, The Woodlands, TX 77380", phone="(281) 343-3747", tel="2813433747",
         email="info@thrivedripspa.com", hours=[("Mon–Sun", "10am–6pm")], ig="thrivedripspa", meevo="201319",
         maps="https://maps.app.goo.gl/eY9qpj22prVBVRZZA", reviews=689, img="loc-woodlands.jpg",
         services=["emsculpt-neo"], kicker="Refresh &amp; Revive",
         blurb="Tucked away in the serene environment of The Woodlands, our spa offers an exclusive wellness experience for locals who prioritize health, beauty and relaxation.",
         intro="Strength revived. The Woodlands pairs the full drip and shot menu with Emsculpt NEO — burn fat and build muscle in 30-minute sessions, then settle into the lounge for your drip."),
    dict(slug="clear-lake", label="Clear Lake", city="Houston", region="Greater Houston",
         addr="3535 Clearlake City Blvd, Ste 700, Houston, TX 77059", phone="(281) 783-4108", tel="2817834108",
         email="admin_clearlaketx@thrivedripspa.com", hours=[("Mon–Fri", "9am–7pm"), ("Sun", "10am–6pm"), ("Sat", "Call for hours")], ig="thrivedripspa_clearlake", meevo="203215",
         maps="https://maps.app.goo.gl/8cscPquQKZmMoHvy7", reviews=352, img="lounge-couple-phones.webp",
         services=["infrared-sauna", "emsculpt-neo", "nad"], kicker="Renew &amp; Revitalize",
         blurb="Positioned near the heart of Clear Lake, this location is perfect for boaters and residents seeking premium hydration and wellness in a serene waterfront community.",
         intro="Real results by the water: signature drips, NAD+ for balance and vitality, Emsculpt NEO body contouring, and an infrared sauna for recovery days."),
    dict(slug="highland-park", label="Highland Park", city="Dallas", region="North Texas",
         addr="5301 W Lovers Ln, Suite 103, Dallas, TX 75209", phone="(214) 214-3747", tel="2142143747",
         email="admin_hpdallas@thrivedripspa.com", hours=HRS_STD, ig="thrivedripspa_highlandpark", meevo="203321",
         maps="https://maps.app.goo.gl/BCoZRjKenycPjTGF7", reviews=218, img="front-desk-welcome.webp",
         services=["emface", "emsculpt-neo", "emtone"], kicker="Luxury Wellness, Dallas",
         blurb="Serving the prestigious Highland Park area, our spa delivers elite IV therapy to those who demand the best in one of Dallas' most luxurious neighborhoods.",
         intro="Premium IV therapy, vitamin infusions and wellness spa services on Lovers Lane — with the complete BTL suite (EMFACE, Emsculpt NEO, EMTONE) to elevate your glow, shape and refresh."),
    dict(slug="fort-worth", label="Fort Worth", city="Fort Worth", region="North Texas",
         addr="2708 S Hulen St, Fort Worth, TX 76109", phone="(682) 747-3747", tel="6827473747",
         email="admin_ftw@thrivedripspa.com", hours=HRS_STD, ig="thrivedripspa_ftworth", meevo="203322",
         maps="https://maps.app.goo.gl/iXfUq6jsh2SGkBCR8", reviews=313, img="wall-guests.webp",
         services=["emface", "emsculpt-neo"], kicker="Hydrate, Energize &amp; Restore",
         blurb="Located in the dynamic city of Fort Worth, our spa provides cutting-edge IV therapy to professionals, athletes and visitors looking to optimize their wellness journey.",
         intro="Rehydrate and recharge on Hulen Street with personalized IV drip therapy, vitamin boosters and shots — plus EMFACE and Emsculpt NEO to contour and renew."),
]
LOC_BY = {l["slug"]: l for l in LOCATIONS}
REGIONS = ["Houston Metro", "Greater Houston", "North Texas"]


def meevo(l):
    """Booking link for a lounge: our booking flow with the lounge preselected (?loc=<Meevo id>)
    where it supports that lounge, otherwise the Meevo portal for that location."""
    if l["meevo"] in BOOK_FLOW_LOCS:
        return f"{BOOK}/?loc={l['meevo']}"
    return f"{MEEVO}&locationId={l['meevo']}"


# ============================================================ data: drips
DRIPS = [
    dict(slug="hydrate", name="Hydrate", file="hydrate-drip.html", price=150, member=120, tile="tile-hydrate.webp", imgs=["iv-bag-hang.webp", "lounge-chairs.webp"],
         kicker="Rapid Rehydration", tag="The original drip that started it all — and still stays strong.",
         card="Hydrate with fluids and electrolytes to boost energy, support body function and help you feel your best.",
         ingredients=["1 L IV fluids", "Electrolytes"], addons=["Extra 0.5 L fluids"],
         body="The Hydrate Drip is our foundational IV service — every drip on the menu begins here. Used in medicine for decades to treat dehydration, a liter of IV fluids with electrolytes goes straight to the bloodstream for instant relief when you're depleted from heat, travel, training, illness or one too many.",
         for_=["Brain fog", "Dehydration", "Fatigue", "Lethargy", "Muscle aches", "Weakness"],
         more_h="Instant hydration", more=["Classic IV hydration to reset how you feel", "Add an extra 0.5 L for maximum hydration", "Direct-to-bloodstream fluids and electrolytes", "Instant relief from dehydration symptoms", "Balances the mental, emotional and physical effects of running dry"]),
    dict(slug="myers", name="Myers", file="myers-drip.html", price=190, member=150, tile="tile-myers.webp", imgs=["nurse-mixing.webp", "lounge-two-guests.webp"],
         kicker="Feel Recharged", tag="The classic cocktail — mood, skin, energy and inflammation, all in one bag.",
         card="This nutrient-rich infusion supports energy, skin wellness and recovery — a popular choice for a boost from within.",
         ingredients=["1 L IV fluids", "Electrolytes", "Vitamin C", "Magnesium", "B-Complex", "B12"], addons=["Glutathione", "Zinc"],
         body="Developed by Dr. John Myers, the Myers Drip has been known to enhance mood, improve the appearance of skin, elevate energy and reduce inflammation. Effects can last for weeks — many clients pair it with the Detox Drip or a Total Wellness booster.",
         for_=["Low mood", "Fatigue", "Insomnia", "Migraines", "Muscle pain", "Menstrual cramps"],
         more_h="What's inside, and why", more=["Vitamin C — tissue growth and repair, immune support, collagen", "Magnesium — anti-inflammatory; supports calm, cardiovascular and bone health", "B vitamins — energy, stress resilience and cognition"]),
    dict(slug="detox", name="Detox", file="detox-drip.html", price=190, member=150, tile="tile-detox.webp", imgs=["iv-bags-rack.webp", "lounge-guest-relax.jpg"],
         kicker="The Ultimate Detox", tag="Help your body flush toxins more efficiently.",
         card="Supports natural wellness and helps you feel more grounded, clear and recharged from within.",
         ingredients=["1 L IV fluids", "Electrolytes", "Glutathione"], addons=["Total Wellness", "Zinc", "Vitamin C"],
         body="Stress, diet, alcohol and illness all leave a residue. The Detox Drip leads with glutathione — the body's master antioxidant — to support the liver, neutralize free radicals and leave you feeling clear. Combine with the Myers Drip or a Vitamin C booster for a full reset.",
         for_=["Brain fog", "Fatigue", "Inflammation", "Stress", "A heavy week"],
         more_h="Purify &amp; protect", more=["Glutathione — antioxidant support, free-radical defense, immune function", "Electrolytes to restore balance", "A liver-focused formula for the morning after a heavy week"]),
    dict(slug="party", name="Party", file="party-drip.html", price=190, member=150, tile="tile-party.webp", imgs=["lounge-friends.jpg", "wall-guests.webp"],
         kicker="Rewind Your Hangover", tag="Rehydrate, recharge and feel like yourself again.",
         card="Rehydrate and recharge with fluids and nutrients designed to restore balance after a big night.",
         ingredients=["1 L IV fluids", "Electrolytes", "Toradol (anti-inflammatory)", "Zofran (anti-nausea)"], addons=["Extra 0.5 L fluids", "Pepcid", "Glutathione"],
         body="Hangovers are dehydration plus the byproducts of ethanol — and the ability to bounce back only diminishes with age. The Party Drip pairs a full liter of fluids with anti-inflammatory and anti-nausea medication so you can get on with your day. Before Toradol, make sure you haven't taken any NSAIDs (such as ibuprofen or naproxen) in the 4–6 hours prior and aren't allergic. Feeling extremely nauseous? Ask your nurse about a double dose of Zofran.",
         for_=["Dehydration", "Dizziness", "Headache", "Muscle aches", "Nausea"],
         more_h="Bounce-back infusion", more=["Fluids and electrolytes to rehydrate fast", "Toradol for headache and body aches", "Zofran to settle the stomach — a double dose is available for extreme nausea", "Add Pepcid for acid reflux or glutathione for the liver"]),
    dict(slug="fit", name="Fit", file="fit-drip.html", price=190, member=150, badge="Total Wellness amino blend", tile="tile-fit.webp", imgs=["iv-insert.webp", "lounge-couple-phones.webp"],
         kicker="Fuel Your Performance", tag="Enhanced muscle recovery and deep hydration in one powerful infusion.",
         card="Amino acids and nutrients that replenish vitamins and help you feel strong before or after workouts.",
         ingredients=["1 L IV fluids", "Electrolytes", "Total Wellness blend", "Glutamine", "Ornithine", "Arginine", "Lysine", "Citrulline", "Carnitine"], addons=["CoQ10 shot — sustained energy", "Zinc — helps reduce inflammation"],
         body="Built for pre-endurance and post-workout. Our Total Wellness blend — glutamine, ornithine, arginine, lysine, citrulline and carnitine — supports muscle repair, circulation and energy so you recover faster and feel strong. Stack it with a CoQ10 shot for sustained energy levels and Zinc to help reduce inflammation.",
         for_=["Maximum output", "Metabolism and fat burn", "Faster workout recovery", "Less muscle soreness"],
         more_h="Peak performance", more=["Glutamine &amp; Ornithine — muscle recovery and repair", "Arginine &amp; Citrulline — circulation and blood flow", "Lysine — protein building and tissue repair", "Carnitine — turns fat into fuel for muscle, heart and brain"]),
    dict(slug="slim", name="Slim", file="slim-drip.html", price=190, member=150, tile="tile-slim.webp", imgs=["nurse-prep.webp", "step-3.jpg"],
         kicker="Boost Your Burn", tag="Speed up metabolism with this boost of ingredients.",
         card="Support natural energy and feel refreshed with an infusion that complements your wellness goals and active lifestyle.",
         ingredients=["1 L IV fluids", "Electrolytes", "High-dose Carnitine", "Amino acids", "B12"], addons=["Taurine", "NAD+ shot", "GLP-1 shot"],
         body="Carnitine converts stored fat into energy and lifts mood; amino acids help regulate the hormones that drive metabolism. Pair the Slim Drip with a Taurine booster or an NAD+ shot for an extra metabolism boost — or with our weight-loss program — to keep momentum going.",
         for_=["Burn more fat", "Boost metabolism", "Grow and repair tissue", "Better workout performance", "More energy"],
         more_h="Ignite your energy", more=["Carnitine — fat to energy, brighter mood", "Amino acids — hormone regulation and tissue repair", "Electrolytes — balance and hydration"]),
    dict(slug="libido", name="Libido", file="libido-drip.html", price=190, member=150, tile="tile-libido.webp", imgs=["lounge-couple.webp", "iv-hand-detail.webp"],
         kicker="Sexual Wellness Reimagined", tag="Heightened energy, mood and endurance — for men and women.",
         card="Support vitality and energy with a formula that helps you feel more connected, confident and in tune with your body.",
         ingredients=["1 L IV fluids", "Electrolytes", "L-Arginine", "B12"], addons=["Magnesium", "B-Complex", "Zinc"],
         body="A natural alternative to pharmaceuticals. L-Arginine promotes vasodilation and blood flow while B12 lifts energy and mood — a formula designed for both men and women. Add Magnesium to help with hormone regulation and stress reduction.",
         for_=["Boost energy", "Heighten mood", "Improve performance and pleasure", "Increase endurance", "Shorten recovery"],
         more_h="Ignite your passion", more=["B12 — energy and mood", "L-Arginine — circulation and blood flow", "Electrolytes — stamina and balance"]),
    dict(slug="beauty", name="Beauty", file="beauty-drip.html", price=190, member=150, tile="tile-beauty.webp", imgs=["lounge-selfie.jpg", "wall-friends.webp"],
         kicker="Ageless Radiance", tag="Glow from the inside out. Refresh, renew, radiate.",
         card="Glow from within with nutrients that support skin hydration, inner balance and a radiant, refreshed feeling.",
         ingredients=["1 L IV fluids", "Electrolytes", "Vitamin C", "High-dose Glutathione"], addons=["Zinc", "Biotin", "Proline"],
         body="Skin, hair and nails are built from the inside. Vitamin C drives collagen while glutathione brightens and protects — the combination behind our most-booked drip for events and weddings. Add biotin and proline for hair and nails.",
         for_=["Dehydration", "Dull or dry skin", "Fine lines and wrinkles", "Low energy"],
         more_h="Radiant renewal", more=["Vitamin C — collagen synthesis and a brighter complexion", "Glutathione — the antioxidant behind the glow", "Electrolytes — hydration where skin needs it"]),
    dict(slug="migraine", name="Migraine", file="migraine-drip.html", price=190, member=150, tile="tile-migraine.webp", imgs=["lounge-tv.webp", "nurse-iv-lounge.jpg"],
         kicker="Targeted Relief", tag="Relax with the ingredients needed to curb a nauseating migraine.",
         card="A soothing blend that supports relaxation and comfort when a migraine has you off balance.",
         ingredients=["1 L IV fluids", "Electrolytes", "Magnesium", "Reglan", "Toradol"], addons=["Benadryl (free)", "B-Complex"],
         body="Magnesium calms inflammation and headache, Reglan settles the nausea of an acute migraine, and Toradol delivers fast NSAID pain relief — before Toradol, make sure you haven't taken any NSAIDs (such as ibuprofen or naproxen) in the 4–6 hours prior and aren't allergic. Benadryl can be added at no cost: either bring a driver, or wait 45 minutes after your IV and drive yourself home. Zofran can substitute for Reglan.",
         for_=["Migraine and headache", "Anxiety", "Dehydration", "Muscle tightness", "Nausea and vomiting"],
         more_h="Calm &amp; comfort", more=["Magnesium — inflammation, headaches, PMS and anxiety", "Reglan — nausea in acute migraine", "Toradol — fast-acting pain relief"]),
    dict(slug="high-c", name="High C", file="high-c-drip.html", price=230, member=200, tile="tile-high-c.webp", imgs=["iv-bags.webp", "iv-start-lounge.webp"],
         kicker="High C Recharge", tag="Our max dose of vitamin C to help boost the immune system.",
         card="Our max dose of Vitamin C to support immunity, hydration and a refreshed, ready-to-go feeling.",
         ingredients=["1 L IV fluids", "Electrolytes", "10 g Vitamin C"], addons=["Zinc", "Glutathione"],
         body="Ten grams of vitamin C, straight to the bloodstream — a dose no tablet can match. It fuels white blood cells, drives collagen for healing and delivers powerful antioxidant support. Pair with zinc or glutathione when you feel something coming on.",
         for_=["Enhanced immune response", "Increased energy", "Accelerated healing", "Antioxidant support", "Overall wellness"],
         more_h="IV vs. oral vitamin C", more=["Boosts iron absorption", "Enhances brain function", "Improves collagen synthesis", "Increases antioxidant levels", "Supports cartilage, bones and teeth"]),
    dict(slug="nad", name="NAD+", file="nad.html", price=None, member=None, tile="tile-nad.webp", imgs=["iv-bags-2.webp", "nurse-lounge-walk.webp"],
         kicker="Cellular Renewal", tag="Mental focus, inner vitality, healthy aging and whole-body cellular renewal.",
         card="Support focus, energy and clarity with NAD+, a coenzyme that helps recharge the body and sharpen the mind.",
         ingredients=["1 L IV fluids", "Electrolytes", "NAD+"], addons=[],
         body="Nicotinamide adenine dinucleotide is the coenzyme every cell uses to make energy. Levels fall with age and stress; an NAD+ infusion restores them directly. Clients report improved energy, sharper focus and a foundation for healthy aging. Infusions run longer than a standard drip — plan for up to two hours.",
         for_=["Energy levels", "Mental clarity and focus", "Healthy aging", "Foundational, whole-body wellness"],
         more_h="Your boost for balance", more=["Enhances focus, vitality and balance", "Direct-to-bloodstream absorption", "Supports healthy aging at the cellular level"]),
    dict(slug="immuno", name="Immuno", file="immuno-drip.html", price=310, member=250, tile="tile-immuno.webp", imgs=["step-2.jpg", "lounge-two-friends.webp"],
         kicker="Shield Your Health", tag="Our strongest immune formula — our max dose of vitamin C, plus zinc and glutathione, in one bag.",
         card="Our max dose of Vitamin C, plus Zinc and Glutathione, to boost immunity and promote strength, balance and resilience.",
         ingredients=["1 L IV fluids", "Electrolytes", "Max-dose Vitamin C", "High-dose Glutathione", "Zinc"], addons=["NAD+ shot"],
         body="Feel better faster. Our max dose of vitamin C fuels the immune response, glutathione protects cells, and zinc shortens colds and speeds healing. It's the drip our nurses reach for during back-to-school season, travel weeks and flu season.",
         for_=["Fatigue", "Frequent sickness", "Inflammation", "Stress", "A weakened immune system"],
         more_h="Feel better faster", more=["Vitamin C — immune response and healing", "Glutathione — cellular protection", "Zinc — shorter colds, faster wound healing"]),
]
DRIP_BY = {d["slug"]: d for d in DRIPS}

BOOSTERS = [
    ("Zofran", "$25", "Reduces nausea and vomiting — motion sickness, migraines, hangovers."),
    ("Vitamin C", "$25", "Antioxidant support for immunity, skin and collagen."),
    ("Anti-Acid", "$25", "Reduces stomach acid — heartburn, reflux, ulcers."),
    ("Magnesium", "$25", "Nerve and muscle function, relaxation, migraines, sleep."),
    ("Toradol", "$25", "Fast anti-inflammatory for pain, fever, migraines and post-workout aches."),
    ("Zinc", "$25", "Immune support, wound healing, skin and inflammation."),
    ("Reglan", "$25", "Reflux, nausea, vomiting and bloating."),
    ("B12", "$25", "Energy, metabolism, mental clarity and red blood cells."),
    ("Benadryl", "$25", "Antihistamine for allergies, hay fever and cold symptoms."),
    ("Proline", "$40", "Amino acid for collagen, joints and gut health."),
    ("ALA (Alpha Lipoic Acid)", "from $25", "Antioxidant for detox and energy."),
    ("Taurine", "$40", "Athletic performance, fat burn and inflammation."),
    ("Glutathione", "$40", "Brightens skin, supports liver detox and immunity."),
    ("Arginine", "$40", "Circulation, oxygen flow, heart health and recovery."),
    ("Carnitine", "$40", "Fat metabolism, energy and performance."),
    ("B-Complex", "$40", "Energy, metabolism, cognition and stress."),
    ("Biotin", "$40", "Hair, skin, nails and metabolism (10 mg)."),
    ("Total Wellness", "$70", "Amino-acid blend for energy, immunity and muscle."),
    ("High-C", "$80", "High-dose vitamin C."),
    ("NAD+", "from $125", "Energy, clarity, vitality and healthy aging."),
    ("Immuno", "$160 · $130 member", "Vitamin C + Zinc + Glutathione blend."),
]
SHOTS = [
    ("Toradol", "$25", "Anti-inflammatory and pain relief; reduces fever."),
    ("Zofran", "$25", "Anti-nausea, anti-vomiting."),
    ("B12", "$25", "Methylcobalamin for energy, clarity and healthy nerves."),
    ("Fit Shot", "$40", "Six-plus amino acids for endurance, repair and blood flow."),
    ("Vitamin D3", "$40", "Bones, immunity, brain and cardiovascular support."),
    ("Lipo B", "$40", "B-complex + B12 for fat burning, energy and clarity."),
    ("Lipo C", "$40", "Carnitine + B-complex to burn stored fat and lift energy."),
    ("Biotin", "$40", "Hair, skin, nails and metabolism."),
    ("CoQ10", "$40", "Heart health, blood-sugar regulation and less muscle fatigue."),
    ("Tri-Immuno", "$70", "Immunity, detox and free-radical defense."),
    ("NAD+", "$50 · 50 mg / $75 · 75 mg / $100 · 100 mg", "Cellular energy, DNA repair, anti-aging and cognition."),
]

MEMBERSHIPS = [
    ("Select", "$95", "/mo", "$140 monthly credit to spend on any service — more value than your membership fee, every month.", False),
    ("Premium", "$165", "/mo", "$260 monthly credit — your standard glow-up, fully covered, on any services you choose.", True),
    ("Luxe", "$285", "/mo", "$490 monthly credit — the full monthly reset, spent however you like.", False),
]
MEMBER_FAMILY = [("Family Premium", "$129", "/mo", "1 Premium IV and 1 Wellness Booster each month."),
                 ("Family Luxe", "$229", "/mo", "2 Premium IVs and 1 Wellness Booster each month.")]
MEMBER_STUDENT = [("Student Premium", "$105", "/mo", "Same included services as Premium, with a valid student ID."),
                  ("Student Luxe", "$180", "/mo", "Same included services as Luxe, with a valid student ID.")]
MEMBER_NAD = [("NAD+ Premium", "$350", "/mo", "500 mg of NAD+ every month."),
              ("NAD+ Luxe", "$700", "/mo", "1,000 mg of NAD+ every month."),
              ("NAD+ Platinum", "$999", "/mo", "1,500 mg of NAD+ every month.")]

# services used in nav / cards
SERVICES = [
    ("NAD+ Therapy", "nad.html", "Cellular energy, focus and healthy aging", "nurse-lounge-walk.webp"),
    ("Boosters", "boosters.html", "Add vitamins and medications to any drip", "boosters.webp"),
    ("Vitamin Shots", "shots.html", "In and out in 15 minutes, from $25", "shots.webp"),
    ("Mobile IV", "mobile-iv.html", "Concierge drips at home, hotel, office or event", "mobile-van-team.webp"),
    ("Weight Loss", "weight-loss.html", "Clinically proven weight-loss injections", "glp-1.webp"),
    ("EMFACE", "emface.html", "Needle-free facial lifting and toning", "emface.webp"),
    ("Emsculpt NEO", "emsculpt-neo.html", "Burn fat and build muscle in 30 minutes", "emsculpt-neo-session.jpg"),
    ("EMTONE", "emtone.html", "Cellulite reduction and skin tightening", "emtone-device.webp"),
    ("Infrared Sauna", "infrared-sauna.html", "Detox sweat at a lower temperature", "infrared-sauna.webp"),
]
SERVICE_BY = {s[1].replace(".html", ""): s for s in SERVICES}


# ============================================================ brand + chrome
DROP_SVG = '<svg viewBox="0 0 100 130" aria-hidden="true"><path d="M50 0C50 0 0 62 0 88a50 50 0 0 0 100 0C100 62 50 0 50 0z" fill="currentColor"/></svg>'


def brand_logo(footer=False):
    src = f"{IMG}/logo-white.webp" if footer else f"{IMG}/logo-color.webp"
    return f'<img class="brand__logo" src="{src}" alt="ThrIVe Drip Spa">'


NAV_DRIPS = [(d["name"] + " Drip" if d["slug"] != "nad" else "NAD+ Drip", d["file"], d["kicker"] + (f' · ${d["price"]}' if d["price"] else "")) for d in DRIPS]
NAV_SERVICES = [(s[0], s[1], s[2]) for s in SERVICES]

MENU = [
    ("Home", "index.html"),
    ("Book Now", "book.html"),
    ("IV Drip Menu", "iv-therapy.html"),
    ("NAD+", "nad.html"),
    ("Boosters & Shots", "boosters.html"),
    ("Mobile IV", "mobile-iv.html"),
    ("Body & Face", "body-contouring.html"),
    ("Weight Loss", "weight-loss.html"),
    ("Memberships", "memberships.html"),
    ("Packages", "packages.html"),
    ("Promotions", "promotions.html"),
    ("Locations", "locations.html"),
    ("About", "about.html"),
    ("Blog", "blog.html"),
    ("FAQ", "faq.html"),
    ("Franchise", "franchise.html"),
]


def head(title, desc, canonical_img=None, path="", extra=""):
    url = SITE_URL + ("" if path in ("", "index.html") else path)
    robots = '<meta name="robots" content="noindex">\n' if NOINDEX else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
{robots}<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{SITE_URL}{IMG}/{canonical_img or 'nurse-iv-lounge.jpg'}">
<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);}})(window,document,'script','dataLayer','{GTM_ID}');</script>
{extra}<meta name="theme-color" content="#053948">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700&family=Figtree:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">
<link rel="preload" href="assets/fonts/Grotters.ttf" as="font" type="font/ttf" crossorigin>
<link rel="icon" type="image/png" href="{IMG}/drop-mark.png">
<link rel="apple-touch-icon" href="{IMG}/drop-mark.png">
<link rel="stylesheet" href="assets/css/main.css?v={V}">
<script>(function(){{try{{
  if(sessionStorage.getItem("tds-intro"))document.documentElement.classList.add("no-preloader");
  if(sessionStorage.getItem("tds-util"))document.documentElement.classList.add("no-util");
  var v=localStorage.getItem("tds-view");
  document.documentElement.setAttribute("data-view", v==="member"?"member":"guest");
}}catch(e){{}}}})();</script>
</head>
<body>
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={GTM_ID}" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<div class="preloader" aria-hidden="true">
  <img class="preloader__logo" src="{IMG}/logo-color.webp" alt="">
  <div class="preloader__drop">{DROP_SVG}</div>
  <div class="preloader__bar"><i></i></div>
</div>
"""


def _drop_list(items, wide=False, head_label=None, all_link=None):
    out = f'<div class="nav-drop{" nav-drop--wide" if wide else ""}">'
    if head_label:
        out += f'<div class="nav-drop__head">{head_label}</div>'
    for l, h, sub in items:
        out += f'<a href="{h}">{DROP_SVG_SM}<span>{l}<small>{sub}</small></span></a>'
    if all_link:
        out += f'<div class="nav-drop__all"><a href="{all_link[1]}">{all_link[0]} →</a></div>'
    return out + "</div>"


DROP_SVG_SM = '<svg viewBox="0 0 100 130" aria-hidden="true" style="width:9px;height:12px;flex:0 0 auto;color:var(--teal)"><path d="M50 0C50 0 0 62 0 88a50 50 0 0 0 100 0C100 62 50 0 50 0z" fill="currentColor"/></svg>'


def header_html(active=""):
    def nav_item(label, href, items, wide=False, head_label=None, all_link=None, group_by=None):
        act = " is-active" if active == href or any(active == h for _, h, _ in items) else ""
        if group_by:
            drop = '<div class="nav-drop nav-drop--wide">'
            for reg in REGIONS:
                drop += f'<div class="nav-drop__head" style="grid-column:auto">{reg}</div>' if False else ""
            for reg in REGIONS:
                drop += f'<div><div class="nav-drop__head">{reg}</div>' + "".join(
                    f'<a href="{l["slug"]}.html">{DROP_SVG_SM}<span>{l["label"]}<small>{l["city"]}</small></span></a>' for l in LOCATIONS if l["region"] == reg) + "</div>"
            drop += f'<div class="nav-drop__all"><a href="{all_link[1]}">{all_link[0]} →</a></div></div>'
        else:
            drop = _drop_list(items, wide, head_label, all_link)
        return f'<div class="nav-item{act}"><a href="{href}">{label}</a>{drop}</div>'
    links = (
        nav_item("IV Drips", "iv-therapy.html", NAV_DRIPS, wide=True, head_label="12 signature drips", all_link=("Full drip menu, boosters &amp; shots", "iv-therapy.html"))
        + nav_item("Services", "body-contouring.html", NAV_SERVICES, wide=True, head_label="Wellness · Body · Face", all_link=("All services", "body-contouring.html"))
        + nav_item("Locations", "locations.html", [], group_by=True, all_link=("All 10 locations + mobile", "locations.html"))
        + f'<a href="memberships.html"{" class=is-active" if active == "memberships.html" else ""}>Memberships</a>'
        + f'<a href="packages.html"{" class=is-active" if active == "packages.html" else ""}>Packages</a>'
    )
    menu_links = "".join(
        (f'<a href="{h}" target="_blank" rel="noopener"><span class="idx">{i:02d}</span>{l}</a>' if h.startswith("http")
         else f'<a href="{h}"><span class="idx">{i:02d}</span>{l}</a>')
        for i, (l, h) in enumerate(MENU, 1))
    locs = "".join(f'<a href="{l["slug"]}.html">{l["label"]}</a>' for l in LOCATIONS)
    return f"""
<div class="util-bar">
  <span class="util-bar__promo">New client? <a href="book.html">25% off your first IV drip →</a></span>
  <span class="util-bar__promo" style="opacity:.8">Now offering weight-loss therapy · <a href="weight-loss.html">telehealth consults</a></span>
</div>
<header class="site-header">
  <div class="site-header__inner">
    <a class="brand" href="index.html" aria-label="ThrIVe Drip Spa — home">{brand_logo()}</a>
    <nav class="nav-desktop" aria-label="Primary">{links}</nav>
    <div class="header-cta">
      <div class="view-toggle" role="group" aria-label="View site as">
        <button type="button" data-view-set="guest">New Here</button>
        <button type="button" data-view-set="member">Member</button>
      </div>
      <a class="header-phone" href="{TEL}">{PHONE}</a>
      <a class="btn btn--solid btn--sm" href="book.html">Book Now <span class="arr">→</span></a>
      <button class="menu-toggle" aria-expanded="false" aria-label="Open menu">
        <span>Menu</span><span class="menu-toggle__icon"><i></i><i></i></span>
      </button>
    </div>
  </div>
</header>
<div class="menu-overlay" role="dialog" aria-label="Site menu">
  <div class="menu-overlay__grid">
    <nav class="menu-list" aria-label="All pages">{menu_links}</nav>
    <aside class="menu-side">
      <div class="menu-side__pass">
        <p>Feel better in about <span class="brush">an hour.</span></p>
        <a class="btn btn--solid btn--sm" href="book.html">Book a Drip <span class="arr">→</span></a>
      </div>
      <div class="menu-side__group">
        <h6>Locations</h6>
        {locs}
      </div>
    </aside>
    <aside class="menu-side">
      <div class="menu-side__group">
        <h6>Quick links</h6>
        <a href="{TEL}">Call {PHONE}</a>
        <a href="{GIFT}" target="_blank" rel="noopener">eGift Cards</a>
        <a href="{LOGIN}" target="_blank" rel="noopener">Member Login</a>
        <a href="gfe-process.html">Good Faith Exam</a>
        <a href="careers.html">Careers</a>
        <a href="events.html">Events</a>
        <a href="contact.html">Contact</a>
      </div>
      <div class="menu-side__group">
        <h6>Follow</h6>
        <a href="https://www.instagram.com/thrivedripspa/" target="_blank" rel="noopener">Instagram</a>
        <a href="https://www.facebook.com/thrivedripspa" target="_blank" rel="noopener">Facebook</a>
      </div>
    </aside>
  </div>
</div>
<main id="mainContent">
"""


def footer_html():
    loc_links = "".join(f'<a href="{l["slug"]}.html">{l["label"]}</a>' for l in LOCATIONS)
    return f"""
</main>
<div class="sticky-cta">
  <a class="btn btn--solid" href="book.html">Book Now</a>
  <a class="btn" href="{TEL}">Call Us</a>
</div>
<footer class="site-footer">
  <div class="wrap">
    <div class="site-footer__top">
      <div class="site-footer__brand">
        <a class="brand brand--footer" href="index.html">{brand_logo(footer=True)}</a>
        <p>ThrIVe Drip Spa is an IV vitamin infusion therapy and lifestyle wellness spa — founded in Houston as the first IV therapy drip spa in Texas, with franchised locations across Texas and the U.S. We modernize traditional medical treatments with a fresh, innovative approach to wellness.</p>
        <div class="socials">
          <a href="https://www.instagram.com/thrivedripspa/" aria-label="Instagram" target="_blank" rel="noopener">IG</a>
          <a href="https://www.facebook.com/thrivedripspa" aria-label="Facebook" target="_blank" rel="noopener">FB</a>
        </div>
      </div>
      <div>
        <h5>Locations</h5>
        <div class="site-footer__links">{loc_links}<a href="mobile-iv.html">Mobile IV</a></div>
      </div>
      <div>
        <h5>Services</h5>
        <div class="site-footer__links">
          <a href="iv-therapy.html">IV Drip Menu</a>
          <a href="nad.html">NAD+ Therapy</a>
          <a href="boosters.html">Boosters</a>
          <a href="shots.html">Vitamin Shots</a>
          <a href="body-contouring.html">Body &amp; Face</a>
          <a href="weight-loss.html">Weight Loss</a>
          <a href="infrared-sauna.html">Infrared Sauna</a>
        </div>
      </div>
      <div>
        <h5>ThrIVe</h5>
        <div class="site-footer__links">
          <a href="memberships.html">Memberships</a>
          <a href="packages.html">Packages</a>
          <a href="promotions.html">Promotions</a>
          <a href="about.html">About</a>
          <a href="gfe-process.html">Good Faith Exam</a>
          <a href="faq.html">FAQ</a>
          <a href="blog.html">Blog</a>
          <a href="events.html">Events</a>
          <a href="careers.html">Careers</a>
          <a href="franchise.html">Franchise</a>
        </div>
      </div>
      <div class="site-footer__contact">
        <h5>Book &amp; Connect</h5>
        <a class="tel" href="{TEL}">{PHONE}</a>
        <a href="book.html">Book online — under a minute</a>
        <a href="{GIFT}" target="_blank" rel="noopener">Send an eGift card</a>
        <a href="{LOGIN}" target="_blank" rel="noopener">Member login</a>
        <a href="contact.html">Contact us</a>
        <form class="news-form" data-demo>
          <input type="email" placeholder="Join our newsletter" aria-label="Email address" required>
          <button type="submit">Join</button>
        </form>
      </div>
    </div>
  </div>
  <div class="site-footer__mega" aria-hidden="true">Thrive</div>
  <div class="wrap">
    <p class="site-footer__disclaimer">{DISCLAIMER}</p>
    <div class="site-footer__bottom">
      <span>© 2026 ThrIVe Drip Spa · I Thrive Drip Holdings, LLC · Houston · Dallas · Fort Worth</span>
      <div class="legal">
        <a href="https://www.legitscript.com/websites/?checker_keywords=thrivedripspa.com" target="_blank" rel="noopener">LegitScript certified</a>
        <a href="privacy.html">Privacy</a>
        <a href="terms.html">Terms</a>
        <a href="contact.html">Contact</a>
      </div>
    </div>
  </div>
</footer>
<script src="assets/js/main.js?v={V}"></script>
<script src="assets/js/chat-config.js?v={V}"></script>
<script src="assets/js/chat.js?v={V}" defer></script>
</body>
</html>
"""


# ============================================================ section helpers
def _btn(a):
    label, href, solid = a[0], a[1], a[2]
    extra = (" " + a[3]) if len(a) > 3 else ""
    cls = ("btn btn--solid" if solid else "btn") + extra
    tgt = ' target="_blank" rel="noopener"' if href.startswith("http") else ""
    return f'<a class="{cls}" href="{href}"{tgt}>{label} <span class="arr">→</span></a>'


def hero(kicker, lines, sub="", img=None, video=None, poster=None, crumb=None, actions=None, meta=None, page=False, badge=None, alt=""):
    lns = "".join(f'<span class="ln"><span style="transition-delay:{0.1+i*0.08:.2f}s">{ln}</span></span>' for i, ln in enumerate(lines))
    media = (f'<video src="{video}" poster="{poster or ""}" autoplay muted loop playsinline></video>' if video
             else (f'<img src="{img}" alt="{alt}" fetchpriority="high">' if img else ""))
    acts = ('<div class="hero__actions">' + "".join(_btn(a) for a in actions) + "</div>") if actions else ""
    crumb_html = f'<div class="hero__crumb"><a href="index.html">Home</a> &nbsp;/&nbsp; {crumb}</div>' if crumb else ""
    meta_html = ('<div class="hero__meta">' + "".join(f"<span>{m}</span>" for m in meta) + "</div>") if meta else ""
    sub_html = f'<p class="hero__sub">{sub}</p>' if sub else ""
    badge_html = f'<div class="hero__badge"><i></i>{badge}</div>' if badge else ""
    return f"""
<section class="hero{' hero--page' if page else ''}">
  <div class="hero__drop-bg" aria-hidden="true"></div>
  <div class="hero__grid">
    <div class="hero__inner">
      {crumb_html}
      <p class="hero__kicker">{kicker}</p>
      <h1 class="hero__title">{lns}</h1>
      {sub_html}{acts}{meta_html}
    </div>
    <div class="hero__media">{media}{badge_html}</div>
  </div>
</section>
"""


def hero_photo(kicker, lines, sub="", img=None, crumb=None, actions=None, meta=None, alt=""):
    lns = "".join(f'<span class="ln"><span style="transition-delay:{0.1+i*0.08:.2f}s">{ln}</span></span>' for i, ln in enumerate(lines))
    acts = ('<div class="hero__actions">' + "".join(_btn(a) for a in actions) + "</div>") if actions else ""
    crumb_html = f'<div class="hero__crumb"><a href="index.html">Home</a> &nbsp;/&nbsp; {crumb}</div>' if crumb else ""
    meta_html = ('<div class="hero__meta">' + "".join(f"<span>{m}</span>" for m in meta) + "</div>") if meta else ""
    sub_html = f'<p class="hero__sub">{sub}</p>' if sub else ""
    return f"""
<section class="hero hero--photo">
  <div class="hero__bg"><img src="{img}" alt="{alt}" fetchpriority="high"></div>
  <div class="hero__inner">
    {crumb_html}
    <p class="hero__kicker">{kicker}</p>
    <h1 class="hero__title">{lns}</h1>
    {sub_html}{acts}{meta_html}
  </div>
</section>
"""


def marquee(words, deep=False):
    seg = "".join(f"<span>{w} <i></i></span>" for w in words)
    return f'\n<div class="marquee{" marquee--deep" if deep else ""}" aria-hidden="true"><div class="marquee__track">{seg}</div><div class="marquee__track">{seg}</div></div>\n'


def stats_band(items, cls=""):
    cells = "".join(f"""
      <div class="stat"><div class="stat__num"><span data-count="{n}">0</span><span class="sfx">{s}</span></div>
      <div class="stat__label">{l}</div></div>""" for n, s, l in items)
    return f'\n<section class="section--flush {cls}"><div class="stats"><div class="wrap" style="padding:0"><div class="stats__grid">{cells}</div></div></div></section>\n'


def split(eyebrow, num, title, paras, img, alt, rev=False, cta=None, tag=None, cls="", wide=False, drop=False, extra=""):
    body = "".join(f'<p class="body-copy">{p}</p>' for p in paras)
    cta_html = ""
    if cta:
        cta_html = '<div class="split__cta">' + "".join(
            (_btn(c) if len(c) > 2 else f'<a class="inline-link" href="{c[1]}">{c[0]} →</a>') for c in (cta if isinstance(cta, list) else [cta])) + "</div>"
    tag_html = f'<span class="tag">{tag}</span>' if tag else ""
    mcls = "split__media" + (" split__media--wide" if wide else "") + (" split__media--drop" if drop else "")
    return f"""
<section class="section {cls}">
  <div class="wrap"><div class="split{' split--rev' if rev else ''}">
    <div class="{mcls} reveal-img"><img src="{img}" alt="{alt}" loading="lazy">{tag_html}</div>
    <div class="split__body">
      <p class="eyebrow"><span class="num">{num}</span> {eyebrow}</p>
      <h2 class="h-display">{title}</h2>
      <div class="reveal">{body}{extra}{cta_html}</div>
    </div>
  </div></div>
</section>
"""


def cta_band(title_html, text, img="neon-best-life.webp", primary=("Book Your Drip", "book.html"), secondary=("Find a Location", "locations.html")):
    sec = _btn((secondary[0], secondary[1], False)) if secondary else ""
    return f"""
<section class="cta-band">
  <div class="cta-band__media"><img src="{IMG}/{img}" alt="" loading="lazy"></div>
  <div class="wrap">
    <h2 class="reveal">{title_html}</h2><p class="reveal">{text}</p>
    <div class="hero__actions reveal">{_btn((primary[0], primary[1], True))}{sec}</div>
  </div>
</section>
"""


def accordion(items, open_first=True):
    out = '<div class="acc reveal">'
    for i, (q, a) in enumerate(items):
        op = open_first and i == 0
        a_html = a if a.strip().startswith("<") else f"<p>{a}</p>"
        out += (f'<div class="acc__item{" is-open" if op else ""}"><button class="acc__head" aria-expanded="{str(op).lower()}"><h3>{q}</h3><span class="acc__icon"></span></button>'
                f'<div class="acc__body"{" style=max-height:2000px" if op else ""}><div class="acc__body-inner">{a_html}</div></div></div>')
    return out + "</div>"


def cards_head(num, eyebrow, title, link=None, lede=None):
    l = f'<a class="inline-link reveal" href="{link[1]}">{link[0]} →</a>' if link else ""
    ld = f'<p class="lede reveal">{lede}</p>' if lede else ""
    return f'<div class="cards-head"><div><p class="eyebrow"><span class="num">{num}</span> {eyebrow}</p><h2 class="h-display reveal">{title}</h2>{ld}</div>{l}</div>'


def card(label, href, im, sub=None, num=None, wide=False, below=None):
    n = f'<span class="card__num">{num}</span>' if num else ""
    b = f'<div class="card__below"><p>{below}</p></div>' if below else ""
    tgt = ' target="_blank" rel="noopener"' if href.startswith("http") else ""
    return (f'<a class="card" href="{href}"{tgt}><div class="card__media{" card__media--wide" if wide else ""}"><img src="{im if im.startswith(("http","assets","../")) else IMG + "/" + im}" alt="{label}" loading="lazy">{n}'
            f'<div class="card__label"><h3>{label}</h3><span class="go">{sub or "Explore"} →</span></div></div>{b}</a>')


def rows(items, hrefs=None):
    out = '<div class="rows reveal">'
    for i, (t, d) in enumerate(items, 1):
        tag = "a" if hrefs else "div"
        href = f' href="{hrefs[i-1]}"' if hrefs else ""
        out += (f'<{tag} class="row-item"{href}><span class="row-item__idx">{i:02d}</span><span class="row-item__title">{t}</span>'
                f'<span class="row-item__desc">{d}</span><span class="row-item__arrow">→</span></{tag}>')
    return out + "</div>"


def pillars(items, cols=4, icons=False):
    cls = "pillars" + ({2: " pillars--2", 3: " pillars--3"}.get(cols, ""))
    out = f'<div class="{cls}" data-stagger>'
    for i, it in enumerate(items, 1):
        n, d = it[0], it[1]
        link = f'<a class="inline-link" href="{it[2]}">Learn more →</a>' if len(it) > 2 and it[2] else ""
        out += f'<div class="pillar"><span class="pillar__num">{i:02d}</span><h3>{n}</h3><p>{d}</p>{link}</div>'
    return out + "</div>"


def price_table(items, head=("Service", "Price")):
    out = f'<table class="ptable reveal"><thead><tr><th>{head[0]}</th><th></th><th style="text-align:right">{head[1]}</th></tr></thead><tbody>'
    for n, p, d in items:
        out += f'<tr><td>{n}</td><td><small style="margin:0">{d}</small></td><td>{p}</td></tr>'
    return out + "</tbody></table>"


def drip_grid(limit=None, hrefs=True):
    out = '<div class="drip-grid" data-stagger>'
    for i, d in enumerate(DRIPS[:limit] if limit else DRIPS, 1):
        price = f'<span class="drip__price">{"$" + str(d["price"]) if d["price"] else "Ask a consultant"}</span>'
        out += (f'<a class="drip" href="{d["file"]}"><div class="drip__tile"><img src="{IMG}/{d["tile"]}" alt="" loading="lazy"></div>'
                f'<div class="drip__photo"><img src="{IMG}/{d["imgs"][0]}" alt="" loading="lazy"></div>'
                f'<span class="drip__idx">{i:02d}</span>{price}<h3>{d["name"]}</h3><p>{d["card"]}</p><span class="go">View drip →</span></a>')
    return out + "</div>"


def membership_block(num="04", cls="section--ice"):
    cards = ""
    for n, p, per, d, feat in MEMBERSHIPS:
        tag = '<span class="price-card__tag">Most popular</span>' if feat else ""
        cards += (f'<div class="price-card{" price-card--feat" if feat else ""}">{tag}<h3>{n}</h3><div class="price-card__amt">{p}<span>{per}</span></div><p>{d}</p>'
                  f'<ul><li>Member pricing on every drip</li><li>Birthday drip on us</li><li>Priority booking &amp; promos</li><li>Month-to-month basis</li></ul>'
                  f'{_btn(("Join " + n, "book.html", feat))}</div>')
    return f"""
<section class="section {cls}"><div class="wrap">
  {cards_head(num, "Memberships", 'More value <span class="brush">every month</span>', ("Compare all plans", "memberships.html"), "Each month your membership loads a service credit worth more than what you pay — and it works on any service: drips, shots, boosters, NAD+ and BTL treatments.")}
  <div class="price-grid" data-stagger>{cards}</div>
  <p class="form-note reveal" style="text-align:center;margin:22px auto 0">Family, student and NAD+ memberships too — see <a href="memberships.html" style="color:var(--teal-deep);text-decoration:underline">all memberships</a>. All memberships run on a month-to-month basis.</p>
</div></section>
"""


def location_picker(num="06", cls=""):
    cards = "".join(card(l["label"], f'{l["slug"]}.html', l["img"], sub=l["city"], num=f"{i:02d}") for i, l in enumerate(LOCATIONS, 1))
    return f"""
<section class="section {cls}"><div class="wrap">
  {cards_head(num, "Visit us", 'Ten lounges. <span class="brush">One drip.</span>', ("All locations + mobile", "locations.html"), "Founded in Houston as the first IV therapy drip spa in Texas — now across Greater Houston, Dallas and Fort Worth, plus mobile service to your door.")}
  <div class="card-grid card-grid--4" data-stagger>{cards}</div>
</div></section>
"""


def form_section(sec_id, num, eyebrow, title_html, text, btn="Send Request", cls="section--ice", interests=None, extra_fields="", note=None):
    interests = interests or ["IV Drip Therapy", "NAD+", "Boosters or Shots", "Mobile / Concierge IV", "Body Contouring (Emsculpt NEO, EMFACE, EMTONE)", "Weight Loss", "Memberships", "Something else"]
    fields = [("text", "name", "Full name"), ("email", "email", "Email address"), ("tel", "phone", "Phone")]
    f_html = "".join(f'<div class="field{" field--full" if n == "name" else ""}"><input type="{t}" name="{n}" id="{sec_id}-{n}" placeholder=" " required><label for="{sec_id}-{n}">{l}</label></div>' for t, n, l in fields)
    locs = "".join(f"<option>{l['label']}</option>" for l in LOCATIONS) + "<option>Mobile / Concierge</option>"
    opts = "".join(f"<option>{o}</option>" for o in interests)
    return f"""
<section class="section {cls}" id="{sec_id}">
  <div class="wrap"><div class="intro-grid">
    <div>
      <p class="eyebrow"><span class="num">{num}</span> {eyebrow}</p>
      <h2 class="h-display reveal">{title_html}</h2>
      <p class="lede reveal" style="margin-top:24px">{text}</p>
    </div>
    <div class="intro-grid__right reveal"><form class="form-grid form-card" data-demo>{f_html}
      <div class="field"><select name="location" id="{sec_id}-loc" aria-label="Preferred location"><option value="">&nbsp;</option>{locs}</select><label for="{sec_id}-loc">Preferred location</label></div>
      <div class="field"><select name="interest" id="{sec_id}-int" aria-label="What are you interested in?"><option value="">&nbsp;</option>{opts}</select><label for="{sec_id}-int">I'm interested in</label></div>
      {extra_fields}
      <div class="field field--full"><textarea name="message" id="{sec_id}-msg" rows="3" placeholder=" "></textarea><label for="{sec_id}-msg">Message (optional)</label></div>
      <button class="btn btn--solid field--full" type="submit">{btn} <span class="arr">→</span></button>
    </form><p class="form-note">{note or "We'll reply by text or email within one business day. By submitting you agree to receive messages from ThrIVe Drip Spa; reply STOP to opt out."}</p></div>
  </div></div>
</section>
"""


def page(filename, title, desc, active, body, manifest=True, og=None, schema=None):
    PAGES.append((filename, title))
    extra = f'<script type="application/ld+json">{_json.dumps(schema, ensure_ascii=False)}</script>\n' if schema else ""
    html = copy_layer.compose(filename, head(title, desc, og, filename, extra), header_html(active), footer_html(), body, manifest=manifest)
    with open(os.path.join(OUT, filename), "w") as f:
        f.write(html)
    print("built", filename)


def page_sub(filename, title, desc, body, og=None):
    PAGES.append((filename, title))
    html = copy_layer.compose(filename, head(title, desc, og, filename), header_html("blog.html"), footer_html(), body, manifest=False)
    html = _re.sub(r'(href|src)="/(?!/)', r'\1="../', html)
    html = _re.sub(r'(href|src)="assets/', r'\1="../assets/', html)
    html = _re.sub(r'(href)="([a-z0-9-]+\.html)(#[^"]*)?"', r'\1="../\2\3"', html)
    os.makedirs(os.path.join(OUT, "blog"), exist_ok=True)
    with open(os.path.join(OUT, filename), "w") as f:
        f.write(html)
    print("built", filename)


# CMS content
POSTS = load_collection("blog")
PROMOS = load_collection("promotions", key="ends")
EVENTS = load_collection("events")

member_strip = f"""
<div class="member-strip only-member"><div class="wrap">
  <span class="hello">Welcome back</span>
  <a href="book.html">Book with member pricing</a>
  <a href="{LOGIN}" target="_blank" rel="noopener">Member portal</a>
  <a href="packages.html">Member-only packages</a>
  <a href="promotions.html">This month's promos</a>
  <a href="{GIFT}" target="_blank" rel="noopener">eGift cards</a>
</div></div>
"""

HOW_FAQ = [
    ("What is IV vitamin therapy?", "IV vitamin therapy delivers fluids and essential nutrients directly into the bloodstream for maximum absorption. Up to 85% of a vitamin pill can be lost to digestion; an IV delivers close to 100%. It helps combat dehydration, boost energy, support immunity and enhance overall wellness."),
    ("What is the Drip Lounge experience like?", "Relaxing. You'll settle into a reclining lounge chair while a registered nurse places your IV and builds your drip. Complimentary beverages, protein bars and cozy blankets are part of the visit. Timing varies by drip and by guest; NAD+ runs longer."),
    ("Are the treatments safe?", "Every drip is administered by experienced registered nurses following a Good Faith Exam with a licensed provider. Our spa consultants walk you through the menu and help you choose. We're LegitScript certified."),
    ("What can it help with?", "Dehydration, fatigue, immune support, hangovers, migraine relief, athletic recovery, skin and beauty goals, and more. If you're not sure which drip fits, our nurses will build one for you."),
    ("How fast does it work?", "Fluids and nutrients reach the bloodstream immediately. Many clients feel the difference before they leave the chair; the effects of a Myers or Beauty drip can last for weeks."),
]

# ============================================================ HOME
home_body = hero(
    "Houston · Dallas · Fort Worth · Mobile",
    ["Hydrate.", "Energize.", '<span class="brush">Thrive.</span>'],
    "Your destination for IV therapy, vitamin infusions and wellness spa services. Twelve signature drips, NAD+, boosters and shots — built by registered nurses, in a lounge that feels like a spa. Feel better in about an hour.",
    img=f"{IMG}/nurse-iv-lounge.jpg", alt="A ThrIVe nurse placing an IV in the drip lounge",
    actions=[("Book Your Drip", "book.html", True), ("See the Drip Menu", "iv-therapy.html", False)],
    meta=["Registered nurses", "Customizable drips", "10 lounges + mobile", "No card to book"],
    badge="Drips from $150 · members from $120",
) + member_strip + marquee(["Hydrate", "Myers", "Detox", "Party", "Fit", "Slim", "Libido", "Beauty", "Migraine", "High C", "NAD+", "Immuno"]) + f"""
<section class="section">
  <div class="wrap"><div class="intro-grid">
    <div><p class="eyebrow"><span class="num">01</span> The first IV drip spa in Texas</p>
      <h2 class="h-display reveal">Health, <span class="brush">innovated.</span></h2></div>
    <div class="intro-grid__right">
      <p class="lede reveal">ThrIVe Drip Spa was founded in Houston as the first IV therapy drip spa in Texas. We took treatments that have lived in hospitals for decades — a liter of fluids, vitamins straight to the bloodstream — and moved them into a lounge with reclining chairs, blankets and a nurse who knows your name.</p>
      <p class="body-copy reveal">Led by MIT graduate Dr. Eugene Lou, our drips are formulated by physicians and pharmacists and administered by registered nurses after a Good Faith Exam. Rehydrate, restore and recharge — then get on with your day.</p>
      <div class="reveal"><a class="inline-link" href="about.html">Our story →</a></div>
    </div>
  </div></div>
</section>
<section class="section section--ice section--tight"><div class="wrap">
  {cards_head("02", "12 signature drips", 'Pick your <span class="brush">drip</span>', ("Full menu, boosters &amp; shots", "iv-therapy.html"), "Every drip starts with a liter of fluids and electrolytes. Add boosters, stack a shot, or let our nurses build a custom formula so you look, feel and perform better.")}
  {drip_grid()}
  <p class="form-note reveal" style="text-align:center;margin:22px auto 0">Walk-in prices shown. Members pay $120–$250. Drip times vary by formula and by guest; boosters and shots take just minutes.</p>
</div></section>
""" + stats_band([(12, "", "Signature drips"), (10, "+", "Lounges across Texas"), (100, "%", "Absorption, straight to the bloodstream"), (4500, "+", "Google reviews")]) + f"""
<section class="section"><div class="wrap">
  {cards_head("03", "How it works", 'Three steps to <span class="brush">better</span>', ("Read about the Good Faith Exam", "gfe-process.html"))}
  <div class="steps" data-stagger>
    <div class="step"><div class="step__media"><img src="{IMG}/step-1.webp" alt="Spa consultant reviewing options on a tablet with a client" loading="lazy"></div><div class="step__body"><span class="step__num">01</span><h3>Consultation</h3><p>Book online in under a minute — no card, no account. A licensed provider completes a quick Good Faith Exam and our consultants help you pick from the 12 signature drips.</p></div></div>
    <div class="step"><div class="step__media"><img src="{IMG}/step-2.jpg" alt="A nurse holding a prepared IV bag" loading="lazy"></div><div class="step__body"><span class="step__num">02</span><h3>Customization</h3><p>We tailor your drip with boosters for whatever the week threw at you — fatigue, headaches, muscle recovery, skin, immunity — or build a fully custom formula.</p></div></div>
    <div class="step"><div class="step__media"><img src="{IMG}/step-3.jpg" alt="A guest relaxing in a lounge chair during her drip" loading="lazy"></div><div class="step__body"><span class="step__num">03</span><h3>Administration</h3><p>Recline, pick a drink and a blanket, and let a registered nurse take it from there. 100% absorption, and you walk out feeling like yourself again.</p></div></div>
  </div>
</div></section>
""" + split(
    "Most loved", "04", 'The treatments Texas <span class="brush">keeps booking</span>',
    ["<strong>NAD+</strong> for focus, energy and healthy aging. <strong>Weight-loss injections</strong> with telehealth consults. <strong>Emsculpt NEO, EMFACE and EMTONE</strong> to sculpt, lift and smooth with zero downtime. An <strong>infrared sauna</strong> for recovery days at our Clear Lake and Katy lounges. And <strong>mobile IV</strong> that brings our menu to your home, hotel, office or event.",
     "Everything is delivered by licensed medical professionals in a setting that feels like a spa — because consistency is the secret, and consistency should be a pleasure."],
    f"{IMG}/emsculpt-neo-session.jpg", "An Emsculpt NEO session at ThrIVe", rev=True, tag="Body · Face · Wellness",
    cta=[("NAD+ Therapy", "nad.html", False), ("Body &amp; Face", "body-contouring.html", False), ("Weight Loss", "weight-loss.html", False)], cls="section--ice"
) + membership_block("05", cls="") + f"""
<section class="section section--deep"><div class="wrap">
  <div class="intro-grid">
    <div><p class="eyebrow"><span class="num">06</span> From the founder</p>
      <h2 class="h-display reveal">Stay optimized to look, feel and <span class="brush">perform</span></h2></div>
    <div class="intro-grid__right">
      <p class="lede reveal">"ThrIVe is a preventative-health-oriented wellness center designed to help people mitigate the risks of stress from work and their environment — and allow oneself to stay optimized to look, feel and perform better every day."</p>
      <p class="body-copy reveal">— Dr. Eugene Lou, MD · CEO &amp; founder. MIT graduate, orthopedic surgeon for more than 20 years, published at the Whitehead Institute alongside three Nobel laureates.</p>
      <div class="reveal"><a class="inline-link" href="about.html">Meet the team →</a></div>
    </div>
  </div>
</div></section>
<section class="section"><div class="wrap">
  {cards_head("07", "Happy customers", 'Where wellness meets <span class="brush">happiness</span>')}
  <div class="t-slider reveal">
    <div class="t-slider__track">
      <div class="t-slide"><figure class="quote-band"><div class="stars">★★★★★</div><blockquote>The lounge is gorgeous, the nurses are gentle, and I walked out feeling like a new person. Jasmine is the best.</blockquote><figcaption>Google review · Memorial</figcaption></figure></div>
      <div class="t-slide"><figure class="quote-band"><div class="stars">★★★★★</div><blockquote>I had a hangover, and then I found ThrIVe. The Party Drip fixed me in 40 minutes. Booked again before I left.</blockquote><figcaption>Google review · West University</figcaption></figure></div>
      <div class="t-slide"><figure class="quote-band"><div class="stars">★★★★★</div><blockquote>Stephanie explained every ingredient in my Myers drip and made my first IV completely painless. Beautiful, calm space.</blockquote><figcaption>Google review · The Woodlands</figcaption></figure></div>
      <div class="t-slide"><figure class="quote-band"><div class="stars">★★★★★</div><blockquote>Emsculpt NEO here has been a game changer. Four sessions in and the difference is real — and the staff are so kind.</blockquote><figcaption>Google review · Highland Park</figcaption></figure></div>
    </div>
    <div class="t-slider__nav"><button data-dir="prev" aria-label="Previous">←</button><button data-dir="next" aria-label="Next">→</button></div>
  </div>
  <p class="form-note reveal" style="text-align:center;margin:26px auto 0">4,500+ Google reviews across our ten Texas lounges.</p>
</div></section>
""" + location_picker("08", cls="section--ice") + f"""
<section class="section"><div class="wrap">
  {cards_head("09", "Frequently asked", 'Our expert <span class="brush">advice</span>', ("All FAQs", "faq.html"))}
  {accordion(HOW_FAQ)}
</div></section>
""" + cta_band('Feel better in about <span class="brush">an hour.</span>', "Physician-formulated drips, delivered by licensed nurses. No membership, no card to book — you pay when you're in the chair. New clients save 25% on their first IV.")


# ============================================================ IV THERAPY HUB
def drip_price_table():
    out = '<table class="ptable reveal"><thead><tr><th>Drip</th><th>Includes</th><th style="text-align:right">Walk-in · Member</th></tr></thead><tbody>'
    for d in DRIPS:
        p = f'${d["price"]} · <span style="color:var(--teal-deep)">${d["member"]}</span>' if d["price"] else "Ask a consultant"
        out += f'<tr><td><a href="{d["file"]}">{d["name"]}</a></td><td><small style="margin:0">{", ".join(d["ingredients"])}</small></td><td>{p}</td></tr>'
    return out + "</tbody></table>"


iv_body = hero(
    "IV Drip Therapy", ["Twelve drips.", 'One <span class="brush">liter</span> of', "better."],
    "ThrIVe Drip Spa offers 12 signature IV drips and a full menu of boosters and shots to keep you healthy and hydrated. With most people facing vitamin deficiencies and dehydration, our nurses are here to help you feel your best.",
    img=f"{IMG}/iv-bags-rack.webp", alt="IV bags hanging in the ThrIVe prep room", crumb="IV Drips", page=True,
    actions=[("Book a Drip", "book.html", True), ("Boosters &amp; Shots", "boosters.html", False)],
    meta=["From $150 · members from $120", "Registered nurses", "1 L fluids minimum"], badge="Drip, relax, restore",
) + f"""
<section class="section section--tight"><div class="wrap">
  {cards_head("01", "The menu", 'Pick your <span class="brush">drip</span>', None, "All of our drips can be customized. Sessions can be combined, or our certified nurses can help you create a personalized formula.")}
  {drip_grid()}
</div></section>
<section class="section section--ice"><div class="wrap">
  {cards_head("02", "Pricing", 'Simple, <span class="brush">honest</span> pricing', ("Become a member", "memberships.html"), "Every drip is a full liter of IV fluids with electrolytes. Members save $30–$60 on every drip and get member pricing on boosters too.")}
  {drip_price_table()}
  <p class="form-note reveal" style="margin-top:20px">Drip times vary by formula and by guest (NAD+ can take up to two hours). Boosters and injections take just minutes. A Good Faith Exam with a licensed provider is required before your first drip.</p>
</div></section>
""" + split(
    "Hydration starts here", "03", 'Did you know? 1 in 3 Americans are <span class="brush">chronically dehydrated</span>',
    ["Water makes up two-thirds of the body. Sports, heat, illness, travel, work, alcohol and caffeine all drain it — and even 2% dehydration affects skin, organs and how you think and feel.",
     "Up to 85% of a vitamin pill can be lost to digestion. Our drips deliver fluids and nutrients directly to the bloodstream for complete rehydration — every drip includes at least one liter of IV fluids."],
    f"{IMG}/iv-hand-detail.webp", "An IV line placed in a guest's hand in the lounge", cta=("How IV therapy works", "faq.html"), tag="100% absorption"
) + f"""
<section class="section section--ice"><div class="wrap">
  {cards_head("04", "Boost your results", 'Boosters &amp; <span class="brush">shots</span>', ("All boosters &amp; shots", "boosters.html"), "Add a booster to any drip from $25, or stack a vitamin shot — in and out in 15 minutes.")}
  <div class="chips reveal">{"".join(f'<span class="chip">{b[0]}</span>' for b in BOOSTERS)}</div>
  <div class="chips reveal" style="margin-top:14px">{"".join(f'<span class="chip chip--teal">{s[0]} shot</span>' for s in SHOTS)}</div>
</div></section>
""" + membership_block("05", cls="") + f"""
<section class="section section--ice"><div class="wrap">
  {cards_head("06", "Hydration solutions", 'Rehydration, <span class="brush">explained</span>', ("All FAQs", "faq.html"))}
  {accordion([
    ("What is dehydration?", "Water makes up about two-thirds of the body. Common causes of dehydration include sports and exercise, heat, illness, travel, work stress, and alcohol and caffeine. Even mild dehydration shows up as fatigue, headache, brain fog and dry skin."),
    ("How does absorption benefit hydration?", "Up to 85% of a vitamin pill can be lost in digestion — only about 15% reaches your bloodstream. An IV delivers fluids and nutrients directly, so you feel the difference quickly."),
    ("What does complete rehydration mean?", "Even 2% dehydration affects skin, organs and cognition. Every ThrIVe drip includes at least one liter of IV fluids with electrolytes, and you can add an extra half liter for maximum hydration."),
    ("Can I get a customized drip?", "Yes. Our signature drips were created by pharmacists and doctors and can be fully customized with boosters — or our nurses can build a formula around your needs."),
    ("How long does it take?", "Drip times vary by formula and by client. NAD+ infusions run up to two hours. Boosters and shots take just minutes."),
  ])}
</div></section>
""" + location_picker("07") + cta_band('Your first drip is <span class="brush">25% off.</span>', "Book in under a minute — no card required, licensed medical staff, ten lounges plus mobile.")


# ============================================================ DRIP DETAIL
def drip_page(d):
    price_html = (f'<div class="price-card__amt">${d["member"]}<span>member</span></div><p><strong>${d["price"]}</strong> walk-in · includes 1 L IV fluids</p>' if d["price"]
                  else '<div class="price-card__amt">Custom<span>dosing</span></div><p>Speak with a spa consultant for NAD+ pricing — shots from $50, memberships from $350/mo, loading doses available.</p>')
    addons = "".join(f'<span class="chip">{a}</span>' for a in d["addons"]) or '<span class="chip">Boosters available</span>'
    others = "".join(card(o["name"] + (" Drip" if o["slug"] != "nad" else ""), o["file"], o["tile"], sub="View drip") for o in DRIPS if o["slug"] != d["slug"])[:0]
    related = [o for o in DRIPS if o["slug"] != d["slug"]][:4]
    rel_html = '<div class="drip-grid" data-stagger>' + "".join(
        f'<a class="drip" href="{o["file"]}"><div class="drip__tile"><img src="{IMG}/{o["tile"]}" alt="" loading="lazy"></div><div class="drip__photo"><img src="{IMG}/{o["imgs"][0]}" alt="" loading="lazy"></div>'
        f'<span class="drip__price">{"$" + str(o["price"]) if o["price"] else "Ask"}</span><h3>{o["name"]}</h3><p>{o["card"]}</p><span class="go">View drip →</span></a>' for o in related) + "</div>"
    name = d["name"] + (" Drip" if d["slug"] != "nad" else "")
    lines = [f'The <span class="brush">{d["name"]}</span>', "Drip."] if d["slug"] != "nad" else ['<span class="brush">NAD+</span> IV', "therapy."]
    return hero(
        d["kicker"], lines, d["tag"],
        img=f"{IMG}/{d['imgs'][0]}", alt=f"{name} at ThrIVe Drip Spa", crumb=f'<a href="iv-therapy.html">IV Drips</a> &nbsp;/&nbsp; {name}', page=True,
        actions=[("Book This Drip", "book.html", True), ("All 12 Drips", "iv-therapy.html", False)],
        meta=[f'${d["price"]} walk-in · ${d["member"]} member' if d["price"] else "Consultant pricing", "Registered nurses" if d["slug"] != "nad" else "Up to 2 hours", "1 L IV fluids"],
        badge=d.get("badge") or ", ".join(d["ingredients"][2:4]) or "Fluids + electrolytes",
    ) + f"""
<section class="section section--tight"><div class="wrap"><div class="intro-grid">
  <div>
    <p class="eyebrow"><span class="num">01</span> What's in the bag</p>
    <h2 class="h-display reveal">{d["more_h"]}</h2>
    <div class="reveal" style="margin-top:24px"><p class="body-copy">{d["body"]}</p></div>
    <div class="reveal" style="margin-top:28px"><p class="eyebrow" style="margin-bottom:12px">Ingredients</p><div class="chips">{"".join(f'<span class="chip chip--teal">{i}</span>' for i in d["ingredients"])}</div></div>
    <div class="reveal" style="margin-top:22px"><p class="eyebrow" style="margin-bottom:12px">Boost your results</p><div class="chips">{addons}</div></div>
  </div>
  <div class="intro-grid__right">
    <div class="price-card reveal"><h3>{name}</h3>{price_html}
      <ul>{"".join(f"<li>{x}</li>" for x in d["more"])}</ul>
      {_btn(("Book Now", "book.html", True))}</div>
  </div>
</div></div></section>
""" + split(
    "Recommended for", "02", f'Good for <span class="brush">{d["for_"][0].lower()}</span>',
    [f"The {name} is a popular choice for clients dealing with: "],
    f"{IMG}/{d['imgs'][1]}", f"{name} — who it's for", rev=True, tag=d["kicker"], cls="section--ice",
    extra='<ul class="checklist checklist--1" style="margin-top:18px">' + "".join(f"<li>{x}</li>" for x in d["for_"]) + "</ul>",
    cta=[("Book This Drip", "book.html", True), ("Ask the concierge", "faq.html")]
) + f"""
<section class="section"><div class="wrap">
  {cards_head("03", "Pair it with", 'Other drips you might <span class="brush">love</span>', ("All 12 drips", "iv-therapy.html"))}
  {rel_html}
</div></section>
""" + membership_block("04") + cta_band(f'Book the <span class="brush">{d["name"]}</span> today.', "Under a minute to book, no card required. Walk in, recline, and feel the difference before you leave.")


# ============================================================ NAD+ (service page, replaces the plain drip page)
nad = DRIP_BY["nad"]
nad_body = hero(
    "NAD+ Therapy", ['<span class="brush">NAD+</span> for energy,', "focus &amp; healthy", "aging."],
    "Nicotinamide adenine dinucleotide is the coenzyme every cell uses to make energy. Levels fall with age and stress — an NAD+ infusion restores them directly. Drips, shots, memberships and multi-day loading doses at every ThrIVe lounge.",
    img=f"{IMG}/{nad['imgs'][1]}", alt="A ThrIVe nurse in the NAD+ lounge", crumb="NAD+", page=True,
    actions=[("Book NAD+", "book.html", True), ("NAD+ Memberships", "memberships.html#nad", False)],
    meta=["Shots from $50", "Drip 4-packs from $1,250", "2-, 3- and 5-day loading doses"], badge="Cellular renewal",
) + split(
    "What is NAD+", "01", 'Your boost for balance and <span class="brush">vitality</span>',
    ["NAD+ IV therapy delivers the coenzyme straight to the bloodstream, where it powers mitochondrial energy production, DNA repair and cellular signaling. Clients report improved energy, sharper mental clarity and focus, and a foundation for healthy aging.",
     "Infusions run longer than a standard drip — plan on up to two hours in the lounge. Prefer something quicker? NAD+ shots take minutes, and an NAD+ booster can be added to any drip."],
    f"{IMG}/{nad['imgs'][0]}", "NAD+ IV bags at ThrIVe", tag="Whole-body renewal",
    extra='<ul class="checklist" style="margin-top:18px"><li>Improved energy levels</li><li>Enhanced mental clarity and focus</li><li>Support for healthy aging</li><li>Foundational, whole-body wellness</li></ul>'
) + f"""
<section class="section section--ice"><div class="wrap">
  {cards_head("02", "NAD+ menu", 'Every way to <span class="brush">get NAD+</span>', ("Packages", "packages.html"), "Speak with a spa consultant for infusion pricing — our team will match dose and cadence to your goals.")}
  <div class="price-grid price-grid--4" data-stagger>
    <div class="price-card"><h3>NAD+ Drip</h3><div class="price-card__amt">Ask<span>consultant</span></div><p>1 L IV fluids, electrolytes and NAD+. Up to two hours in the lounge.</p>{_btn(("Book", "book.html", False))}</div>
    <div class="price-card"><h3>NAD+ Shot</h3><div class="price-card__amt">$50<span>50 mg</span></div><p>$75 for 75 mg · $100 for 100 mg. In and out in minutes.</p>{_btn(("Book", "book.html", False))}</div>
    <div class="price-card"><h3>NAD+ Booster</h3><div class="price-card__amt">$125<span>from</span></div><p>Add NAD+ to any of the 12 signature drips.</p>{_btn(("See drips", "iv-therapy.html", False))}</div>
    <div class="price-card price-card--feat"><span class="price-card__tag">Best value</span><h3>NAD+ Membership</h3><div class="price-card__amt">$350<span>/mo · 500 mg</span></div><p>Luxe 1,000 mg $700/mo · Platinum 1,500 mg $999/mo.</p>{_btn(("Join", "memberships.html#nad", True))}</div>
  </div>
</div></section>
<section class="section"><div class="wrap">
  {cards_head("03", "Packages &amp; loading doses", 'NAD+ <span class="brush">packages</span>', None, "Drip and shot packs for staying consistent — or a concentrated multi-day reset for clients who want to front-load their NAD+.")}
  {price_table([("NAD+ Drip 4-Pack · 250 mg", "$1,250", "Four 250 mg NAD+ drips"), ("NAD+ Drip 4-Pack · 500 mg", "$1,750", "Four 500 mg NAD+ drips"), ("2-Day Loading Dose", "$1,750 member · $2,375 non-member", "2,500 mg over two days"), ("3-Day Loading Dose", "$2,450 member · $3,325 non-member", "3,500 mg over three days"), ("5-Day Loading Dose", "$4,200 member · $5,700 non-member", "6,000 mg over five days"), ("Shot Package · Select", "$300", "Four 100 mg NAD+ shots (400 mg)"), ("Shot Package · Premium", "$375", "Five 100 mg NAD+ shots (500 mg)")], head=("Package", "Price"))}
</div></section>
<section class="section section--ice"><div class="wrap">
  {cards_head("04", "Good to know", 'NAD+ <span class="brush">questions</span>', ("All FAQs", "faq.html"))}
  {accordion([
    ("How does NAD+ work?", "NAD+ is a coenzyme found in every cell. It drives energy production in the mitochondria, supports DNA repair and regulates cellular signaling. Levels naturally decline with age; IV delivery restores them directly."),
    ("What does an NAD+ infusion feel like?", "Most clients feel warmth or mild pressure as the infusion runs; our nurses slow the rate to keep you comfortable. Plan on up to two hours — bring a book or a laptop."),
    ("Who is NAD+ for?", "Clients looking for more energy, sharper focus, help with stress and recovery, and support for healthy aging. Ask our consultants which dose fits your goals."),
    ("Drip, shot or membership?", "Shots are quick and affordable. Drips deliver a larger dose over time. Memberships (500–1,500 mg per month) are the most cost-effective way to stay consistent; loading doses front-load a reset over 2–5 days."),
  ])}
</div></section>
""" + cta_band('Recharge at the <span class="brush">cellular</span> level.', "NAD+ drips, shots and memberships at all ten ThrIVe lounges. Book online or call a spa consultant for pricing.")


# ============================================================ BOOSTERS & SHOTS
boosters_body = hero(
    "Instant Recharge", ["Get the boost", 'you <span class="brush">need.</span>'],
    "Any vitamin or nutrient deficiency can throw the body off. Boosters add targeted vitamins and medications to any drip from $25 — so your infusion does exactly what your week needs.",
    img=f"{IMG}/boosters.webp", alt="An IV bag with a booster being added", crumb="Boosters", page=True,
    actions=[("Book a Drip + Booster", "book.html", True), ("Vitamin Shots", "shots.html", False)],
    meta=["From $25", "Add to any drip", "Member pricing on Immuno"], badge="21 boosters on the menu",
) + f"""
<section class="section section--tight"><div class="wrap">
  {cards_head("01", "Booster menu", 'Thrive with targeted <span class="brush">boosters</span>', ("See the drips", "iv-therapy.html"), "Delivering high-quality vitamins and medications straight into your drip.")}
  {price_table(BOOSTERS, head=("Booster", "Price"))}
  <p class="form-note reveal" style="margin-top:18px">Boosters are added to an IV drip. Want it on its own? See <a href="shots.html" style="color:var(--teal-deep);text-decoration:underline">vitamin shots</a>. With Benadryl, bring a driver or wait 45 minutes after your IV before driving.</p>
</div></section>
""" + split(
    "Popular pairings", "02", 'Drips and boosters that <span class="brush">belong together</span>',
    ["<strong>Myers + Glutathione</strong> for a brighter, calmer week. <strong>Party + Pepcid</strong> when the night got away from you. <strong>Beauty + Biotin + Proline</strong> before the event. <strong>Immuno + NAD+</strong> when you can't afford to get sick.",
     "Not sure? Our spa consultants and nurses build combinations every day — ask at check-in or send us a note."],
    f"{IMG}/nurse-mixing.webp", "A ThrIVe nurse preparing a drip", rev=True, cls="section--ice", tag="Built by nurses", cta=("Book now", "book.html", True)
) + membership_block("03", cls="") + f"""
<section class="section section--ice"><div class="wrap">
  {cards_head("04", "Buy in bulk", 'Shot &amp; booster <span class="brush">packages</span>', ("All packages", "packages.html"))}
  {price_table([("Shots/Boosters — Premium", "Buy 4, get 1 free", "Any $25–$40 shot or booster"), ("Shots/Boosters — Premium+", "Buy 8, get 3 free", "Any $25–$40 shot or booster"), ("B12 Package", "Buy 8, get 2 free", "Weekly energy, sorted"), ("Tri-Immuno Package", "5 for $300", "Immune support through the season"), ("NAD+ Shot Package — Select", "$300", "Four 100 mg NAD+ shots (400 mg)"), ("NAD+ Shot Package — Premium", "$375", "Five 100 mg NAD+ shots (500 mg)")], head=("Package", "Deal"))}
</div></section>
""" + cta_band('Add a little <span class="brush">extra.</span>', "Boosters from $25, added to any drip. Book online or ask your nurse at check-in.")

shots_body = hero(
    "Vital Boost", ["Vitamin shots,", 'done in <span class="brush">15 min.</span>'],
    "Intramuscular vitamin injections are the quickest way to support your routine. B12, Biotin, Lipo B, Lipo C, Vitamin D3, Toradol, NAD+ and more — fast-acting, from $25, no chair time required.",
    img=f"{IMG}/shots.webp", alt="A nurse holding a vitamin injection", crumb="Vitamin Shots", page=True,
    actions=[("Book a Shot", "book.html", True), ("Boosters for Drips", "boosters.html", False)],
    meta=["From $25", "No appointment chair time", "Buy 4, get 1 free"], badge="Fast-acting injections",
) + f"""
<section class="section section--tight"><div class="wrap">
  {cards_head("01", "Shot menu", 'The ultimate <span class="brush">energy boost</span>', ("Packages", "packages.html"))}
  {price_table(SHOTS, head=("Shot", "Price"))}
</div></section>
<section class="section section--ice"><div class="wrap">
  {cards_head("02", "Good to know", 'Shots, <span class="brush">explained</span>', ("All FAQs", "faq.html"))}
  {accordion([
    ("What are vitamin shots, and how do they work?", "They're intramuscular injections of concentrated vitamins and nutrients. Because they bypass digestion, absorption is quick and complete."),
    ("How long does it take to feel the effects?", "Usually within a few hours to a day. B12 and Lipo B tend to give an immediate lift; Biotin builds over weeks."),
    ("How often should I get them?", "B12 and Lipo C can be taken weekly; most others biweekly or monthly. Our nurses will suggest a cadence for your goals — packages make weekly shots easy."),
    ("Are vitamin shots safe?", "Yes — when administered by trained medical professionals using medical-grade vitamins, as ours are. A quick Good Faith Exam is completed before your first visit."),
  ])}
</div></section>
""" + membership_block("03", cls="") + cta_band('Quick. <span class="brush">Effective.</span> Done.', "Walk in for a shot at any lounge, or book online in under a minute.")


# ============================================================ MOBILE IV
mobile_body = hero(
    "Anywhere, Anytime", ["Concierge IV,", 'delivered to <span class="brush">you.</span>'],
    "ThrIVe brings the full IV and shot menu to your home, hotel, office or event across Houston. One of our registered nurses comes to you — for one person or a whole group.",
    img=f"{IMG}/mobile-van-team.webp", alt="The ThrIVe mobile IV van with two team members", crumb="Mobile IV", page=True,
    actions=[("Request Mobile Service", "#mobile-request", True), ("Call " + PHONE, TEL, False)],
    meta=["Home · hotel · office · event", "Groups welcome", "Full drip & shot menu"], badge="Nurse comes to you",
) + split(
    "Hydration & wellness, delivered", "01", 'Don\'t come to us. <span class="brush">We\'ll come to you.</span>',
    ["Our on-call concierge service sends a trained nurse to your door with the complete ThrIVe menu: all 12 signature drips, boosters and vitamin shots. Perfect for bachelorette weekends, corporate wellness days, athletic events, film sets, or a Sunday you'd rather not leave the couch.",
     "Tell us where, when and how many. We'll confirm availability, complete the Good Faith Exam and arrive ready."],
    f"{IMG}/concierge-video.webp", "A ThrIVe nurse holding an IV bag on a mobile visit", tag="Houston service area", cls="section--ice",
    extra='<ul class="checklist" style="margin-top:18px"><li>Full drip and shot menu</li><li>Registered nurses</li><li>Individuals and groups</li><li>Home, hotel, office, event</li></ul>'
) + form_section("mobile-request", "02", "Request mobile IV", 'Book ThrIVe\'s <span class="brush">mobile</span> drips',
                 "Wellness, delivered to you. Share the details and a spa consultant will confirm availability and pricing.", btn="Request Mobile Service", cls="",
                 interests=["Individual drip", "Group / party (2–6)", "Large group / event (7+)", "Corporate wellness day", "Shots only"],
                 extra_fields='<div class="field"><input type="text" name="address" id="mobile-request-addr" placeholder=" "><label for="mobile-request-addr">Address (city is fine)</label></div><div class="field"><input type="text" name="when" id="mobile-request-when" placeholder=" "><label for="mobile-request-when">Date &amp; time</label></div>',
                 note="Mobile service is currently available in the Houston area. Pricing depends on group size and travel; we'll confirm before booking.") \
    + cta_band('Your lounge, <span class="brush">wherever</span> you are.', "Prefer to visit? Ten ThrIVe lounges across Houston, Dallas and Fort Worth.", primary=("Request Mobile IV", "#mobile-request"))


# ============================================================ BODY & FACE (BTL suite hub + pages)
BTL = [
    dict(slug="emface", name="EMFACE", kicker="Radiance Restore", h=["Lift and tone,", '<span class="brush">needle free.</span>'],
         sub="EMFACE combines synchronized radiofrequency and HIFES energy to lift, tone and smooth the forehead, submentum, eyes and cheeks in a 20-minute session. No needles, no downtime.",
         img="emface.webp", img2="emface-2.jpg", tag="20 minutes · zero downtime", series="Series of 4",
         para=["As we age, facial muscle tone decreases, the face sags and expression wrinkles set in. EMFACE treats the cause, not just the surface: radiofrequency heats the dermis to build collagen and elastin while HIFES energy contracts the facial muscles thousands of times per session.",
               "Applicators are placed on the treatment areas; it feels like a warm-stone massage with gentle contractions. You can go straight back to your day."],
         faq=[("What areas can be treated?", "The forehead, submentum (under the chin), eyes and cheeks — for a lifted brow, smoother lines, a more defined jawline and fuller cheeks."),
              ("How is the procedure performed and how does it feel?", "After a facial cleanse you lie down for about 20 minutes while the applicators work. Expect warmth and muscle contractions similar to a hot-stone massage. Resume your routine immediately."),
              ("How does EMFACE compare to a surgical facelift?", "No incisions, no anesthesia, no recovery. Results are natural and subtler than surgery — you look rested, not different."),
              ("How long until I see results?", "Many clients notice visible improvement after one treatment; optimal results come after the full series of four sessions, and collagen keeps building for weeks afterward.")],
         locs=["memorial", "memorial-green", "west-university", "highland-park", "fort-worth"]),
    dict(slug="emsculpt-neo", name="Emsculpt NEO", kicker="Body Refinement", h=["Burn fat.", "Build muscle.", '<span class="brush">At once.</span>'],
         sub="Emsculpt NEO pairs radiofrequency heating with HIFEM contractions in a single 30-minute session — reducing fat and building muscle simultaneously across the abs, glutes, biceps, triceps, thighs, calves and flanks (love handles).",
         img="emsculpt-neo-session.jpg", img2="emsculpt-neo-arm.webp", tag="30 minutes · 6 sessions", series="Series of 6",
         para=["RF energy warms the tissue to break down fat cells while HIFEM energy triggers thousands of supramaximal contractions in the muscle beneath — the equivalent of a workout your body can't do on its own. Two results from one applicator, and it's the most-requested body treatment across our lounges.",
               "Treatment areas: abs, glutes, biceps, triceps, thighs, calves and flanks (love handles). Most clients complete six 30-minute sessions, one every 5–7 days. It feels like an intense workout with a warming sensation — no needles, no anesthesia, no downtime."],
         faq=[("What is Emsculpt NEO and how does it work?", "It combines HIFEM and radiofrequency to build muscle and burn fat simultaneously — the RF heats and reduces fat while the HIFEM contractions strengthen the muscle."),
              ("What areas can be treated?", "Abs, glutes, biceps, triceps, thighs, calves and flanks (love handles)."),
              ("How many sessions?", "Six 30-minute sessions, one every 5–7 days, with results building over the following weeks."),
              ("Is it painful?", "It feels like an intense workout with a warming sensation. No downtime — you can train, work or head to dinner right after."),
              ("Who is the ideal candidate?", "Anyone looking to tone and reduce fat — NEO works across a wide range of body types.")],
         locs=["memorial", "memorial-green", "west-university", "vintage-park", "the-woodlands", "clear-lake", "highland-park", "fort-worth"]),
    dict(slug="emtone", name="EMTONE", kicker="Radiant Skin", h=["Smooth cellulite,", 'tighten <span class="brush">skin.</span>'],
         sub="EMTONE is the first and only device that delivers thermal and mechanical energy at once — treating every major cause of cellulite while tightening and firming skin. About 20 minutes, no downtime.",
         img="emtone-device.webp", img2="emtone-abs.webp", tag="90% client satisfaction", series="Series of 4",
         para=["Radiofrequency heats the tissue to boost collagen and circulation while targeted pressure energy improves elasticity and breaks up the fibrous bands that cause dimpling.",
               "Results are visible after a single session and keep improving for months. Most clients complete four treatments, once or twice a week."],
         faq=[("Who is a good candidate?", "Anyone bothered by cellulite or loose, crepey skin on the thighs, buttocks, abdomen or arms."),
              ("How long does one treatment last?", "About 20 minutes. Most clients do four treatments, scheduled once or twice a week."),
              ("How fast will I see results?", "Often after a single session, with continued improvement over the following months. No downtime."),
              ("How does it work?", "Simultaneous thermal and mechanical energy boosts collagen, circulation and elasticity while addressing the structural causes of cellulite.")],
         locs=["memorial", "highland-park"]),
]
BTL_BY = {b["slug"]: b for b in BTL}


def btl_page(b):
    where = ", ".join(f'<a href="{s}.html" style="color:var(--teal-deep);text-decoration:underline">{LOC_BY[s]["label"]}</a>' for s in b["locs"])
    others = "".join(card(o["name"], f'{o["slug"]}.html', o["img"], sub="Learn more") for o in BTL if o["slug"] != b["slug"])
    return hero(
        b["kicker"], b["h"], b["sub"], img=f"{IMG}/{b['img']}", alt=f"{b['name']} treatment at ThrIVe", crumb=f'<a href="body-contouring.html">Body &amp; Face</a> &nbsp;/&nbsp; {b["name"]}', page=True,
        actions=[("Book a Consultation", "book.html", True), ("Call " + PHONE, TEL, False)],
        meta=["Non-invasive", "No downtime", b["series"]], badge=b["tag"],
    ) + split("How it works", "01", f'What is <span class="brush">{b["name"]}</span>?', b["para"], f"{IMG}/{b['img2']}", f"{b['name']} at ThrIVe", tag="BTL technology", cls="section--ice",
              cta=[("Book a Consultation", "book.html", True)],
              extra=f'<p class="body-copy" style="margin-top:18px"><strong>Available at:</strong> {where}.</p>') + f"""
<section class="section"><div class="wrap">
  {cards_head("02", "Good to know", f'{b["name"]} <span class="brush">questions</span>', ("All FAQs", "faq.html"))}
  {accordion(b["faq"])}
  <p class="form-note reveal" style="margin-top:18px">Pricing for BTL treatments is quoted at your consultation and varies by area and series length. Membership credits can be applied to BTL services.</p>
</div></section>
<section class="section section--ice"><div class="wrap">
  {cards_head("03", "The BTL suite", 'More ways to <span class="brush">sculpt</span>', ("Body &amp; Face overview", "body-contouring.html"))}
  <div class="card-grid" data-stagger>{others}</div>
</div></section>
""" + cta_band(f'Book your <span class="brush">{b["name"]}</span> consult.', "Consultations are complimentary. Membership credits apply to every BTL treatment.")


body_hub = hero(
    "Body &amp; Face", ["Sculpt, lift,", "smooth.", '<span class="brush">No downtime.</span>'],
    "The complete BTL suite: Emsculpt NEO for muscle and fat, EMFACE for needle-free facial lifting, EMTONE for cellulite — plus infrared sauna. Science-based treatments in a spa setting.",
    img=f"{IMG}/emsculpt-neo-table.webp", alt="An Emsculpt NEO treatment in progress", crumb="Body &amp; Face", page=True,
    actions=[("Book a Consultation", "book.html", True), ("Find a Location", "locations.html", False)],
    meta=["Non-invasive", "20–30 minute sessions", "Membership credits apply"], badge="Define your shape",
) + f"""
<section class="section section--tight"><div class="wrap">
  {cards_head("01", "Treatments", 'Choose your <span class="brush">result</span>')}
  <div class="card-grid" data-stagger>
    {card("Emsculpt NEO", "emsculpt-neo.html", "emsculpt-neo-session.jpg", sub="Burn fat + build muscle", num="01")}
    {card("EMFACE", "emface.html", "emface.webp", sub="Needle-free lift", num="02")}
    {card("EMTONE", "emtone.html", "emtone-device.webp", sub="Cellulite & tightening", num="03")}
  </div>
</div></section>
<section class="section section--ice"><div class="wrap">
  {cards_head("02", "Recovery &amp; more", 'Restore and <span class="brush">recover</span>')}
  <div class="card-grid" data-stagger>
    {card("Infrared Sauna", "infrared-sauna.html", "infrared-sauna.webp", sub="Katy & Clear Lake", num="01")}
    {card("Styku 3D Body Scan", "memorial-green.html", "body-scan.webp", sub="Memorial Green", num="02")}
  </div>
</div></section>
""" + split(
    "Why ThrIVe", "03", 'Transform your body with <span class="brush">high satisfaction</span>',
    ["Every BTL treatment is delivered by trained staff in a private treatment room — with a drip lounge next door. Stack an Emsculpt NEO session with a Fit Drip, or an EMFACE series with the Beauty Drip, and use membership credits on all of it.",
     "Consultations are complimentary. We'll map the series, the areas and the cadence to your goals."],
    f"{IMG}/contouring-chair.webp", "A client during a body-contouring session", rev=True, tag="Consult is free", cta=("Book a consultation", "book.html", True)
) + cta_band('Define your <span class="brush">shape.</span>', "Emsculpt NEO, EMFACE and EMTONE across Houston, Dallas and Fort Worth. Book a complimentary consultation.")

sauna_body = hero(
    "Glow Session", ["Infrared sauna,", '<span class="brush">under an hour.</span>'],
    "Infrared light warms the body from the inside, so you sweat deeply at a lower, more comfortable temperature. Clients report clearer skin, fewer aches and better sleep. Available at Katy and Clear Lake.",
    img=f"{IMG}/infrared-sauna.webp", alt="Two guests in the infrared sauna", crumb="Infrared Sauna", page=True,
    actions=[("Book a Session", "book.html", True), ("Katy", "katy.html", False), ("Clear Lake", "clear-lake.html", False)],
    meta=["Katy · Clear Lake", "Lower temp, deeper sweat", "1–3 sessions a week"], badge="Relaxation does more",
) + f"""
<section class="section section--ice"><div class="wrap">
  {cards_head("01", "Unlocking wellness", 'Infrared, <span class="brush">explained</span>', ("All FAQs", "faq.html"))}
  {accordion([
    ("What does an infrared sauna do?", "Infrared light penetrates the skin and warms the body directly rather than heating the air, producing a deep sweat at a lower temperature. Clients use it for relaxation, recovery, skin and sleep."),
    ("Are infrared saunas good for detox?", "Sweating is one of the body's natural ways to clear waste; a deep infrared sweat supports that process. Hydrate before and after — a Hydrate Drip is a natural pairing."),
    ("How is infrared different from a regular sauna?", "A traditional sauna heats the air to 180°F or more. Infrared works at a lower ambient temperature while warming you from within — more comfortable, easier to stay longer."),
    ("Can infrared saunas help with weight loss?", "They're not a magic bullet, but sessions raise heart rate and mimic light cardio, and they support the recovery that keeps a routine going."),
    ("How often should I go?", "Once or twice a week is a good rhythm; two to three sessions a week for deeper recovery or skin goals."),
  ])}
</div></section>
""" + cta_band('Sweat it out, <span class="brush">gently.</span>', "Book an infrared session at Katy or Clear Lake — and hydrate after with a drip.")

weight_body = hero(
    "Weight Loss Therapy", ["Weight loss,", "clinically", '<span class="brush">proven.</span>'],
    "ThrIVe Drip Spa now offers medically supervised weight-loss therapy with weekly injections and telehealth consults. Non-surgical, no downtime, and paired with the drips and shots that keep energy up while the weight comes off.",
    img=f"{IMG}/glp-1.webp", alt="A woman celebrating weight-loss progress", crumb="Weight Loss", page=True,
    actions=[("Book a Consultation", "book.html", True), ("Call " + PHONE, TEL, False)],
    meta=["Telehealth consults", "Weekly injections", "Results in the first month"], badge="Now offering",
) + split("What are weight-loss injections", "01", 'Weight loss that <span class="brush">lasts</span>',
          ["Prescription weight-loss injections work with your body's own appetite and blood-sugar signals so you feel satisfied sooner and eat less without white-knuckling it. Paired with movement, sleep and hydration, they're a smarter path than the crash diet.",
           "Treatment starts with a consultation — in person or by telehealth — with a licensed provider who confirms you're a good candidate and sets your dose. Most clients receive weekly injections and continue for several months.",
           "We offer concierge wellness throughout your program — our team keeps in touch at every step of the journey to make sure your needs are met and you're satisfied with your progress."],
          f"{IMG}/weight-loss-jeans.webp", "Weight-loss progress", tag="Safe & effective", cls="section--ice",
          extra='<ul class="checklist" style="margin-top:18px"><li>Non-surgical, no downtime</li><li>Improvements within weeks</li><li>Mild, manageable side effects</li><li>Dose adjusted to you</li></ul>',
          cta=[("Book a consultation", "book.html", True)]) + split(
    "Keep momentum", "02", 'Support the program with a <span class="brush">Slim Drip</span>',
    ["Weight loss can drain energy and nutrients. The Slim Drip (carnitine, B12) and Lipo B / Lipo C shots support metabolism and keep you feeling strong. Members can apply credits to injections, drips and shots alike.",
     "Read our guide to supporting weight loss while using GLP-1 medications on the blog."],
    f"{IMG}/scale.webp", "Stepping on a scale", rev=True, cta=[("Slim Drip", "slim-drip.html"), ("Blog: GLP-1 support", "blog.html")]
) + f"""
<section class="section section--ice"><div class="wrap">
  {cards_head("03", "Good to know", 'Weight-loss <span class="brush">questions</span>', ("All FAQs", "faq.html"))}
  {accordion([
    ("Am I a good candidate?", "Adults who want medically supervised support for weight loss and are cleared at consultation. Our provider reviews your history, goals and any medications before prescribing."),
    ("How long does treatment last?", "Most patients receive weekly injections and continue therapy for several months, with dose and duration adjusted to progress."),
    ("What are the side effects?", "Commonly mild nausea, bloating or changes in bowel habits in the first weeks; your dose is adjusted to keep them manageable."),
    ("How fast will I see results?", "Many clients see changes within the first month; significant progress is typical after 12–16 weeks."),
  ])}
  <div class="notice reveal" style="margin-top:28px"><p><strong>Pharmacy disclosure.</strong> For verification or pharmacy-related inquiries only: {PHARMACY}.</p></div>
</div></section>
""" + cta_band('Gain your <span class="brush">confidence.</span>', "Book a weight-loss consultation — in person at any lounge or by telehealth.")


# ============================================================ MEMBERSHIPS
def _tier_cards(tiers, feat=None):
    return "".join(f'<div class="price-card{" price-card--feat" if n == feat else ""}"><h3>{n}</h3><div class="price-card__amt">{p}<span>{per}</span></div><p>{d}</p>{_btn(("Join " + n.split()[0] if n.split()[0] in ("NAD+",) else "Join", "book.html", n == feat))}</div>' for n, p, per, d in tiers)


memberships_body = hero(
    "Wellness Perks", ["Find your", '<span class="brush">membership.</span>'],
    "Our memberships are shaped by how people actually live. Each month your membership loads a service credit worth more than what you pay — and it works on any service you choose: drips, shots, boosters, NAD+ and BTL treatments — on a month-to-month basis.",
    img=f"{IMG}/lounge-chairs.webp", alt="The ThrIVe drip lounge with reclining chairs", crumb="Memberships", page=True,
    actions=[("Join Today", "book.html", True), ("Member Login", LOGIN, False)],
    meta=["Month-to-month", "Credits roll over", "Birthday drip on us"], badge="More value every month",
) + membership_block("01", cls="") + f"""
<section class="section section--ice" id="family"><div class="wrap">
  {cards_head("02", "Family &amp; student", 'Memberships for the whole <span class="brush">household</span>', None, "Family plans require someone in the household with a regular IV membership. Student plans need a valid student ID.")}
  <div class="price-grid price-grid--4" data-stagger>{_tier_cards(MEMBER_FAMILY + MEMBER_STUDENT)}</div>
</div></section>
<section class="section" id="nad"><div class="wrap">
  {cards_head("03", "NAD+ memberships", 'Stay consistent with <span class="brush">NAD+</span>', ("About NAD+", "nad.html"))}
  <div class="price-grid" data-stagger>{_tier_cards(MEMBER_NAD, feat="NAD+ Luxe")}</div>
</div></section>
<section class="section section--ice"><div class="wrap">
  {cards_head("04", "Exclusive member perks", 'Why members <span class="brush">stay</span>')}
  {pillars([("Birthday Drip", "A complimentary drip in your birthday month. Our treat."), ("Priority Booking", "Members get first access to appointments and exclusive promotions."), ("Exclusive Pricing", "Member-only pricing on every drip ($150 vs $190 for a Myers), boosters, packages and more."), ("More Value Every Month", "Credits worth more than your fee, usable on NAD+, BTL services, drips, shots and boosters. Unused services roll over.")])}
  <p class="form-note reveal" style="margin-top:22px">Membership credits can be used towards NAD+, BTL services, IV drips, shots and boosters. Memberships run on a month-to-month basis.</p>
</div></section>
""" + cta_band('Consistency is <span class="brush">key.</span>', "Join at any lounge or online in about two minutes. Your first drip is waiting.", primary=("Join Today", "book.html"), secondary=("Member Login", LOGIN))

packages_body = hero(
    "Package Options", ["Buy more,", 'thrive <span class="brush">more.</span>'],
    "Choosing a package is the easiest way to stay consistent with high-quality, science-backed wellness. Shots, boosters, NAD+ and members-only drip bundles — at a better rate than one at a time.",
    img=f"{IMG}/iv-bags.webp", alt="Prepared IV bags at ThrIVe", crumb="Packages", page=True,
    actions=[("Book Now", "book.html", True), ("Memberships", "memberships.html", False)],
    meta=["Shots & boosters", "NAD+ loading doses", "Members-only drip bundles"], badge="Boost your health",
) + f"""
<section class="section section--tight"><div class="wrap">
  {cards_head("01", "Shots &amp; boosters", 'Stock up on <span class="brush">shots</span>', ("Shot menu", "shots.html"))}
  {price_table([("Shots/Boosters — Premium", "Buy 4, get 1 free", "Any shot or booster"), ("Shots/Boosters — Premium+", "Buy 8, get 3 free", "Any shot or booster"), ("B12 Package", "Buy 8, get 2 free", "Weekly energy"), ("Tri-Immuno Package", "5 for $300", "Immune support all season")], head=("Package", "Deal"))}
</div></section>
<section class="section section--ice"><div class="wrap">
  {cards_head("02", "NAD+", 'NAD+ <span class="brush">packages</span>', ("About NAD+", "nad.html"))}
  {price_table([("NAD+ Shot Package — Select", "$300", "Four 100 mg shots (400 mg)"), ("NAD+ Shot Package — Premium", "$375", "Five 100 mg shots (500 mg)"), ("NAD+ Drip 4-Pack · 250 mg", "$1,250", "Four 250 mg drips"), ("NAD+ Drip 4-Pack · 500 mg", "$1,750", "Four 500 mg drips"), ("2-Day Loading Dose", "$1,750 member · $2,375", "2,500 mg"), ("3-Day Loading Dose", "$2,450 member · $3,325", "3,500 mg"), ("5-Day Loading Dose", "$4,200 member · $5,700", "6,000 mg")], head=("Package", "Price"))}
</div></section>
<section class="section"><div class="wrap">
  {cards_head("03", "Members only", 'Premium drip <span class="brush">bundles</span>', ("Become a member", "memberships.html"))}
  <div class="price-grid price-grid--2" data-stagger>
    <div class="price-card"><h3>Premium Drips — Select</h3><div class="price-card__amt">$500<span>4 drips</span></div><p>Four premium drips ($190 menu) for $125 each. Members only.</p>{_btn(("Book", "book.html", False))}</div>
    <div class="price-card price-card--feat"><span class="price-card__tag">Best value</span><h3>Premium Drips — Premium</h3><div class="price-card__amt">$1,100<span>10 drips</span></div><p>Ten premium drips for $110 each. Members only.</p>{_btn(("Book", "book.html", True))}</div>
  </div>
</div></section>
""" + cta_band('Stay <span class="brush">consistent.</span>', "Packages are sold at every lounge — ask a spa consultant or book online.")

promotions_body = hero(
    "Monthly Promotions", ["Deals on the", "services you", '<span class="brush">already love.</span>'],
    "Your go-to treatments, now with even better timing. This month's offers make it easier to stay consistent and feel your best.",
    img=f"{IMG}/guests-drinks.webp", alt="Two guests enjoying drinks in the ThrIVe lounge", crumb="Promotions", page=True,
    actions=[("Book Now", "book.html", True), ("Send an eGift", GIFT, False)],
    meta=["Updated monthly", "Members get first access", "eGift cards available"], badge="Promos worth calendaring",
)


def promos_section():
    if PROMOS:
        cards = "".join(
            f'<div class="price-card"><h3>{p.get("title","")}</h3><div class="price-card__amt">{p.get("price","")}</div><p>{p.get("_body","")[3:-4]}</p>'
            + (f'<p class="form-note" style="margin-top:0">Valid through {fmt_date(p.get("ends"))}</p>' if p.get("ends") else "")
            + _btn(("Book", cms_link(p.get("link", "book.html")), True)) + "</div>" for p in PROMOS)
    else:
        cards = ""
    fixed = f"""
    <div class="price-card price-card--feat"><span class="price-card__tag">New clients</span><h3>25% off your first IV</h3><div class="price-card__amt">25%<span>off</span></div><p>Physician-formulated drips, delivered by licensed nurses. No membership, no card to book — you pay in the chair.</p>{_btn(("Book Your First Drip", "book.html", True))}</div>
    <div class="price-card"><h3>Free Benadryl with the Migraine Drip</h3><div class="price-card__amt">$0<span>add-on</span></div><p>Added at no cost to help you rest through a migraine. Bring a driver, or wait 45 minutes after your IV before driving yourself home.</p>{_btn(("Migraine Drip", "migraine-drip.html", False))}</div>
    <div class="price-card"><h3>Good Faith Exam credit</h3><div class="price-card__amt">Credit<span>back</span></div><p>Your Good Faith Exam fee is returned to your account as credit toward services.</p>{_btn(("How the GFE works", "gfe-process.html", False))}</div>
    """
    return f"""
<section class="section section--tight"><div class="wrap">
  {cards_head("01", "This month", 'Offers worth putting on your <span class="brush">calendar</span>', ("Memberships", "memberships.html"))}
  <div class="price-grid" data-stagger>{cards}{fixed}</div>
  <p class="form-note reveal" style="margin-top:20px">Promotions vary by location and can't be combined with other offers. Staff can add this month's specials from the content manager.</p>
</div></section>
"""


promotions_body += promos_section() + membership_block("02") + cta_band('Give the gift of <span class="brush">thriving.</span>', "eGift cards work at every ThrIVe lounge — for drips, shots, NAD+ and more.", primary=("Send an eGift Card", GIFT), secondary=("Book Now", "book.html"))


# ============================================================ LOCATIONS
def _loc_cards():
    out = ""
    for reg in REGIONS:
        out += f'<div class="cards-head" style="margin:40px 0 20px"><div><p class="eyebrow" style="margin-bottom:0">{reg}</p></div></div><div class="card-grid card-grid--4" data-stagger>'
        out += "".join(card(l["label"], f'{l["slug"]}.html', l["img"], sub=l["phone"]) for l in LOCATIONS if l["region"] == reg)
        out += "</div>"
    return out


locations_body = hero(
    "Find a location near you", ["Ten lounges", 'across <span class="brush">Texas.</span>'],
    "ThrIVe Drip Spa was founded in Houston, the first IV therapy drip spa in Texas. With lounges throughout Greater Houston, we've expanded to Dallas and Fort Worth — and our mobile concierge brings the menu to your door.",
    img=f"{IMG}/lounge-interior.webp", alt="The ThrIVe lounge interior", crumb="Locations", page=True,
    actions=[("Book at Any Lounge", "book.html", True), ("Mobile IV", "mobile-iv.html", False)],
    meta=["Houston Metro", "Greater Houston", "Dallas · Fort Worth"], badge="Open 7 days",
) + f"""
<section class="section section--tight"><div class="wrap">
  {cards_head("01", "The lounges", 'Choose your <span class="brush">lounge</span>')}
  {_loc_cards()}
  <div class="card-grid card-grid--4" data-stagger style="margin-top:20px">{card("Mobile IV — Houston", "mobile-iv.html", "mobile-van-team.webp", sub="We come to you")}</div>
</div></section>
""" + split("Franchise", "02", 'Bring ThrIVe to <span class="brush">your city</span>',
            ["ThrIVe is franchising across Texas and the U.S. If you're a healthcare professional, entrepreneur or investor who wants to open a lounge, we'd love to talk."],
            f"{IMG}/franchise-ribbon.webp", "A ThrIVe franchise ribbon cutting", rev=True, cls="section--ice", cta=("Franchise opportunities", "franchise.html")) \
    + cta_band('See you in the <span class="brush">lounge.</span>', "Book at any of our ten locations in under a minute.")


def loc_page(l):
    hours = "".join(f"<div><dt>{d}</dt><dd>{h}</dd></div>" for d, h in l["hours"])
    svc = [SERVICE_BY[s] for s in l["services"] if s in SERVICE_BY]
    svc_cards = "".join(card(s[0], s[1], s[3], sub=s[2]) for s in svc)
    if "styku" in l["services"]:
        svc_cards += card("Styku 3D Body Scan", "memorial-green.html#styku", "body-scan.webp", sub="Under 60 seconds")
    svc_section = f"""
<section class="section section--ice"><div class="wrap">
  {cards_head("02", "Science-based treatments", f'Beyond the drip at <span class="brush">{l["label"]}</span>', ("Body &amp; Face", "body-contouring.html"))}
  <div class="card-grid card-grid--4" data-stagger>{svc_cards}</div>
</div></section>""" if svc else f"""
<section class="section section--ice"><div class="wrap">
  {cards_head("02", "Trusted results", 'Relax, restore, <span class="brush">rejuvenate</span>', ("Body &amp; Face at other lounges", "body-contouring.html"), f"{l['label']} is a dedicated drip lounge: 12 signature IV drips, boosters and vitamin shots, delivered by registered nurses.")}
  <div class="card-grid" data-stagger>{card("IV Drip Menu", "iv-therapy.html", "iv-bags.webp", sub="12 signature drips")}{card("Boosters", "boosters.html", "boosters.webp", sub="From $25")}{card("Vitamin Shots", "shots.html", "shots.webp", sub="From $25")}</div>
</div></section>"""
    styku = f"""
<section class="section" id="styku"><div class="wrap">{split("3D body insight", "03", 'Precision meets <span class="brush">progress</span>', ["Experience fast, private 3D body scans in under 60 seconds. Styku provides highly accurate measurements of body fat percentage, lean mass and circumferences — and before-and-after comparisons so you can see exactly what Emsculpt NEO and your drips are doing."], f"{IMG}/styku.webp", "Styku 3D body scanning", tag="Memorial Green only", cta=("Book a scan", "book.html", True)).replace('<section class="section ">', "<div>").replace("</section>", "</div>")}</div></section>""" if "styku" in l["services"] else ""
    maps_q = l["addr"].replace("&amp;", "and").replace(" ", "+")
    return hero_photo(
        f'ThrIVe Drip Spa · {l["region"]}', [f'<span class="brush">{l["label"]}</span>', "drip lounge."],
        f'{l["intro"]}',
        img=f"{IMG}/{l['img']}", alt=f"ThrIVe Drip Spa {l['label']}", crumb=f'<a href="locations.html">Locations</a> &nbsp;/&nbsp; {l["label"]}',
        actions=[("Book at " + l["label"], meevo(l), True), ("Call " + l["phone"], f'tel:{l["tel"]}', False)],
        meta=[l["hours"][0][0] + " " + l["hours"][0][1], f'{l["reviews"]}+ Google reviews', "Registered nurses"],
    ) + f"""
<section class="section section--tight"><div class="wrap"><div class="loc-grid" data-stagger>
  <div class="loc-item"><h4>Visit</h4><a href="{l['maps']}" target="_blank" rel="noopener">{l['addr'].replace(', ', '<br>', 1)}</a></div>
  <div class="loc-item"><h4>Call or email</h4><a class="phone" href="tel:{l['tel']}">{l['phone']}</a><a href="mailto:{l['email']}" style="font-size:14px;font-weight:500;display:block;margin-top:6px">{l['email']}</a></div>
  <div class="loc-item"><h4>Spa hours</h4><dl class="hours">{hours}</dl></div>
  <div class="loc-item"><h4>Follow</h4><a href="https://www.instagram.com/{l['ig']}" target="_blank" rel="noopener">@{l['ig']}</a><span style="display:block;margin-top:8px"><span class="stars">★★★★★</span> <small style="color:var(--muted)">{l['reviews']}+ Google reviews</small></span></div>
</div></div></section>
<section class="section"><div class="wrap">
  {cards_head("01", l["kicker"], 'Twelve signature <span class="brush">drips</span>', ("Full menu &amp; pricing", "iv-therapy.html"), l["blurb"])}
  {drip_grid()}
</div></section>
{svc_section}{styku}
""" + membership_block("04", cls="") + f"""
<section class="section section--ice"><div class="wrap">
  {cards_head("05", "Directions", f'Visit our <span class="brush">{l["label"]}</span> lounge')}
  <div class="map-embed reveal"><iframe src="https://www.google.com/maps?q={maps_q}&output=embed" loading="lazy" title="Map to ThrIVe Drip Spa {l['label']}" allowfullscreen referrerpolicy="no-referrer-when-downgrade"></iframe></div>
</div></section>
""" + form_section(f"contact-{l['slug']}", "06", "Contact " + l["label"], f'Say hello to <span class="brush">{l["label"]}</span>',
                   f"Questions about drips, memberships or {', '.join(s[0] for s in svc[:2]) if svc else 'boosters'}? Send a note and the {l['label']} team will get back to you.", cls="") \
        + cta_band(f'Book at <span class="brush">{l["label"]}</span> today.', f"{l['addr']} · {l['phone']}. Online booking takes under a minute.", primary=("Book Now", meevo(l)), secondary=("All Locations", "locations.html"))


# ============================================================ BOOK
book_body = hero(
    "Book online", ["Feel better in", 'about <span class="brush">an hour.</span>'],
    "Physician-formulated IV therapy, delivered by licensed nurses. No membership, no card to book — you pay when you're in the chair. New clients save 25% on their first IV.",
    img=f"{IMG}/lounge-selfie.jpg", alt="A guest relaxing with her drip in the lounge", crumb="Book Now", page=True,
    actions=[("I'm New — Quick Booking", BOOK_NEW, True), ("I'm a Client — Sign In", LOGIN, False)],
    meta=["No card required", "Booked in under a minute", "Licensed medical staff"], badge="25% off your first IV",
) + f"""
<section class="section section--tight"><div class="wrap">
  {cards_head("01", "Choose your lounge", 'Book at a <span class="brush">location</span>', ("Mobile IV instead", "mobile-iv.html"), "Pick your lounge to see live availability. Booking opens in our secure scheduling portal.")}
  <div class="pillars" data-stagger>{"".join(f'<div class="pillar"><span class="pillar__num">{l["region"]}</span><h3>{l["label"]}</h3><p>{l["addr"]}<br>{l["phone"]}</p><a class="inline-link" href="{meevo(l)}" target="_blank" rel="noopener">Book {l["label"]} →</a></div>' for l in LOCATIONS)}</div>
</div></section>
<section class="section section--ice"><div class="wrap">
  {cards_head("02", "The menu", 'What to <span class="brush">book</span>')}
  {price_table([("Hydrate Drip", "$150", "Pure fluids and electrolytes to reset and rehydrate"), ("Myers · Detox · Beauty · Slim · Party · Fit · Libido · Migraine", "$190", "The classics"), ("High C Drip", "$230", "Our max dose of vitamin C"), ("Immuno Drip", "$310", "Our strongest immune formula"), ("NAD+ Drip", "Consultant pricing", "Up to two hours; shots from $50"), ("B12, pain-relief & anti-nausea shots", "$25", "In and out in 15 minutes"), ("Body & face consultations", "Complimentary", "Emsculpt NEO, EMFACE, EMTONE"), ("Weight-loss consultation", "In person or telehealth", "Weekly injections")], head=("Service", "Walk-in price"))}
  <p class="form-note reveal" style="margin-top:18px">Members pay $120–$250 per drip. A quick Good Faith Exam with a licensed provider is completed before your first treatment; the fee is credited back to your account.</p>
</div></section>
""" + cta_band('Ready when <span class="brush">you</span> are.', "Prefer to talk? Call " + PHONE + " and a spa consultant will book you in.", primary=("Book Online", BOOK), secondary=("Call " + PHONE, TEL))


# ============================================================ ABOUT
about_body = hero(
    "About ThrIVe", ["The first drip", 'spa in <span class="brush">Texas.</span>'],
    "ThrIVe Drip Spa is an IV vitamin therapy and lifestyle wellness spa that took traditional medical treatments and gave them a modern, refreshing twist. Whether your needs are reparative or preventative, IV therapy is the only process that ensures up to 100% of nutrients are absorbed.",
    img=f"{IMG}/front-desk-welcome.webp", alt="A guest being welcomed at the ThrIVe front desk", crumb="About", page=True,
    actions=[("Book a Drip", "book.html", True), ("Our Locations", "locations.html", False)],
    meta=["Founded in Houston", "Physician-led", "LegitScript certified"], badge="Health, innovated",
) + split(
    "Our story", "01", 'Hospital-grade care, <span class="brush">spa-grade</span> comfort',
    ["ThrIVe was founded in Houston as the first IV therapy drip spa in Texas. The idea was simple: the treatments that keep patients hydrated and nourished in hospitals — a liter of fluids, vitamins straight to the bloodstream — shouldn't require a hospital. So we built a lounge.",
     "Today ThrIVe is a franchised brand with ten lounges across Greater Houston, Dallas and Fort Worth, a mobile concierge service, and a menu that has grown from twelve signature drips into NAD+, weight-loss therapy and the full BTL body-and-face suite. Every drip is still formulated by physicians and pharmacists, and administered by registered nurses after a Good Faith Exam."],
    f"{IMG}/lounge-two-friends.webp", "Two friends relaxing in the ThrIVe lounge", tag="Since 2016", cls="section--ice"
) + split(
    "Leadership", "02", 'Meet <span class="brush">Dr. Eugene Lou</span>',
    ["ThrIVe's CEO and founder is an MIT graduate who studied genetics and molecular biology and published alongside three Nobel laureates at the Whitehead Institute. He has practiced as an orthopedic surgeon for more than 20 years.",
     "\"ThrIVe is a preventative-health-oriented wellness center designed to help people mitigate the risks of stress from work and their environment — and allow oneself to stay optimized to look, feel and perform better every day.\""],
    f"{IMG}/founder-dr-lou.webp", "Dr. Eugene Lou, MD, CEO of ThrIVe Drip Spa", rev=True, tag="Orthopedic surgeon · CEO"
) + f"""
<section class="section section--ice"><div class="wrap">
  {cards_head("03", "What we stand for", 'The ThrIVe <span class="brush">way</span>')}
  {pillars([("Medical first", "Licensed providers, registered nurses, a Good Faith Exam for every client, and pharmacist-formulated drips. We're LegitScript certified."), ("Customized to you", "Twelve signature drips, 21 boosters and a nurse who will build a formula around your week."), ("A lounge, not a clinic", "Reclining chairs, blankets, complimentary drinks and protein bars. Consistency should be a pleasure."), ("Consistency pays", "Memberships load a credit worth more than you pay, every month, on any service.")])}
</div></section>
""" + stats_band([(10, "", "Lounges across Texas"), (12, "", "Signature drips"), (21, "", "Boosters on the menu"), (4500, "+", "Google reviews")]) + f"""
<section class="section"><div class="wrap">
  {cards_head("04", "As seen on", 'ABC13 tried the <span class="brush">Party Drip</span>', ("Read the story", "blog/abc13-tries-thrive.html"))}
  <div class="split"><div class="split__media split__media--wide reveal-img"><img src="{IMG}/press-abc13.gif" alt="ABC13 Houston segment on ThrIVe Drip Spa" loading="lazy"></div>
  <div class="split__body"><p class="lede reveal">ABC13 Houston's Natasha Barrett came in to try IV vitamin therapy for herself — and reported on the new drip spa offering IV treatment for everyday ailments.</p><p class="body-copy reveal" style="margin-top:16px">We've since been featured for our mobile concierge, EMFACE and NAD+ programs. Media inquiries: <a href="mailto:info@thrivedripspa.com">info@thrivedripspa.com</a>.</p></div></div>
</div></section>
""" + location_picker("05", cls="section--ice") + cta_band('Come see for <span class="brush">yourself.</span>', "Book a drip at any lounge — your first IV is 25% off.")


# ============================================================ GFE
gfe_body = hero(
    "Good Faith Exam", ["It starts with", '<span class="brush">understanding.</span>'],
    "At ThrIVe, your journey begins with a Good Faith Exam to make sure your care is safe, personalized and medically sound. It's required by Texas law — and the fee comes straight back to you as account credit.",
    img=f"{IMG}/consult-tablet.webp", alt="A spa consultant reviewing a client's chart", crumb="Good Faith Exam", page=True,
    actions=[("Book Your Exam + Drip", "book.html", True), ("FAQ", "faq.html", False)],
    meta=["$35 · $45 with bloodwork", "Credited back to your account", "Video or in-lounge"], badge="Transparency in wellness",
) + f"""
<section class="section section--tight"><div class="wrap"><div class="intro-grid">
  <div><p class="eyebrow"><span class="num">01</span> Transparency in wellness</p><h2 class="h-display reveal">What the exam <span class="brush">is</span></h2></div>
  <div class="intro-grid__right">
    <p class="lede reveal">In accordance with Jenifer's Law, a Texas state requirement, all clients complete a Good Faith Exam with a licensed medical provider before treatment.</p>
    <ul class="checklist checklist--1 reveal">
      <li><strong>New clients:</strong> the exam is required prior to your first service.</li>
      <li><strong>Returning clients:</strong> renewed annually on your client anniversary, or any time your medical history changes.</li>
      <li><strong>Fee:</strong> $35 non-refundable ($45 if bloodwork is included) — and you receive the same amount in account credit toward your next visit.</li>
    </ul>
  </div>
</div></div></section>
<section class="section section--ice"><div class="wrap">
  {cards_head("02", "What to expect", 'Three quick <span class="brush">steps</span>')}
  <div class="steps" data-stagger>
    <div class="step"><div class="step__media"><img src="{IMG}/front-desk-checkin.webp" alt="Checking in at ThrIVe" loading="lazy"></div><div class="step__body"><span class="step__num">01</span><h3>Convenience</h3><p>Complete the exam from home with a scheduled video appointment, or in one of our private rooms during your visit.</p></div></div>
    <div class="step"><div class="step__media"><img src="{IMG}/consult-tablet.webp" alt="Video consultation with a licensed provider" loading="lazy"></div><div class="step__body"><span class="step__num">02</span><h3>Method</h3><p>A video consultation with a licensed medical professional to discuss your personal health history and wellness goals.</p></div></div>
    <div class="step"><div class="step__media"><img src="{IMG}/iv-start-lounge.webp" alt="A nurse beginning a drip in the lounge" loading="lazy"></div><div class="step__body"><span class="step__num">03</span><h3>Afterwards</h3><p>Your chart is reviewed and passed to our registered nurse staff. From there, you begin your ThrIVe experience with confidence.</p></div></div>
  </div>
  <p class="form-note reveal" style="margin-top:22px">Thank you for trusting ThrIVe to be part of your wellness journey. Our nurses use lidocaine to numb the site (no allergy permitting) — our goal is one stick, every time.</p>
</div></section>
""" + cta_band('Safe. Personal. <span class="brush">Yours.</span>', "Book your exam and first drip together — it takes under a minute online.")


# ============================================================ FAQ
FAQ_IV = [
    ("What is IV therapy?", "IV therapy administers vitamins, minerals, antioxidants and amino acids directly into the bloodstream through intravenous infusion. It bypasses the digestive system and has been clinically shown to be more effective than oral supplements."),
    ("Is IV therapy safe?", "Our treatments are administered by experienced registered nurses using safe, effective procedures, after a Good Faith Exam with a licensed provider. Our spa consultants guide you through the process and build a personalized plan."),
    ("Is it just a trend?", "Celebrities and athletes made it visible, but the medical community has used IV therapy for decades to safely treat and manage a range of conditions and help people improve overall health."),
    ("Does the process hurt?", "Every client is different, but our goal is one 'stick'. Our registered nurses use lidocaine to numb the site for each treatment (if you have no allergy)."),
    ("How often can I get an IV?", "The benefits are felt with a single treatment. On average our clients visit one to two times per week, depending on their goals."),
    ("How long does it take?", "Drip times vary by formula and by client; plan a little extra time on your first visit for the Good Faith Exam. NAD+ infusions take up to two hours. Shots take minutes."),
    ("How long does IV therapy stay in my system?", "Fluids and electrolytes 2–3 days; vitamins 2–3 weeks (water-soluble C and B used within a day); minerals 1–2 weeks; antioxidants like glutathione 1–3 days. Effects on energy, skin and immunity often last longer."),
]
FAQ_VISIT = [
    ("What is the Drip Lounge experience like?", "A relaxing lounge with reclining chairs, complimentary beverages, protein bars and cozy blankets. Read, work, watch TV or nap while your drip runs."),
    ("What is the Good Faith Exam?", "A Texas-required screening with a licensed provider before your first service, renewed annually. $35 ($45 with bloodwork), credited in full to your account. See the <a href='gfe-process.html'>GFE page</a>."),
    ("What should I do before my first visit?", "Wear loose layers so a sleeve rolls up, eat a light meal, drink water, and arrive 10–15 minutes early. Afterwards, avoid heavy lifting and stay hydrated."),
    ("Do I need an appointment?", "Walk-ins are welcome, but booking online takes under a minute and guarantees your chair. No card is required to book."),
    ("Do you offer financing?", "Yes — Affirm financing is available on services and packages. eGift cards are available online for any amount."),
]
FAQ_MEMBER = [
    ("How do memberships work?", "Month-to-month. Each month your membership loads a service credit worth more than your fee — Select $95 → $140 credit, Premium $165 → $260, Luxe $285 → $490 — usable on drips, shots, boosters, NAD+ and BTL services. Unused services roll over, and you get a complimentary birthday drip."),
    ("Can I cancel my membership?", "Memberships run on a month-to-month basis. To cancel, contact the front desk at your lounge — cancellations require two weeks' notice."),
    ("What is member pricing?", "Members save on every drip (Myers $150 vs $190, Immuno $250 vs $310), on the Immuno booster ($130 vs $160), and get access to members-only drip bundles."),
]
FAQ_BODY = [
    ("What areas does EMFACE treat?", "The forehead, submentum (under the chin), eyes and cheeks. Twenty-minute sessions, no needles, no downtime; best results after a series of four."),
    ("How many Emsculpt NEO sessions do I need?", "Six 30-minute sessions, one every 5–7 days. It feels like an intense workout with a warming sensation."),
    ("How does EMTONE work?", "Simultaneous radiofrequency and targeted pressure energy to treat the causes of cellulite and tighten skin. About 20 minutes; most clients do four treatments."),
    ("Is the infrared sauna different from a regular sauna?", "Yes — it warms the body directly at a lower air temperature, so you sweat deeply and comfortably. Offered at Katy and Clear Lake."),
]
faq_body = hero(
    "Quick Answers", ["Frequently asked", '<span class="brush">questions.</span>'],
    "Everything you want to know about IV drips, the Good Faith Exam, memberships, body contouring and your first visit. Can't find it? Ask the ThrIVe Concierge in the corner of your screen, or call us.",
    img=f"{IMG}/lounge-couple.webp", alt="Two guests relaxing in the lounge", crumb="FAQ", page=True,
    actions=[("Book a Drip", "book.html", True), ("Call " + PHONE, TEL, False)],
    meta=["IV therapy", "Your visit", "Memberships", "Body & face"], badge="Informed choices",
) + f"""
<section class="section section--tight"><div class="wrap">{cards_head("01", "IV drip therapy", 'About the <span class="brush">drips</span>')}{accordion(FAQ_IV)}</div></section>
<section class="section section--ice"><div class="wrap">{cards_head("02", "Your visit", 'Before you <span class="brush">arrive</span>')}{accordion(FAQ_VISIT, open_first=False)}</div></section>
<section class="section"><div class="wrap">{cards_head("03", "Memberships", 'Member <span class="brush">questions</span>', ("See memberships", "memberships.html"))}{accordion(FAQ_MEMBER, open_first=False)}</div></section>
<section class="section section--ice"><div class="wrap">{cards_head("04", "Body &amp; face", 'BTL <span class="brush">treatments</span>', ("Body &amp; Face", "body-contouring.html"))}{accordion(FAQ_BODY, open_first=False)}</div></section>
""" + cta_band('Still <span class="brush">curious?</span>', "Our spa consultants are a call away — or book and ask your nurse in the chair.", primary=("Call " + PHONE, TEL), secondary=("Book Now", "book.html"))


# ============================================================ CAREERS / FRANCHISE / EVENTS / CONTACT
careers_body = hero(
    "Start your career", ["Your future", 'in <span class="brush">wellness.</span>'],
    "Join the ThrIVe Drip Spa team and make a meaningful impact in the wellness industry. We're looking for passionate professionals ready to help clients look, feel and perform at their best.",
    img=f"{IMG}/team-front-desk.webp", alt="Two ThrIVe team members at the front desk", crumb="Careers", page=True,
    actions=[("Apply by Email", "mailto:antasia@thrivedripspa.com?subject=ThrIVe%20career%20inquiry", True), ("Our Locations", "locations.html", False)],
    meta=["Spa consultants", "Registered nurses", "Ten lounges + mobile"], badge="We're hiring",
) + f"""
<section class="section section--tight"><div class="wrap">
  {cards_head("01", "Current openings", 'Open <span class="brush">roles</span>', None, "Inquire within — email your résumé and the role you're interested in to antasia@thrivedripspa.com.")}
  {rows([("Spa Consultant — West University", "Front-of-house guide for our Houston West U lounge: greet guests, walk them through the menu, book and follow up."), ("Spa Consultant — The Woodlands", "Same role, at our Six Pines lounge. Weekends included."), ("Spa Consultant — Memorial", "Our founding lounge on Wirt Road. Hospitality experience a plus."), ("Registered Nurse — All lounges", "RNs with IV experience for lounges and the mobile concierge team. Send your license state and availability.")],
         hrefs=["mailto:antasia@thrivedripspa.com?subject=Spa%20Consultant%20-%20West%20University", "mailto:antasia@thrivedripspa.com?subject=Spa%20Consultant%20-%20The%20Woodlands", "mailto:antasia@thrivedripspa.com?subject=Spa%20Consultant%20-%20Memorial", "mailto:antasia@thrivedripspa.com?subject=Registered%20Nurse"])}
</div></section>
<section class="section section--ice"><div class="wrap">
  {cards_head("02", "Why ThrIVe", 'A place to <span class="brush">thrive</span>')}
  {pillars([("Growing brand", "Ten lounges and counting, with franchise expansion across Texas and the U.S."), ("Medical standards", "Licensed providers, protocols and training — the LegitScript-certified way."), ("Team culture", "Small teams, real hospitality, and clients who come back every week."), ("Perks", "Team drips and shots, member pricing for family, flexible schedules.")])}
</div></section>
""" + cta_band('Help people <span class="brush">thrive.</span>', "Send your résumé and preferred location — we reply to every inquiry.", primary=("Email Us", "mailto:antasia@thrivedripspa.com"), secondary=("Franchise Instead", "franchise.html"))

franchise_body = hero(
    "Franchise", ["Bring ThrIVe to", 'your <span class="brush">city.</span>'],
    "ThrIVe Drip Spa is dedicated to personalized wellness that empowers clients to look, feel and perform at their best. As we grow, we welcome strategic franchise partners who share that passion — with extensive support, industry-leading training and a proven business model.",
    img=f"{IMG}/franchise-ribbon.webp", alt="A ThrIVe franchise ribbon cutting", crumb="Franchise", page=True,
    actions=[("Request Franchise Info", "#franchise-form", True), ("Our Lounges", "locations.html", False)],
    meta=["Texas & U.S.", "Proven model", "Full training & support"], badge="Join a leading brand",
) + split(
    "Thrive with us", "01", 'Invest in a <span class="brush">thriving</span> industry',
    ["ThrIVe franchisees become part of a brand reshaping self-care, recovery and performance for clients nationwide. Cutting-edge IV therapy, NAD+, body sculpting, recovery treatments and weight-loss therapy under one roof, with a membership model that builds recurring revenue.",
     "Our program includes site selection support, build-out standards, medical-director and compliance frameworks, nurse and consultant training, marketing, and the booking and CRM stack that runs every lounge."],
    f"{IMG}/lounge-chairs.webp", "The ThrIVe lounge", tag="Proven business model", cls="section--ice",
    extra='<ul class="checklist" style="margin-top:18px"><li>Site selection & design</li><li>Medical compliance & training</li><li>Marketing & launch support</li><li>Booking, CRM & memberships</li></ul>'
) + form_section("franchise-form", "02", "Join the wellness revolution", 'Request franchise <span class="brush">information</span>',
                 "Tell us where you'd like to open and a bit about your background. Our franchise team will follow up with the next steps.", btn="Request Information", cls="",
                 interests=["I'm a healthcare professional", "I'm an entrepreneur / operator", "I'm an investor", "I currently own a franchise"],
                 extra_fields='<div class="field field--full"><input type="text" name="city" id="franchise-form-city" placeholder=" "><label for="franchise-form-city">Which city or state are you interested in?</label></div>',
                 note="Franchisor: I Thrive Drip Holdings, LLC. This is not an offer to sell a franchise; offers are made only by a Franchise Disclosure Document in states where permitted.") \
    + cta_band('Reshape self-care in <span class="brush">your market.</span>', "Ten lounges across Texas and growing. Let's talk.", primary=("Request Information", "#franchise-form"), secondary=("Call " + PHONE, TEL))


def events_body():
    if EVENTS:
        cards = "".join(card(e.get("title", ""), cms_link(e.get("link", "contact.html")), cms_img(e.get("image"), "wall-friends.webp"), sub=f'{fmt_date(e.get("date"))} · {e.get("location", "")}', wide=True, below=e.get("_body", "")[3:-4][:160]) for e in EVENTS[:6])
        grid = f'<div class="card-grid" data-stagger>{cards}</div>'
    else:
        grid = f'<div class="notice reveal"><p><strong>Events coming soon.</strong> Follow <a href="https://www.instagram.com/thrivedripspa/" target="_blank" rel="noopener">@thrivedripspa</a> for pop-ups, EMFACE demos and member appreciation nights — or join the newsletter below.</p></div>'
    return hero(
        "Events", ["Wellness, for", '<span class="brush">real life.</span>'],
        "From exclusive EMFACE demos to wellness pop-ups and member appreciation nights, ThrIVe events are your chance to experience what we do best — with early access, live treatments and exclusive pricing.",
        img=f"{IMG}/wall-friends.webp", alt="Guests in front of the 'Living My Best Life' wall", crumb="Events", page=True,
        actions=[("Book a Drip", "book.html", True), ("Sponsor an Event", "mailto:sydney@thrivedripspa.com", False)],
        meta=["Houston · Dallas · Fort Worth", "Live demos", "Exclusive pricing"], badge="Your first look starts here",
    ) + f"""
<section class="section section--tight"><div class="wrap">
  {cards_head("01", "Upcoming", 'On the <span class="brush">calendar</span>')}
  {grid}
</div></section>
""" + split("Host with us", "02", 'Bring ThrIVe to your <span class="brush">event</span>',
            ["Corporate wellness days, bachelorette weekends, race-day recovery, film sets. Our mobile concierge team brings the drip and shot menu to you — and our lounges host private group bookings.",
             "Want to be a sponsor? Contact <a href='mailto:sydney@thrivedripspa.com'>sydney@thrivedripspa.com</a>."],
            f"{IMG}/mobile-van-team.webp", "The ThrIVe mobile team", rev=True, cls="section--ice", cta=("Mobile IV", "mobile-iv.html")) \
        + cta_band('See you <span class="brush">there.</span>', "Join the newsletter for early invitations to every ThrIVe event.")


contact_body = hero(
    "Contact", ["Say <span class=\"brush\">hello.</span>"],
    "Questions about drips, memberships, mobile service or body contouring? Call, email, or send a note — a spa consultant will get back to you within one business day.",
    img=f"{IMG}/front-desk-phone.webp", alt="A ThrIVe consultant on the phone at the front desk", crumb="Contact", page=True,
    actions=[("Call " + PHONE, TEL, True), ("Book Online", "book.html", False)],
    meta=["Ten lounges", "info@thrivedripspa.com", "Open 7 days"], badge="We reply fast",
) + form_section("contact", "01", "Send a message", 'How can we <span class="brush">help?</span>',
                 "Tell us what you're interested in and your preferred lounge. For bookings, the fastest route is online — under a minute, no card needed.") + f"""
<section class="section"><div class="wrap">
  {cards_head("02", "Direct lines", 'Every <span class="brush">lounge</span>')}
  <div class="loc-grid" data-stagger>{"".join(f'<div class="loc-item"><h4>{l["label"]}</h4><a class="phone" href="tel:{l["tel"]}">{l["phone"]}</a><a href="{l["slug"]}.html" style="font-size:14px;font-weight:500;display:block;margin-top:6px">{l["addr"]}</a></div>' for l in LOCATIONS)}</div>
  <p class="form-note reveal" style="margin-top:20px">Careers: antasia@thrivedripspa.com · Events &amp; sponsorship: sydney@thrivedripspa.com · SMS support: bella@thrivedripspa.com · General: info@thrivedripspa.com</p>
</div></section>
""" + cta_band('Or just <span class="brush">come in.</span>', "Walk-ins are welcome at every lounge, seven days a week.")

thanks_body = hero(
    "Thank you", ["For choosing", '<span class="brush">ThrIVe.</span>'],
    "At ThrIVe, your health and comfort are our top priorities. Whether you're boosting immunity, recharging energy or giving your body a little extra love, we're here to help you feel your best — every time. We'll be in touch shortly.",
    img=f"{IMG}/lounge-guest-relax.jpg", alt="A guest relaxing during her drip", crumb="Thank You", page=True,
    actions=[("Book a Drip", "book.html", True), ("See the Drip Menu", "iv-therapy.html", False)],
) + location_picker("01", cls="section--ice")


# ============================================================ LEGAL
def legal_page(title, kicker, sections):
    body = "".join(f'<h2>{h}</h2>{p}' for h, p in sections)
    return f"""
<section class="hero hero--page"><div class="hero__grid" style="grid-template-columns:1fr"><div class="hero__inner">
  <div class="hero__crumb"><a href="index.html">Home</a> &nbsp;/&nbsp; {title}</div>
  <p class="hero__kicker">{kicker}</p>
  <h1 class="hero__title" style="font-size:clamp(38px,5vw,72px)"><span class="ln"><span style="transition-delay:.1s">{title}</span></span></h1>
</div></div></section>
<section class="section section--tight"><div class="wrap wrap--narrow"><div class="post-body reveal">{body}</div></div></section>
"""


privacy_body = legal_page("Privacy Policy", "How we handle data", [
    ("Our commitment", "<p>ThrIVe Drip Spa (I Thrive Drip Holdings, LLC) respects your privacy. This policy explains what we collect, how we use it, and the choices you have. By using thrivedripspa.com or our services you consent to the practices described here.</p>"),
    ("Information we collect", "<p>Contact details you provide (name, email, phone) when you book, join the newsletter, submit a form or text us; billing information processed by our payment providers; health information collected during your Good Faith Exam and treatment, which is protected as described in our Notice of Privacy Practices; and anonymous technical data such as IP address, browser and pages visited, collected through cookies and analytics.</p>"),
    ("How we use it", "<p>To schedule and deliver your treatments, communicate about appointments and your account, send marketing you have opted into, process payments, improve our website and services, and meet legal and regulatory obligations. We rely on your consent, our contract with you, or our legitimate interests as the basis for each use.</p>"),
    ("Text marketing and notifications", "<p>With your consent we send recurring automated marketing messages and appointment reminders by SMS to the number you provide. Message and data rates may apply. Reply STOP to unsubscribe at any time and HELP for help. Consent is not a condition of purchase. Support: bella@thrivedripspa.com.</p>"),
    ("Sharing", "<p>We share data only with service providers who help us operate (scheduling, payments, messaging, analytics, advertising platforms) under confidentiality obligations, and when required by law. We do not sell your personal information.</p>"),
    ("Your rights and choices", "<p>You may access, correct or delete your personal information, opt out of marketing, and manage cookies through your browser. Email info@thrivedripspa.com with any request. Our services are intended for adults; we do not knowingly collect information from children under 13.</p>"),
    ("Notice of Privacy Practices", "<p>Your health information is protected. You have the right to see and get a copy of your records, ask us to correct them, request confidential communications, ask us to limit what we share, get a list of those we've shared information with, and get a copy of this notice. We use and share health information to treat you, run our organization, bill for services, and as required by law. We will never use your health information for marketing or sell it without your written permission. We are required by law to maintain the privacy and security of your protected health information and to notify you promptly if a breach occurs.</p>"),
    ("Changes", "<p>We may update this policy; the current version is always posted here. Questions: info@thrivedripspa.com or 844-820-1713.</p>"),
])

terms_body = legal_page("Terms &amp; Conditions", "Important policy details", [
    ("Use and consent", "<p>thrivedripspa.com is operated by I Thrive Drip Holdings, LLC. By using the site or booking services you agree to these terms. Services are available to adults 18 and older. Treatments are provided only after a Good Faith Exam with a licensed medical provider.</p>"),
    ("Appointments, cancellations and refunds", "<p>Book online, by phone or in person. Please give us 24 hours' notice to cancel or reschedule so we can offer the chair to someone else. The Good Faith Exam fee ($35, or $45 with bloodwork) is non-refundable but is credited to your account. Memberships run on a month-to-month basis; cancellations require two weeks' notice with the front desk. Unused services roll over. Packages and eGift cards are non-refundable. Promotions cannot be combined and may vary by location.</p>"),
    ("SMS program", "<p>Our mobile message program sends marketing and appointment messages to opted-in numbers. Reply STOP, END, CANCEL, UNSUBSCRIBE or QUIT to opt out; HELP for help. Message and data rates may apply. Participants must be 18–75. Support: bella@thrivedripspa.com.</p>"),
    ("Medical disclaimer", "<p>Our services support wellness and are not intended to diagnose, treat, cure or prevent any disease, nor to replace care from your physician. Individual results vary. Tell your provider about all medications, conditions and allergies before treatment.</p>"),
    ("Intellectual property and your conduct", "<p>Site content, the ThrIVe name and marks are ours; you may not copy or reuse them without permission. Content you submit (reviews, photos) may be used by us to promote our services. Harassment of staff or guests, in person or online, is not tolerated and may result in refusal of service.</p>"),
    ("Liability and disputes", "<p>To the extent permitted by law, our liability for any claim relating to the site or services is limited to the amount you paid for the service in question. Disputes are resolved by binding individual arbitration in Texas; no punitive damages. Texas law governs.</p>"),
    ("Contact", "<p>I Thrive Drip Holdings, LLC · info@thrivedripspa.com · 844-820-1713.</p>"),
])


# ============================================================ BLOG
def blog_index_body():
    if not POSTS:
        cards = '<p class="body-copy">No posts yet — check back soon.</p>'
    else:
        cards = "".join(card(p.get("title", ""), f'blog/{p["_slug"]}.html', cms_img(p.get("image"), "lounge-chairs.webp"), sub="Read", num=f'{fmt_date(p.get("date"))}', wide=True, below=p.get("excerpt", "")) for p in POSTS)
    return hero(
        "Insightful articles", ["Explore optimal", '<span class="brush">health.</span>'],
        "Expert insights from the ThrIVe team on IV therapy, NAD+, hydration, immunity, body contouring and weight loss — so you can make informed choices about how you look, feel and perform.",
        img=f"{IMG}/lounge-tv.webp", alt="Guests relaxing in the ThrIVe lounge", crumb="Blog", page=True,
        actions=[("Book a Drip", "book.html", True)], meta=["IV therapy", "NAD+", "Beauty & body", "Wellness"],
    ) + f"""
<section class="section section--tight"><div class="wrap">
  {cards_head("01", "Latest posts", 'On the <span class="brush">blog</span>')}
  <div class="card-grid" data-stagger>{cards}</div>
</div></section>
""" + cta_band('Read it, then <span class="brush">feel it.</span>', "Book the drip you just read about — your first IV is 25% off.")


def blog_post_body(p):
    others = [o for o in POSTS if o["_slug"] != p["_slug"]][:3]
    more = "".join(card(o.get("title", ""), f'../blog/{o["_slug"]}.html', "../" + cms_img(o.get("image"), "lounge-chairs.webp"), sub="Read", wide=True) for o in others)
    more_html = f"""
<section class="section section--ice"><div class="wrap">
  {cards_head("02", "Keep reading", 'More from the <span class="brush">blog</span>', ("All posts", "../blog.html"))}
  <div class="card-grid" data-stagger>{more}</div>
</div></section>""" if others else ""
    return hero_photo(
        f'{p.get("category", "Blog")} · {fmt_date(p.get("date"))}', [p.get("title", "")],
        p.get("excerpt", ""), img="../" + cms_img(p.get("image"), "lounge-chairs.webp"), crumb='<a href="../blog.html">Blog</a>',
        actions=[("Book a Drip", "../book.html", True)], meta=[p.get("author", "ThrIVe Drip Spa")],
    ).replace('class="hero__title"', 'class="hero__title" style="font-size:clamp(32px,4.4vw,64px);max-width:22ch"') + f"""
<section class="section section--tight"><div class="wrap wrap--narrow">
  <div class="post-body reveal">{p['_body']}</div>
  <div class="reveal" style="margin-top:40px;display:flex;gap:12px;flex-wrap:wrap">{_btn(("Book a Drip", "../book.html", True))}{_btn(("Back to the blog", "../blog.html", False))}</div>
</div></section>
{more_html}
""" + cta_band('Feel better in about <span class="brush">an hour.</span>', "Ten lounges across Houston, Dallas and Fort Worth — plus mobile.", primary=("Book Now", "../book.html"), secondary=("Locations", "../locations.html")).replace(f'src="{IMG}/', f'src="../{IMG}/')


# ============================================================ STRUCTURED DATA (schema.org, for Google local results)
_DAYS = {"Mon": "Mo", "Tue": "Tu", "Wed": "We", "Thu": "Th", "Fri": "Fr", "Sat": "Sa", "Sun": "Su"}


def _hhmm(t):
    m = _re.match(r"(\d{1,2})(?::(\d{2}))?(am|pm)", t)
    h = int(m.group(1)) % 12 + (12 if m.group(3) == "pm" else 0)
    return f"{h:02d}:{m.group(2) or '00'}"


def _opening_hours(hours):
    out = []
    for days, times in hours:
        tm = _re.match(r"(\d{1,2}(?::\d{2})?(?:am|pm))–(\d{1,2}(?::\d{2})?(?:am|pm))$", times)
        if not tm:          # e.g. "Call for hours"
            continue
        d = "-".join(_DAYS[x] for x in days.split("–"))
        out.append(f"{d} {_hhmm(tm.group(1))}-{_hhmm(tm.group(2))}")
    return out


ORG_SCHEMA = {
    "@context": "https://schema.org", "@type": "Organization", "name": "ThrIVe Drip Spa", "url": SITE_URL,
    "logo": f"{SITE_URL}{IMG}/logo-color.webp", "telephone": "+1-" + PHONE,
    "sameAs": ["https://www.instagram.com/thrivedripspa/", "https://www.facebook.com/thrivedripspa"],
}


def loc_schema(l):
    street, city, rest = (l["addr"].split(", ") + ["", ""])[:3]
    if rest.count(" ") == 0:            # "Ste 210" sits between street and city
        street, city, rest = l["addr"].rsplit(", ", 2)
    region, postal = rest.split(" ", 1)
    return {
        "@context": "https://schema.org", "@type": "MedicalBusiness",
        "name": f"ThrIVe Drip Spa {l['label']}", "url": f"{SITE_URL}{l['slug']}.html",
        "image": f"{SITE_URL}{IMG}/{l['img']}", "telephone": l["phone"], "email": l["email"],
        "address": {"@type": "PostalAddress", "streetAddress": street, "addressLocality": city,
                    "addressRegion": region, "postalCode": postal, "addressCountry": "US"},
        "openingHours": _opening_hours(l["hours"]), "hasMap": l["maps"], "priceRange": "$$",
        "parentOrganization": {"@type": "Organization", "name": "ThrIVe Drip Spa", "url": SITE_URL},
    }


# ============================================================ BUILD
os.makedirs(OUT, exist_ok=True)
page("index.html", "IV Therapy, NAD+ & Wellness Spa | ThrIVe Drip Spa — Houston, Dallas & Fort Worth", "ThrIVe Drip Spa: 12 signature IV drips, NAD+, boosters, shots, mobile IV, body contouring and infrared sauna in Houston, Dallas and Fort Worth. Feel better in about an hour.", "index.html", home_body, schema=ORG_SCHEMA)
page("iv-therapy.html", "IV Drip Menu & Pricing | ThrIVe Drip Spa", "Twelve signature IV drips from $150 (members from $120): Hydrate, Myers, Detox, Party, Fit, Slim, Libido, Beauty, Migraine, High C, NAD+ and Immuno. Registered nurses.", "iv-therapy.html", iv_body, og="iv-bags-rack.webp")
for d in DRIPS:
    if d["slug"] == "nad":
        continue
    page(d["file"], f'{d["name"]} Drip — ${d["price"]} · ${d["member"]} member | ThrIVe Drip Spa', f'{d["tag"]} {", ".join(d["ingredients"])}. Good for {", ".join(x.lower() for x in d["for_"][:3])}. Book at ten Texas lounges or mobile.', d["file"], drip_page(d), og=d["imgs"][0])
page("nad.html", "NAD+ IV Therapy, Shots & Memberships | ThrIVe Drip Spa", "NAD+ drips, 4-packs, shots ($50–$100), boosters, memberships (500–1,500 mg/mo) and multi-day loading doses for energy, focus and healthy aging. Houston, Dallas, Fort Worth.", "nad.html", nad_body, og=nad["imgs"][1])
page("boosters.html", "IV Boosters — Vitamin C, Glutathione, NAD+, B12 & more | ThrIVe Drip Spa", "Add targeted vitamins and medications to any drip from $25. 21 boosters including Glutathione, Zinc, Magnesium, Toradol, Biotin, Total Wellness and NAD+.", "boosters.html", boosters_body, og="boosters.webp")
page("shots.html", "Vitamin Shots — B12, Biotin, Lipo, NAD+, Vitamin D | ThrIVe Drip Spa", "Fast-acting intramuscular vitamin injections from $25: B12, Biotin, Lipo B, Lipo C, Vitamin D3, Toradol, Zofran, CoQ10, Tri-Immuno and NAD+. In and out in 15 minutes.", "shots.html", shots_body, og="shots.webp")
page("mobile-iv.html", "Mobile IV Therapy Houston — Concierge Drips to Your Door | ThrIVe Drip Spa", "ThrIVe's concierge nurses bring the full IV and shot menu to your home, hotel, office or event in Houston. Individuals and groups.", "mobile-iv.html", mobile_body, og="mobile-van-team.webp")
page("body-contouring.html", "Body & Face — Emsculpt NEO, EMFACE, EMTONE, Infrared Sauna | ThrIVe Drip Spa", "Non-invasive body contouring and facial lifting with the BTL suite, plus infrared sauna, at ThrIVe lounges across Texas.", "body-contouring.html", body_hub, og="emsculpt-neo-table.webp")
for b in BTL:
    page(f'{b["slug"]}.html', f'{b["name"]} in Houston & Dallas | ThrIVe Drip Spa', b["sub"], f'{b["slug"]}.html', btl_page(b), og=b["img"])
page("infrared-sauna.html", "Infrared Sauna Therapy — Katy & Clear Lake | ThrIVe Drip Spa", "Infrared sauna sessions for recovery, skin and sleep at ThrIVe Katy and Clear Lake.", "infrared-sauna.html", sauna_body, og="infrared-sauna.webp")
page("weight-loss.html", "Weight Loss Injections & Telehealth Consults | ThrIVe Drip Spa", "Medically supervised weight-loss injections with telehealth consults at ThrIVe Drip Spa. Non-surgical, no downtime, weekly injections.", "weight-loss.html", weight_body, og="glp-1.webp")
page("memberships.html", "Memberships from $95/mo | ThrIVe Drip Spa", "Select $95, Premium $165, Luxe $285 — monthly credits worth more than you pay, usable on any service. Family, student and NAD+ memberships, month to month.", "memberships.html", memberships_body, og="lounge-chairs.webp")
page("packages.html", "IV Therapy, Shot & NAD+ Packages | ThrIVe Drip Spa", "Buy 4 get 1 free on shots and boosters, NAD+ shot packages and loading doses, and members-only premium drip bundles.", "packages.html", packages_body, og="iv-bags.webp")
page("promotions.html", "Monthly Promotions | ThrIVe Drip Spa", "This month's offers at ThrIVe Drip Spa — 25% off your first IV, free Benadryl with the Migraine Drip, and more.", "promotions.html", promotions_body, og="guests-drinks.webp")
page("locations.html", "Locations — Houston, Katy, The Woodlands, Clear Lake, Dallas & Fort Worth | ThrIVe Drip Spa", "Ten ThrIVe Drip Spa lounges across Greater Houston, Dallas and Fort Worth, plus mobile IV. Addresses, hours and booking.", "locations.html", locations_body, og="lounge-interior.webp")
for l in LOCATIONS:
    page(f'{l["slug"]}.html', f'ThrIVe Drip Spa {l["label"]} — IV Therapy in {l["city"]}, TX', f'IV drips, NAD+, boosters and shots at ThrIVe Drip Spa {l["label"]}, {l["addr"]}. Call {l["phone"]}. {l["blurb"]}', f'{l["slug"]}.html', loc_page(l), og=l["img"], schema=loc_schema(l))
page("book.html", "Book Online — Under a Minute, No Card Required | ThrIVe Drip Spa", "Book IV therapy at any ThrIVe lounge in under a minute. New clients save 25% on their first drip.", "book.html", book_body, og="lounge-selfie.jpg")
page("about.html", "About ThrIVe Drip Spa — The First IV Drip Spa in Texas", "Founded in Houston and led by Dr. Eugene Lou, ThrIVe Drip Spa modernized IV therapy with a spa-grade lounge experience. Ten lounges across Texas.", "about.html", about_body, og="front-desk-welcome.webp")
page("gfe-process.html", "Good Faith Exam Process | ThrIVe Drip Spa", "How the Texas-required Good Faith Exam works at ThrIVe: video or in-lounge, $35 ($45 with bloodwork), credited back to your account.", "gfe-process.html", gfe_body, og="consult-tablet.webp")
page("faq.html", "FAQ — IV Therapy, Memberships & Body Contouring | ThrIVe Drip Spa", "Answers about IV drips, the Good Faith Exam, your first visit, memberships and BTL treatments at ThrIVe Drip Spa.", "faq.html", faq_body, og="lounge-couple.webp")
page("careers.html", "Careers — Spa Consultants & Nurses | ThrIVe Drip Spa", "Join the ThrIVe Drip Spa team. Open spa consultant roles in West University, The Woodlands and Memorial, plus RNs at all lounges.", "careers.html", careers_body, og="team-front-desk.webp")
page("franchise.html", "Franchise Opportunities | ThrIVe Drip Spa", "Open a ThrIVe Drip Spa lounge. Proven model, medical compliance frameworks, training and marketing support across Texas and the U.S.", "franchise.html", franchise_body, og="franchise-ribbon.webp")
page("events.html", "Events — Demos, Pop-ups & Member Nights | ThrIVe Drip Spa", "ThrIVe events across Houston, Dallas and Fort Worth: EMFACE demos, wellness pop-ups and member appreciation nights.", "events.html", events_body(), og="wall-friends.webp")
page("contact.html", "Contact ThrIVe Drip Spa — 844-820-1713", "Call, email or message ThrIVe Drip Spa. Direct lines for all ten lounges.", "contact.html", contact_body, og="front-desk-phone.webp")
page("thank-you.html", "Thank You | ThrIVe Drip Spa", "Thanks for contacting ThrIVe Drip Spa — we'll be in touch shortly.", "", thanks_body)
page("privacy.html", "Privacy Policy | ThrIVe Drip Spa", "How ThrIVe Drip Spa collects, uses and protects your information, including our Notice of Privacy Practices.", "", privacy_body)
page("terms.html", "Terms & Conditions | ThrIVe Drip Spa", "Terms of use, appointment and refund policies, SMS program terms and medical disclaimer for ThrIVe Drip Spa.", "", terms_body)
page("blog.html", "Blog — IV Therapy, NAD+ & Wellness Insights | ThrIVe Drip Spa", "Expert articles on IV therapy, hydration, NAD+, immunity, body contouring and weight loss from ThrIVe Drip Spa.", "blog.html", blog_index_body(), og="lounge-tv.webp")
for p in POSTS:
    page_sub(f'blog/{p["_slug"]}.html', f'{p.get("title","")} | ThrIVe Drip Spa', p.get("excerpt", ""), blog_post_body(p), og=cms_img(p.get("image"), "lounge-chairs.webp").replace(IMG + "/", ""))

page("404.html", "Page Not Found | ThrIVe Drip Spa", "This page has moved. Find IV drips, NAD+, memberships and locations at ThrIVe Drip Spa.", "", hero(
    "Page not found", ["This page has", '<span class="brush">moved.</span>'],
    "We've redesigned our site, so some addresses have changed. Find what you're looking for below — or book your drip in under a minute.",
    img=f"{IMG}/lounge-guest-relax.jpg", alt="A guest relaxing during her drip", page=True,
    actions=[("Book a Drip", "book.html", True), ("See the Drip Menu", "iv-therapy.html", False)],
) + location_picker("01", cls="section--ice"))

# retired pages → redirect old links (not listed in the sitemap)
for old, new in [("emsculpt.html", "emsculpt-neo.html"), ("normatec.html", "body-contouring.html")]:
    with open(os.path.join(OUT, old), "w") as f:
        f.write(f'<!DOCTYPE html>\n<html lang="en"><head><meta charset="UTF-8"><title>ThrIVe Drip Spa</title>'
                f'<meta name="robots" content="noindex"><link rel="canonical" href="{new}">'
                f'<meta http-equiv="refresh" content="0; url={new}"></head>'
                f'<body><p><a href="{new}">Continue to ThrIVe Drip Spa →</a></p></body></html>\n')

# Old thrivedripspa.com (WordPress) addresses → new pages. Azure serves these as permanent (301)
# redirects so search rankings, Google Business Profile links and old bookmarks carry over.
OLD_URLS = {
    # pages
    "/about/": "/about.html", "/blog/": "/blog.html", "/book-now/": "/book.html", "/booster/": "/boosters.html",
    "/biotin/": "/shots.html", "/careers/": "/careers.html", "/category/uncategorized/": "/blog.html",
    "/certified-medical-drips/": "/iv-therapy.html", "/concierge-services/": "/mobile-iv.html", "/drips/": "/iv-therapy.html",
    "/drips/beauty/": "/beauty-drip.html", "/drips/detoxing/": "/detox-drip.html", "/drips/fit/": "/fit-drip.html",
    "/drips/hangover-recovery/": "/party-drip.html", "/drips/hydration/": "/hydrate-drip.html",
    "/drips/immunity/": "/immuno-drip.html", "/drips/libido/": "/libido-drip.html", "/drips/migraine/": "/migraine-drip.html",
    "/drips/myers/": "/myers-drip.html", "/drips/nad/": "/nad.html", "/drips/slim/": "/slim-drip.html",
    "/drips/vitamin-c/": "/high-c-drip.html", "/high-c-drip/": "/high-c-drip.html", "/emface/": "/emface.html",
    "/emsculpt/": "/emsculpt-neo.html", "/emtone/": "/emtone.html", "/events/": "/events.html", "/faqs/": "/faq.html",
    "/franchise/": "/franchise.html", "/gfe-process/": "/gfe-process.html", "/infrared-sauna-therapy/": "/infrared-sauna.html",
    "/locations/": "/locations.html", "/lp-drips/": "/iv-therapy.html", "/memberships/": "/memberships.html",
    "/packages/": "/packages.html", "/privacy-policy/": "/privacy.html", "/promotions/": "/promotions.html",
    "/shots/": "/shots.html", "/sitemap/": "/locations.html", "/terms-and-conditions/": "/terms.html",
    "/thank-you/": "/thank-you.html", "/weight-loss/": "/weight-loss.html",
    "/emsculpt.html": "/emsculpt-neo.html", "/normatec.html": "/body-contouring.html",
    # blog posts → the matching new post, or the closest service page
    "/7-wellness-boosters-that-support-energy-levels/": "/boosters.html",
    "/9-benefits-of-hydration-iv-therapy/": "/blog/9-benefits-of-hydration-iv-therapy.html",
    "/abc13-news-anchor-reports-on-houston-beauty-drip-spa/": "/blog/abc13-tries-thrive.html",
    "/an-iv-med-spa-is-the-ultimate-destination-for-hydration-health-and-beauty/": "/blog/what-is-iv-therapy.html",
    "/beat-the-summer-heat/": "/hydrate-drip.html",
    "/beyond-the-finish-line-the-importance-of-hydration-performance-recovery-this-halloween-weekend/": "/fit-drip.html",
    "/breaking-down-the-science-of-a-myers-cocktail-iv-and-why-it-works/": "/blog/myers-cocktail-science.html",
    "/covid-19-primer-and-immunity-a-message-from-our-ceo/": "/immuno-drip.html",
    "/dont-miss-a-beat-on-your-houston-trip-iv-therapy-for-jetlag-recovery/": "/hydrate-drip.html",
    "/emface-at-thrive-drip-spa-a-revolutionary-approach-to-preventing-facial-aging-and-boosting-collagen/": "/emface.html",
    "/emface-for-noninvasive-facial-contouring-welcome-to-the-future/": "/emface.html",
    "/emsculpt-neo-for-body-contouring/": "/emsculpt-neo.html",
    "/experience-the-benefits-of-ultimate-detox-with-iv-therapy/": "/detox-drip.html",
    "/facial-contouring-without-surgery-top-non-invasive-solutions-for-jawline-and-skin-tightening-2/": "/emface.html",
    "/finding-the-right-balance-with-vitamin-d/": "/shots.html",
    "/glp-1-microdosing-a-smarter-approach-to-inflammation-metabolism-weight-support/": "/blog/glp-1-microdosing.html",
    "/how-do-zinc-glutathione-and-vitamin-c-benefit-you/": "/immuno-drip.html",
    "/how-does-an-iv-drip-support-your-holistic-weight-loss-program/": "/slim-drip.html",
    "/how-does-iv-infusion-work-what-to-expect-from-a-drip-spa/": "/blog/first-iv-visit.html",
    "/how-infrared-sauna-therapy-supports-muscle-recovery-and-pain-relief/": "/infrared-sauna.html",
    "/how-iv-drips-fit-into-todays-modern-wellness-lifestyle/": "/blog/what-is-iv-therapy.html",
    "/how-iv-therapy-services-support-holistic-health/": "/blog/what-is-iv-therapy.html",
    "/how-long-does-iv-therapy-stay-in-your-system/": "/blog/how-long-does-iv-therapy-last.html",
    "/how-thrive-services-help-kickstart-a-healthier-lifestyle/": "/iv-therapy.html",
    "/how-to-prevent-back-to-school-illness-with-immune-iv-therapy/": "/immuno-drip.html",
    "/how-to-support-weight-loss-while-using-glp-1-medications/": "/blog/glp-1-microdosing.html",
    "/i-had-a-hangover-and-then-i-found-thrive-iv-therapy/": "/party-drip.html",
    "/i-tried-nad-iv-therapy-does-it-actually-work/": "/blog/benefits-of-nad-drips.html",
    "/introducing-thrive-migraine-drip/": "/migraine-drip.html",
    "/is-a-wellness-infusion-right-for-you-heres-who-benefits-most/": "/blog/who-benefits-from-a-wellness-infusion.html",
    "/iv-infusion-houston-beat-dehydration/": "/hydrate-drip.html",
    "/mobile-iv-drip-dont-come-to-us-well-come-to-you/": "/mobile-iv.html",
    "/myers-iv-therapy-recovery-made-simple/": "/myers-drip.html",
    "/nad-therapy-for-mental-health-stress-addiction-support/": "/nad.html",
    "/the-benefits-of-a-detox-drip/": "/detox-drip.html",
    "/the-benefits-of-emtone-for-skin-firming-and-muscle-toning-treatment/": "/emtone.html",
    "/the-pros-and-cons-of-botox-houston-thrive/": "/blog.html",
    "/thrive-guide-to-looking-your-best-this-summer/": "/beauty-drip.html",
    "/tips-for-making-wellness-iv-drip-therapy-part-of-your-healthy-lifestyle/": "/iv-therapy.html",
    "/top-non-invasive-solutions-for-jawline-and-skin-tightening/": "/emface.html",
    "/top-tips-for-staying-hydrated-in-houston/": "/hydrate-drip.html",
    "/ultimate-self-care-checklist-for-west-houston/": "/west-university.html",
    "/what-are-the-benefits-of-nad-drips/": "/blog/benefits-of-nad-drips.html",
    "/what-is-emsculpt-neo-and-how-does-it-work/": "/emsculpt-neo.html",
    "/what-is-iv-therapy-the-benefits-and-breakdown/": "/blog/what-is-iv-therapy.html",
    "/what-is-nad-and-how-will-it-help-you-improve-your-neuro-function-and-general-wellness-with-nad-today/": "/nad.html",
    "/what-to-expect-during-your-first-iv-drip-therapy-session/": "/blog/first-iv-visit.html",
    "/whats-better-than-a-tall-glass-of-water-a-visit-to-a-hydration-spa-of-course/": "/hydrate-drip.html",
    "/youve-lost-the-weight-now-lose-the-flab/": "/emsculpt-neo.html",
}
OLD_URLS.update({f'/{l["slug"]}/': f'/{l["slug"]}.html' for l in LOCATIONS})
for _new in set(OLD_URLS.values()):
    assert os.path.exists(os.path.join(OUT, _new.lstrip("/"))), f"redirect target missing: {_new}"
# One route per address as Google indexed it (with the trailing slash); Azure caps this file at 20 KB.
routes = [{"route": old, "redirect": new, "statusCode": 301} for old, new in OLD_URLS.items()]
with open(os.path.join(OUT, "staticwebapp.config.json"), "w") as f:      # Azure Static Web Apps
    _json.dump({"routes": routes,
                "responseOverrides": {"404": {"rewrite": "/404.html", "statusCode": 404}},
                "globalHeaders": {"X-Content-Type-Options": "nosniff", "Referrer-Policy": "strict-origin-when-cross-origin"}},
               f, separators=(",", ":"))

# sitemap.xml + robots
NOT_IN_SITEMAP = {"404.html", "thank-you.html"}
with open(os.path.join(OUT, "sitemap.xml"), "w") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
            "".join(f"  <url><loc>{SITE_URL}{'' if fn == 'index.html' else fn}</loc></url>\n"
                    for fn, _ in PAGES if fn not in NOT_IN_SITEMAP) + "</urlset>\n")
with open(os.path.join(OUT, "robots.txt"), "w") as f:
    f.write("User-agent: *\nAllow: /\n" + ("" if NOINDEX else f"Sitemap: {SITE_URL}sitemap.xml\n"))
open(os.path.join(OUT, ".nojekyll"), "w").close()

copy_layer.publish(OUT, [(fn, title) for fn, title in PAGES if not fn.startswith("blog/")], REPO, "main")
print(f"done — {len(PAGES)} pages")
