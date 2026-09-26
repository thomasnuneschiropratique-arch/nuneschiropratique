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

C'est fini. Ensuite, pour chaque modification, tu pourras simplement
double-cliquer sur **`Publier les modifications.command`** dans le dossier.

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

Chez ton registrar (là où tu as acheté `nuneschiropratique.fr`), zone DNS.

**Supprime** les enregistrements A / CNAME existants qui pointent vers WordPress,
puis ajoute :

| Type | Nom / Hôte | Valeur | TTL |
|---|---|---|---|
| A | `@` | `185.199.108.153` | 3600 |
| A | `@` | `185.199.109.153` | 3600 |
| A | `@` | `185.199.110.153` | 3600 |
| A | `@` | `185.199.111.153` | 3600 |
| CNAME | `www` | `thomasnuneschiropratique-arch.github.io.` | 3600 |

(Adresses vérifiées le jour de la rédaction en interrogeant directement
`thomasnuneschiropratique-arch.github.io`, pas recopiées d'une documentation.)

Aujourd'hui ton domaine pointe vers WordPress (`192.0.78.24` et `192.0.78.25`)
et `www` est un alias vers le domaine principal. Ce sont ces enregistrements-là
qu'il faut remplacer.

Les quatre A sont obligatoires (GitHub répartit la charge). Selon le registrar,
`@` peut s'appeler « racine », « vide » ou le nom de domaine complet.

Si tu préfères l'IPv6, ajoute aussi (facultatif) :
`2606:50c0:8000::153`, `2606:50c0:8001::153`, `2606:50c0:8002::153`, `2606:50c0:8003::153` en AAAA.

**Vérification** (quelques minutes à quelques heures de propagation) :

```bash
dig +short nuneschiropratique.fr
dig +short www.nuneschiropratique.fr
```

Puis dans GitHub : **Settings → Pages**, le domaine doit passer au vert, et
**Enforce HTTPS** devient cochable (certificat Let's Encrypt automatique).

---

## 5. Après la bascule

- [ ] **Google Search Console** : ajouter la propriété `nuneschiropratique.fr`,
      soumettre `https://nuneschiropratique.fr/sitemap.xml`.
- [ ] **Fiche Google Business** : vérifier que le site déclaré est bien
      `https://nuneschiropratique.fr`. (Le bouton « Voir tous les avis » de la page
      Avis pointe déjà vers ta fiche.)
- [ ] Parcourir le site sur ton téléphone.
- [ ] Coller le lien du site dans un message (WhatsApp, LinkedIn) pour voir
      l'aperçu : c'est l'image `static/img/og.png`, le logo sur fond papier.
      Pour la refaire après un changement de logo : `python3 tools/make-og.py`.
- [ ] Envoyer un message test via le formulaire.
- [ ] Ne ferme le site WordPress qu'une fois tout vérifié.

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
