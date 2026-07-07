# GitHub Upload Guide

Recommended repository name:

```text
mobile-communication-system-simulator
```

## First-time upload

```bash
cd mobile_comm_sim

git init
git add .
git commit -m "Initial commit: mobile communication simulator"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/mobile-communication-system-simulator.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

## Run locally

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
python main.py
```

## Build executable

```bash
pip install pyinstaller
pyinstaller mobile_comm_sim.spec
```
