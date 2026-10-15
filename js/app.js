/* RANDFALS — bygger sidene fra js/data.js. Du trenger normalt ikke endre denne filen. */
(() => {
  "use strict";
  const D = window.RANDFALS;
  const app = document.getElementById("app");
  const side = document.body.dataset.side;
  const redusert = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const lenke = (p) => `prosjekt.html?p=${encodeURIComponent(p.slug)}`;
  const nr = (i) => String(i + 1).padStart(2, "0");

  const bilde = (b, { lat = true, alt } = {}) =>
    b ? `<img src="${esc(b.src)}" alt="${esc(alt ?? b.alt ?? "")}"${b.w ? ` width="${b.w}" height="${b.h}"` : ""}${lat ? ' loading="lazy"' : ""} decoding="async" draggable="false">` : "";

  /* ---------- felles: meny, bunn, tema, klokke ---------- */
  const nav = () => `
    <header class="nav">
      <a href="./" class="logo" aria-label="${esc(D.navn)} — forside">${esc(D.navn)}<i></i></a>
      <a href="liste.html" class="strek"${side === "liste" ? ' aria-current="page"' : ""}>Index</a>
      <a href="om.html" class="strek"${side === "om" ? ' aria-current="page"' : ""}>Om</a>
      <div class="nav-h">
        <a href="om.html#kontakt" class="strek">Kontakt</a>
        <button class="tema" type="button" aria-label="Bytt mellom hvit og sort" aria-pressed="false"><span></span></button>
      </div>
    </header>`;

  const bunn = () => `
    <footer class="bunn">
      <span>© ${new Date().getFullYear()} ${esc(D.navn)}</span>
      <span class="klokke" aria-label="Lokal tid">${esc(D.sted)} <time></time></span>
    </footer>`;

  function felles() {
    const knapp = $(".tema");
    const oppdater = () => knapp && knapp.setAttribute("aria-pressed", document.documentElement.dataset.tema === "sort");
    oppdater();
    knapp?.addEventListener("click", () => {
      const ny = document.documentElement.dataset.tema === "sort" ? "hvit" : "sort";
      document.documentElement.dataset.tema = ny;
      try { localStorage.setItem("randfals-tema", ny); } catch (e) {}
      oppdater();
    });
    const t = $(".klokke time");
    if (t) {
      const fmt = new Intl.DateTimeFormat("nb-NO", { timeZone: D.tidssone || "Europe/Oslo", hour: "2-digit", minute: "2-digit" });
      const tikk = () => (t.textContent = fmt.format(new Date()));
      tikk();
      setInterval(tikk, 15000);
    }
    // fade inn ved scroll
    const io = "IntersectionObserver" in window && new IntersectionObserver((e) => e.forEach((x) => x.isIntersecting && (x.target.classList.add("synlig"), io.unobserve(x.target))), { rootMargin: "0px 0px -8% 0px" });
    $$(".vis-ved-scroll").forEach((el) => (io ? io.observe(el) : el.classList.add("synlig")));
  }

  /* ---------- sideoverganger (View Transitions) ---------- */
  // Bildet man klikker på i stripen "flyr" til toppbildet i prosjektet.
  function navngiHero(el) {
    $$("[style*='view-transition-name']").forEach((x) => (x.style.viewTransitionName = ""));
    if (el) el.style.viewTransitionName = "hero";
  }
  window.addEventListener("pagereveal", (e) => {
    if (!e.viewTransition) return;
    document.documentElement.classList.add("vt");
    e.viewTransition.finished.finally(() => document.documentElement.classList.remove("vt"));
    if (side !== "hjem") return;
    const fra = window.navigation?.activation?.from?.url;
    const slug = fra && new URL(fra).searchParams.get("p");
    const img = slug && $(`.kort[data-slug="${CSS.escape(slug)}"] img`);
    if (img) {
      navngiHero(img);
      e.viewTransition.finished.finally(() => navngiHero(null));
    }
  });

  /* ---------- forside ---------- */
  function hjem() {
    const grov = matchMedia("(pointer: coarse)").matches;
    const kort = (p, skjult) => `
      <a class="kort" href="${lenke(p)}" data-slug="${esc(p.slug)}"${skjult ? ' aria-hidden="true" tabindex="-1"' : ""} draggable="false">
        ${bilde(p.forside, { lat: false, alt: skjult ? "" : p.tittel })}
        <span class="bt"><b>${esc(p.tittel)}</b><br>${esc(p.undertittel || p.kategori)}</span>
      </a>`;
    const sett = (skjult) => D.prosjekter.map((p) => kort(p, skjult)).join("");

    app.innerHTML = `
      ${nav()}
      <main class="hjem">
        <section class="stripe${grov ? " native" : ""}" aria-label="Prosjekter">
          <div class="spor">${sett(false)}</div>
        </section>
        <div class="ordmerke-boks"><h1 class="ordmerke inn" style="--i:2"><span>${esc(D.navn)}</span></h1></div>
        <p class="ingress inn" style="--i:4">${esc(D.ingress)}</p>
        ${bunn()}
      </main>`;
    felles();
    tilpassOrdmerke();
    $$(".kort").forEach((k, i) => (k.style.setProperty("--i", i), k.classList.add("inn")));
    $(".spor").addEventListener("click", (e) => {
      const k = e.target.closest(".kort");
      if (k) navngiHero($("img", k));
    });
    if (!grov) uendeligStripe(sett);
  }

  // Uendelig horisontal stripe: hjul, dra, piltaster + rolig auto-gli.
  function uendeligStripe(sett) {
    const stripe = $(".stripe"), spor = $(".spor");
    let periode = 0;
    const mal = () => {
      const forste = spor.children[0], n = D.prosjekter.length;
      periode = spor.children[n] ? spor.children[n].offsetLeft - forste.offsetLeft : 0;
      if (!periode) {
        // legg til kopier til stripen er minst to skjermer bred
        const enkel = spor.scrollWidth + parseFloat(getComputedStyle(spor).gap || 0);
        const kopier = Math.max(2, Math.ceil((innerWidth * 2) / enkel));
        spor.insertAdjacentHTML("beforeend", Array.from({ length: kopier }, () => sett(true)).join(""));
        periode = spor.children[n].offsetLeft - forste.offsetLeft;
      }
    };
    mal();
    addEventListener("resize", () => { periode = spor.children[D.prosjekter.length].offsetLeft - spor.children[0].offsetLeft; tilpassOrdmerke(); });

    let x = 0, mal_ = 0, drar = false, flyttet = 0, startX = 0, startMal = 0, over = false;
    const drift = redusert ? 0 : 0.35;

    addEventListener("wheel", (e) => {
      const kanScrolle = document.documentElement.scrollHeight > innerHeight + 4;
      if (kanScrolle && !stripe.contains(e.target)) return;
      e.preventDefault();
      const d = Math.abs(e.deltaX) > Math.abs(e.deltaY) ? e.deltaX : e.deltaY;
      mal_ += d * (e.deltaMode === 1 ? 40 : 1);
    }, { passive: false });

    stripe.addEventListener("pointerdown", (e) => {
      if (e.button !== 0) return;
      drar = true; flyttet = 0; startX = e.clientX; startMal = mal_;
    });
    addEventListener("pointermove", (e) => {
      if (!drar) return;
      const dx = e.clientX - startX;
      flyttet = Math.max(flyttet, Math.abs(dx));
      if (flyttet > 4) stripe.classList.add("drar");
      mal_ = startMal - dx * 1.4;
    });
    addEventListener("pointerup", () => { drar = false; stripe.classList.remove("drar"); });
    stripe.addEventListener("click", (e) => { if (flyttet > 6) { e.preventDefault(); e.stopPropagation(); } }, true);
    stripe.addEventListener("mouseenter", () => (over = true));
    stripe.addEventListener("mouseleave", () => (over = false));
    addEventListener("keydown", (e) => {
      if (e.key === "ArrowRight") mal_ += 260;
      if (e.key === "ArrowLeft") mal_ -= 260;
    });
    // tastaturfokus: hold fokusert kort synlig
    stripe.addEventListener("focusin", (e) => {
      const k = e.target.closest(".kort");
      if (k) { stripe.scrollLeft = 0; mal_ = k.offsetLeft - innerWidth * 0.2; }
    });

    const tikk = () => {
      if (!drar && !over && !document.hidden) mal_ += drift;
      x += (mal_ - x) * (redusert ? 1 : 0.085);
      if (periode) {
        while (x >= periode) { x -= periode; mal_ -= periode; startMal -= periode; }
        while (x < 0) { x += periode; mal_ += periode; startMal += periode; }
      }
      spor.style.transform = `translate3d(${-x}px,0,0)`;
      requestAnimationFrame(tikk);
    };
    requestAnimationFrame(tikk);
  }

  // Ordmerket fyller hele bredden
  function tilpassOrdmerke() {
    const h = $(".ordmerke"), s = h && $("span", h);
    if (!s) return;
    const juster = () => {
      h.style.fontSize = "100px";
      const bredde = h.parentElement.clientWidth - parseFloat(getComputedStyle(h.parentElement).paddingLeft) * 2;
      h.style.fontSize = (100 * bredde) / s.getBoundingClientRect().width + "px";
    };
    juster();
    document.fonts?.ready.then(juster);
  }

  /* ---------- prosjekt ---------- */
  function galleri(bilder) {
    let html = "";
    for (let i = 0; i < bilder.length; i++) {
      const b = bilder[i];
      const media = (x) => x.type === "video"
        ? `<video src="${esc(x.src)}"${x.plakat ? ` poster="${esc(x.plakat)}"` : ""}${x.w ? ` width="${x.w}" height="${x.h}"` : ""} muted loop playsinline autoplay preload="metadata"></video>`
        : bilde(x);
      const fig = (x, kl = "") => `<figure class="${kl} vis-ved-scroll">${media(x)}${x.tekst ? `<figcaption>${esc(x.tekst)}</figcaption>` : ""}</figure>`;
      if (b.format === "halv" && bilder[i + 1]?.format === "halv") {
        html += `<div class="g-par">${fig(b)}${fig(bilder[i + 1])}</div>`;
        i++;
      } else {
        html += fig(b, { smal: "g-smal", hoyre: "g-hoyre", halv: "g-smal" }[b.format] || "g-full");
      }
    }
    return html;
  }

  function prosjekt() {
    const slug = new URLSearchParams(location.search).get("p");
    const i = D.prosjekter.findIndex((p) => p.slug === slug);
    if (i < 0) return ikkeFunnet();
    const p = D.prosjekter[i];
    const neste = D.prosjekter[(i + 1) % D.prosjekter.length];
    document.title = `${p.tittel} — ${D.navn}`;
    const fakta = { "År": p.aar, "Sted": p.sted, "Kategori": p.kategori, ...(p.fakta || {}) };

    app.innerHTML = `
      ${nav()}
      <main class="prosjekt">
        <section class="p-topp">
          <h1 class="p-tittel inn">${esc(p.tittel)}</h1>
          <p class="meta inn" style="--i:1"><span>${nr(i)} / ${nr(D.prosjekter.length - 1)}</span><span>${esc(p.kategori)}</span><span>${esc(p.sted)}</span><span>${esc(p.aar)}</span></p>
        </section>
        <figure class="hero">${bilde(p.forside, { lat: false })}</figure>
        ${p.tekst?.length ? `
        <section class="p-tekst">
          <span class="etikett vis-ved-scroll">Om prosjektet</span>
          <div class="avsnitt vis-ved-scroll">${p.tekst.map((t) => `<p>${esc(t)}</p>`).join("")}</div>
        </section>` : ""}
        <section class="galleri" aria-label="Bilder">${galleri(p.bilder || [])}</section>
        <section class="fakta vis-ved-scroll">
          <span class="etikett">Fakta</span>
          <dl>${Object.entries(fakta).filter(([, v]) => v !== "" && v != null).map(([k, v]) => `<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join("")}</dl>
        </section>
        <a class="neste" href="${lenke(neste)}">
          <span class="etikett">Neste prosjekt <span class="pil">→</span></span>
          <span class="stor">${esc(neste.tittel)}</span>
        </a>
        ${bunn()}
      </main>`;
    felles();
  }

  /* ---------- liste ---------- */
  function liste() {
    app.innerHTML = `
      ${nav()}
      <main class="liste">
        <div class="rad-topp inn"><span>Nr</span><span>Prosjekt</span><span class="kat">Kategori</span><span class="sted">Sted</span><span class="aar">År</span></div>
        <div class="liste-rader">
          ${D.prosjekter.map((p, i) => `
          <a class="rad inn" style="--i:${i + 1}" href="${lenke(p)}" data-i="${i}">
            <span>${nr(i)}</span><span class="navn">${esc(p.tittel)}</span><span class="kat">${esc(p.kategori)}</span><span class="sted">${esc(p.sted)}</span><span class="aar">${esc(p.aar)}</span>
          </a>`).join("")}
        </div>
      </main>
      <div class="flyt" aria-hidden="true"></div>
      ${bunn()}`;
    felles();
    // bilde som følger musepekeren
    if (!matchMedia("(hover: hover)").matches) return;
    const flyt = $(".flyt");
    let mx = 0, my = 0, fx = 0, fy = 0;
    $(".liste-rader").addEventListener("mouseover", (e) => {
      const r = e.target.closest(".rad");
      if (!r) return;
      const p = D.prosjekter[r.dataset.i];
      flyt.innerHTML = bilde(p.forside, { lat: false, alt: "" });
      flyt.classList.add("vis");
    });
    $(".liste-rader").addEventListener("mouseleave", () => flyt.classList.remove("vis"));
    addEventListener("mousemove", (e) => { mx = e.clientX + 24; my = e.clientY - 60; });
    const tikk = () => {
      fx += (mx - fx) * (redusert ? 1 : 0.18);
      fy += (my - fy) * (redusert ? 1 : 0.18);
      flyt.style.transform = `translate(${Math.min(fx, innerWidth - 240)}px, ${fy}px)`;
      requestAnimationFrame(tikk);
    };
    tikk();
  }

  /* ---------- om ---------- */
  function om() {
    const o = D.om;
    app.innerHTML = `
      ${nav()}
      <main class="om">
        <p class="om-tekst inn">${esc(o.tekst)}</p>
        <div class="om-blokk inn" style="--i:2"><span class="etikett">Tjenester</span><ul>${o.tjenester.map((t) => `<li>${esc(t)}</li>`).join("")}</ul></div>
        <div class="om-blokk inn" style="--i:3"><span class="etikett">Finn oss</span><ul>${o.lenker.map((l) => `<li><a href="${esc(l.url)}" target="_blank" rel="noopener">${esc(l.navn)}</a></li>`).join("")}</ul></div>
        <div class="om-blokk inn" id="kontakt" style="--i:4"><span class="etikett">Kontakt</span><ul>
          ${o.epost ? `<li><a href="mailto:${esc(o.epost)}">${esc(o.epost)}</a></li>` : ""}
          ${o.telefon ? `<li><a href="tel:${esc(o.telefon.replace(/\s/g, ""))}">${esc(o.telefon)}</a></li>` : ""}
        </ul></div>
        ${o.bilde ? `<figure class="om-bilde vis-ved-scroll">${bilde(o.bilde)}</figure>` : ""}
      </main>
      ${bunn()}`;
    felles();
  }

  function ikkeFunnet() {
    document.title = `Fant ikke siden — ${D.navn}`;
    app.innerHTML = `${nav()}<main class="p-topp" style="padding-top:20vh"><h1 class="p-tittel">Fant ikke siden</h1><p class="meta"><a class="strek" href="./">Tilbake til forsiden</a></p></main>`;
    felles();
  }

  ({ hjem, prosjekt, liste, om, ikkefunnet: ikkeFunnet }[side] || hjem)();
})();
