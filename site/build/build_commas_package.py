#!/usr/bin/env python3
"""Build the Commas Code-view paste package from index.html.
html = full page minus the <script> block, every local asset path swapped for its hosted URL.
js   = the script block content.
Fails loudly on any local asset path that has no hosted URL."""
import json, re, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
src = (ROOT / 'index.html').read_text(encoding='utf-8')
urls = json.loads((ROOT / 'assets/gen/hosted-urls.json').read_text())['urls']
out = ROOT / 'build'

m = re.search(r'<script>(.*?)</script>\s*', src, re.S)
if not m or src.count('<script') != 1:
    sys.exit('expected exactly one <script> block')
js = m.group(1).strip('\n') + '\n'
html = src[:m.start()] + src[m.end():]

# assets/favicon.svg is not hosted; the data: URI favicon on the line above already covers it, so drop that link.
html, n = re.subn(r'\s*<link rel="icon" type="image/svg\+xml" href="assets/favicon\.svg">', '', html)
if n != 1: sys.exit('favicon.svg link not found exactly once (%d)' % n)

# Lead capture: swap the presentational #bookForm for Commas's native Lead form block (CRM form
# "Book a Teardown Call", public id below). The builder serialises that block as a data-react-component div;
# submissions land in Commas CRM > Contacts and the first pipeline stage.
FORM_ID = 'GypJT9tmyCm1wezV'
lead = ('<div class="form bw-glass cf-host" id="bookForm">'
        '<div class="cf-slot" data-react-component="LeadForm" data-react-props="{&quot;formPublicId&quot;:&quot;%s&quot;}"></div>'
        '</div>') % FORM_ID
html, n = re.subn(r'<form class="form bw-glass" id="bookForm".*?</form>', lead, html, flags=re.S)
if n != 1: sys.exit('bookForm not found exactly once (%d)' % n)

# Style the native block to match the page, and give its button the page's hover light.
css_add = (out / 'lead-form.css').read_text(encoding='utf-8')
i = html.rfind('</style>')
if i < 0: sys.exit('no </style>')
html = html[:i] + css_add + html[i:]
js = js + (out / 'lead-form.js').read_text(encoding='utf-8')

missing = []
def swap(mo):
    name = mo.group(2)
    if name not in urls:
        missing.append(mo.group(0)); return mo.group(0)
    return urls[name]
pat = re.compile(r'(?:\.\./|\./)?assets/(?:gen/(?:web|host)/|gen/)?([A-Za-z0-9_.-]+/)*?([A-Za-z0-9_.-]+\.(?:webp|png|jpe?g|gif|svg))')
html = pat.sub(swap, html)
js = pat.sub(swap, js)
if missing:
    sys.exit('UNMAPPED local asset paths: %s' % sorted(set(missing)))

for label, text in (('html', html), ('js', js)):
    left = re.findall(r'''(?:src|href|content|data-[a-z-]+|srcset)\s*=\s*["'](?!https?:|data:|#|mailto:|tel:)[^"']*\.(?:webp|png|jpe?g|gif|svg|ico)''', text)
    left += re.findall(r'url\(\s*["\']?(?!https?:|data:|#)[^)"\']+\.(?:webp|png|jpe?g|gif|svg)', text)
    left += re.findall(r'assets/', text)
    if left:
        sys.exit('relative asset refs remain in %s: %s' % (label, left[:10]))

(out / 'commas-html.html').write_text(html, encoding='utf-8')
(out / 'commas.js').write_text(js, encoding='utf-8')
print('html bytes', len(html), 'js bytes', len(js), 'hosted refs', html.count('assets.fanbasis.com'))
