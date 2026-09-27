#!/usr/bin/env python3
"""Generate WordPress block markup for every page of the college site.

Facts come from ../Info (researched 26 Sep 2026). Anything the college still has to
supply is rendered as a highlighted `sr-placeholder` note so it is easy to find and replace.

Output: content/pages/<slug>.html and content/pages.json (key, title, slug, parent, template, order).
Tokens replaced at install time by scripts/setup.sh:
  {{CONTACT_FORM}}  -> Contact Form 7 shortcode block (or a fallback note)
  {{FEE_PDF}}       -> URL of the Haryana Gazette fee PDF in the media library

Hindi: the same page definitions are run a second time with SR_LANG=hi. Every piece of text
passes through t(), which looks it up in tools/hindi.py (English text -> Hindi text). Hindi
pages go to content/pages/hi/ and are published under /hi/ with the same slugs. A string
missing from hindi.py stops the build and is listed, so the two versions cannot drift apart.
"""
import html as _html
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "content", "pages")
LANG = os.environ.get("SR_LANG", "en")
MISSING = []

if LANG == "hi":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from hindi import HI
    OUT = os.path.join(OUT, "hi")


def t(text):
    """Text in the language being built. Strings without Latin letters (numbers, dashes, markup
    only, or text already translated) pass through unchanged."""
    if LANG == "en" or text is None:
        return text
    if text in HI:
        return HI[text]
    if re.search(r"[A-Za-z]", re.sub(r"<[^>]*>|&[a-z]+;|\{\{[^}]*\}\}|\[[^\]]*\]", "", text)):
        MISSING.append(text)
    return text


# ---------------------------------------------------------------- block helpers
def _attrs(d):
    return (" " + json.dumps(d, separators=(",", ":"), ensure_ascii=False)) if d else ""


def _cls(*names):
    return " ".join(n for n in names if n)


def p(text, cls=None, align=None):
    a = {}
    if align:
        a["align"] = align
    if cls:
        a["className"] = cls
    c = _cls("has-text-align-" + align if align else None, cls)
    open_tag = f'<p class="{c}">' if c else "<p>"
    return f"<!-- wp:paragraph{_attrs(a)} -->\n{open_tag}{t(text)}</p>\n<!-- /wp:paragraph -->"


def h(text, level=2, cls=None, align=None):
    a = {}
    if level != 2:
        a["level"] = level
    if align:
        a["textAlign"] = align
    if cls:
        a["className"] = cls
    c = _cls("wp-block-heading", "has-text-align-" + align if align else None, cls)
    return f'<!-- wp:heading{_attrs(a)} -->\n<h{level} class="{c}">{t(text)}</h{level}>\n<!-- /wp:heading -->'


def ul(items, cls=None):
    a = {"className": cls} if cls else {}
    lis = "\n".join(f"<!-- wp:list-item -->\n<li>{t(i)}</li>\n<!-- /wp:list-item -->" for i in items)
    return f'<!-- wp:list{_attrs(a)} -->\n<ul class="{_cls("wp-block-list", cls)}">{lis}</ul>\n<!-- /wp:list -->'


def ol(items):
    lis = "\n".join(f"<!-- wp:list-item -->\n<li>{t(i)}</li>\n<!-- /wp:list-item -->" for i in items)
    return f'<!-- wp:list {{"ordered":true}} -->\n<ol class="wp-block-list">{lis}</ol>\n<!-- /wp:list -->'


PAD = {"top": "var:preset|spacing|60", "bottom": "var:preset|spacing|60"}


def group(children, cls=None, bg=None, text=None, align=None, layout=None, pad=None, tag="div", margin_top=None):
    a = {}
    if tag != "div":
        a["tagName"] = tag
    if align:
        a["align"] = align
    if cls:
        a["className"] = cls
    if bg:
        a["backgroundColor"] = bg
    if text:
        a["textColor"] = text
    style = {}
    css = []
    if pad:
        style.setdefault("spacing", {})["padding"] = pad
        for side, v in pad.items():
            css.append(f"padding-{side}:" + v.replace("var:preset|spacing|", "var(--wp--preset--spacing--") + (")" if v.startswith("var:") else ""))
    if margin_top:
        style.setdefault("spacing", {})["margin"] = {"top": margin_top}
        css.insert(0, "margin-top:" + margin_top.replace("var:preset|spacing|", "var(--wp--preset--spacing--") + (")" if margin_top.startswith("var:") else ""))
    if style:
        a["style"] = style
    a["layout"] = layout or {"type": "constrained"}
    classes = _cls(
        "wp-block-group",
        "align" + align if align else None,
        cls,
        f"has-{text}-color" if text else None,
        f"has-{bg}-background-color" if bg else None,
        "has-text-color" if text else None,
        "has-background" if bg else None,
    )
    st = f' style="{";".join(css)}"' if css else ""
    body = "\n".join(children)
    return f'<!-- wp:group{_attrs(a)} -->\n<{tag} class="{classes}"{st}>\n{body}\n</{tag}>\n<!-- /wp:group -->'


def section(children, bg=None, cls=None, wide=True, size="1200px", pad=PAD):
    """Full-width band. `size` sets the inner width: 680px (narrow), 960px, 1200px (default), 1400px (extra wide)."""
    return group(children, cls=cls, bg=bg, align="full", pad=pad,
                 layout={"type": "constrained", "contentSize": size, "wideSize": size} if wide else None)


def split(first, second, side="l", cls=None, valign="center"):
    """Edge-to-edge two-column band: the column on `side` bleeds to the screen edge (give it a panel
    className), the other keeps its text aligned to the 1200px grid.
    first/second: (className, blocks) tuples or plain block lists."""
    return cols([first, second], cls=_cls("sr-split", f"sr-bleed-{side}", cls), align="full", valign=valign)


def ticker(items):
    """Full-bleed scrolling strip. Items are duplicated so the loop is seamless."""
    li = "".join(f'<li>{t(i)}</li>' for i in items)
    return html(f'<div class="sr-ticker" role="region" aria-label="{t("Recognition and highlights")}"><ul class="sr-ticker__track">{li}</ul>'
                f'<ul class="sr-ticker__track" aria-hidden="true">{li}</ul></div>')


def wide(children, cls=None, margin_top="var:preset|spacing|50"):
    return group(children, cls=cls, align="wide", margin_top=margin_top, layout={"type": "default"})


def flex(children, cls=None, justify=None):
    lay = {"type": "flex", "flexWrap": "wrap"}
    if justify:
        lay["justifyContent"] = justify
    return group(children, cls=cls, layout=lay)


def cols(columns, cls=None, align=None, valign=None):
    """columns: list of block lists, or (className, blocks) tuples for a styled column."""
    a = {}
    if valign:
        a["verticalAlignment"] = valign
    if align:
        a["align"] = align
    if cls:
        a["className"] = cls
    parts = []
    for c in columns:
        ccls, blocks = c if isinstance(c, tuple) else (None, c)
        ca = {"className": ccls} if ccls else {}
        parts.append(f'<!-- wp:column{_attrs(ca)} -->\n<div class="{_cls("wp-block-column", ccls)}">\n{chr(10).join(blocks)}\n</div>\n<!-- /wp:column -->')
    classes = _cls("wp-block-columns", "align" + align if align else None,
                   "are-vertically-aligned-" + valign if valign else None, cls)
    return f'<!-- wp:columns{_attrs(a)} -->\n<div class="{classes}">\n{chr(10).join(parts)}\n</div>\n<!-- /wp:columns -->'


def icon_cls(icon, variant=None, extra=None):
    return _cls(extra, "sr-icon", f"sr-icon--{variant}" if variant else None, f"ico-{icon}") if icon else extra


PHOTOS = {ph["slug"]: ph for ph in json.load(open(os.path.join(ROOT, "Photos", "web", "photos.json"), encoding="utf-8"))}


def photo(slug, cls=None, caption=None):
    """Campus photo from the media library. Contributor photos always carry their credit."""
    ph = PHOTOS[slug]
    cap = t(caption or ph["credit"])
    a = {"id": "__ID__", "sizeSlug": "full", "linkDestination": "none"}
    if cls:
        a["className"] = cls
    attrs = _attrs(a).replace('"__ID__"', "{{IMGID:" + slug + "}}")
    figcap = f'<figcaption class="wp-element-caption">{cap}</figcaption>' if cap else ""
    return (f'<!-- wp:image{attrs} -->\n<figure class="{_cls("wp-block-image size-full", cls)}">'
            f'<img src="{{{{IMG:{slug}}}}}" alt="{t(ph["alt"])}" class="wp-image-{{{{IMGID:{slug}}}}}"/>{figcap}</figure>\n<!-- /wp:image -->')


def hero_cover(slug, children):
    """Full-bleed Cover block: campus photo in the background, navy tint on top (see .sr-hero CSS)."""
    a = {"url": "__URL__", "id": "__ID__", "dimRatio": 90, "overlayColor": "dark", "isDark": True, "align": "full",
         "className": "sr-hero", "layout": {"type": "constrained", "contentSize": "1200px"}}
    attrs = _attrs(a).replace('"__URL__"', '"{{IMG:' + slug + '}}"').replace('"__ID__"', "{{IMGID:" + slug + "}}")
    body = "\n".join(children)
    return (f'<!-- wp:cover{attrs} -->\n<div class="wp-block-cover alignfull is-dark sr-hero">'
            f'<span aria-hidden="true" class="wp-block-cover__background has-dark-background-color has-background-dim-90 has-background-dim"></span>'
            f'<img class="wp-block-cover__image-background wp-image-{{{{IMGID:{slug}}}}}" alt="" src="{{{{IMG:{slug}}}}}" data-object-fit="cover"/>'
            f'<div class="wp-block-cover__inner-container">\n{body}\n</div></div>\n<!-- /wp:cover -->')


def mosaic(slugs, per_row=3, cls="sr-mosaic sr-mosaic--photos"):
    """Edge-to-edge rows of photos with no gaps."""
    return "\n".join(cols([[photo(x)] for x in slugs[i:i + per_row]], cls=cls, align="full") for i in range(0, len(slugs), per_row))


def image(src, alt, cls=None):
    a = {"sizeSlug": "full"}
    if cls:
        a["className"] = cls
    return (f'<!-- wp:image{_attrs(a)} -->\n<figure class="{_cls("wp-block-image size-full", cls)}"><img src="{src}" alt="{t(alt)}"/></figure>\n<!-- /wp:image -->')


def card(children, icon=None, variant=None, cls=None):
    return group(children, cls=icon_cls(icon, variant, _cls("sr-card", cls)))


def grid(cards, per_row=3, align="wide"):
    rows = [cards[i:i + per_row] for i in range(0, len(cards), per_row)]
    out = []
    for r in rows:
        r = r + [[]] * (per_row - len(r)) if len(rows) > 1 else r
        out.append(cols([[c] if c else [] for c in r], align=align))
    return "\n".join(out)


def table(head, rows, caption=None, cls=None):
    a = {"className": cls} if cls else {}
    th = "".join(f"<th>{t(x)}</th>" for x in head) if head else ""
    trs = "".join("<tr>" + "".join(f"<td>{t(x)}</td>" for x in r) + "</tr>" for r in rows)
    cap = f'<figcaption class="wp-element-caption">{t(caption)}</figcaption>' if caption else ""
    return (f'<!-- wp:table{_attrs(a)} -->\n<figure class="{_cls("wp-block-table", cls)}"><table>{"<thead><tr>"+th+"</tr></thead>" if th else ""}'
            f"<tbody>{trs}</tbody></table>{cap}</figure>\n<!-- /wp:table -->")


def buttons(items, justify=None):
    a = {"layout": {"type": "flex", "justifyContent": justify}} if justify else {}
    bs = []
    for label, url, *style in items:
        outline = bool(style and style[0])
        ba = {"className": "is-style-outline"} if outline else {}
        cls = _cls("wp-block-button", "is-style-outline" if outline else None)
        bs.append(f'<!-- wp:button{_attrs(ba)} -->\n<div class="{cls}"><a class="wp-block-button__link wp-element-button" href="{url}">{t(label)}</a></div>\n<!-- /wp:button -->')
    return f'<!-- wp:buttons{_attrs(a)} -->\n<div class="wp-block-buttons">{"".join(bs)}</div>\n<!-- /wp:buttons -->'


def details(q, answer_blocks):
    return f'<!-- wp:details -->\n<details class="wp-block-details"><summary>{t(q)}</summary>{chr(10).join(answer_blocks)}</details>\n<!-- /wp:details -->'


def todo(text):
    return p(text, cls="sr-placeholder")


def html(raw):
    return f"<!-- wp:html -->\n{raw}\n<!-- /wp:html -->"


def shortcode(sc):
    return f"<!-- wp:shortcode -->\n{sc}\n<!-- /wp:shortcode -->"


def sep():
    return '<!-- wp:separator -->\n<hr class="wp-block-separator has-alpha-channel-opacity"/>\n<!-- /wp:separator -->'


def head(tag, title, lead=None, align=None):
    parts = [p(tag, cls="sr-tag", align=align), h(title, align=align)]
    if lead:
        parts.append(p(lead, align=align))
    return group(parts, cls="sr-section-head is-centered" if align == "center" else "sr-section-head", layout={"type": "default"})


# ---------------------------------------------------------------- shared data
COURSES = [
    dict(slug="bsc-nursing", photo="skill-practice", name="B.Sc Nursing", kind="Degree", years="4 years", seats="50", icon="nurse",
         blurb="A four-year professional degree that builds a strong foundation in nursing science, anatomy and direct patient care, with extensive hospital practice."),
    dict(slug="post-basic-bsc-nursing", photo="hospital-ward-2", name="Post Basic B.Sc Nursing", kind="Degree", years="2 years", seats="40", icon="graduation",
         blurb="A two-year degree for registered GNM nurses who want to upgrade to a B.Sc qualification and take on greater clinical and leadership roles."),
    dict(slug="bsc-paramedical-science", photo="lab-hall", name="B.Sc Paramedical Science", kind="Degree", years="3 years", seats="50", icon="microscope",
         blurb="A three-year allied-health degree awarded by Pt. B.D. Sharma UHS, Rohtak, preparing technologists for hospital and diagnostic settings."),
    dict(slug="gnm", photo="nursing-foundation-lab", name="GNM – General Nursing &amp; Midwifery", kind="Diploma", years="3 years", seats=None, icon="stethoscope",
         blurb="A diploma programme in general nursing and midwifery, leading to registration as a nurse and midwife with the state council."),
    dict(slug="anm", photo="maternity-room", name="ANM – Auxiliary Nurse Midwifery", kind="Diploma", years="2 years", seats="30", icon="heart",
         blurb="A two-year diploma that trains community health workers in maternal and child health, first aid and primary care."),
]


def course_card(c):
    seats = t(f"{c['seats']} seats" if c["seats"] else "Seats as approved")
    kind = c["kind"].lower()
    return group([
        image("{{THEME}}/assets/images/courses/" + c["slug"] + ".svg", "", cls="sr-course-card__art"),
        group([
            p(f"{c['kind']} programme", cls="sr-tag"),
            h(c["name"], 3),
            p(f'<span class="sr-chip sr-chip--time">{t(c["years"])}</span><span class="sr-chip sr-chip--seats">{seats}</span>', cls="sr-chips"),
            p(c["blurb"]),
            p(f'<a href="/courses/{c["slug"]}/">View course details</a>', cls="sr-more"),
        ], cls=icon_cls(c["icon"], "accent" if kind == "diploma" else None, "sr-course-card__body"), layout={"type": "default"}),
    ], cls=f"sr-course-card sr-kind-{kind}", layout={"type": "default"})


COURSE_FILTER = html(
    f'<div class="sr-filter" role="group" aria-label="{t("Filter programmes")}">'
    f'<button type="button" class="is-active" data-filter="all" aria-pressed="true">{t("All programmes")}</button>'
    f'<button type="button" data-filter="degree" aria-pressed="false">{t("Degrees")}</button>'
    f'<button type="button" data-filter="diploma" aria-pressed="false">{t("Diplomas")}</button></div>')


def course_bento():
    """Filterable photo grid: the first course is a large feature card spanning two rows."""
    return group([course_card(c) for c in COURSES], cls="sr-bento", layout={"type": "default"})


APPROVALS = [
    ("Indian Nursing Council", "INC, New Delhi: national regulator approving our nursing programmes.", "shield"),
    ("Haryana Nurses &amp; Midwives Council", "HNRC: state recognition and registration of nurses and midwives.", "award"),
    ("Pt. B.D. Sharma UHS, Rohtak", "Affiliating university for our degree programmes and examinations.", "graduation"),
    ("Government of Haryana", "Recognised institution; admissions and fees follow DMER Haryana norms.", "file"),
]

pages = []


def add(slug, title, body, parent=None, template=None, order=0, featured=None):
    """Write one page. `key` identifies it in pages.json (and names its file): the slug for English,
    "hi/<slug>" for Hindi, where the Hindi home page ("hi/home", slug "hi") is the parent of the rest."""
    key = slug
    text = "\n\n".join(body) + "\n"
    if LANG == "hi":
        key = "hi/" + slug
        if slug == "home":
            slug, template = "hi", "page-no-title"
        parent = "hi/" + (parent or "home") if key != "hi/home" else None
        # Site links point at the Hindi twin pages; the enquiry form is the Hindi one.
        text = re.sub(r'href="/(?!hi/)', 'href="/hi/', text).replace("{{CONTACT_FORM}}", "{{CONTACT_FORM_HI}}")
    pages.append(dict(key=key, slug=slug, title=_html.unescape(t(title)), parent=parent, template=template, order=order,
                      featured=featured, lang=LANG))
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, f"{slug if LANG == 'en' else key[3:]}.html"), "w", encoding="utf-8") as f:
        f.write(text)


def cta_band(title, text, btns):
    return group([
        h(title, align="center"),
        p(text, align="center"),
        buttons(btns, justify="center"),
    ], cls="sr-dark sr-cta-band", align="full", pad=PAD, layout={"type": "constrained", "contentSize": "680px"})


def feature(icon, title, text):
    return group([p(f"<strong>{title}</strong>{text}")], cls=icon_cls(icon, "soft", "sr-feature"), layout={"type": "default"})


# ---------------------------------------------------------------- HOME
# Width rhythm: hero art bleeds right -> stats 1200 -> about panel bleeds left -> courses 1400
# -> ticker edge-to-edge -> pillars tiles edge-to-edge -> hospital panel bleeds left
# -> steps 960 -> notices / CTA panel bleeds right.
NOTICES_QUERY = (
    '<!-- wp:query {"queryId":2,"query":{"perPage":3,"postType":"post","order":"desc","orderBy":"date","inherit":false},"className":"sr-notices"} -->\n'
    '<div class="wp-block-query sr-notices">\n'
    '<!-- wp:post-template -->\n<!-- wp:post-date {"fontSize":"small"} /-->\n<!-- wp:post-title {"isLink":true,"level":3} /-->\n<!-- /wp:post-template -->\n'
    '<!-- wp:query-no-results -->\n' + p("New notices will appear here.") + '\n<!-- /wp:query-no-results -->\n'
    '</div>\n<!-- /wp:query -->')

home = [
    hero_cover("campus-wide", [
        split(
            ("sr-hero-text", [
                p("Digrota · Satnali · Mahendragarh · Haryana", cls="sr-eyebrow"),
                h("Shaping skilled, <em>compassionate</em> nurses &amp; healthcare professionals", 1),
                p("Nursing and paramedical programmes approved by the Indian Nursing Council and affiliated to Pt. B.D. Sharma University of Health Sciences, Rohtak, with hands-on clinical training at our own 100-bed hospital.", cls="sr-lead"),
                buttons([("Apply for Admission", "/admissions/"), ("Explore Courses", "/courses/", True)]),
                flex([p("✓ INC Approved"), p("✓ HNRC Recognised"), p("✓ UHSR Rohtak Affiliated")], cls="sr-badges"),
            ]),
            ("sr-hero-art", [
                image("{{THEME}}/assets/images/hero-illustration.svg", "Illustration of the college hospital with a heartbeat line", cls="sr-hero-img"),
                p("<strong>100-bed</strong>attached hospital", cls="sr-float sr-float--1"),
                p("<strong>5</strong>programmes", cls="sr-float sr-float--2"),
            ]),
            side="r", cls="sr-hero-cols"),
    ]),

    cols([
        ("sr-icon sr-icon--soft ico-bed", [p("100", cls="sr-stat__num"), p("Bed attached hospital", cls="sr-stat__label")]),
        ("sr-icon sr-icon--soft ico-graduation", [p("5", cls="sr-stat__num"), p("Nursing &amp; paramedical programmes", cls="sr-stat__label")]),
        ("sr-icon sr-icon--soft ico-users", [p("170+", cls="sr-stat__num"), p("Approved seats every year", cls="sr-stat__label")]),
        ("sr-icon sr-icon--soft ico-home", [p("2", cls="sr-stat__num"), p("Separate hostels for girls &amp; boys", cls="sr-stat__label")]),
    ], cls="sr-stats", align="wide"),

    split(
        ("sr-panel sr-panel--teal", [
            p("Since", cls="sr-tag"),
            p("2012", cls="sr-bignum__n"),
            p("A trusted name in nursing education in Mahendragarh district.", cls="sr-panel__lead"),
            ul(["Approved by the Indian Nursing Council", "Recognised by the Haryana Nurses &amp; Midwives Council",
                "Affiliated to Pt. B.D. Sharma UHS, Rohtak", "Private, co-educational institution"], cls="sr-icon-list"),
        ]),
        ("sr-split__text", [
            head("About the college", "Quality nursing education in the heart of rural Haryana"),
            p("Shri Ram College of Medical Science &amp; Research at Digrota, Mahendragarh, runs <strong>Shri Ram College of Nursing</strong> and <strong>Shri Ram School of Nursing</strong>, offering degree and diploma programmes in nursing and allied health."),
            cols([
                [feature("hospital", "Own 100-bed hospital", "Clinical exposure from the early semesters."),
                 feature("microscope", "Modern laboratories", "Anatomy, physiology, microbiology &amp; nursing skills."),
                 feature("book", "Well-stocked library", "3,500+ books, journals and e-resources.")],
                [feature("home", "Safe hostels", "Separate hostels for girls and boys, with mess."),
                 feature("bus", "College transport", "Buses on routes around the campus."),
                 feature("wifi", "Wi-Fi campus", "Plus a gym, sports complex and canteen.")],
            ], cls="sr-features"),
            buttons([("More about us", "/about/", True)]),
        ]),
        side="l"),

    section([
        group([
            head("Programmes", "Courses we offer", "Degree and diploma programmes in nursing and allied health sciences, with clinical training in our own hospital."),
            COURSE_FILTER,
        ], cls="sr-courses-head", layout={"type": "flex", "flexWrap": "wrap", "justifyContent": "space-between", "verticalAlignment": "bottom"}),
        course_bento(),
        p('<a href="/courses/">Compare all courses side by side</a>', cls="sr-more", align="center"),
    ], bg="light", size="1400px", cls="sr-courses"),

    group([ticker([
        "INC Approved", "HNRC Recognised", "Affiliated to Pt. B.D. Sharma UHS, Rohtak", "Recognised by Govt. of Haryana",
        "Own 100-Bed Hospital", "B.Sc Nursing", "Post Basic B.Sc Nursing", "B.Sc Paramedical", "GNM", "ANM",
    ])], cls="sr-ticker-band", align="full", layout={"type": "default"}),

    group([
        p("Life at Shri Ram", cls="sr-tag", align="center"),
        h("A campus built for learning and care", align="center"),
    ], align="full", pad={"top": "var:preset|spacing|60", "bottom": "var:preset|spacing|40"}, layout={"type": "constrained", "contentSize": "680px"}),
    mosaic(["students-batch", "skill-practice", "library-hall", "hospital-ward", "classroom-students"], per_row=5),

    group([
        group([
            p("Our pillars", cls="sr-tag", align="center"),
            h("Care. Compassion. Competence.", align="center"),
            p("Three values that guide how we teach and how our students serve.", align="center"),
        ], layout={"type": "constrained", "contentSize": "680px"}),
        cols([
            ("sr-tile", [group([h("Care", 3), p("Patient-centred nursing is at the heart of everything we teach, from the first classroom lesson to the hospital ward.")], cls="sr-pillar sr-icon sr-icon--accent ico-hands")]),
            ("sr-tile", [group([h("Compassion", 3), p("We shape professionals who treat every patient with dignity, empathy and respect, whatever their background.")], cls="sr-pillar sr-icon sr-icon--accent ico-heart")]),
            ("sr-tile", [group([h("Competence", 3), p("Strong science, supervised clinical practice and professional ethics prepare graduates for real-world healthcare.")], cls="sr-pillar sr-icon sr-icon--accent ico-award")]),
        ], cls="sr-tiles", align="full"),
    ], cls="sr-dark sr-pillars", align="full", pad={"top": "var:preset|spacing|60"}, layout={"type": "constrained", "contentSize": "1200px"}),

    split(
        ("sr-panel sr-panel--navy", [
            photo("hospital-building", cls="sr-panel-photo"),
            p("Clinical training", cls="sr-tag"),
            p("100", cls="sr-bignum__n"),
            h("bed hospital on our own campus", 3),
            p("Students learn at the bedside under supervision, rotating through wards and services, alongside community health postings in the surrounding villages."),
            buttons([("About the hospital", "/hospital/")]),
        ]),
        ("sr-split__text", [
            head("Campus life", "Everything you need on one campus"),
            cols([
                [card([h("Classrooms", 3), p("Spacious halls with audio-visual aids.")], icon="monitor", variant="soft", cls="sr-icon--sm"),
                 card([h("Auditorium", 3), p("Seminars, workshops and events.")], icon="stage", variant="soft", cls="sr-icon--sm")],
                [card([h("Skill labs", 3), p("Hands-on practice before the ward.")], icon="flask", variant="soft", cls="sr-icon--sm"),
                 card([h("Canteen &amp; gym", 3), p("Hygienic food, fitness and sports.")], icon="utensils", variant="soft", cls="sr-icon--sm")],
            ]),
            p('<a href="/campus-facilities/">Explore all facilities</a>', cls="sr-more"),
        ]),
        side="l", cls="sr-split--light"),

    section([
        head("Admissions", "Your path to a nursing career", "Admissions follow the rules of DMER Haryana and Pt. B.D. Sharma UHS, Rohtak.", align="center"),
        cols([
            [group([h("Check eligibility", 3), p("10+2 with the required subjects and marks; minimum age 17 by 31 December.")], cls="sr-step")],
            [group([h("Apply / appear", 3), p("B.Sc courses: UHSR entrance test &amp; counselling. ANM/GNM: merit-based.")], cls="sr-step")],
            [group([h("Choose Shri Ram", 3), p("Select Shri Ram College of Nursing, Digrota, in counselling, or contact us.")], cls="sr-step")],
            [group([h("Report &amp; enrol", 3), p("Bring original documents, pay the fee and begin your journey.")], cls="sr-step")],
        ], cls="sr-steps"),
        buttons([("Admission details", "/admissions/"), ("Fee structure", "/fee-structure/", True)], justify="center"),
    ], size="960px"),

    split(
        ("sr-split__text", [
            head("Latest", "Notices &amp; announcements"),
            NOTICES_QUERY,
            p('<a href="/notices/">All notices</a>', cls="sr-more"),
        ]),
        ("sr-panel sr-panel--cta sr-icon sr-icon--accent ico-lamp", [
            h("Begin your career in healthcare"),
            p("Talk to our admissions team about courses, eligibility, fees and hostel availability."),
            buttons([("Contact Admissions", "/contact/"), ("Admission Process", "/admissions/", True)]),
        ]),
        side="r"),
]
add("home", "Home", home, order=1)

# ---------------------------------------------------------------- ABOUT
about = [
    p("Shri Ram College of Medical Science &amp; Research, Digrota (Mahendragarh), is a private, co-educational institution for nursing and allied health education. Through <strong>Shri Ram College of Nursing</strong> (degree programmes) and <strong>Shri Ram School of Nursing</strong> (diploma programmes), it has served students of Mahendragarh and the surrounding districts since 2012.", cls="has-large-font-size"),
    p("The college is approved by the Indian Nursing Council (INC), New Delhi, and the Haryana Nurses &amp; Midwives Council, and is affiliated to Pt. B.D. Sharma University of Health Sciences, Rohtak. The campus has spacious, fully furnished classrooms, well-established laboratories, a comprehensive library and an auditorium. Students also train at our own 100-bed hospital, which gives them the clinical exposure a good nurse needs."),
    p("The institution is run by <strong>Shri Ram Krishan Param Hans Shiksha Parishad</strong> and is part of the <strong>Shri Ram Group of Institutions (SRGI), Haryana</strong>. On the same campus, the group also runs <strong>Shri Ram Ayurvedic Medical College &amp; Hospital</strong>, offering the BAMS programme, approved by CCIM, New Delhi (Ministry of AYUSH) and affiliated to Shri Krishna AYUSH University, Kurukshetra."),
    todo("Please confirm the year each institution was established (online sources say 2012 for the group and 2019 for the College of Nursing) and the name of the managing trust or society."),

    split(
        ("sr-split__text", [
            group([h("Our Vision")], cls=icon_cls("eye", None, "sr-vision"), layout={"type": "default"}),
            p("To be a leading centre of nursing and paramedical education in rural Haryana, producing competent, ethical and compassionate healthcare professionals who serve their communities.", cls="has-large-font-size"),
        ]),
        ("sr-panel sr-panel--teal sr-icon sr-icon--accent ico-target", [
            h("Our Mission"),
            ul([
                "Deliver INC and university-standard education with strong clinical training",
                "Make quality healthcare education accessible to rural students, especially young women",
                "Instil empathy, discipline and professional ethics",
                "Serve the community through health camps and outreach",
            ], cls="sr-icon-list"),
        ]),
        side="r"),
    todo("The Vision and Mission above are drafts written for the website. Please review or replace them with the college's official statements."),

    section([
        head("Key facts", "At a glance", align="center"),
        table(None, [
            ["Location", "VPO Digrota, Nangal Mala Road, Tehsil Satnali, Distt. Mahendragarh, Haryana – 123024"],
            ["Managing society", "Shri Ram Krishan Param Hans Shiksha Parishad (Shri Ram Group of Institutions, Haryana)"],
            ["Type", "Private (self-financed), co-educational"],
            ["Approvals", "Indian Nursing Council (INC), New Delhi; Haryana Nurses &amp; Midwives Council (HNRC)"],
            ["Affiliation", "Pt. B.D. Sharma University of Health Sciences, Rohtak"],
            ["Programmes", "B.Sc Nursing, Post Basic B.Sc Nursing, B.Sc Paramedical Science, GNM, ANM"],
            ["Hospital", "Own 100-bed hospital for clinical training"],
            ["Residential", "Separate hostels for girls and boys"],
        ]),
    ], bg="light", size="960px"),

    wide([
        h("Leadership"),
        cols([
            [card([p("Chairman", cls="sr-tag"), h("Sh. Sukesh Diwan", 3), p("Chairman, Shri Ram Group of Institutions", cls="sr-meta")], icon="idcard", variant="soft")],
            [card([p("CEO", cls="sr-tag"), h("Sh. Manish Diwan", 3), p("Chief Executive Officer, Shri Ram Group of Institutions", cls="sr-meta")], icon="idcard", variant="soft")],
            [card([p("Director", cls="sr-tag"), h("Sh. Hawa Singh", 3), p("Director", cls="sr-meta")], icon="idcard", variant="soft")],
            [card([p("Principal", cls="sr-tag"), h("Name to be added", 3), todo("Principal's name, photo and message.")], icon="idcard", variant="soft")],
        ]),
        todo("Leadership names are taken from the college's 2018–19 admission notice posted on its Google listing. Please confirm they are current and send photos and messages."),
    ]),
]
add("about", "About the College", about, order=2, featured="main-gate")

# ---------------------------------------------------------------- COURSES
courses = [
    p("We offer degree and diploma programmes in nursing and allied health sciences. All nursing programmes are approved by the Indian Nursing Council and the Haryana Nurses &amp; Midwives Council. Degrees are awarded by Pt. B.D. Sharma University of Health Sciences, Rohtak.", cls="has-large-font-size"),
    wide([
        table(["Programme", "Level", "Duration", "Seats", "Minimum qualification"], [
            ['<a href="/courses/bsc-nursing/">B.Sc Nursing</a>', "UG Degree", "4 years", "50", "10+2 with PCB &amp; English (50%)"],
            ['<a href="/courses/post-basic-bsc-nursing/">Post Basic B.Sc Nursing</a>', "UG Degree", "2 years", "40", "10+2 + GNM, registered nurse &amp; midwife"],
            ['<a href="/courses/bsc-paramedical-science/">B.Sc Paramedical Science</a>', "UG Degree", "3 years", "50", "10+2 with Science"],
            ['<a href="/courses/gnm/">GNM</a>', "Diploma", "3 years", "As approved", "10+2 (any stream)"],
            ['<a href="/courses/anm/">ANM</a>', "Diploma", "2 years", "30", "10+2 (any stream)"],
            ["BAMS (Ayurveda) *", "UG Degree", "5½ years", "—", "10+2 with PCB + NEET"],
        ], caption="* BAMS is offered by Shri Ram Ayurvedic Medical College &amp; Hospital on the same campus (CCIM / Ministry of AYUSH; Shri Krishna AYUSH University, Kurukshetra). Seat numbers are the approved intake published by the regulators and may change each session."),
    ]),
    section([
        group([head("Programmes", "Explore each course"), COURSE_FILTER], cls="sr-courses-head",
              layout={"type": "flex", "flexWrap": "wrap", "justifyContent": "space-between", "verticalAlignment": "bottom"}),
        course_bento(),
    ], bg="light", size="1400px", cls="sr-courses"),
    cta_band("Not sure which course fits you?", "Our admissions team can guide you on eligibility, seats and career paths.",
             [("Talk to admissions", "/contact/"), ("Admission process", "/admissions/", True)]),
]
add("courses", "Courses", courses, order=3, featured="classroom-students")


def course_page(c, facts, eligibility, study, careers, extra=None):
    body = [
        p(c["blurb"], cls="has-large-font-size"),
        section([cols([
            [group([h("Key facts", 3)], cls=icon_cls("clipboard", "soft", "sr-feature"), layout={"type": "default"}), table(None, facts)],
            [group([h("Eligibility", 3)], cls=icon_cls("check", "soft", "sr-feature"), layout={"type": "default"}), ul(eligibility, cls="sr-icon-list")],
        ])], bg="light", pad={"top": "var:preset|spacing|50", "bottom": "var:preset|spacing|50"}),
        h("What you will study"),
        ul(study),
    ]
    if extra:
        body += extra
    body += [
        h("Career opportunities"),
        ul(careers),
        cta_band("Ready to apply?", "See the admission process, documents required and fees, or send us an enquiry.",
                 [("Admission process", "/admissions/"), ("Enquire now", "/contact/", True)]),
    ]
    add(c["slug"], c["name"], body, parent="courses", order=COURSES.index(c) + 1, featured=COURSE_PHOTOS[c["slug"]])


COURSE_PHOTOS = {c["slug"]: c["photo"] for c in COURSES}

NURSE_CAREERS = [
    "Staff nurse in government and private hospitals",
    "Community health nurse / public health programmes",
    "Military Nursing Service, railways and ESIC hospitals",
    "Nursing tutor (with higher qualifications)",
    "Opportunities abroad, including the Middle East and the UK, after licensing exams",
]

course_page(COURSES[0],
    [["Level", "Undergraduate degree"], ["Duration", "4 years (including internship)"], ["Seats", "50"],
     ["Affiliation", "Pt. B.D. Sharma UHS, Rohtak"], ["Approval", "INC &amp; HNRC"], ["Admission", "UHSR entrance test &amp; counselling"]],
    ["10+2 from a recognised board with Physics, Chemistry, Biology and English",
     "Minimum 50% aggregate in PCB (relaxation for SC/ST/OBC as per government norms)",
     "Minimum age 17 years on or before 31 December of the admission year",
     "Admission through the entrance test and counselling conducted by Pt. B.D. Sharma UHS, Rohtak"],
    ["Anatomy, physiology, biochemistry, microbiology and pharmacology",
     "Nursing foundations and adult health (medical-surgical) nursing",
     "Child health, mental health and community health nursing",
     "Midwifery and obstetrical nursing",
     "Nursing research, management and professional ethics",
     "Supervised clinical practice in our 100-bed hospital and the community"],
    NURSE_CAREERS + ["Higher studies: M.Sc Nursing, MBA in Hospital Management, MPH"])

course_page(COURSES[1],
    [["Level", "Undergraduate degree"], ["Duration", "2 years"], ["Seats", "40"],
     ["Affiliation", "Pt. B.D. Sharma UHS, Rohtak"], ["Approval", "INC &amp; HNRC"], ["Admission", "UHSR counselling"]],
    ["Passed 10+2 (Science stream preferred)",
     "Passed the GNM (General Nursing &amp; Midwifery) course",
     "Registered nurse and midwife with a State Nursing Registration Council"],
    ["Advanced nursing practice and nursing education",
     "Community health nursing",
     "Maternal, child and mental health nursing",
     "Introduction to nursing research and statistics",
     "Nursing administration and ward management"],
    ["Senior staff nurse and ward in-charge roles", "Public health and community nursing",
     "Nursing tutor / clinical instructor", "Higher studies: M.Sc Nursing"])

course_page(COURSES[2],
    [["Level", "Undergraduate degree"], ["Duration", "3 years"], ["Seats", "50"],
     ["Degree awarded by", "Pt. B.D. Sharma UHS, Rohtak"], ["Mode", "Full time"], ["Admission", "UHSR counselling / merit"]],
    ["10+2 with Science from a recognised board (CBSE, ISC, HBSE or equivalent)",
     "Other conditions as notified by Pt. B.D. Sharma UHS, Rohtak for the session"],
    ["Human anatomy, physiology and biochemistry",
     "Pathology and microbiology",
     "Specialisation subjects and hands-on laboratory work",
     "Hospital postings in diagnostic and operating departments"],
    ["Medical laboratory, radiology or operation theatre technologist", "Diagnostic centres and blood banks",
     "Hospital and emergency services", "Higher studies: M.Sc in the chosen allied-health field"],
    extra=[todo("Please list the specialisations offered under B.Sc Paramedical Science (e.g. Medical Lab Technology, Operation Theatre Technology, Radiology &amp; Imaging) with seats for each.")])

course_page(COURSES[3],
    [["Level", "Diploma"], ["Duration", "3 years"], ["Seats", "As approved by INC / HNRC"],
     ["Examining body", "Pt. B.D. Sharma UHS, Rohtak"], ["Approval", "INC &amp; HNRC"], ["Admission", "Merit"]],
    ["10+2 from a recognised board (Science preferred; other streams as per INC norms)",
     "Minimum age 17 years on or before 31 December of the admission year"],
    ["Bio-sciences and behavioural sciences",
     "Fundamentals of nursing and first aid",
     "Medical-surgical, community health and mental health nursing",
     "Child health nursing and midwifery",
     "Clinical practice in our hospital and community postings"],
    NURSE_CAREERS[:4] + ["Further study: Post Basic B.Sc Nursing"],
    extra=[todo("Please confirm the approved GNM intake (seats) for the current session.")])

course_page(COURSES[4],
    [["Level", "Diploma"], ["Duration", "2 years"], ["Seats", "30"],
     ["Regulated by", "HNRC &amp; INC"], ["Selection", "Merit based"], ["Mode", "Full time"]],
    ["10+2 in Arts, Science, Commerce or Health Care Science (Vocational) from a recognised board",
     "Students who passed 10+2 through the National Institute of Open Schooling (NIOS) may also apply",
     "Minimum age 17 years on or before 31 December of the admission year"],
    ["Community health nursing and health promotion",
     "Primary health care and first aid",
     "Child health nursing",
     "Midwifery and maternal care",
     "Health centre management"],
    ["ANM / health worker at sub-centres and PHCs", "National health programmes and immunisation drives",
     "Hospitals, nursing homes and maternity centres", "Further study: GNM and nursing degrees"])

# ---------------------------------------------------------------- ADMISSIONS
admissions = [
    p("Admissions to Shri Ram College of Nursing and Shri Ram School of Nursing follow the rules of the Indian Nursing Council, the Department of Medical Education &amp; Research (DMER), Haryana, and Pt. B.D. Sharma University of Health Sciences, Rohtak.", cls="has-large-font-size"),
    h("Admission process"),
    wide([cols([
        [card([h("B.Sc Nursing, Post Basic B.Sc &amp; B.Sc Paramedical", 3), ol([
            "Register for the entrance test / counselling on the UHSR admissions portal (uhsrcetadmissions.in) when it is notified.",
            "Appear in the entrance test (CET) conducted by Pt. B.D. Sharma UHS, Rohtak.",
            "Fill in choices during online counselling and select <em>Shri Ram College of Nursing, Digrota, Mahendergarh</em>.",
            "On allotment, report to the college with original documents and pay the fee within the given dates.",
        ]), p("Management-quota seats are filled as per state rules. Contact the college office for details.", cls="sr-meta")], icon="graduation")],
        [card([h("GNM &amp; ANM", 3), ol([
            "Obtain the application form from the college office (or enquire online).",
            "Admission is made on merit in the qualifying examination, as per HNRC / Govt. of Haryana norms.",
            "Attend document verification.",
            "Pay the fee and complete enrolment.",
        ])], icon="nurse", variant="accent")],
    ])]),
    h("Eligibility at a glance"),
    table(["Course", "Qualification", "Age"], [
        ["B.Sc Nursing", "10+2 with PCB + English, 50% in PCB (relaxation for reserved categories)", "17 years by 31 Dec"],
        ["Post Basic B.Sc Nursing", "10+2 + GNM; registered nurse &amp; midwife", "—"],
        ["B.Sc Paramedical Science", "10+2 with Science", "As per UHSR"],
        ["GNM", "10+2 (as per INC norms)", "17 years by 31 Dec"],
        ["ANM", "10+2 in any stream (incl. NIOS / vocational health care)", "17 years by 31 Dec"],
    ]),
    h("Documents required"),
    ul([
        "10th and 12th mark sheets and certificates (originals + 2 self-attested copies)",
        "Entrance test score card and allotment letter (B.Sc courses)",
        "Haryana domicile / resident certificate (for state-quota seats)",
        "Caste / category certificate, if applicable",
        "Aadhaar card and 6 recent passport-size photographs",
        "Character certificate from the last institution attended",
        "Migration certificate (for boards outside Haryana)",
        "Medical fitness certificate",
        "GNM certificate and nursing council registration (Post Basic B.Sc only)",
    ], cls="sr-icon-list"),
    todo("Please confirm this document list and add the admission office timings."),
    h("Frequently asked questions"),
    details("Is the college approved by the Indian Nursing Council?", [p("Yes. Our nursing programmes are approved by the Indian Nursing Council (INC), New Delhi, and the Haryana Nurses &amp; Midwives Council. See <a href=\"/approvals/\">Approvals &amp; Affiliations</a>.")]),
    details("Which university awards the degree?", [p("Degrees are awarded by Pt. B.D. Sharma University of Health Sciences (UHSR), Rohtak.")]),
    details("Is hostel accommodation available?", [p("Yes. There are separate hostels for girls and boys, with mess facilities and security.")]),
    details("Is the college co-educational?", [p("Yes. Both male and female candidates can apply, subject to the eligibility rules of each course.")]),
    details("Where do students do their clinical training?", [p("At our own 100-bed hospital, plus community health postings. See <a href=\"/hospital/\">Hospital</a>.")]),
    details("What are the fees?", [p("Fees follow the structure notified by the Government of Haryana. See <a href=\"/fee-structure/\">Fee Structure</a>.")]),
    split(
        ("sr-panel sr-panel--navy sr-icon sr-icon--accent ico-mail", [
            h("Admission enquiry"),
            p("Leave your details and our admissions office will call you back with guidance on eligibility, counselling dates, fees and hostels.", cls="sr-panel__lead"),
            ul(["Course and eligibility guidance", "Help with UHSR counselling", "Hostel and transport information"], cls="sr-icon-list"),
        ]),
        ("sr-split__text", ["{{CONTACT_FORM}}"]),
        side="l", cls="sr-split--light"),
]
add("admissions", "Admissions", admissions, order=4, featured="students-batch")

# ---------------------------------------------------------------- FEES
fees = [
    p("Fees at Shri Ram College of Nursing follow the fee structure for private colleges notified by the Government of Haryana (Haryana Govt. Gazette, 21 June 2024, Annexure-VI).", cls="has-large-font-size"),
    todo("Please add the college's own fee sheet for the current session (tuition, hostel, mess, transport) for every course, including GNM, ANM and B.Sc Paramedical."),
    h("Government-notified fee norms for private colleges"),
    table(["Fee head", "B.Sc &amp; Post Basic B.Sc Nursing (per year)"], [
        ["Tuition fee (incl. development charges)", "₹60,000, with an annual increase of 5%"],
        ["Library fee", "₹3,000"],
        ["Sports &amp; medical charges", "₹2,000"],
        ["Internet charges", "₹1,000"],
        ["Examination &amp; university charges", "As actual"],
        ["Hostel fee", "Not more than ₹60,000 or actual, whichever is less (no charge for fan &amp; lighting)"],
        ["Mess charges", "As actual"],
        ["Transport (if availed)", "As actual"],
        ["NRI seats (15%)", "USD 15,000 for the entire course"],
    ], caption='Source: Haryana Govt. Gazette (Extra.), 21 June 2024, Annexure-VI, <a href="{{FEE_PDF}}">download PDF</a>.'),
    p("Scholarships for SC/BC and other eligible students are available under Government of Haryana and central schemes, subject to their rules. Ask the college office for guidance on applying."),
    todo("Please confirm which scholarship schemes students of the college commonly use (e.g. Post-Matric Scholarship on the Haryana Saral / NSP portal)."),
]
add("fee-structure", "Fee Structure", fees, order=5, featured="campus-building")

# ---------------------------------------------------------------- APPROVALS
approvals = [
    p("Our programmes are approved by the national and state regulators for nursing education, and our degrees are awarded by the state health sciences university.", cls="has-large-font-size"),
    wide([cols([
        [card([p("National regulator", cls="sr-tag"), h("Indian Nursing Council, New Delhi", 3), p("Approves the B.Sc Nursing, Post Basic B.Sc Nursing, GNM and ANM programmes and their intake."), p('<a href="https://www.indiannursingcouncil.org" target="_blank" rel="noopener">indiannursingcouncil.org ↗</a>')], icon="shield")],
        [card([p("State council", cls="sr-tag"), h("Haryana Nurses &amp; Midwives Council", 3), p("Recognises the institution in Haryana and registers our graduates as nurses and midwives.")], icon="award")],
    ]), cols([
        [card([p("Affiliating university", cls="sr-tag"), h("Pt. B.D. Sharma University of Health Sciences, Rohtak", 3), p("Awards our degrees, conducts entrance tests, counselling and examinations (including GNM finals)."), p('<a href="https://www.uhsr.ac.in" target="_blank" rel="noopener">uhsr.ac.in ↗</a>')], icon="graduation")],
        [card([p("State government", cls="sr-tag"), h("DMER, Government of Haryana", 3), p("Recognition of the institution; admission counselling and fee norms for nursing colleges."), p('<a href="https://dmer.haryana.gov.in" target="_blank" rel="noopener">dmer.haryana.gov.in ↗</a>')], icon="file")],
    ])]),
    h("Approval documents"),
    table(["Document", "Reference / date", "Download"], [
        ["INC approval letter (current session)", "—", "—"],
        ["HNRC recognition letter", "—", "—"],
        ["UHSR affiliation letter", "—", "—"],
        ["Essentiality certificate / Govt. of Haryana NOC", "—", "—"],
    ]),
    todo("Please send scanned copies of these letters (PDF) so they can be uploaded and linked here."),
]
add("approvals", "Approvals &amp; Affiliations", approvals, order=6, featured="main-gate-2018")

# ---------------------------------------------------------------- HOSPITAL
hospital = [
    p("Shri Ram College has its own <strong>100-bed hospital</strong>, where students gain supervised, hands-on clinical experience, an essential part of becoming a confident professional nurse or technologist.", cls="has-large-font-size"),
    split(
        ("sr-panel sr-panel--navy", [
            p("Attached hospital", cls="sr-tag"),
            p("100", cls="sr-bignum__n"),
            p("beds for supervised clinical practice on our own campus.", cls="sr-panel__lead"),
        ]),
        ("sr-split__text", [
            head("On the wards", "Learning where care happens"),
            p("From the early semesters, students move from skill labs to real patients under the guidance of nursing faculty and hospital staff, building confidence one posting at a time."),
        ]),
        side="l"),
    wide([cols([
        [card([h("Clinical learning", 3), ul([
            "Bedside nursing care under qualified nursing faculty",
            "Rotations through medical, surgical, paediatric and maternity wards",
            "Exposure to emergency, operation theatre and diagnostic services",
            "Case studies, care plans and clinical presentations",
        ], cls="sr-icon-list")], icon="stethoscope")],
        [card([h("Community postings", 3), ul([
            "Community health nursing in the villages around Digrota",
            "Health surveys, immunisation and awareness drives",
            "Maternal and child health outreach",
            "Health camps organised by the college",
        ], cls="sr-icon-list")], icon="users", variant="accent")],
    ])]),
    mosaic(["hospital-ward", "emergency", "maternity-room", "skill-lab-bed", "hospital-ward-2", "ward-visit"]),
    h("Departments &amp; services"),
    todo("Please share the hospital's name, departments/specialities, number of doctors, and OPD timings, along with photographs."),
]
add("hospital", "Hospital", hospital, order=7, featured="hospital-building")

# ---------------------------------------------------------------- FACILITIES
FAC = [
    ("Classrooms", "monitor", "Spacious, fully furnished lecture halls with comfortable seating and advanced teaching aids."),
    ("Laboratories", "flask", "Labs with models, charts, specimens, microscopes and slides for anatomy, physiology and microbiology, plus nursing skill labs for practical training."),
    ("Audio-visual lab", "stage", "OHP, LCD projector, TV, posters, flannel boards, models and other teaching-learning material."),
    ("Library", "book", "A full library with 3,500+ medical and nursing books, 10 journals, Indian and international e-journals, newspapers and magazines."),
    ("Auditorium", "users", "A venue for seminars, workshops, guest lectures and cultural events."),
    ("Hostels", "home", "Separate hostels for girls and boys with mess facilities and security."),
    ("Canteen", "utensils", "A hygienic canteen serving meals and refreshments on campus."),
    ("Transport", "bus", "College buses connect the campus with nearby towns and villages."),
    ("Wi-Fi campus", "wifi", "Internet access for learning and research across the campus."),
    ("Gym &amp; sports", "dumbbell", "A gym and sports complex for fitness and recreation."),
    ("Hospital", "hospital", "Our own 100-bed hospital for clinical training."),
    ("Medical care", "firstaid", "Medical facilities for students on campus."),
]
FAC_PHOTOS = {"Classrooms": "classroom", "Laboratories": "anatomy-models", "Audio-visual lab": "lab-hall",
              "Library": "library", "Hospital": "hospital-ward", "Medical care": "emergency"}
facilities = [
    p("Our campus at Digrota is designed for focused study, practical training and a safe residential life.", cls="has-large-font-size"),
    todo("Please share photographs of the hostels, canteen, buses, auditorium and sports facilities, and the bus routes served."),
    section([grid([card(([photo(FAC_PHOTOS[t], cls="sr-card__img")] if t in FAC_PHOTOS else []) + [h(t, 3), p(d)],
                        icon=None if t in FAC_PHOTOS else i, variant="accent" if n % 2 else None,
                        cls="sr-card--photo" if t in FAC_PHOTOS else None) for n, (t, i, d) in enumerate(FAC)], 4, align=None)],
            bg="light", size="1400px"),
    cta_band("See the campus for yourself", "Visitors and parents are welcome. Contact the college office to plan a visit.",
             [("Plan a visit", "/contact/")]),
]
add("campus-facilities", "Campus &amp; Facilities", facilities, order=8, featured="campus-wide")

# ---------------------------------------------------------------- FACULTY
faculty = [
    p("Our teaching team of qualified nursing and medical faculty is led by the Principal, as required by Indian Nursing Council norms."),
    table(["Name", "Designation", "Qualification", "Experience"], [
        ["—", "Principal", "—", "—"],
        ["—", "Vice Principal", "—", "—"],
        ["—", "Professor / Associate Professor", "—", "—"],
        ["—", "Assistant Professor / Tutor", "—", "—"],
    ]),
    todo("Please share the faculty list (name, designation, qualification, experience, photo)."),
]
add("faculty", "Faculty", faculty, order=9, featured="classroom")

# ---------------------------------------------------------------- GALLERY
gallery = [
    p("A glimpse of life at Shri Ram College: the campus, our hospital and labs, and our students.", cls="has-large-font-size"),
    h("Campus"),
    mosaic(["campus-wide", "main-gate", "campus-building", "hospital-building", "campus-evening", "main-gate-2018"]),
    h("Hospital &amp; laboratories"),
    mosaic(["hospital-ward", "emergency", "nursing-foundation-lab", "anatomy-models", "obstetric-models", "nutrition-lab",
            "library", "herbal-lab", "anatomy-mannequin"]),
    h("Student life"),
    mosaic(["students-group", "students-batch", "students-lawn", "classroom-students", "skill-practice", "farewell-2024",
            "lamp-ceremony-stage", "cultural-event", "library-hall"]),
    todo("Photos are from the college's Google Maps listing. Photos credited to other people were posted by visitors; get their permission (or replace them) before launch."),
]
add("gallery", "Gallery", gallery, order=10, featured="students-lawn")

# ---------------------------------------------------------------- CONTACT
contact = [
    wide([cols([
        [card([h("Address", 3), p("Shri Ram College of Medical Science &amp; Research<br>VPO Digrota, Nangal Mala Road<br>Tehsil Satnali, Distt. Mahendragarh<br>Haryana – 123024"),
               p('<a href="https://www.google.com/maps?q=28.365143,76.040255" target="_blank" rel="noopener">Open in Google Maps ↗</a>')], icon="pin")],
        [card([h("Phone &amp; email", 3), p('Phone: [sr_contact field="phone"]'), p('Mobile: <a href="tel:+918930132210">089301 32210</a>'), p('Email: [sr_contact field="email"]'), p("Office hours: from 9:00 AM", cls="sr-meta")], icon="phone", variant="accent")],
        [card([h("How to reach", 3), ul([
            "About 50 km by road from Mahendragarh town, via Satnali",
            "Nearest railway station: Nanwan (NWN)",
            "Nearest major airport: IGI Airport, New Delhi",
            "College buses available on nearby routes",
        ])], icon="train")],
    ])], margin_top="0"),
    group([html(f'<div class="sr-map sr-map-full"><iframe title="{t("Map to Shri Ram College, Digrota")}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" src="https://maps.google.com/maps?q=28.365143,76.040255&amp;z=13&amp;output=embed"></iframe></div>')], align="full", layout={"type": "default"}),
    group([
        head("Enquiry", "Send us an enquiry", "Questions about admissions, courses, fees or hostels? Fill in the form and we will get back to you.", align="center"),
        "{{CONTACT_FORM}}",
    ], cls="sr-narrow", layout={"type": "default"}),
]
add("contact", "Contact Us", contact, order=11, featured="campus-evening")

# ---------------------------------------------------------------- MANDATORY DISCLOSURE
disclosure = [
    p("Information disclosed in line with the requirements of the Indian Nursing Council and the affiliating university."),
    table(["Item", "Details"], [
        ["Name of institution", "Shri Ram College of Nursing / Shri Ram School of Nursing (Shri Ram College of Medical Science &amp; Research)"],
        ["Address", "VPO Digrota, Nangal Mala Road, Tehsil Satnali, Distt. Mahendragarh, Haryana – 123024"],
        ["Managing society", "Shri Ram Krishan Param Hans Shiksha Parishad"],
        ["Year of establishment", "—"],
        ["Approvals", "Indian Nursing Council; Haryana Nurses &amp; Midwives Council"],
        ["Affiliating university", "Pt. B.D. Sharma University of Health Sciences, Rohtak"],
        ["Courses &amp; intake", "B.Sc Nursing (50), Post Basic B.Sc Nursing (40), B.Sc Paramedical Science (50), ANM (30), GNM (—)"],
        ["Parent hospital", "Own 100-bed hospital"],
        ["Principal", "—"],
        ["Fee structure", '<a href="/fee-structure/">See Fee Structure</a>'],
        ["Anti-ragging committee", "—"],
        ["Grievance redressal / Internal complaints committee", "—"],
    ]),
    todo("Please fill in the blank rows and send committee member lists, so this page meets the regulator's disclosure requirements."),
]
add("mandatory-disclosure", "Mandatory Disclosure", disclosure, order=12, featured="corridor")

# Notices: the English page is the posts page (content comes from the home.html template).
# The Hindi page lists the same notices with its own query block.
add("notices", "Notices", [] if LANG == "en" else [
    p("Admission notices, examination schedules, results and campus news.", cls="has-large-font-size"),
    '<!-- wp:query {"queryId":3,"query":{"perPage":12,"postType":"post","order":"desc","orderBy":"date","inherit":false},"className":"sr-notices"} -->\n'
    '<div class="wp-block-query sr-notices">\n'
    '<!-- wp:post-template -->\n<!-- wp:post-date {"fontSize":"small"} /-->\n<!-- wp:post-title {"isLink":true,"level":2} /-->\n'
    '<!-- wp:post-excerpt {"excerptLength":30} /-->\n<!-- /wp:post-template -->\n'
    '<!-- wp:query-pagination {"layout":{"type":"flex","justifyContent":"center"}} -->\n<!-- wp:query-pagination-previous /-->\n'
    '<!-- wp:query-pagination-numbers /-->\n<!-- wp:query-pagination-next /-->\n<!-- /wp:query-pagination -->\n'
    '<!-- wp:query-no-results -->\n' + p("No notices have been published yet.") + '\n<!-- /wp:query-no-results -->\n'
    '</div>\n<!-- /wp:query -->',
], order=13)

if MISSING:
    sys.exit("Missing Hindi text in tools/hindi.py for:\n" + "\n".join(f"  {m!r}" for m in dict.fromkeys(MISSING)))

if LANG == "hi":
    # Hindi alt text for featured images (page banners), stored on each photo by load-pages.php.
    with open(os.path.join(ROOT, "content", "photo-alt-hi.json"), "w", encoding="utf-8") as f:
        json.dump({slug: t(ph["alt"]) for slug, ph in PHOTOS.items()}, f, indent=1, ensure_ascii=False)
    json.dump(pages, sys.stdout, ensure_ascii=False)
    sys.exit(0)

hindi = subprocess.run([sys.executable, os.path.abspath(__file__)], env={**os.environ, "SR_LANG": "hi"},
                       capture_output=True, text=True)
if hindi.returncode:
    sys.exit(hindi.stderr)
pages += json.loads(hindi.stdout)
with open(os.path.join(ROOT, "content", "pages.json"), "w", encoding="utf-8") as f:
    json.dump(pages, f, indent=2, ensure_ascii=False)
print(f"Wrote {len(pages)} pages ({sum(pg['lang'] == 'hi' for pg in pages)} in Hindi) to {OUT}")
