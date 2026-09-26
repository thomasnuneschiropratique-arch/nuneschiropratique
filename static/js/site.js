/* =========================================================================
   Cabinet chiropratique Thomas Nunes — interactions
   Vanilla, sans dépendance. Tout est optionnel : si ce fichier ne se charge
   pas, le site reste entièrement lisible et navigable.
   ========================================================================= */
(function () {
  'use strict';

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
     Ici on ne gère que le voile de chargement et le secours si rien ne vient. */
  (function () {
    var host = document.querySelector('[data-booking]');
    if (!host) return;
    var frame = host.querySelector('[data-booking-frame]');
    var fallback = host.querySelector('[data-booking-fallback]');
    if (!frame || !fallback) return;

    var DEADLINE = 15000;
    var done = false;

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

    var timer = setTimeout(function () { settled(false); }, DEADLINE);
    frame.addEventListener('load', function () { settled(true); });
    frame.addEventListener('error', function () { settled(false); });

    // l'iframe peut avoir fini de charger avant l'exécution de ce script
    try {
      if (frame.contentWindow && frame.contentWindow.length >= 0 && frame.complete !== false) {
        setTimeout(function () { if (!done) settled(true); }, 2500);
      }
    } catch (e) { /* cross-origin : normal, on attend l'événement load */ }
  })();




  /* ---------------------------------------------------------------- 11. Mesure publicitaire
     Pixel Meta, chargé UNIQUEMENT après accord explicite du visiteur.
     Tant que PIXEL_ID vaut le texte d'attente, rien n'est chargé et le bandeau
     ne s'affiche pas : le site reste sans aucun traceur.

     Pour activer : remplacer la valeur ci-dessous par l'identifiant du pixel
     (Gestionnaire d'événements Meta -> Sources de données -> ton pixel).  */
  var PIXEL_ID = 'VOTRE_ID_PIXEL_META';

  (function () {
    var KEY = 'nc-consent-pub';
    var banner = $('[data-consent]');
    var configured = PIXEL_ID && PIXEL_ID.indexOf('VOTRE_ID') === -1;

    function stored() {
      try { return localStorage.getItem(KEY); } catch (e) { return null; }
    }
    function remember(value) {
      try { localStorage.setItem(KEY, value); } catch (e) { /* navigation privée */ }
    }

    function loadPixel() {
      if (!configured || window.fbq) return;

      /* extrait officiel Meta, recopié tel quel */
      !function (f, b, e, v, n, t, s) {
        if (f.fbq) return; n = f.fbq = function () {
          n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments);
        };
        if (!f._fbq) f._fbq = n; n.push = n; n.loaded = !0; n.version = '2.0'; n.queue = [];
        t = b.createElement(e); t.async = !0; t.src = v;
        s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s);
      }(window, document, 'script', 'https://connect.facebook.net/fr_FR/fbevents.js');

      window.fbq('init', PIXEL_ID);
      window.fbq('track', 'PageView');

      // La page de réservation est l'intention d'achat : on la remonte comme
      // « Lead ». C'est l'équivalent du suivi qui était posé sur le bouton,
      // en plus fiable — le bouton mène désormais à une page du site.
      if (location.pathname.indexOf('/prendre-rendez-vous') === 0) {
        window.fbq('track', 'Lead');
      }
    }

    function show() { if (banner) banner.hidden = false; }
    function hide() { if (banner) banner.hidden = true; }

    function decide(value) {
      remember(value);
      hide();
      if (value === 'oui') loadPixel();
    }

    if (!configured) { hide(); return; }

    var choice = stored();
    if (choice === 'oui') loadPixel();
    else if (choice !== 'non') show();

    if (banner) {
      var yes = banner.querySelector('[data-consent-yes]');
      var no = banner.querySelector('[data-consent-no]');
      if (yes) yes.addEventListener('click', function () { decide('oui'); });
      if (no) no.addEventListener('click', function () { decide('non'); });
    }

    // « Gérer les cookies » en pied de page : permet de revenir sur son choix
    $$('[data-consent-open]').forEach(function (link) {
      link.addEventListener('click', function (e) {
        e.preventDefault();
        show();
        if (banner) banner.scrollIntoView({ block: 'nearest' });
      });
    });
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

})();
