# -*- coding: utf-8 -*-
"""Genera las subpáginas del sitio del Dr. Urueta a partir de una sola plantilla."""
import io, json, html

BASE = "https://www.druruetacirugiacadera.com.mx"
WA   = "https://wa.me/526142157019?text=Hola%2C%20me%20gustar%C3%ADa%20agendar%20una%20cita"
MAPS = ("https://www.google.com/maps/place/Dr.+Nicolas+Urueta%2FCirugia+de+Cadera/"
        "@28.6292229,-106.0764218,16z/data=!3m1!4b1!4m6!3m5!1s0x86ea5dfb6e43054b:"
        "0x865b34112a9fd4a!8m2!3d28.6292229!4d-106.0738469!16s%2Fg%2F11rzkf9728")

WA_ICON = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
  'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
  '<path d="M21 11.5a8.4 8.4 0 0 1-9 8.4 9 9 0 0 1-3.7-.8L3 20.5l1.4-4.2A8.3 8.3 0 0 1 3.6 12'
  'a8.4 8.4 0 0 1 8.4-8.4 8.4 8.4 0 0 1 9 7.9Z"/></svg>')

NAV = ("""  <header class="nav">
    <div class="wrap nav-inner">
      <a class="brand" href="/">
        <span class="dot"></span>
        <span class="brandname">Dr. Nicolás Urueta</span>
      </a>
      <nav aria-label="Principal">
        <ul>
          <li><a href="/#motivos">Empezar aquí</a></li>
          <li><a href="/#procedimientos">Procedimientos</a></li>
          <li><a href="/dr-nicolas-urueta">Perfil</a></li>
          <li><a href="/preguntas-frecuentes">Preguntas</a></li>
          <li><a href="/#contacto">Contacto</a></li>
        </ul>
      </nav>
      <a class="nav-cta" href="%s">""" + WA_ICON + """ WhatsApp</a>
    </div>
  </header>
""") % WA

FOOT = """  <footer>
    <div class="wrap">
      <p class="muted" style="margin:0 0 6px"><strong>Dr. Nicolás David Urueta García</strong> · Céd. Prof. 7298201 · Céd. Esp. 10598988</p>
      <p class="muted" style="margin:0 0 6px">Paseo Simón Bolívar 1000, interior 307-309, Col. Centro, 31000 Chihuahua, Chih. · <a href="tel:+526144794215">614 479 4215</a></p>
      <p class="muted" style="margin:0">© <span id="y"></span> Dr. Nicolás Urueta — Cirugía de Cadera. La información de este sitio es orientativa y no sustituye una valoración médica presencial.</p>
    </div>
  </footer>
  <a class="whatsapp-float" href="%s" aria-label="Escribir por WhatsApp">
    <svg viewBox="0 0 24 24" fill="#fff" aria-hidden="true"><path d="M12.04 2A9.9 9.9 0 0 0 2.1 11.9c0 1.75.46 3.46 1.34 4.96L2 22l5.28-1.38a9.9 9.9 0 0 0 4.76 1.21h.01a9.9 9.9 0 0 0 9.9-9.9A9.9 9.9 0 0 0 12.04 2Zm5.8 14.03c-.24.68-1.4 1.3-1.93 1.35-.53.05-1.03.24-3.48-.72-2.95-1.16-4.8-4.2-4.95-4.4-.14-.2-1.17-1.56-1.17-2.98 0-1.42.74-2.12 1-2.41.26-.29.57-.36.76-.36l.55.01c.17 0 .41-.07.64.49.24.58.8 1.98.87 2.12.07.15.12.32.02.51-.1.2-.15.32-.29.5-.15.17-.31.38-.44.51-.15.14-.3.3-.13.6.17.29.76 1.26 1.63 2.04 1.12 1 2.06 1.31 2.35 1.46.29.14.46.12.63-.07.17-.2.73-.85.93-1.14.19-.29.39-.24.65-.15.27.1 1.7.8 1.99.95.29.14.48.22.55.34.07.13.07.75-.17 1.43Z"/></svg>
  </a>
  <script>document.getElementById('y').textContent=new Date().getFullYear();</script>
</body>
</html>
""" % WA


def faq_html(items):
    out = ['  <h2>Preguntas frecuentes</h2>']
    for q, a in items:
        cuerpo = "".join("<p>%s</p>" % p for p in a)
        out.append('  <details class="faq"><summary>%s</summary><div class="body">%s</div></details>' % (q, cuerpo))
    return "\n".join(out)


def faq_schema(items):
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": " ".join(a)}}
            for q, a in items
        ],
    }


def related_html(actual, paginas):
    otras = [p for p in paginas if p["slug"] != actual and p.get("es_procedimiento")][:4]
    tarjetas = "".join(
        '<a href="/%s"><b>%s</b><span>%s</span></a>' % (p["slug"], p["nav"], p["resumen_corto"])
        for p in otras)
    return '  <h2>Otros procedimientos</h2>\n  <div class="related">%s</div>' % tarjetas


def build(p, paginas):
    url = "%s/%s" % (BASE, p["slug"])

    schemas = [{
        "@type": "MedicalWebPage",
        "@id": url + "#page",
        "url": url,
        "name": p["title"],
        "description": p["desc"],
        "inLanguage": "es-MX",
        "isPartOf": {"@type": "WebSite", "url": BASE + "/"},
        "about": {"@id": BASE + "/#physician"},
        "author": {"@id": BASE + "/#physician"},
    }, {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Inicio", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": p["nav"], "item": url},
        ],
    }]

    if p.get("procedimiento"):
        schemas.append({
            "@type": "MedicalProcedure",
            "@id": url + "#procedimiento",
            "name": p["procedimiento"],
            "procedureType": "https://schema.org/SurgicalProcedure",
            "bodyLocation": "Cadera",
            "description": p["desc"],
            "howPerformed": p.get("como", ""),
            "preparation": p.get("preparacion", ""),
            "followup": p.get("seguimiento", ""),
            "url": url,
        })

    if p.get("faq"):
        schemas.append(faq_schema(p["faq"]))

    ld = json.dumps({"@context": "https://schema.org", "@graph": schemas},
                    ensure_ascii=False, indent=2)

    img = ""
    if p.get("imagen"):
        from PIL import Image as _Im
        with _Im.open(p["imagen"]) as _i:
            _w, _h = _i.size
        img = ('\n  <img class="procedure-image" src="/%s" alt="%s" loading="lazy" width="%d" height="%d">'
               % (p["imagen"], p["imagen_alt"], _w, _h))

    resumen = ""
    if p.get("resumen"):
        filas = "".join("<div><b>%s</b><span>%s</span></div>" % (k, v) for k, v in p["resumen"])
        resumen = ('<div class="card"><h4>En resumen</h4><div class="keyval" style="margin:0;border:none">%s</div></div>'
                   % filas)

    bloques = [p["cuerpo"]]
    if p.get("faq"):
        bloques.append(faq_html(p["faq"]))
    bloques.append(related_html(p["slug"], paginas))

    doc = """<!doctype html>
<html lang="es-MX">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="google-site-verification" content="ORVi8z3fPBfjzz4dWHsPCKyTEjBym1CVmNgonIQuiCM">
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-1K8H9Z2335"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-1K8H9Z2335');
  </script>
  <title>%(title)s</title>
  <meta name="description" content="%(desc)s">
  <link rel="canonical" href="%(url)s">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <meta name="theme-color" content="#F0B429">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <meta name="geo.region" content="MX-CHH">
  <meta name="geo.placename" content="Chihuahua">

  <meta property="og:type" content="article">
  <meta property="og:locale" content="es_MX">
  <meta property="og:site_name" content="Dr. Nicolás Urueta · Cirugía de Cadera">
  <meta property="og:title" content="%(title)s">
  <meta property="og:description" content="%(desc)s">
  <meta property="og:url" content="%(url)s">
  <meta property="og:image" content="%(base)s/og.jpg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="%(title)s">
  <meta name="twitter:description" content="%(desc)s">
  <meta name="twitter:image" content="%(base)s/og.jpg">

  <link rel="preconnect" href="https://fonts.googleapis.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500&family=Public+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/estilos.css">

  <script type="application/ld+json">
%(ld)s
  </script>
</head>
<body>

%(nav)s
  <div class="wrap crumb"><a href="/">Inicio</a><span>/</span>%(nav_name)s</div>

  <section class="page-hero" style="border-top:none;padding-top:14px">
    <div class="wrap">
      <span class="chip">%(chip)s</span>
      <h1>%(h1)s</h1>
      <p class="lead">%(lead)s</p>
      <div class="cta-row">
        <a class="btn btn-primary" href="%(wa)s">%(cta)s</a>
        <a class="btn btn-ghost" href="tel:+526144794215">614 479 4215</a>
      </div>
    </div>
  </section>

  <section style="border-top:none;padding-top:8px">
    <div class="wrap layout">
      <div class="prose">%(img)s
%(cuerpo)s
      </div>
      <div class="aside">
        %(resumen)s
        <div class="card">
          <h4>Consultorio</h4>
          <ul>
            <li>Paseo Simón Bolívar 1000, int. 307-309, Col. Centro</li>
            <li>Lunes a jueves 15:00–20:00</li>
            <li>Viernes 10:00–13:00</li>
            <li>WhatsApp lun–sáb 8:00–20:00</li>
          </ul>
          <p style="margin:14px 0 0"><a href="%(maps)s">Ver ubicación en Google Maps</a></p>
        </div>
      </div>
    </div>
  </section>

  <section style="border-top:none">
    <div class="wrap">
      <div class="cta-band">
        <h2>¿Tienes dudas sobre tu caso?</h2>
        <p>Cada cadera es distinta. La indicación se define con tu historia, la exploración física y tus radiografías; no con un diagnóstico a distancia.</p>
        <a class="btn btn-primary" href="%(wa)s">Escribir por WhatsApp</a>
      </div>
    </div>
  </section>

%(foot)s""" % {
        "title": html.escape(p["title"], quote=True),
        "desc": html.escape(p["desc"], quote=True),
        "url": url, "base": BASE, "ld": ld, "nav": NAV,
        "nav_name": p["nav"], "chip": p["chip"], "h1": p["h1"], "lead": p["lead"],
        "wa": p.get("wa", WA), "cta": p.get("cta_texto", "Agendar valoración por WhatsApp"), "maps": MAPS, "img": img,
        "cuerpo": "\n".join(bloques), "resumen": resumen, "foot": FOOT,
    }
    io.open(p["slug"] + ".html", "w", encoding="utf-8").write(doc)
    return p["slug"] + ".html", len(doc)


if __name__ == "__main__":
    from contenido import PAGINAS
    for p in PAGINAS:
        f, n = build(p, PAGINAS)
        print("%-34s %6d bytes" % (f, n))
