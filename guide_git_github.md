
# 📘 Guide Git & GitHub – Du Début au Merge

## 🧱 1. Initialisation du projet

```bash
git init
```
> Initialise un dépôt Git local.

```bash
git remote add origin https://github.com/nom-utilisateur/nom-depot.git
```
> Lie le dépôt local à un dépôt distant GitHub.

---

## 📦 2. Première version / Commit initial

```bash
git add .
```
> Ajoute tous les fichiers au staging area.

```bash
git commit -m "Initial commit"
```
> Crée un commit avec un message.

```bash
git branch -M main
git push -u origin main
```
> Renomme la branche par défaut en `main` et envoie le projet sur GitHub.

---

## 🌿 3. Création d'une branche pour une fonctionnalité

```bash
git checkout -b nom-de-branche
```
> Crée une nouvelle branche et se positionne dessus.

---

## ✍️ 4. Développement & commits

```bash
git add fichier_modifié
git commit -m "Description de la modification"
```
> Ajoute et commit les changements.

---

## ⬆️ 5. Push de la branche sur GitHub

```bash
git push -u origin nom-de-branche
```
> Envoie la branche sur GitHub.

---

## ✅ 6. Création d'une Pull Request (PR)

Sur GitHub :
- Aller dans le dépôt
- Cliquer sur "Compare & pull request"
- Ajouter un titre, une description
- Choisir la branche de destination (souvent `main`)

---

## 🔍 7. Revue de code (optionnelle)

- Les membres de l’équipe peuvent commenter.
- Des changements peuvent être demandés.

---

## 🔀 8. Merge de la Pull Request

Sur GitHub :
- Cliquer sur **"Merge pull request"**
- Puis sur **"Confirm merge"**

Optionnel :
```bash
git branch -d nom-de-branche
git push origin --delete nom-de-branche
```
> Supprimer la branche localement et à distance si elle n’est plus nécessaire.

---

## 🔄 9. Mise à jour locale

```bash
git checkout main
git pull origin main
```
> Met à jour la branche `main` locale avec les derniers changements depuis GitHub.

---

## 10. copier des fichiers sur sa branche
```bash
git checkout branche-contenant-fichier-aCopier -- nom-du-fichier
```

## 📝 Résumé visuel du workflow

```
main
 │
 ├──> feature/ma-fonctionnalité
 │     └──> PR -> merge
 └──> main (mis à jour)
```
