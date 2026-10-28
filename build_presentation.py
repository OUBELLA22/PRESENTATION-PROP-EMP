#!/usr/bin/env python3
"""Generate Smart_Car_W2_Instrumentation.pptx using only the Python standard library."""
import zipfile
from xml.sax.saxutils import escape

OUT = "Smart_Car_W2_Instrumentation.pptx"
EMU = 914400  # EMU per inch
SW, SH = 13.333, 7.5

NAVY, BLUE, CYAN = "0B2A4A", "0070AD", "12ABDB"
LIGHT, GREY, WHITE = "EEF5FB", "5A6772", "FFFFFF"
GREEN, LGREEN = "2E9E5B", "E8F5EE"
ORANGE, LORANGE = "E07B00", "FDF1E3"
RED, LRED = "C0392B", "FBECEA"
FONT = "Calibri"

NS = ('xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
      'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"')


def e(v):
    return str(int(round(v * EMU)))


class P:
    """A paragraph. text: str or list of (text, dict(b=, color=, sz=, i=))."""

    def __init__(self, text, sz=14, color=NAVY, b=False, i=False, algn="l",
                 bullet=False, before=0, bucolor=CYAN):
        self.runs = [(text, {})] if isinstance(text, str) else text
        self.sz, self.color, self.b, self.i = sz, color, b, i
        self.algn, self.bullet, self.before, self.bucolor = algn, bullet, before, bucolor

    def xml(self):
        ppr = f'<a:pPr algn="{self.algn}"'
        if self.bullet:
            ppr += ' marL="228600" indent="-228600"'
        ppr += '>'
        if self.before:
            ppr += f'<a:spcBef><a:spcPts val="{int(self.before * 100)}"/></a:spcBef>'
        if self.bullet:
            ppr += (f'<a:buClr><a:srgbClr val="{self.bucolor}"/></a:buClr>'
                    '<a:buFont typeface="Arial"/><a:buChar char="&#8226;"/>')
        else:
            ppr += '<a:buNone/>'
        ppr += '</a:pPr>'
        runs = ""
        for text, o in self.runs:
            sz = o.get("sz", self.sz)
            b = o.get("b", self.b)
            i = o.get("i", self.i)
            c = o.get("color", self.color)
            runs += (f'<a:r><a:rPr lang="fr-FR" sz="{int(sz * 100)}" b="{1 if b else 0}" '
                     f'i="{1 if i else 0}" dirty="0"><a:solidFill><a:srgbClr val="{c}"/></a:solidFill>'
                     f'<a:latin typeface="{FONT}"/><a:cs typeface="{FONT}"/></a:rPr>'
                     f'<a:t>{escape(text)}</a:t></a:r>')
        end = f'<a:endParaRPr lang="fr-FR" sz="{int(self.sz * 100)}" dirty="0"/>'
        return f'<a:p>{ppr}{runs}{end}</a:p>'


class Slide:
    def __init__(self, bg=WHITE):
        self.bg = bg
        self.items = []
        self.nid = 2

    def shape(self, x, y, w, h, paras=None, fill=None, line=None, lw=1.0,
              geom="rect", anchor="t", inset=0.1, adj=None):
        sid = self.nid
        self.nid += 1
        av = "<a:avLst/>" if adj is None else f'<a:avLst><a:gd name="adj" fmla="val {adj}"/></a:avLst>'
        fill_xml = f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>' if fill else '<a:noFill/>'
        line_xml = (f'<a:ln w="{int(lw * 12700)}"><a:solidFill><a:srgbClr val="{line}"/></a:solidFill></a:ln>'
                    if line else '<a:ln><a:noFill/></a:ln>')
        ins = e(inset)
        body = "".join(p.xml() for p in (paras or [])) or '<a:p><a:endParaRPr lang="fr-FR" dirty="0"/></a:p>'
        self.items.append(
            f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="Shape {sid}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{e(x)}" y="{e(y)}"/><a:ext cx="{e(w)}" cy="{e(h)}"/></a:xfrm>'
            f'<a:prstGeom prst="{geom}">{av}</a:prstGeom>{fill_xml}{line_xml}</p:spPr>'
            f'<p:txBody><a:bodyPr wrap="square" lIns="{ins}" tIns="{ins}" rIns="{ins}" bIns="{ins}" '
            f'anchor="{anchor}" rtlCol="0"><a:noAutofit/></a:bodyPr><a:lstStyle/>{body}</p:txBody></p:sp>')

    def text(self, x, y, w, h, paras, anchor="t", inset=0.05):
        self.shape(x, y, w, h, paras, anchor=anchor, inset=inset)

    def xml(self):
        return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:sld {NS}><p:cSld>'
                f'<p:bg><p:bgPr><a:solidFill><a:srgbClr val="{self.bg}"/></a:solidFill><a:effectLst/></p:bgPr></p:bg>'
                '<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
                '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/>'
                '<a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
                + "".join(self.items) +
                '</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>')


slides = []


def content_slide(num, title, subtitle=None):
    s = Slide()
    s.shape(0, 0, SW, 0.12, fill=BLUE)
    s.shape(0.5, 0.4, 0.95, 0.75, [P(num, 26, WHITE, b=True, algn="ctr")], fill=CYAN, anchor="ctr", inset=0)
    s.text(1.65, 0.35, 11.2, 0.6, [P(title, 26, NAVY, b=True)], anchor="ctr")
    if subtitle:
        s.text(1.65, 0.88, 11.2, 0.4, [P(subtitle, 14, GREY, i=True)], anchor="ctr")
    s.shape(0.5, 1.35, SW - 1.0, 0.03, fill=CYAN)
    s.text(0.5, 7.0, 9, 0.35, [P("Smart_Car_W2  |  Optimisation de la connexion instrumentation  |  STELLANTIS × Capgemini",
                                 10, GREY)], anchor="ctr")
    s.text(SW - 1.5, 7.0, 1.0, 0.35, [P(str(len(slides) + 1), 10, GREY, algn="r")], anchor="ctr")
    return s


def header_box(s, x, y, w, h, title, color, light, paras, title_h=0.5):
    s.shape(x, y, w, title_h, [P(title, 16, WHITE, b=True)], fill=color, anchor="ctr", inset=0.15)
    s.shape(x, y + title_h, w, h - title_h, paras, fill=light, anchor="t", inset=0.18)


# ---------------------------------------------------------------- 1. Title
s = Slide(bg=NAVY)
s.shape(0, 0, 0.25, SH, fill=CYAN)
s.text(0.9, 0.8, 11, 0.4, [P("STELLANTIS  ×  Capgemini", 16, CYAN, b=True)])
s.text(0.9, 1.6, 11.5, 1.0, [P("Smart_Car_W2", 48, WHITE, b=True)])
s.text(0.9, 2.6, 11.5, 0.8, [P("Optimisation de la connexion instrumentation", 30, WHITE)])
s.shape(0.9, 3.55, 2.0, 0.05, fill=CYAN)
s.text(0.9, 3.8, 11.0, 0.9, [P("Suppression du connecteur instrumentation du faisceau planche de bord "
                               "et accès à la fonction via une bretelle dédiée et détachable.", 18, "C9D6E3")])
s.shape(0.9, 5.2, 4.6, 0.6, [P("Catégorie : Amélioration / Innovation", 16, NAVY, b=True, algn="ctr")],
        fill=CYAN, geom="roundRect", anchor="ctr", adj=30000)
s.shape(5.8, 5.2, 3.6, 0.6, [P("CC21  ·  CC24  ·  OV24", 16, WHITE, b=True, algn="ctr")],
        line=CYAN, lw=1.5, geom="roundRect", anchor="ctr", adj=30000)
slides.append(s)

# ---------------------------------------------------------------- 2. Synthèse
s = content_slide("★", "Catégorie · Réalisations · Impact", "Synthèse de la contribution")
s.shape(0.5, 1.6, SW - 1.0, 0.6,
        [P([("Catégorie :  ", {"b": True, "color": NAVY}),
            ("Amélioration", {"b": True, "color": BLUE}),
            ("  (optimisation de l'architecture faisceau)   +   ", {"color": GREY}),
            ("Innovation", {"b": True, "color": BLUE}),
            ("  (solution bretelle réutilisable)", {"color": GREY})], 16)],
        fill=LIGHT, geom="roundRect", anchor="ctr", inset=0.2, adj=20000)
header_box(s, 0.5, 2.45, 6.05, 4.35, "Réalisations", BLUE, LIGHT, [
    P("Conception d'une solution bretelle détachable remplaçant le connecteur instrumentation "
      "du faisceau planche de bord standard.", 14, bullet=True),
    P("Déclinaison de la solution sur les trois silhouettes : CC21, CC24 et OV24.", 14, bullet=True, before=8),
    P("Réalisation d'un premier prototype, testé et validé par le responsable des essais véhicules.",
      14, bullet=True, before=8),
    P("Analyse de l'impact industriel en pré-série (temps de cycle, poste, opérateur).", 14, bullet=True, before=8),
    P("Définition d'une stratégie de déploiement par jalon : F06/26, F11/26 et F03/27.", 14, bullet=True, before=8),
])
header_box(s, 6.78, 2.45, 6.05, 4.35, "Impact", GREEN, LGREEN, [
    P([("Impact TPC estimé ≈ -6 € ", {"b": True}), ("lié à la suppression du connecteur.", {})],
      14, bullet=True, bucolor=GREEN),
    P([("Cybersécurité : ", {"b": True}), ("plus d'accès permanent à la fonction instrumentation.", {})],
      14, bullet=True, before=8, bucolor=GREEN),
    P([("Prise diag conservée : ", {"b": True}), ("diagnostic et contrôles électriques toujours possibles.", {})],
      14, bullet=True, before=8, bucolor=GREEN),
    P([("Prototype sans défaut ", {"b": True}), ("constaté pendant les essais.", {})],
      14, bullet=True, before=8, bucolor=GREEN),
    P([("Approche réutilisable : ", {"b": True}),
       ("l'équipe essais souhaite l'appliquer à d'autres projets.", {})],
      14, bullet=True, before=8, bucolor=GREEN),
])
slides.append(s)

# ---------------------------------------------------------------- 3. Plan
s = content_slide("≡", "Plan")
plan = [("01", "Contexte & Objectif"), ("02", "Challenges & Solutions"), ("03", "Prototype & Validation"),
        ("04", "Faisabilité industrielle"), ("05", "Stratégie retenue"), ("06", "Impact")]
for idx, (n, t) in enumerate(plan):
    col, row = idx % 2, idx // 2
    x, y = 0.9 + col * 6.1, 1.85 + row * 1.6
    s.text(x, y, 1.4, 1.1, [P(n, 44, CYAN, b=True)], anchor="ctr")
    s.shape(x + 1.45, y + 0.2, 0.04, 0.7, fill=BLUE)
    s.text(x + 1.65, y, 4.2, 1.1, [P(t, 22, NAVY, b=True)], anchor="ctr")
slides.append(s)

# ---------------------------------------------------------------- 4. Contexte
s = content_slide("01", "Contexte & Objectif", "Pourquoi changer l'architecture de connexion instrumentation ?")
s.text(0.5, 1.6, 6.2, 2.4, [
    P([("Smart_Car_W2", {"b": True}), (" est l'un des projets stratégiques du groupe STELLANTIS.", {})], 15),
    P([("Objectif : ", {"b": True, "color": BLUE}),
       ("retirer le connecteur instrumentation du faisceau planche de bord standard et le remplacer "
        "par une petite bretelle détachable, utilisée uniquement lorsque l'accès à la fonction "
        "instrumentation est nécessaire.", {})], 15, before=10),
])
s.text(0.5, 4.0, 6.2, 0.4, [P("Silhouettes concernées", 14, GREY, b=True)])
for k, v in enumerate(["CC21", "CC24", "OV24"]):
    s.shape(0.5 + k * 2.0, 4.45, 1.8, 0.6, [P(v, 18, WHITE, b=True, algn="ctr")],
            fill=BLUE, geom="roundRect", anchor="ctr", adj=25000)
s.shape(0.5, 5.4, 6.2, 1.3, [
    P("Point clé", 14, GREEN, b=True),
    P("La prise diag est conservée sur le véhicule : les contrôles électriques et les opérations "
      "de diagnostic restent possibles.", 14, before=4)], fill=LGREEN, line=GREEN, inset=0.18)
# Avant / Après
header_box(s, 7.2, 1.6, 5.63, 2.15, "AVANT", RED, LRED, [
    P("Faisceau planche de bord standard", 15, b=True),
    P("Connecteur instrumentation intégré en permanence sur chaque faisceau.", 14, before=6)])
s.shape(9.6, 3.85, 0.8, 0.6, fill=CYAN, geom="downArrow")
header_box(s, 7.2, 4.55, 5.63, 2.15, "APRÈS", GREEN, LGREEN, [
    P("Faisceau standard sans connecteur instrumentation", 15, b=True),
    P("+ Bretelle détachable, branchée uniquement lorsque l'accès instrumentation est requis.", 14, before=6)])
slides.append(s)

# ---------------------------------------------------------------- 5. Challenges & Solutions
s = content_slide("02", "Challenges & Solutions", "Coût · Cybersécurité · Diversité · Faisabilité industrielle")
cols = [(0.5, 2.4, "Enjeu"), (2.95, 5.15, "Challenges"), (8.15, 4.68, "Solutions")]
for x, w, t in cols:
    s.shape(x, 1.6, w - 0.05, 0.5, [P(t, 16, WHITE, b=True)], fill=NAVY if t == "Enjeu" else
            (RED if t == "Challenges" else GREEN), anchor="ctr", inset=0.15)
rows = [
    ("Coût", "Connecteur instrumentation présent sur chaque faisceau planche de bord.",
     "Suppression du connecteur : impact TPC estimé ≈ -6 €."),
    ("Cybersécurité", "Accès permanent à la fonction instrumentation, en conflit avec la contrainte cyber.",
     "Accès à la fonction uniquement via la bretelle, lorsque nécessaire."),
    ("Diversité", "Après le breakpoint, le faisceau est livré en PN fini : pas de gestion par codage. "
                  "Impact sur la famille faisceau IP / références PDB.",
     "Création de nouvelles références sans connecteur, introduites par jalon."),
    ("Faisabilité industrielle", "La bretelle devrait être branchée / débranchée sur 100 % des véhicules pré-série.",
     "Stratégie mixte : connecteur conservé en F06/26, bretelle à partir de F11/26."),
]
y = 2.15
for k, (a, b, c) in enumerate(rows):
    h = 0.98
    bg = LIGHT if k % 2 == 0 else WHITE
    s.shape(0.5, y, 2.35, h, [P(a, 15, BLUE, b=True)], fill=bg, anchor="ctr", inset=0.15)
    s.shape(2.95, y, 5.1, h, [P(b, 13)], fill=bg, anchor="ctr", inset=0.15)
    s.shape(8.15, y, 4.63, h, [P(c, 13, b=True, color=GREEN)], fill=bg, anchor="ctr", inset=0.15)
    y += h + 0.04
s.shape(0.5, 6.35, SW - 1.0, 0.55,
        [P("Objectif : réduire le coût et maîtriser la cybersécurité, tout en gardant un accès contrôlé "
           "à la fonction instrumentation.", 15, WHITE, b=True, algn="ctr")],
        fill=BLUE, geom="roundRect", anchor="ctr", adj=20000)
slides.append(s)

# ---------------------------------------------------------------- 6. Prototype
s = content_slide("03", "Prototype & Validation", "Une solution testée sur véhicule")
steps = [("1", "Prototype", "Premier prototype réalisé sans connexions GND ni PWR dédiées."),
         ("2", "Essais", "Fonctionnement correct, aucun défaut constaté pendant les essais."),
         ("3", "Validation", "Prototype validé par le responsable des essais véhicules.")]
for k, (n, t, d) in enumerate(steps):
    x = 0.5 + k * 4.18
    s.shape(x, 1.75, 3.9, 3.0, [
        P(t, 20, NAVY, b=True, algn="ctr"),
        P(d, 15, GREY, algn="ctr", before=10)], fill=LIGHT, geom="roundRect", anchor="ctr", inset=0.25, adj=8000)
    s.shape(x + 1.55, 1.45, 0.8, 0.8, [P(n, 22, WHITE, b=True, algn="ctr")],
            fill=CYAN, geom="ellipse", anchor="ctr", inset=0)
    if k < 2:
        s.shape(x + 3.92, 3.05, 0.24, 0.4, fill=BLUE, geom="rightArrow")
s.shape(0.5, 5.05, SW - 1.0, 0.95, [
    P([("Retour de l'équipe essais : ", {"b": True, "color": GREEN}),
       ("elle souhaite voir la même approche appliquée à d'autres projets, "
        "ce qui ouvre un potentiel de réutilisation et de standardisation.", {})], 16)],
    fill=LGREEN, line=GREEN, geom="roundRect", anchor="ctr", inset=0.25, adj=15000)
s.text(0.5, 6.2, SW - 1.0, 0.5, [P([("Solution déclinée sur les trois silhouettes : ", {"color": GREY}),
                                     ("CC21 · CC24 · OV24", {"b": True, "color": BLUE})], 15, algn="ctr")],
       anchor="ctr")
slides.append(s)

# ---------------------------------------------------------------- 7. Faisabilité industrielle
s = content_slide("04", "Faisabilité industrielle",
                  "Pourquoi la bretelle n'est pas généralisée à toute la pré-série ?")
s.text(0.5, 1.55, 12, 0.45, [P("Séquence nécessaire en pré-série avec la bretelle :", 15, NAVY, b=True)])
flow = ["Brancher la bretelle", "Réaliser le test instrumentation", "Débrancher la bretelle",
        "Contrôle avant la suite du flux"]
for k, t in enumerate(flow):
    s.shape(0.5 + k * 3.1, 2.05, 3.2, 1.05, [P(t, 14, WHITE, b=True, algn="ctr")],
            fill=BLUE if k % 2 == 0 else CYAN, geom="chevron" if k else "homePlate",
            anchor="ctr", inset=0.35, adj=30000)
s.shape(0.5, 3.3, SW - 1.0, 0.55,
        [P([("À répéter sur ", {}), ("100 % des véhicules pré-série", {"b": True, "color": ORANGE}),
            (", et non sur quelques véhicules ciblés.", {})], 16, algn="ctr")],
        fill=LORANGE, geom="roundRect", anchor="ctr", adj=20000)
impacts = [("+ Temps de cycle", "Allongement du cycle de production"),
           ("+ 1 poste de travail", "Poste supplémentaire nécessaire en ligne"),
           ("+ 1 opérateur", "Opérateur supplémentaire en ligne de production")]
for k, (t, d) in enumerate(impacts):
    x = 0.5 + k * 4.18
    s.shape(x, 4.1, 3.9, 1.35, [P(t, 20, ORANGE, b=True, algn="ctr"), P(d, 13, GREY, algn="ctr", before=4)],
            fill=WHITE, line=ORANGE, lw=1.5, geom="roundRect", anchor="ctr", adj=10000)
s.text(0.5, 5.65, SW - 1.0, 0.4, [P("Le défi n'est pas seulement technique : il faut trouver l'équilibre entre",
                                     14, GREY, algn="ctr")], anchor="ctr")
pills = ["Optimisation technique", "Coût", "Cybersécurité", "Faisabilité industrielle"]
pw, gap = 2.6, 0.6
x0 = (SW - (4 * pw + 3 * gap)) / 2
for k, t in enumerate(pills):
    x = x0 + k * (pw + gap)
    s.shape(x, 6.1, pw, 0.6, [P(t, 14, WHITE, b=True, algn="ctr")], fill=NAVY, geom="roundRect",
            anchor="ctr", inset=0.05, adj=40000)
    if k < 3:
        s.shape(x + pw + 0.08, 6.25, gap - 0.16, 0.3, fill=CYAN, geom="leftRightArrow")
slides.append(s)

# ---------------------------------------------------------------- 8. Stratégie retenue
s = content_slide("05", "Stratégie retenue", "Une stratégie mixte et maîtrisée, par jalon")
s.shape(0.8, 2.25, 11.7, 0.12, fill=GREY)
s.shape(12.4, 2.06, 0.35, 0.5, fill=GREY, geom="rightArrow")
for x, label, color in [(3.3, "F06/26", BLUE), (9.6, "F11/26  &  F03/27", GREEN)]:
    s.shape(x - 0.25, 2.06, 0.5, 0.5, fill=color, geom="ellipse")
    s.text(x - 2.0, 1.5, 4.0, 0.5, [P(label, 20, color, b=True, algn="ctr")], anchor="ctr")
header_box(s, 0.5, 2.85, 5.95, 3.15, "Références existantes AVEC connecteur", BLUE, LIGHT, [
    P("Les références existantes sont prolongées avec le connecteur instrumentation.", 14, b=True),
    P("Pourquoi :", 14, BLUE, b=True, before=10),
    P("Pas de nouvelle introduction critique prévue dans les phases suivantes.", 14, bullet=True, before=4),
    P("Exception possible pour une modification gérée en GRAV B hors fenêtre.", 14, bullet=True, before=4),
])
header_box(s, 6.88, 2.85, 5.95, 3.15, "Nouvelles références SANS connecteur", GREEN, LGREEN, [
    P("Les nouvelles références sont créées sans le connecteur instrumentation.", 14, b=True),
    P("Accès à la fonction :", 14, GREEN, b=True, before=10),
    P("Via la bretelle dédiée, uniquement lorsque nécessaire.", 14, bullet=True, before=4, bucolor=GREEN),
    P("Prise diag conservée pour le diagnostic et les contrôles électriques.", 14, bullet=True, before=4,
      bucolor=GREEN),
])
s.shape(0.5, 6.2, SW - 1.0, 0.6,
        [P("La solution technique a été adaptée aux contraintes industrielles et au planning projet, "
           "au lieu d'être imposée en production.", 15, WHITE, b=True, algn="ctr")],
        fill=NAVY, geom="roundRect", anchor="ctr", adj=20000)
slides.append(s)

# ---------------------------------------------------------------- 9. Impact
s = content_slide("06", "Impact", "Résultats et bénéfices")
cards = [("≈ -6 €", "Impact TPC estimé lié à la suppression du connecteur", GREEN),
         ("Cyber", "Accès instrumentation maîtrisé, plus d'accès permanent", BLUE),
         ("3", "Silhouettes couvertes : CC21, CC24, OV24", BLUE),
         ("0", "Défaut constaté sur le prototype pendant les essais", GREEN),
         ("Réutilisable", "Approche souhaitée par l'équipe essais pour d'autres projets", CYAN)]
cw, cg = 2.33, 0.2
for k, (big, d, c) in enumerate(cards):
    x = 0.5 + k * (cw + cg)
    s.shape(x, 1.75, cw, 3.2, fill=LIGHT, geom="roundRect", adj=8000)
    s.shape(x, 1.75, cw, 0.12, fill=c)
    s.text(x + 0.1, 2.1, cw - 0.2, 1.1, [P(big, 30 if len(big) < 8 else 22, c, b=True, algn="ctr")],
           anchor="ctr")
    s.text(x + 0.15, 3.3, cw - 0.3, 1.5, [P(d, 14, NAVY, algn="ctr")], anchor="t")
s.shape(0.5, 5.25, SW - 1.0, 1.4, [
    P("En résumé", 16, CYAN, b=True),
    P("Une architecture faisceau optimisée qui réduit le coût et maîtrise l'accès à la fonction instrumentation, "
      "tout en conservant la prise diag, avec un déploiement adapté aux contraintes industrielles.",
      15, WHITE, before=4)], fill=NAVY, geom="roundRect", anchor="ctr", inset=0.25, adj=12000)
slides.append(s)

# ---------------------------------------------------------------- 10. Merci
s = Slide(bg=NAVY)
s.shape(0, 0, 0.25, SH, fill=CYAN)
s.text(0.9, 2.4, 11.5, 1.2, [P("Merci", 54, WHITE, b=True)])
s.text(0.9, 3.6, 11.5, 0.8, [P("Questions ?", 30, CYAN)])
s.text(0.9, 5.6, 11.5, 0.5, [P("Smart_Car_W2  |  Optimisation de la connexion instrumentation", 14, "C9D6E3")])
slides.append(s)

# ================================================================ package parts
N = len(slides)
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "application/vnd.openxmlformats-officedocument.presentationml"

content_types = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                 '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                 '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                 '<Default Extension="xml" ContentType="application/xml"/>'
                 f'<Override PartName="/ppt/presentation.xml" ContentType="{CT}.presentation.main+xml"/>'
                 f'<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="{CT}.slideMaster+xml"/>'
                 f'<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="{CT}.slideLayout+xml"/>'
                 '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>'
                 f'<Override PartName="/ppt/presProps.xml" ContentType="{CT}.presProps+xml"/>'
                 f'<Override PartName="/ppt/viewProps.xml" ContentType="{CT}.viewProps+xml"/>'
                 f'<Override PartName="/ppt/tableStyles.xml" ContentType="{CT}.tableStyles+xml"/>'
                 '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
                 '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
                 + "".join(f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="{CT}.slide+xml"/>'
                           for i in range(1, N + 1)) + '</Types>')

root_rels = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="{PKG_REL}">'
             f'<Relationship Id="rId1" Type="{REL}/officeDocument" Target="ppt/presentation.xml"/>'
             f'<Relationship Id="rId2" Type="{PKG_REL}/metadata/core-properties" Target="docProps/core.xml"/>'
             f'<Relationship Id="rId3" Type="{REL}/extended-properties" Target="docProps/app.xml"/>'
             '</Relationships>')

core = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        '<dc:title>Smart_Car_W2 - Optimisation de la connexion instrumentation</dc:title>'
        '<dcterms:created xsi:type="dcterms:W3CDTF">2026-10-28T00:00:00Z</dcterms:created>'
        '</cp:coreProperties>')
app = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
       '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">'
       f'<Application>Microsoft Office PowerPoint</Application><Slides>{N}</Slides></Properties>')

presentation = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:presentation {NS} saveSubsetFonts="1">'
                '<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>'
                '<p:sldIdLst>' + "".join(f'<p:sldId id="{255 + i}" r:id="rId{i + 1}"/>' for i in range(1, N + 1)) +
                '</p:sldIdLst><p:sldSz cx="12192000" cy="6858000"/><p:notesSz cx="6858000" cy="9144000"/>'
                '</p:presentation>')
pres_rels = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="{PKG_REL}">'
             f'<Relationship Id="rId1" Type="{REL}/slideMaster" Target="slideMasters/slideMaster1.xml"/>'
             + "".join(f'<Relationship Id="rId{i + 1}" Type="{REL}/slide" Target="slides/slide{i}.xml"/>'
                       for i in range(1, N + 1)) +
             f'<Relationship Id="rId{N + 2}" Type="{REL}/theme" Target="theme/theme1.xml"/>'
             f'<Relationship Id="rId{N + 3}" Type="{REL}/presProps" Target="presProps.xml"/>'
             f'<Relationship Id="rId{N + 4}" Type="{REL}/viewProps" Target="viewProps.xml"/>'
             f'<Relationship Id="rId{N + 5}" Type="{REL}/tableStyles" Target="tableStyles.xml"/>'
             '</Relationships>')

EMPTY_TREE = ('<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
              '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/>'
              '<a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree>')
master = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:sldMaster {NS}>'
          '<p:cSld><p:bg><p:bgRef idx="1001"><a:schemeClr val="bg1"/></p:bgRef></p:bg>' + EMPTY_TREE + '</p:cSld>'
          '<p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" '
          'accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>'
          '<p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>'
          '<p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles></p:sldMaster>')
master_rels = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="{PKG_REL}">'
               f'<Relationship Id="rId1" Type="{REL}/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>'
               f'<Relationship Id="rId2" Type="{REL}/theme" Target="../theme/theme1.xml"/></Relationships>')
layout = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:sldLayout {NS} type="blank" preserve="1">'
          '<p:cSld name="Blank">' + EMPTY_TREE + '</p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>'
          '</p:sldLayout>')
layout_rels = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="{PKG_REL}">'
               f'<Relationship Id="rId1" Type="{REL}/slideMaster" Target="../slideMasters/slideMaster1.xml"/>'
               '</Relationships>')
slide_rels = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="{PKG_REL}">'
              f'<Relationship Id="rId1" Type="{REL}/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>'
              '</Relationships>')


def fill(c):
    return f'<a:solidFill><a:srgbClr val="{c}"/></a:solidFill>'


theme = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
         '<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Capgemini">'
         '<a:themeElements><a:clrScheme name="Capgemini">'
         '<a:dk1><a:srgbClr val="000000"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>'
         f'<a:dk2><a:srgbClr val="{NAVY}"/></a:dk2><a:lt2><a:srgbClr val="{LIGHT}"/></a:lt2>'
         f'<a:accent1><a:srgbClr val="{BLUE}"/></a:accent1><a:accent2><a:srgbClr val="{CYAN}"/></a:accent2>'
         f'<a:accent3><a:srgbClr val="{GREEN}"/></a:accent3><a:accent4><a:srgbClr val="{ORANGE}"/></a:accent4>'
         f'<a:accent5><a:srgbClr val="{RED}"/></a:accent5><a:accent6><a:srgbClr val="{GREY}"/></a:accent6>'
         f'<a:hlink><a:srgbClr val="{BLUE}"/></a:hlink><a:folHlink><a:srgbClr val="{GREY}"/></a:folHlink>'
         '</a:clrScheme><a:fontScheme name="Calibri">'
         '<a:majorFont><a:latin typeface="Calibri"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont>'
         '<a:minorFont><a:latin typeface="Calibri"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont>'
         '</a:fontScheme><a:fmtScheme name="Office"><a:fillStyleLst>'
         + ('<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>' * 3)
         + '</a:fillStyleLst><a:lnStyleLst>'
         + ('<a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>' * 3)
         + '</a:lnStyleLst><a:effectStyleLst>'
         + ('<a:effectStyle><a:effectLst/></a:effectStyle>' * 3)
         + '</a:effectStyleLst><a:bgFillStyleLst>'
         + ('<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>' * 3)
         + '</a:bgFillStyleLst></a:fmtScheme></a:themeElements><a:objectDefaults/><a:extraClrSchemeLst/>'
         '</a:theme>')

parts = {
    "[Content_Types].xml": content_types,
    "_rels/.rels": root_rels,
    "docProps/core.xml": core,
    "docProps/app.xml": app,
    "ppt/presentation.xml": presentation,
    "ppt/_rels/presentation.xml.rels": pres_rels,
    "ppt/slideMasters/slideMaster1.xml": master,
    "ppt/slideMasters/_rels/slideMaster1.xml.rels": master_rels,
    "ppt/slideLayouts/slideLayout1.xml": layout,
    "ppt/slideLayouts/_rels/slideLayout1.xml.rels": layout_rels,
    "ppt/theme/theme1.xml": theme,
    "ppt/presProps.xml": f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:presentationPr {NS}/>',
    "ppt/viewProps.xml": f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:viewPr {NS}/>',
    "ppt/tableStyles.xml": ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                            '<a:tblStyleLst xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
                            'def="{5C22544A-7EE6-4342-B048-85BDC9FD1C3A}"/>'),
}
for i, sl in enumerate(slides, 1):
    parts[f"ppt/slides/slide{i}.xml"] = sl.xml()
    parts[f"ppt/slides/_rels/slide{i}.xml.rels"] = slide_rels

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", parts.pop("[Content_Types].xml"))
    for name, data in parts.items():
        z.writestr(name, data)
print(f"Wrote {OUT} with {N} slides")
