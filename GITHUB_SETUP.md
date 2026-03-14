# GitHub Setup Guide

## Step 1: Initialize Git Repository

```bash
git init
```

## Step 2: Add All Files

```bash
git add .
```

## Step 3: Create Initial Commit

```bash
git commit -m "Initial commit: Resume Parser application"
```

## Step 4: Create GitHub Repository

1. Go to: https://github.com/new
2. Repository name: `resume-parser`
3. **Select "Private"** (important for security)
4. Click "Create repository"

## Step 5: Add Remote and Push

```bash
git remote add origin https://github.com/YOUR_USERNAME/resume-parser.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

## Security Checklist

✓ `.gitignore` - Protects `.env` and sensitive files
✓ `.env` - NOT committed (in .gitignore)
✓ `logs/` - NOT committed (in .gitignore)
✓ `uploads/` - NOT committed (in .gitignore)
✓ `__pycache__/` - NOT committed (in .gitignore)
✓ Repository set to **Private**

## What Gets Committed

✓ Source code (`.py` files)
✓ Templates (`.html`)
✓ Static files (`.css`, `.js`)
✓ Configuration (`.env.example`, `requirements.txt`)
✓ Documentation (`README.md`)
✓ `.gitignore` and `.gitattributes`

## What Does NOT Get Committed

✗ `.env` (contains API key)
✗ `logs/` (runtime logs)
✗ `uploads/` (temporary files)
✗ `drive_downloads/` (temporary files)
✗ `zip_extracted/` (temporary files)
✗ `__pycache__/` (Python cache)
✗ `.vscode/` (IDE settings)

## After Cloning

When someone clones your repository:

1. They need to create their own `.env` file:
```bash
cp .env.example .env
```

2. Add their own API key to `.env`:
```
GOOGLE_DRIVE_API_KEY=their_api_key_here
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download spaCy model:
```bash
python -m spacy download en_core_web_sm
```

5. Run the application:
```bash
python app.py
```

## Verify Before Pushing

Check what will be committed:

```bash
git status
```

Should show:
- Source files (`.py`, `.html`, `.css`, `.js`)
- Configuration files (`.env.example`, `requirements.txt`)
- Documentation (`README.md`, `SETUP.md`)
- Git files (`.gitignore`, `.gitattributes`)

Should NOT show:
- `.env` (sensitive)
- `logs/` (runtime)
- `uploads/` (temporary)
- `__pycache__/` (cache)

## Making Repository Private

If you already pushed to public:

1. Go to repository settings
2. Scroll to "Danger Zone"
3. Click "Change repository visibility"
4. Select "Private"
5. Confirm

## Updating After Changes

```bash
git add .
git commit -m "Description of changes"
git push
```

## Cloning Your Private Repository

```bash
git clone https://github.com/YOUR_USERNAME/resume-parser.git
cd resume-parser
```

You'll need to authenticate with GitHub (use personal access token or SSH key).

