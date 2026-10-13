/* =========================================================================
   Cabinet chiropratique Thomas Nunes — interactions
   Vanilla, sans dépendance. Tout est optionnel : si ce fichier ne se charge
   pas, le site reste entièrement lisible et navigable.
   ========================================================================= */
(function () {
  'use strict';

  /* ---------------------------------------------------------------- 0. Confirmation de réservation
     Après une réservation, PracticeHub redirige vers /reservation-confirmee/
     en ajoutant à l'adresse des données du patient (identifiant, type de
     rendez-vous...). Cette redirection se fait dans le cadre de l'agenda.
     On affiche alors la confirmation en pleine page, à une adresse nettoyée
     de ces données, et on la nettoie aussi quand elle s'ouvre directement
     en pleine page. Aucune donnée n'est envoyée nulle part. */
  (function () {
    var CONFIRMATION = /^\/reservation-confirmee(\/(index\.html)?)?$/;
    if (!CONFIRMATION.test(location.pathname)) return;
    var propre = '/reservation-confirmee/';
    if (window.top === window.self) {
      if (location.search || location.hash) {
        try { history.replaceState(null, '', propre); } catch (e) { /* rien de grave */ }
      }
      return;
    }
    var memeSite = false;
    try { memeSite = window.top.location.origin === location.origin; } catch (e) { /* cadre sur un autre site */ }
    if (!memeSite) return;
    try { window.top.location.replace(propre); } catch (e) { /* on reste dans le cadre */ }
  })();

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var coarse = window.matchMedia('(pointer: coarse)').matches;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  /* ---------------------------------------------------------------- 1. Défilement
     Pas de défilement « amorti » maison : on laisse le défilement natif, qui
     reste le plus fiable (trackpad, molette, clavier, lecteurs d'écran, zoom).
     Le rythme du site vient des apparitions au scroll (section 5) et du
     comportement de l'en-tête (section 2), pas d'une interception de la molette.
     Pour ajouter un amorti type Lenis plus tard, c'est ici que ça se branche. */

  /* ---------------------------------------------------------------- 2. En-tête
     Visible en haut de page ; se masque en descendant, réapparaît en montant. */
  (function () {
    var header = $('[data-header]');
    if (!header) return;
    var hero = $('.hero');
    var last = window.scrollY, ticking = false;
    var THRESHOLD = 80;

    function update() {
      var y = window.scrollY;
      var down = y > last && y > THRESHOLD;
      var menuOpen = document.body.classList.contains('is-locked');

      header.classList.toggle('is-hidden', down && !menuOpen);
      header.classList.toggle('is-stuck', y > 10);

      if (hero) {
        var over = y < hero.offsetHeight - header.offsetHeight - 10;
        header.classList.toggle('is-over-hero', over && !menuOpen);
      }
      last = y; ticking = false;
    }
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
    update();
  })();

  /* ---------------------------------------------------------------- 3. Menu mobile */
  (function () {
    var burger = $('[data-burger]'), drawer = $('[data-drawer]');
    if (!burger || !drawer) return;

    var header = document.querySelector('[data-header]');

    function setOpen(open) {
      burger.setAttribute('aria-expanded', String(open));
      burger.setAttribute('aria-label', open ? 'Fermer le menu' : 'Ouvrir le menu');
      document.body.classList.toggle('is-locked', open);

      // Le tiroir a un fond clair : l'en-tête doit quitter sa variante blanche
      // (utilisée au-dessus du hero sombre), sinon logo et croix disparaissent.
      if (header) {
        if (open) {
          header.classList.remove('is-over-hero', 'is-hidden');
        } else if (window.scrollY < 80) {
          var hero = document.querySelector('.hero');
          if (hero) header.classList.add('is-over-hero');
        }
      }
      if (open) {
        drawer.hidden = false;
        void drawer.offsetHeight;   // reflow forcé : la transition part à coup sûr
        drawer.classList.add('is-open');
      } else {
        drawer.classList.remove('is-open');
        setTimeout(function () { if (!drawer.classList.contains('is-open')) drawer.hidden = true; }, 420);
      }
    }
    burger.addEventListener('click', function () {
      setOpen(burger.getAttribute('aria-expanded') !== 'true');
    });
    drawer.addEventListener('click', function (e) { if (e.target.closest('a')) setOpen(false); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && burger.getAttribute('aria-expanded') === 'true') { setOpen(false); burger.focus(); }
    });
    window.addEventListener('resize', function () {
      if (window.innerWidth > 980 && burger.getAttribute('aria-expanded') === 'true') setOpen(false);
    });
  })();

  /* ---------------------------------------------------------------- 4. Découpe du texte
     Enveloppe mots / lettres pour les révéler en cascade, sans toucher aux
     éléments enfants (liens, <em>, <br>) ni au texte lu par les lecteurs d'écran. */
  function splitTextNodes(root, mode) {
    var i = 0;
    function walk(node) {
      var kids = Array.prototype.slice.call(node.childNodes);
      kids.forEach(function (child) {
        if (child.nodeType === 3) {
          var text = child.nodeValue;
          if (!text.trim()) return;
          var frag = document.createDocumentFragment();
          var parts = mode === 'chars' ? text.split('') : text.split(/(\s+)/);
          parts.forEach(function (part) {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
            var outer = document.createElement('span');
            outer.className = mode === 'chars' ? 'ch' : 'word';
            var inner = document.createElement('span');
            inner.textContent = part;
            inner.style.setProperty(mode === 'chars' ? '--ci' : '--wi', i++);
            outer.appendChild(inner);
            frag.appendChild(outer);
          });
          node.replaceChild(frag, child);
        } else if (child.nodeType === 1 && !child.classList.contains('word') && !child.classList.contains('ch')) {
          walk(child);
        }
      });
    }
    walk(root);
  }

  if (!reduced) {
    $$('[data-words]').forEach(function (el) { splitTextNodes(el, 'words'); });
    $$('[data-chars]').forEach(function (el) { splitTextNodes(el, 'chars'); });
  }

  /* ---------------------------------------------------------------- 5. Apparition au scroll */
  (function () {
    var targets = $$('[data-reveal],[data-words],[data-chars],.reveal-img');
    if (!targets.length) return;

    if (!('IntersectionObserver' in window) || reduced) {
      targets.forEach(function (el) { el.classList.add('is-in'); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-in');
        io.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.08 });

    targets.forEach(function (el) {
      // déjà visible au chargement : on révèle sans attendre le scroll
      var r = el.getBoundingClientRect();
      if (r.top < window.innerHeight * 0.92 && r.bottom > 0) {
        el.classList.add('is-in');
      } else {
        io.observe(el);
      }
    });
  })();

  /* ---------------------------------------------------------------- 6. Parallaxe du hero */
  (function () {
    var img = $('.hero__img');
    if (!img || reduced || coarse) return;
    var hero = img.closest('.hero'), ticking = false;
    function update() {
      var y = window.scrollY;
      if (y < hero.offsetHeight) img.style.transform = 'translate3d(0,' + (y * 0.16) + 'px,0) scale(1.08)';
      ticking = false;
    }
    img.style.transform = 'scale(1.08)';
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
  })();

  /* ---------------------------------------------------------------- 7. Remplissage des boutons
     La pastille part de l'endroit exact où le curseur entre dans le bouton. */
  (function () {
    if (coarse) return;
    $$('[data-flair], .btn').forEach(function (btn) {
      function place(e) {
        var r = btn.getBoundingClientRect();
        btn.style.setProperty('--fx', ((e.clientX - r.left) / r.width * 100) + '%');
        btn.style.setProperty('--fy', ((e.clientY - r.top) / r.height * 100) + '%');
      }
      btn.addEventListener('pointerenter', place);
      btn.addEventListener('pointerleave', place);
    });
  })();

  /* ---------------------------------------------------------------- 8. FAQ */
  (function () {
    $$('.faq__q').forEach(function (q) {
      q.addEventListener('click', function () {
        var item = q.closest('.faq__item');
        var open = q.getAttribute('aria-expanded') === 'true';
        q.setAttribute('aria-expanded', String(!open));
        item.classList.toggle('is-open', !open);
      });
    });
  })();

  /* ---------------------------------------------------------------- 9. Formulaire de contact
     Envoi AJAX vers le service de formulaire configuré dans l'attribut action.
     Sans JS, le formulaire se soumet normalement (POST classique).
     Tant que l'endpoint n'est pas configuré, on le dit clairement. */
  (function () {
    var form = $('[data-contact-form]');
    if (!form) return;
    var status = $('[data-form-status]', form.parentNode) || $('[data-form-status]');

    function say(msg, isError) {
      if (!status) return;
      status.textContent = msg;
      status.hidden = false;
      status.classList.toggle('form__status--err', !!isError);
      status.setAttribute('role', isError ? 'alert' : 'status');
    }

    form.addEventListener('submit', function (e) {
      var action = form.getAttribute('action') || '';

      // endpoint non encore branché : on n'envoie rien dans le vide
      if (action.indexOf('VOTRE_ID') !== -1 || !action) {
        e.preventDefault();
        say("Le formulaire n'est pas encore relié à sa boîte de réception. "
          + "En attendant, écrivez directement à thomasnunes.chiropratique@gmail.com "
          + "ou appelez le 06 88 75 54 52.", true);
        return;
      }
      if (form.querySelector('[name="_gotcha"]') && form.querySelector('[name="_gotcha"]').value) {
        e.preventDefault();
        return; // piège à robots
      }
      if (!window.fetch) return; // laisse le POST natif faire le travail

      e.preventDefault();
      var btn = form.querySelector('[type="submit"]');
      var label = btn ? btn.querySelector('.btn__label') : null;
      var original = label ? label.textContent : '';
      if (label) label.textContent = 'Envoi…';
      if (btn) btn.disabled = true;

      fetch(action, {
        method: 'POST',
        body: new FormData(form),
        headers: { Accept: 'application/json' }
      }).then(function (res) {
        if (res.ok) {
          form.reset();
          say('Merci, votre message est bien parti. Je vous réponds au plus vite.');
        } else {
          return res.json().then(function (d) {
            throw new Error((d.errors && d.errors.map(function (x) { return x.message; }).join(', ')) || 'Erreur');
          });
        }
      }).catch(function () {
        say("L'envoi n'a pas abouti. Vous pouvez écrire à thomasnunes.chiropratique@gmail.com "
          + 'ou appeler le 06 88 75 54 52.', true);
      }).then(function () {
        if (label) label.textContent = original;
        if (btn) btn.disabled = false;
      });
    });
  })();

  /* ---------------------------------------------------------------- 10. Réservation
     L'agenda PracticeHub est chargé en iframe (testé : l'affichage en cadre
     est bien autorisé). Comme il est sur un autre domaine, on ne peut pas lire
     sa hauteur : elle est réservée en CSS, mesurée sur l'agenda réel.

     Sur la page de publicité, le cadre n'a pas de src au départ (data-src) :
     ses 470 Ko de scripts ne doivent pas ralentir le premier écran. Il est
     lancé une fois la page affichée, ou plus tôt si le visiteur va vers
     l'agenda. Les paramètres de campagne de l'annonce (utm_) sont alors
     ajoutés à son adresse : PracticeHub les enregistre avec la réservation,
     ce qui dit quelles réservations viennent des publicités. Seuls les utm_
     passent, aucun identifiant de clic. Le site n'a aucun traceur
     publicitaire : ni pixel, ni cookie de mesure.

     Ici on gère aussi le voile de chargement et le secours si rien ne vient. */
  var utmAnnonce = (function () {
    if (!document.body.hasAttribute('data-tunnel') || !window.URLSearchParams) return [];
    var liste = [];
    new URLSearchParams(location.search).forEach(function (valeur, cle) {
      if (/^utm_[a-z]+$/.test(cle) && valeur.length < 120) liste.push([cle, valeur]);
    });
    return liste;
  })();
  function avecUtm(adresse) {
    if (!utmAnnonce.length) return adresse;
    try {
      var url = new URL(adresse, location.href);
      utmAnnonce.forEach(function (p) { url.searchParams.set(p[0], p[1]); });
      return url.toString();
    } catch (e) { return adresse; }
  }
  // les liens « ouvrir la réservation » gardent aussi l'origine de la visite
  if (utmAnnonce.length) {
    $$('a[href^="https://thomasnuneschiropratique.neptune.practicehub.io"]').forEach(function (a) {
      a.setAttribute('href', avecUtm(a.getAttribute('href')));
    });
  }

  (function () {
    var host = $('[data-booking]');
    if (!host) return;
    var frame = host.querySelector('[data-booking-frame]');
    var fallback = host.querySelector('[data-booking-fallback]');
    if (!frame || !fallback) return;

    var DEADLINE = 15000;
    var done = false;
    var timer = null;

    function settled(ok) {
      if (done) return;
      done = true;
      clearTimeout(timer);
      if (ok) {
        host.classList.add('is-loaded');
      } else {
        host.classList.add('is-offline');
        fallback.hidden = false;
      }
    }
    // le délai de secours part quand l'agenda est réellement demandé
    function armer() { if (!timer && !done) timer = setTimeout(function () { settled(false); }, DEADLINE); }

    // Un cadre sans src charge about:blank, qui déclenche aussi « load » :
    // on ne compte que le chargement de l'agenda lui-même.
    // Au retour dans l'historique sans bfcache, le navigateur remet lui-même
    // l'agenda dans le cadre alors que l'attribut src est vide : on ne le
    // recharge pas (double chargement, entrée d'historique en trop).
    function dejaCharge() {
      try { return frame.contentWindow.location.href !== 'about:blank'; } catch (e) { return true; }
    }
    frame.addEventListener('load', function () { if (frame.getAttribute('src') || dejaCharge()) settled(true); });
    frame.addEventListener('error', function () { settled(false); });

    var differe = frame.getAttribute('data-src');
    if (!differe) {
      // src écrit dans la page : un petit script placé juste après le cadre
      // note son chargement, au cas où il finirait avant ce fichier.
      if (frame.hasAttribute('data-charge')) settled(true); else armer();
      return;
    }

    function lancer() {
      if (frame.getAttribute('src')) return;
      if (dejaCharge()) { settled(true); return; }   // restauré par l'historique
      frame.setAttribute('src', avecUtm(differe));
      armer();
    }
    if (document.readyState === 'complete') lancer();
    else window.addEventListener('load', lancer);
    $$('a[href="#agenda"]').forEach(function (a) { a.addEventListener('click', lancer); });
    if ('IntersectionObserver' in window) {
      var guet = new IntersectionObserver(function (entries) {
        if (entries[0].isIntersecting) { lancer(); guet.disconnect(); }
      }, { rootMargin: '150% 0px' });
      guet.observe(host);
    }
  })();


  /* ---------------------------------------------------------------- 12. La scène des 3 stress
     Le défilement est retenu par position:sticky (voir le CSS). Ici on se
     contente de traduire « où en est-on dans la section » en un nombre de 0 à 1,
     puis d'en déduire : le niveau d'eau, les cascades allumées, l'étape de
     texte affichée, et le débordement.

     Aucune interception de la molette : si ce script ne tourne pas, la section
     reste une section normale et tout le texte est lisible. */
  (function () {
    var scene = $('[data-scene]');
    if (!scene) return;

    var vase = $('.vase', scene);
    var steps = $$('.scene__step', scene);
    var flux = $$('.flux', scene);
    var hint = $('[data-scene-hint]', scene);
    var track = $('.scene__track', scene);
    if (!vase || !track || !steps.length) return;

    // Mouvement réduit : on montre l'état final, sans épingler la section.
    if (reduced) {
      vase.style.setProperty('--n1', '0.34');
      vase.style.setProperty('--n2', '0.67');
      vase.style.setProperty('--n3', '1');
      vase.classList.add('deborde');
      flux.forEach(function (f) { f.classList.add('is-on'); });
      steps.forEach(function (s) { s.classList.add('is-on'); });
      return;
    }

    // Écran trop court (téléphone en paysage) : on n'épingle pas, la scène
    // resterait illisible. Le texte reste complet, simplement déroulé.
    function tropCourt() { return window.innerHeight < 560; }
    if (tropCourt()) {
      vase.style.setProperty('--n1', '0.34');
      vase.style.setProperty('--n2', '0.67');
      vase.style.setProperty('--n3', '1');
      vase.classList.add('deborde');
      flux.forEach(function (f) { f.classList.add('is-on'); });
      steps.forEach(function (s) { s.classList.add('is-on'); });
      return;
    }

    scene.classList.add('is-pinned');


    // Seuils d'allumage des trois cascades, puis du débordement.
    var DEPART = [0.10, 0.30, 0.50];
    var FIN_REMPLISSAGE = 0.74;
    var ETAPES = [0, 0.10, 0.30, 0.50, 0.74];

    var ticking = false;
    var dernierNiveau = -1, derniereEtape = -1;

    function update() {
      var r = track.getBoundingClientRect();
      var course = track.offsetHeight - window.innerHeight;
      var p = course > 0 ? (-r.top / course) : 0;
      p = p < 0 ? 0 : (p > 1 ? 1 : p);

      // Trois strates : chaque stress remplit son tiers. Une strate reste à
      // zéro tant que sa cascade n'a pas commencé, puis démarre exactement au
      // niveau atteint par la précédente — la jointure est donc invisible.
      var PALIERS = [0, 0.34, 0.67, 1];
      var niveaux = [0, 0, 0];
      var niveau = 0;
      for (var k = 0; k < 3; k++) {
        var debut = DEPART[k];
        var fin = (k < 2 ? DEPART[k + 1] : FIN_REMPLISSAGE);
        if (p >= debut) {
          var t = (p - debut) / (fin - debut);
          t = t < 0 ? 0 : (t > 1 ? 1 : t);
          niveaux[k] = PALIERS[k] + t * (PALIERS[k + 1] - PALIERS[k]);
          niveau = niveaux[k];
        }
      }
      if (Math.abs(niveau - dernierNiveau) > 0.002) {
        vase.style.setProperty('--n1', niveaux[0].toFixed(3));
        vase.style.setProperty('--n2', niveaux[1].toFixed(3));
        vase.style.setProperty('--n3', niveaux[2].toFixed(3));
        dernierNiveau = niveau;
      }

      // cascades : elles s'allument l'une après l'autre, puis se coupent
      // quand le vase déborde — ce n'est plus elles qui comptent.
      var coupure = p > 0.86;
      var uneCoule = false;
      flux.forEach(function (f, i) {
        var actif = !coupure && p >= DEPART[i];
        f.classList.toggle('is-on', actif);
        if (actif) uneCoule = true;
      });
      vase.classList.toggle('coule', uneCoule);

      // débordement
      vase.classList.toggle('deborde', p > FIN_REMPLISSAGE + 0.02);

      // étape de texte
      var etape = 0;
      for (var i = ETAPES.length - 1; i >= 0; i--) {
        if (p >= ETAPES[i]) { etape = i; break; }
      }
      if (etape !== derniereEtape) {
        steps.forEach(function (s, i) { s.classList.toggle('is-on', i === etape); });
        derniereEtape = etape;
      }

      if (hint) hint.classList.toggle('is-on', p > 0.02 && p < 0.92);
      ticking = false;
    }

    function demander() {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }
    window.addEventListener('scroll', demander, { passive: true });
    window.addEventListener('resize', demander, { passive: true });
    update();
  })();


  /* ---------------------------------------------------------------- 13. Le texte qui s'encre
     Les mots passent du gris à leur couleur à mesure que le paragraphe
     traverse l'écran. Vaut pour chaque [data-ink] de la page.
     Mouvement réduit ou script absent : le texte est encré d'emblée. */
  (function () {
    var blocs = $$('[data-ink]');
    if (!blocs.length || reduced) return;

    var suivis = blocs.map(function (bloc) {
      splitTextNodes(bloc, 'words');
      bloc.classList.add('is-inking');
      // ordre du document : un soulignement précède ses propres mots
      return { bloc: bloc, jetons: $$('.word, .surligne', bloc), dernier: -1 };
    });

    var ticking = false;
    function update() {
      var vh = window.innerHeight;
      suivis.forEach(function (s) {
        var r = s.bloc.getBoundingClientRect();
        if (r.bottom < -vh || r.top > vh * 2) return;
        var p = (vh * 0.84 - r.top) / (r.height + vh * 0.3);
        p = p < 0 ? 0 : (p > 1 ? 1 : p);
        var n = Math.round(p * s.jetons.length);
        if (n !== s.dernier) {
          s.jetons.forEach(function (j, k) { j.classList.toggle('is-ink', k < n); });
          s.dernier = n;
        }
      });
      ticking = false;
    }
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
    window.addEventListener('resize', update, { passive: true });
    update();
  })();


  /* ---------------------------------------------------------------- 14. Parallaxe des photos
     Chaque élément [data-parallax="x"] glisse de x fois son écart au centre
     de l'écran. Utilisé à l'intérieur d'un cadre fixe : c'est l'image qui
     bouge, pas la mise en page. */
  (function () {
    var els = $$('[data-parallax]');
    if (!els.length || reduced || coarse) return;
    var ticking = false;
    function update() {
      var vh = window.innerHeight;
      els.forEach(function (el) {
        var r = el.getBoundingClientRect();
        if (r.bottom < -200 || r.top > vh + 200) return;
        var ecart = (r.top + r.height / 2) - vh / 2;
        var f = parseFloat(el.getAttribute('data-parallax')) || 0;
        // on retire la translation déjà appliquée pour mesurer la position d'origine
        var y = -(ecart - (el._py || 0)) * f;
        el.style.transform = 'translate3d(0,' + y.toFixed(1) + 'px,0)';
        el._py = y;
      });
      ticking = false;
    }
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
    window.addEventListener('resize', update, { passive: true });
    update();
  })();


  /* ---------------------------------------------------------------- 15. Le système nerveux
     Les mots du texte et les légendes du dessin allument la partie qu'ils
     nomment. Tant que personne ne survole, les trois parties s'allument à
     tour de rôle, et seulement quand la section est à l'écran. */
  (function () {
    var art = $('[data-nerfs]');
    if (!art) return;
    var section = art.closest('section') || art;
    var PARTIES = ['cerveau', 'colonne', 'corps'];
    var declencheurs = $$('[data-part]', section);
    var mots = $$('.nerfs__mot', section);
    var tour = -1, minuterie = null, visible = false, main = false;

    function allumer(partie) {
      PARTIES.forEach(function (p) { art.classList.toggle('is-' + p, p === partie); });
      mots.forEach(function (m) { m.classList.toggle('is-on', m.getAttribute('data-part') === partie); });
    }
    function suivant() {
      tour = (tour + 1) % PARTIES.length;
      allumer(PARTIES[tour]);
    }
    function relancer() {
      clearInterval(minuterie);
      minuterie = null;
      if (visible && !main && !reduced) {
        minuterie = setInterval(suivant, 2600);
      }
    }

    declencheurs.forEach(function (el) {
      el.addEventListener('mouseenter', function () {
        main = true; relancer();
        allumer(el.getAttribute('data-part'));
      });
      el.addEventListener('mouseleave', function () {
        main = false; allumer(null); relancer();
      });
    });

    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        visible = entries[0].isIntersecting;
        // on laisse le dessin se tracer avant d'allumer quoi que ce soit
        if (visible && tour === -1) setTimeout(function () { relancer(); }, 2400);
        else relancer();
        if (!visible) allumer(null);
      }, { threshold: 0.35 }).observe(art);
    }
  })();


  /* ---------------------------------------------------------------- 16. Le parcours de la première visite
     La ligne se remplit au défilement ; chaque étape s'allume quand la
     ligne l'atteint. Sans script : ligne pleine, toutes les étapes visibles. */
  (function () {
    var liste = $('[data-etapes]');
    if (!liste || reduced) return;
    var etapes = $$('.etape', liste);
    liste.classList.add('is-suivi');
    var ticking = false;

    function update() {
      var r = liste.getBoundingClientRect(), vh = window.innerHeight;
      var vertical = window.innerWidth <= 900;
      var p = vertical
        ? (vh * 0.7 - r.top) / r.height
        : (vh * 0.88 - r.top) / (vh * 0.5);
      p = p < 0 ? 0 : (p > 1 ? 1 : p);
      liste.style.setProperty('--prog', p.toFixed(3));
      etapes.forEach(function (e, i) {
        var seuil = vertical
          ? (e.offsetTop / r.height)
          : (i / etapes.length);
        e.classList.toggle('is-on', p >= seuil + 0.01 || (i === 0 && p > 0));
      });
      ticking = false;
    }
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
    window.addEventListener('resize', update, { passive: true });
    update();
  })();


  /* ---------------------------------------------------------------- 17. Les avis, un à la fois
     Défilement automatique toutes les 8 secondes, suspendu au survol, au
     focus clavier et hors de l'écran. La barre montre le temps restant.
     Mouvement réduit : pas de défilement automatique, les boutons restent. */
  (function () {
    var scene = $('[data-temoins]');
    if (!scene) return;
    var avis = $$('.temoin', scene);
    var noms = $$('.nom');
    var nav = $('[data-temoins-nav]');
    var barre = $('[data-temoins-barre]');
    var num = $('[data-temoins-num]');
    var listeNoms = $('[data-temoins-noms]');
    if (avis.length < 2) return;

    var DUREE = 8000;
    var courant = 0, ecoule = 0, avant = null, raf = null;
    var visible = false, survol = false;

    scene.classList.add('is-actif');
    if (nav) nav.hidden = false;
    if (listeNoms) listeNoms.hidden = false;

    function montrer(i, parLeVisiteur) {
      courant = (i + avis.length) % avis.length;
      avis.forEach(function (a, k) {
        a.classList.toggle('is-on', k === courant);
        a.setAttribute('aria-hidden', String(k !== courant));
      });
      noms.forEach(function (n, k) {
        if (k === courant) n.setAttribute('aria-current', 'true');
        else n.removeAttribute('aria-current');
      });
      if (num) num.textContent = String(courant + 1);
      // annoncé aux lecteurs d'écran seulement quand le visiteur a choisi
      scene.setAttribute('aria-live', parLeVisiteur ? 'polite' : 'off');
      ecoule = 0;
    }

    function boucle(t) {
      if (avant !== null && visible && !survol) ecoule += t - avant;
      avant = t;
      if (barre) barre.style.transform = 'scaleX(' + Math.min(ecoule / DUREE, 1).toFixed(4) + ')';
      if (ecoule >= DUREE) montrer(courant + 1, false);
      raf = requestAnimationFrame(boucle);
    }
    function demarrer() { if (!raf && !reduced) { avant = null; raf = requestAnimationFrame(boucle); } }
    function arreter() { if (raf) { cancelAnimationFrame(raf); raf = null; } }

    $$('[data-sens]', scene).forEach(function (b) {
      b.addEventListener('click', function () {
        montrer(courant + parseInt(b.getAttribute('data-sens'), 10), true);
      });
    });
    noms.forEach(function (n) {
      n.addEventListener('click', function () {
        montrer(parseInt(n.getAttribute('data-cible'), 10), true);
      });
    });

    var zone = scene.closest('section') || scene;
    zone.addEventListener('mouseenter', function () { survol = true; });
    zone.addEventListener('mouseleave', function () { survol = false; });
    zone.addEventListener('focusin', function () { survol = true; });
    zone.addEventListener('focusout', function () { survol = false; });

    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        visible = entries[0].isIntersecting;
        if (visible) demarrer(); else arreter();
      }, { threshold: 0.3 }).observe(scene);
    }
    montrer(0, false);
  })();

  /* ---------------------------------------------------------------- 18. La carte des motifs
     Chaque motif allume la zone du corps qu'il concerne. Au survol ou au
     clavier, on suit le visiteur ; sinon, les motifs défilent seuls tant que
     la carte est à l'écran. Un clic fige le choix. */
  (function () {
    var carte = $('[data-carte]');
    if (!carte) return;
    var boutons = $$('.motif-bt', carte);
    var zones = $$('.zone', carte);
    var tour = -1, minuterie = null, visible = false, main = false, fige = false;

    function allumer(bouton) {
      var z = bouton ? bouton.getAttribute('data-zone') : null;
      zones.forEach(function (c) {
        c.classList.toggle('is-on', z === 'tout' || c.getAttribute('data-zone') === z);
      });
      boutons.forEach(function (b) {
        var on = b === bouton;
        b.classList.toggle('is-on', on);
        b.setAttribute('aria-pressed', String(on));
      });
    }
    function suivant() {
      tour = (tour + 1) % boutons.length;
      allumer(boutons[tour]);
    }
    function relancer() {
      clearInterval(minuterie);
      minuterie = null;
      if (visible && !main && !fige && !reduced) minuterie = setInterval(suivant, 2600);
    }

    boutons.forEach(function (b, i) {
      function entrer() { main = true; tour = i; allumer(b); relancer(); }
      function sortir() { main = false; if (!fige) relancer(); }
      b.addEventListener('mouseenter', entrer);
      b.addEventListener('focus', entrer);
      b.addEventListener('mouseleave', sortir);
      b.addEventListener('blur', sortir);
      b.addEventListener('click', function () { fige = true; tour = i; allumer(b); relancer(); });
    });

    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        visible = entries[0].isIntersecting;
        if (visible && tour === -1) { suivant(); }
        relancer();
      }, { threshold: 0.25 }).observe(carte);
    }
  })();


  /* ---------------------------------------------------------------- 19. Compteur
     [data-compte="5"] : le nombre monte jusqu'à sa valeur à l'apparition.
     Le HTML contient déjà la valeur finale : sans script, rien ne change. */
  (function () {
    var els = $$('[data-compte]');
    if (!els.length || reduced || !('IntersectionObserver' in window)) return;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        io.unobserve(e.target);
        var el = e.target, fin = parseInt(el.getAttribute('data-compte'), 10), debut = null;
        function pas(t) {
          if (debut === null) debut = t;
          var p = Math.min((t - debut) / 1400, 1);
          p = 1 - Math.pow(1 - p, 3);
          el.textContent = String(Math.max(1, Math.round(p * fin)));
          if (p < 1) requestAnimationFrame(pas);
        }
        requestAnimationFrame(pas);
      });
    }, { threshold: 0.5 });
    els.forEach(function (el) { io.observe(el); });
  })();

  /* ---------------------------------------------------------------- 20. Mon approche (accueil)
     L'étape active est la dernière dont le haut a passé le milieu de
     l'écran. Elle s'éclaire, son rameau pousse, la photo de gauche change
     et la colonne se remplit jusqu'à elle. Sans script : tout est visible,
     la première photo reste affichée. */
  (function () {
    var sec = $('[data-approche]');
    if (!sec) return;
    var pas = $$('.voie__pas', sec);
    var imgs = $$('.approche__img', sec);
    var voie = $('.voie', sec);
    if (!pas.length || !voie) return;
    sec.classList.add('is-suivi');

    var dernier = -1, ticking = false;
    function update() {
      var milieu = window.innerHeight * 0.58, actif = 0;
      pas.forEach(function (p, i) {
        if (p.getBoundingClientRect().top < milieu) actif = i + 1;
      });
      if (actif !== dernier) {
        pas.forEach(function (p, i) {
          p.classList.toggle('is-on', i + 1 === actif);
          p.classList.toggle('est-passe', i + 1 <= actif);
        });
        imgs.forEach(function (im) {
          im.classList.toggle('is-on', parseInt(im.getAttribute('data-pas'), 10) === actif);
        });
        dernier = actif;
      }
      var r = voie.getBoundingClientRect();
      var prog = (milieu - r.top) / r.height;
      prog = prog < 0 ? 0 : (prog > 1 ? 1 : prog);
      voie.style.setProperty('--prog', prog.toFixed(3));
      ticking = false;
    }
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
    window.addEventListener('resize', update, { passive: true });
    update();
  })();

  /* ---------------------------------------------------------------- 21. Horaires : le jour d'aujourd'hui
     La colonne du jour courant est simplement soulignée. Rien d'autre :
     on n'affiche pas « ouvert maintenant », un jour férié rendrait ça faux. */
  (function () {
    var semaine = $('[data-semaine]');
    if (!semaine) return;
    var jour = semaine.querySelector('[data-jour="' + new Date().getDay() + '"]');
    if (jour) jour.classList.add('is-aujourdhui');
  })();

  /* ---------------------------------------------------------------- 22. Tunnel : barre fixe en bas d'écran
     Elle apparaît une fois le bouton du haut sorti de l'écran, et s'efface
     quand l'agenda occupe l'écran (inutile, et il faut de la place pour
     réserver). */
  (function () {
    var barre = $('[data-barre]');
    var cta = $('[data-cta-ouverture]');
    if (!barre || !cta || !('IntersectionObserver' in window)) return;
    var agenda = $('[data-agenda]');
    var ctaVisible = true, agendaVisible = false;

    function maj() {
      barre.hidden = ctaVisible || agendaVisible;
    }
    new IntersectionObserver(function (e) { ctaVisible = e[0].isIntersecting; maj(); }).observe(cta);
    if (agenda) {
      new IntersectionObserver(function (e) { agendaVisible = e[0].isIntersecting; maj(); },
        { rootMargin: '-30% 0px -30% 0px' }).observe(agenda);
    }
  })();

})();
