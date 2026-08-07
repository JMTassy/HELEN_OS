# GIT_CRYPT_SELECTIVE_ENCRYPTION_V0

```
zone            : GARDEN / NO_CLAIM
authority       : false
admission       : none
ledger_effect   : none
status          : PROPOSAL — exploratory, not admitted
scope           : Archivist-Director vault (Obsidian + Git second brain)
date_recorded   : 2026-08-07
epistemic_tag   : COMMUNICATION_ACT relayed upstream, reviewed and corrected locally
```

---

## 1. Objet

Évaluer `git-crypt` comme mécanisme de chiffrement **sélectif et transparent**
de fichiers sensibles dans un repo Git servant de second brain gouverné
(Obsidian + plugin Git), sans chiffrer l'ensemble du vault.

## 2. Mécanique (résumé vérifiable)

- Filtres Git clean/smudge ; AES-256 ; ciphertext côté remote, plaintext
  dans le working tree une fois déverrouillé.
- Sélection par `.gitattributes` :

  ```gitattributes
  private/** filter=git-crypt diff=git-crypt
  *.key      filter=git-crypt diff=git-crypt
  ```

- Accès : GPG (`git-crypt add-gpg-user`) ou clé symétrique exportée
  (`git-crypt export-key`), puis `git-crypt unlock` après clone.
- Le plugin Obsidian Git desktop fonctionne sans modification : il appelle
  git, qui applique les filtres.

## 3. Limites reconnues dans l'exploration amont

- Métadonnées visibles : noms de fichiers, arborescence, messages de commit,
  tailles, fréquence de modification.
- Diffs des fichiers chiffrés inutilisables (binaires).
- Non conçu pour chiffrer un vault entier.
- Gestion de clés rudimentaire ; maintenance du projet amont faible.

## 4. Correctifs apportés à l'exploration amont (revue locale)

### 4.1 Pas de révocation rétroactive — limite structurante n°1

Retirer un utilisateur GPG ne re-chiffre pas l'historique. Une clé qui fuit
déchiffre **tout l'historique, définitivement**, sauf réécriture complète du
repo (rotation = rewrite + re-clone partout). Pour un second brain à horizon
long, cette propriété domine toutes les autres considérations.

### 4.2 Mobile : cassé, pas « à friction »

Le plugin Obsidian Git mobile repose sur isomorphic-git, qui n'exécute pas
les filtres clean/smudge. Sur iOS/Android, les chemins protégés apparaissent
en **ciphertext brut**. Tout dossier devant rester lisible sur téléphone est
hors périmètre git-crypt.

### 4.3 Incompatibilité doctrinale avec la spine HELEN

`NO HASH = NO VOICE` suppose la replayabilité : un vérificateur doit pouvoir
recalculer `payload_hash = sha256(canon(payload))` sur ce que le repo
contient. Un chemin chiffré côté remote rend cette vérification impossible
sans détention de clé. Conséquence :

- **Jamais de git-crypt sur les chemins sovereign** — ledger, receipts,
  schemas, closures, registres MAYOR — intégralement hors périmètre.
- Acceptable uniquement pour du matériel privé qui n'entre jamais dans la
  chaîne de preuve.

## 5. Position vis-à-vis de l'existant HELEN

Une grande partie du besoin est déjà couverte par la **ségrégation par repo**
plutôt que par chiffrement in-repo :

- Corpus HELEN sensible → repo privé dédié (décision 2026-06-04).
- Secrets → `~/.helen_env` mode 600, jamais dans git.
- Corpus UZIK → kernel-side, jamais poussé.

git-crypt n'apporte de valeur que pour le cas résiduel : journaux personnels
ou IP client cohabitant **dans le même repo** qu'un knowledge base clair dont
on veut historique, recherche et graphe. Si ce cas est réel pour
l'Archivist-Director, comparer d'abord avec **SOPS + age** (meilleure gestion
de clés, même limite d'historique).

## 6. Pattern recommandé (si adopté)

```text
vault/
├── knowledge/        ← clair (recherche, postures, constitution, graphes)
├── .proposed/        ← staging gouvernance
├── private/          ← git-crypt
│   ├── journals/
│   ├── client/
│   └── credentials/  ← à éviter : préférer ~/.helen_env hors repo
└── .gitattributes    ← private/** filter=git-crypt
```

Règles d'exploitation :

1. Exporter et sauvegarder la clé symétrique immédiatement après
   `git-crypt init` — perte de clé = perte définitive du contenu.
2. La clé ne rentre jamais dans un repo, chiffrée ou non.
3. Nouvelle machine : clone → unlock → ouvrir dans Obsidian.
4. Noms de fichiers sous `private/` : considérer qu'ils sont publics
   (métadonnées non chiffrées) — nommer en conséquence.

## 7. Verdict proposé (non admis)

Sélectif : oui, pour le cas résiduel §5, avec les règles §6.
Global : non. Sovereign : jamais.
Alternative à instruire avant décision : SOPS + age.

---

```
seal      : FOUND ≠ VERIFIED · COPY ≠ ORIGINAL · DOCUMENT ≠ TRUTH
authority : false — ce document ne décide rien ; il instruit une décision.
```

HELEN OS — created by JM Tassy.
