# Mise en ligne - marche à suivre

À faire une seule fois, dans l'ordre. Rien ici ne touche au site actuel tant que
tu n'as pas changé les DNS (étape 4). Tu peux donc tout préparer tranquillement.

---

## 1. Envoyer le site sur GitHub

Le dépôt existe déjà et il est vide :
`https://github.com/thomasnuneschiropratique-arch/nuneschiropratique`

L'adresse est déjà configurée dans le dossier. Il ne manque qu'une chose :
**te connecter à GitHub depuis ton Mac**, une seule fois. Je ne peux pas le
faire à ta place, c'est ton compte.

### Le plus simple : GitHub Desktop

1. Télécharge **GitHub Desktop** : https://desktop.github.com
2. Ouvre-le, connecte-toi avec ton compte GitHub (ça passe par le navigateur,
   pas de mot de passe à recopier).
3. Menu **File → Add Local Repository**, choisis le dossier `Sitechiro`.
4. Clique sur **Publish repository** (ou **Push origin**).

C'est fini. Ensuite, pour chaque modification, double-clique sur
**`Préparer la mise en ligne.command`** : il construit, contrôle et enregistre,
puis ouvre GitHub Desktop, où il ne reste qu'à cliquer sur **Push origin**.

### Ou en ligne de commande

Dans le Terminal, depuis le dossier `Sitechiro` :

```bash
git push -u origin main
```

Git demandera ton nom d'utilisateur (`thomasnuneschiropratique-arch`) puis un
mot de passe. Attention : GitHub n'accepte plus le mot de passe du compte, il
faut un **jeton d'accès**. Pour en créer un :
github.com → photo de profil → Settings → Developer settings →
Personal access tokens → Tokens (classic) → Generate new token →
coche la case `repo` → copie le jeton et colle-le comme mot de passe.

### Puis, sur github.com

5. Dans le dépôt : **Settings → Pages → Build and deployment → Source :
   GitHub Actions**
6. Toujours dans **Settings → Pages → Custom domain** : saisis
   `nuneschiropratique.fr`, puis coche **Enforce HTTPS** (disponible une fois
   les DNS propagés, étape 4).

Le fichier `static/CNAME` contient déjà `nuneschiropratique.fr` : il est
recopié à chaque construction, donc le domaine ne se perdra pas entre deux
déploiements.

---

## 2. Formulaire de contact - fait

Le formulaire est branché sur ton compte Formspree (`xoevkrwl`) et il
fonctionne : deux messages de test sont arrivés, dont un envoyé depuis le
formulaire de la page lui-même.

Tu as dû recevoir ces deux messages, intitulés « Test du formulaire ». Tu peux
les supprimer. Si Formspree t'a demandé de confirmer ton adresse, c'est normal :
c'est le cas au premier envoi.

Les messages des visiteurs arriveront sur `thomasnunes.chiropratique@gmail.com`.
Le plan gratuit accepte 50 messages par mois.

---

## 3. Réservation en ligne - déjà en place

L'agenda PracticeHub est **intégré en iframe** dans la page `/prendre-rendez-vous/`.
Les visiteurs réservent sans jamais quitter nuneschiropratique.fr, et tous les
boutons « Prendre rendez-vous » du site pointent vers cette page interne.

Rien à faire de ton côté. Pour information, sur les deux méthodes possibles :

| Méthode | État |
|---|---|
| **iframe** de la page de réservation | **fonctionne** - c'est ce qui est en place |
| widget JavaScript `booking-form-embed.js` | bloqué par CORS (PracticeHub n'autorise que son propre domaine) |

Le widget aurait permis un rendu encore plus intégré, sans hauteur fixe. Si un jour
tu veux l'essayer, il faut demander à PracticeHub d'ajouter `https://nuneschiropratique.fr`
aux domaines autorisés pour l'intégration. Ce n'est pas nécessaire : l'iframe suffit.

**Pages de confirmation.** Le site actuel a deux pages que PracticeHub utilise
probablement comme destination après une action :

- `/reservation-confirmee/` : « Réservation confirmée ! », après la prise de rendez-vous
- `/reservation-confirmee-copie/` : « Formulaire envoyé avec succès ! », après le
  questionnaire de santé

Je les ai recréées à l'identique, avec ton texte, à la même adresse : les patients
ne tomberont donc pas sur une erreur 404 après avoir réservé. Elles sont masquées
des moteurs de recherche. Dans PracticeHub (réglages de la réservation en ligne),
vérifie que les adresses de redirection sont bien
`https://nuneschiropratique.fr/reservation-confirmee/` et
`https://nuneschiropratique.fr/reservation-confirmee-copie/`. Si un pixel Meta
mesurait les conversions sur ces pages, il faudra le remettre (voir plus bas).

**Un point à surveiller :** PracticeHub n'envoie pas la hauteur de son contenu, et
l'iframe est sur un autre domaine - impossible de la mesurer automatiquement. La
hauteur est donc réservée en CSS, d'après des mesures faites sur ton agenda réel
(≈1650 px en desktop, ≈2400 px en mobile). Si tu ajoutes beaucoup de prestations,
une barre de défilement peut apparaître dans le cadre : dis-le-moi, c'est une valeur
à ajuster dans `static/css/site.css` (chercher `--ph-h`).

---

## 4. DNS - à faire en dernier

Ton domaine est géré chez **WordPress.com** (serveurs `ns1/2/3.wordpress.com`).
C'est là qu'on modifie les enregistrements : WordPress.com, puis Domaines,
`nuneschiropratique.fr`, Enregistrements DNS.

Aujourd'hui :

| Type | Nom | Valeur |
|---|---|---|
| A | `@` | `192.0.78.24` |
| A | `@` | `192.0.78.25` |
| CNAME | `www` | `nuneschiropratique.fr` |

Il n'y a rien d'autre sur ce domaine (ni mail, ni IPv6, ni vérification TXT) :
ces trois lignes sont les seules à toucher.

**Avant de toucher aux DNS**, sur github.com : dépôt, Settings, Pages,
**Custom domain**, saisis `nuneschiropratique.fr` et enregistre. Ton site actuel
n'est pas affecté.

**Ensuite**, chez WordPress.com : supprime les deux A et le CNAME `www`, puis ajoute :

| Type | Nom | Valeur |
|---|---|---|
| A | `@` | `185.199.108.153` |
| A | `@` | `185.199.109.153` |
| A | `@` | `185.199.110.153` |
| A | `@` | `185.199.111.153` |
| CNAME | `www` | `thomasnuneschiropratique-arch.github.io.` |

Les quatre A sont obligatoires. Ces adresses ont été vérifiées en interrogeant
directement `thomasnuneschiropratique-arch.github.io`.

Durée de vie actuelle : 5 minutes. Le changement se voit donc très vite. En
revanche, GitHub doit ensuite fabriquer le certificat HTTPS, ce qui peut prendre
de quelques minutes à une heure : le site peut afficher un avertissement de
sécurité pendant ce laps de temps. Dans Settings, Pages, coche **Enforce HTTPS**
dès qu'elle devient disponible.

**Le bon moment :** le week-end, le cabinet est fermé. Si tu as des publicités qui
tournent, mets-les en pause pendant l'opération.

**Pour revenir en arrière** en cas de problème, remets exactement les trois lignes
d'origine ci-dessus. En 5 minutes tu retrouves l'ancien site.

**Vérification** (depuis le Terminal, ou demande-moi de le faire) :

```bash
dig +short nuneschiropratique.fr
dig +short www.nuneschiropratique.fr
```

**Attention à l'échéance du domaine : il expire le 5 novembre 2026.** Vérifie
dans WordPress.com que le renouvellement automatique est actif, et ne supprime
pas l'abonnement au domaine en résiliant l'hébergement WordPress.

---

## 5. Après la bascule

- [x] DNS basculés vers GitHub Pages - fait le 27 septembre 2026, propagation
      immédiate, certificat HTTPS actif le jour même.
- [x] **Google Search Console** : propriété `nuneschiropratique.fr` validée
      (domaine, via l'enregistrement TXT), sitemap soumis - fait le
      28 septembre 2026.
- [x] **Fiche Google Business** : le domaine n'a pas changé (seule sa
      destination technique a changé), donc rien à modifier sur la fiche.
- [x] Parcourir le site sur ton téléphone.
- [x] Coller le lien du site dans un message (WhatsApp, LinkedIn) pour voir
      l'aperçu : c'est l'image `static/img/og.png`, le logo sur fond papier.
      Pour la refaire après un changement de logo : `python3 tools/make-og.py`.
- [x] Envoyer un message test via le formulaire - vérifié le 28 septembre 2026,
      depuis le vrai domaine en ligne.

Toute la liste est faite. Le site est vérifié de bout en bout ; tu peux fermer
le site WordPress quand tu le souhaites (voir « Fiche Google Business » plus
haut : ne résilie que l'hébergement, jamais l'abonnement au domaine).

---

## 6. Mesure d'audience - rien d'actif aujourd'hui

Le site ne dépose **aucun cookie** et ne charge **aucun traceur**. Pas de bandeau
de consentement, donc, puisqu'il n'y a rien à consentir.

Ton Pixel Meta est sur ton **tunnel de vente**, pas ici : tes campagnes continuent
de remonter leurs conversions comme avant, la refonte du site n'y change rien.

### Si un jour tu envoies des pubs vers le site

L'infrastructure est déjà posée, en sommeil. Une seule ligne à remplir, dans
`static/js/site.js` (section 11) :

```js
var PIXEL_ID = 'VOTRE_ID_PIXEL_META';   // <- remplacer par ton identifiant
```

Dès que la valeur est renseignée :

- un bandeau de consentement sobre apparaît en bas de page à la première visite ;
- le pixel ne se charge **qu'après un clic sur « Accepter »** - c'est ce qu'exige
  la CNIL, et c'est aussi meilleur pour la vitesse du site ;
- l'événement `PageView` part sur toutes les pages, et `Lead` sur la page
  « Prendre rendez-vous » - l'équivalent du suivi posé sur le bouton, en plus
  fiable puisque le bouton mène désormais à une page du site ;
- un lien « Gérer les cookies » en pied de page permet de revenir sur son choix.

L'identifiant se trouve dans le Gestionnaire d'événements Meta, rubrique
« Sources de données ».

Pour Google Analytics, c'est le même principe : dis-le-moi et je le branche
derrière le même bandeau.
