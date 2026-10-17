/* RANDFALS — animert ordmerke på forsiden.
   Modulruter blinker opp på tilfeldige steder. Rutene som treffer bokstavene blir stående
   til hele ordmerket (Randfals Modul) står. Spilles én gang per besøk, deretter vises det ferdige merket.
   Fargen følger temaet (currentColor). Kilde og flere formater: profil/ */
(() => {
  "use strict";
  const D = "M0 700V0H420V140H560V420H420L560 700H420L280 420H140V700ZM140 280H420V140H140ZM700 700V140H840V0H1260V700H1120V420H840V700ZM840 280H1120V140H840ZM1400 700V0H1820V140H1960V700H1820V140H1540V700ZM2100 700V0H2520V140H2660V700ZM2240 560H2520V140H2240ZM2800 700V0H3360V140H2940V280H3220V420H2940V700ZM3500 700V140H3640V0H4060V700H3920V420H3640V700ZM3640 280H3920V140H3640ZM4200 700V0H4340V560H4760V700ZM4900 700V560H5320V420H4900V0H5460V140H5040V280H5460V700Z";
  const U = 140, COLS = 39, ROWS = 5, BUILD = 2.6, ns = "http://www.w3.org/2000/svg";

  window.RANDFALS_ordmerke = (holder) => {
    if (!holder) return;
    let sett = false;
    try { sett = sessionStorage.getItem("randfals-ordmerke") === "1"; } catch (e) {}
    const stille = sett || matchMedia("(prefers-reduced-motion: reduce)").matches;

    const svg = document.createElementNS(ns, "svg");
    svg.setAttribute("viewBox", "0 -140 5460 980");
    svg.setAttribute("aria-hidden", "true");
    svg.setAttribute("focusable", "false");
    const id = "rf-maske";
    svg.innerHTML = `<defs><mask id="${id}" maskUnits="userSpaceOnUse" x="0" y="0" width="5460" height="700"><g></g></mask></defs>
      <g class="rf-stoy" fill="currentColor"></g><path fill="currentColor" d="${D}"></path>`;
    holder.replaceChildren(svg);
    const path = svg.querySelector("path");
    if (stille) return;                       // ferdig merke uten animasjon

    path.setAttribute("mask", `url(#${id})`);
    let seed = 20261017;                      // fast frø: «tilfeldig», men likt hver gang
    const rnd = () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
    const rute = (parent, x, y, fill) => { const r = document.createElementNS(ns, "rect");
      r.setAttribute("x", x); r.setAttribute("y", y); r.setAttribute("width", U); r.setAttribute("height", U); r.setAttribute("shape-rendering", "crispEdges");
      if (fill) r.setAttribute("fill", fill); r.style.display = "none"; parent.appendChild(r); return r; };

    const gMaske = svg.querySelector("mask g"), gStoy = svg.querySelector(".rf-stoy");
    const bli = [], stoy = [];
    for (let c = 0; c < COLS; c++) for (let r = 0; r < ROWS; r++)
      bli.push({ el: rute(gMaske, c * U, r * U, "#fff"), pa: 0.15 + Math.pow(rnd(), 0.75) * (BUILD - 0.15) });
    for (let i = 0; i < 200; i++) {
      const c = Math.floor(rnd() * COLS), r = Math.floor(rnd() * 7) - 1;
      const pa = Math.pow(rnd(), 1.3) * (BUILD - 0.25);
      stoy.push({ el: rute(gStoy, c * U, r * U), pa, av: pa + 0.07 + rnd() * 0.2 });
    }
    const vis = (t) => {
      for (const k of bli) k.el.style.display = t >= k.pa ? "" : "none";
      for (const n of stoy) n.el.style.display = (t >= n.pa && t < n.av) ? "" : "none";
    };
    vis(0);
    let t0 = null;
    const ramme = (na) => {
      if (t0 === null) t0 = na;
      const t = (na - t0) / 1000;
      vis(t);
      if (t < BUILD) return requestAnimationFrame(ramme);
      path.removeAttribute("mask");           // rydd: ferdig merke uten maske
      gMaske.replaceChildren(); gStoy.replaceChildren();
      try { sessionStorage.setItem("randfals-ordmerke", "1"); } catch (e) {}
    };
    requestAnimationFrame(ramme);
  };
})();
