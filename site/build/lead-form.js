
/* ---------- Commas native Lead form block: the same pointer-following hover light as every other button,
   and the muted "Choose…" tone on empty selects. The block mounts after this script, so watch for it. ---------- */
(() => {
  const host = document.querySelector('#book .cf-host');
  if (!host) return;
  const fine = matchMedia('(hover: hover) and (pointer: fine)').matches && !matchMedia('(prefers-reduced-motion: reduce)').matches;
  const PH = { 'given-name': 'Your first name', 'family-name': 'Your last name' }; /* same tone as "Your company" */
  /* The consent line under the button names the Commas organisation ("Ventures Group"); show our brand instead.
     Text nodes only, re-applied whenever React re-renders the block. */
  const rename = () => {
    const w = document.createTreeWalker(host, NodeFilter.SHOW_TEXT);
    let n;
    while ((n = w.nextNode())) if (n.nodeValue.indexOf('Ventures Group') > -1) n.nodeValue = n.nodeValue.replace(/Ventures Group/g, 'BRANDWERX');
  };
  const wire = () => {
    rename();
    host.querySelectorAll('input[autocomplete="given-name"],input[autocomplete="family-name"]').forEach(i => {
      if (!i.getAttribute('placeholder')) i.setAttribute('placeholder', PH[i.getAttribute('autocomplete')]);
    });
    host.querySelectorAll('select').forEach(s => {
      const tone = () => s.classList.toggle('bw-empty', !s.value);
      tone();
      if (!s.__bwTone) { s.__bwTone = true; s.addEventListener('change', tone); }
    });
    const b = host.querySelector('button[type=submit]');
    if (!b || b.__bwHover || !fine) return;
    b.__bwHover = true;
    let r = null, px = 0, py = 0, f = 0;
    const put = () => { f = 0; b.style.setProperty('--mx', px.toFixed(1) + 'px'); b.style.setProperty('--my', py.toFixed(1) + 'px'); };
    const at = (e) => { if (!r) r = b.getBoundingClientRect(); px = e.clientX - r.left; py = e.clientY - r.top; };
    b.addEventListener('pointerenter', e => { r = b.getBoundingClientRect(); at(e); put(); });
    b.addEventListener('pointermove', e => { at(e); if (!f) f = requestAnimationFrame(put); }, { passive: true });
    b.addEventListener('pointerleave', () => { r = null; });
  };
  wire();
  new MutationObserver(wire).observe(host, { childList: true, subtree: true, characterData: true });

  /* Failed submit: bring the first invalid field into view below the fixed nav, then focus it.
     The block validates on submit and sets aria-invalid; give React a moment to render that. */
  const reduceMo = matchMedia('(prefers-reduced-motion: reduce)').matches;
  host.addEventListener('submit', () => {
    setTimeout(() => {
      const f = host.querySelector('form [aria-invalid="true"]');
      if (!f) return;
      const box = (f.closest('form > div') || f).getBoundingClientRect();
      const bar = document.getElementById('topbar');
      const top = (bar ? bar.getBoundingClientRect().bottom : 0) + 16;
      if (box.top < top || box.bottom > innerHeight - 16) {
        scrollTo({ top: Math.max(0, scrollY + box.top - top), behavior: reduceMo ? 'auto' : 'smooth' });
      }
      f.focus({ preventScroll: true });
    }, 80);
  }, true);
})();
