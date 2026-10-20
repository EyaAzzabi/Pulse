# Administration PULSE

L’espace `/admin` reprend les principes de [Jiser](https://github.com/EyaAzzabi/Jiser-code/blob/main/frontend/src/pages/AdminPlateforme.tsx) et de sa [file de demandes](https://github.com/EyaAzzabi/Jiser-code/blob/main/frontend/src/components/DemandesAcces.tsx), avec l’identité visuelle bleue de PULSE.

Aperçus issus d’une base de test isolée : [dashboard](screenshots/admin-dashboard.png), [revue d’un compte](screenshots/admin-validation.png), [version mobile](screenshots/admin-mobile.png). Ces comptes de démonstration ne sont pas ajoutés à la base de l’application.

## Mise en route

Depuis `backend`, appliquer les migrations à la base configurée, puis créer un administrateur dédié :

```powershell
python -m alembic upgrade head
python scripts/create_admin.py admin@example.com --name "Administrateur Pulse"
```

Le mot de passe est demandé de façon interactive, sans affichage. Le script refuse de convertir silencieusement un compte existant. Connectez-vous sur `/login` : le compte administrateur arrive automatiquement sur `/admin`.

Pour une base historique créée uniquement avec `create_all`, sans table `alembic_version`, vérifier d’abord que son schéma correspond à la révision `8aaa48b081f8`. Après sauvegarde et cette vérification, marquer cette révision avec `python -m alembic stamp 8aaa48b081f8`, puis exécuter `upgrade head`. Ne pas utiliser `stamp` sur une base de schéma inconnu.

## Fonctionnement

- Vue d’ensemble : comptes, entreprises, inscriptions sur 14 jours (UTC), répartition des statuts et dernières décisions.
- Validation : recherche, fiche du titulaire, durée d’attente, précontrôles de complétude, validation ou refus motivé.
- Utilisateurs : filtres, pagination, suspension motivée, réactivation et réouverture d’une demande refusée.
- Entreprises : propriétaires, membres, devise et état du parcours de configuration. Aucun accès global aux transactions financières n’est accordé à l’administrateur.
- Services : test de connexion à la base et état de configuration du LLM, de SMTP et des workflows. « Configuré » ne signifie pas que le service externe a été testé.
- Journal : auteur, compte, date, ancien et nouveau statuts, motif. Aucun endpoint de modification ou suppression du journal.

Les nouvelles inscriptions vérifiées par OTP entrent dans `PENDING`. Elles peuvent se connecter et consulter `/account-status`, mais les API métier exigent `APPROVED`. L’onboarding métier reprend après validation. Les comptes existants restent approuvés après migration ; leur ancienne vérification e-mail n’est pas inventée.

Transitions autorisées : `PENDING → APPROVED / REJECTED`, `APPROVED → SUSPENDED`, `SUSPENDED → APPROVED`, `REJECTED → PENDING`. Refus et suspension exigent un motif visible par le titulaire. La revue vérifie le statut attendu pour empêcher deux administrateurs d’écraser leurs décisions concurrentes.

Les décisions sont notifiées dans l’application via la page de statut (actualisation toutes les 30 secondes). Aucun e-mail de décision n’est envoyé par ce module. Les précontrôles vérifient les données présentes, sans prétendre vérifier l’identité juridique ni les justificatifs.

`is_admin` est un privilège de plateforme distinct des rôles d’organisation. Aucun endpoint public ne permet de l’attribuer. Les comptes administrateurs ne sont pas modifiables depuis la file de validation.
