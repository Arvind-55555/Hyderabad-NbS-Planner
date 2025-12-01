# 🚀 Deploy to Streamlit Cloud - Step by Step Guide

## Quick Deployment Guide

Follow these steps to publish your Hyderabad NbS Dashboard online!

---

## 📋 Prerequisites

- ✅ GitHub account (free) - https://github.com
- ✅ Streamlit Cloud account (free) - https://streamlit.io/cloud
- ✅ Your project files ready

---

## 🔧 Step 1: Initialize Git Repository

```bash
cd /home/arvind/Downloads/projects/Working/Hyderabad_Nbs

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Hyderabad NbS Dashboard"
```

---

## 📤 Step 2: Push to GitHub

### Option A: Using GitHub CLI (Recommended)

```bash
# Login to GitHub (if not already)
gh auth login

# Create repository
gh repo create Hyderabad-NbS-Dashboard --public --source=. --remote=origin --push
```

### Option B: Using GitHub Web Interface

1. Go to https://github.com/new
2. Repository name: `Hyderabad-NbS-Dashboard`
3. Description: "Interactive dashboard for Nature-based Solutions analysis in Hyderabad"
4. Make it **Public**
5. Click "Create repository"
6. Follow the commands shown:

```bash
git remote add origin https://github.com/YOUR_USERNAME/Hyderabad-NbS-Dashboard.git
git branch -M main
git push -u origin main
```

---

## ☁️ Step 3: Deploy to Streamlit Cloud

### 3.1 Sign Up for Streamlit Cloud

1. Go to https://streamlit.io/cloud
2. Click "Sign up" (use GitHub account for easy integration)
3. Connect your GitHub account

### 3.2 Deploy Your App

1. Click "New app" button
2. Select:
   - **Repository**: `YOUR_USERNAME/Hyderabad-NbS-Dashboard`
   - **Branch**: `main`
   - **Main file path**: `web_app.py`
3. Click "Deploy!"

### 3.3 Advanced Settings (Optional)

Click "Advanced settings" before deploying:

**Python version**: 3.11

**Add Secrets** (if needed):
```toml
# No secrets needed for this app
```

---

## ⚡ Step 4: Wait for Deployment

- Initial deployment: 2-5 minutes
- Status shown in real-time
- Watch logs for any errors

---

## 🎉 Step 5: Get Your Link!

Once deployed, you'll get a URL like:

**https://your-username-hyderabad-nbs-dashboard.streamlit.app**

Share this link with anyone! 🌍

---

## 🔄 Automatic Updates

Every time you push to GitHub, Streamlit Cloud will automatically redeploy your app!

```bash
# Make changes
git add .
git commit -m "Update analysis"
git push

# App automatically redeploys in ~2 minutes
```

---

## ⚠️ Important Notes

### Data Files

Streamlit Cloud has limited storage. For production:

1. **Option A: Include Sample Data**
   - Keep outputs folder in repo
   - Git will track these files
   - Users see pre-computed results

2. **Option B: Run Analysis on Cloud**
   - Add button to trigger analysis
   - Cache results for 24 hours
   - May timeout on first run

### Recommended: Include Outputs

```bash
# Make sure outputs are tracked
git add outputs/
git commit -m "Add analysis results"
git push
```

---

## 🐛 Troubleshooting

### Build Failed?

**Check requirements.txt:**
```bash
# Ensure all packages are listed
pip freeze > requirements_full.txt
# Compare with requirements.txt
```

**Common Issues:**
1. Missing dependencies → Add to requirements.txt
2. File paths → Use relative paths
3. Large files → Check .gitignore

### App Crashes?

**View Logs:**
1. Go to Streamlit Cloud dashboard
2. Click your app
3. Click "Manage app" → "Logs"
4. Check error messages

**Common Fixes:**
```python
# In web_app.py, ensure paths are relative
output_dir = 'outputs'  # Not absolute path
```

### Data Not Loading?

**Ensure files are committed:**
```bash
git add outputs/reports/
git add outputs/visualizations/
git commit -m "Add data files"
git push
```

---

## 🎨 Customization

### Custom Domain

In Streamlit Cloud:
1. Settings → "Custom subdomain"
2. Enter: `hyderabad-nbs` (if available)
3. New URL: `https://hyderabad-nbs.streamlit.app`

### App Settings

```toml
# .streamlit/config.toml
[theme]
primaryColor = "#2ecc71"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
headless = true
port = 8501
enableCORS = false
```

---

## 📊 Analytics

Streamlit Cloud provides:
- View count
- User sessions
- Error rates
- Performance metrics

Access in: Dashboard → Your App → Analytics

---

## 💰 Pricing

**Free Tier:**
- ✅ Unlimited public apps
- ✅ 1 GB resources per app
- ✅ Community support
- ✅ Auto-deploy from GitHub

**Paid Tiers** (if needed):
- More resources
- Private apps
- Custom authentication
- Priority support

For this project, **Free tier is sufficient!**

---

## 🔒 Security

### Public Repository Considerations:

**Safe to Include:**
- ✅ Code
- ✅ Documentation
- ✅ Analysis results
- ✅ Visualizations
- ✅ Sample data

**Never Include:**
- ❌ API keys
- ❌ Passwords
- ❌ Personal data
- ❌ Proprietary data

### API Keys (if needed):

Use Streamlit Secrets:

```python
# In web_app.py
import streamlit as st
api_key = st.secrets["api_key"]
```

Add in Streamlit Cloud:
Settings → Secrets → Add

---

## 🌐 Sharing Your App

### Share the Link:
```
https://YOUR-APP.streamlit.app
```

### Embed in Website:
```html
<iframe src="https://YOUR-APP.streamlit.app" 
        width="100%" height="800"></iframe>
```

### Social Media:
- Twitter/X: Share link with #NbS #UrbanPlanning
- LinkedIn: Post with project description
- GitHub: Add to README badges

---

## 📈 Post-Deployment

### 1. Update README

Add to your GitHub README:

```markdown
## 🌐 Live Demo

**[View Live Dashboard](https://YOUR-APP.streamlit.app)** 🚀

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://YOUR-APP.streamlit.app)
```

### 2. Monitor Usage

- Check analytics weekly
- Monitor error logs
- Gather user feedback

### 3. Maintain

- Update data monthly
- Fix bugs promptly
- Add new features based on feedback

---

## 🎯 Alternative: Quick Deploy Script

Save as `deploy.sh`:

```bash
#!/bin/bash

# Quick deploy script
echo "🚀 Deploying Hyderabad NbS Dashboard..."

# Ensure on main branch
git checkout main

# Add and commit changes
git add .
git commit -m "Update dashboard - $(date +%Y-%m-%d)"

# Push to GitHub
git push origin main

echo "✅ Pushed to GitHub!"
echo "📊 Streamlit Cloud will auto-deploy in ~2 minutes"
echo "🌐 Check: https://streamlit.io/cloud"
```

Make executable:
```bash
chmod +x deploy.sh
./deploy.sh
```

---

## 📞 Support

### Streamlit Resources:
- Documentation: https://docs.streamlit.io
- Forum: https://discuss.streamlit.io
- GitHub: https://github.com/streamlit/streamlit

### Your Project Resources:
- Issues: GitHub repository issues tab
- Docs: All .md files in project

---

## ✅ Deployment Checklist

Before deploying, ensure:

- [ ] All code committed to Git
- [ ] requirements.txt is complete
- [ ] Outputs folder included (or app can generate)
- [ ] No hardcoded file paths
- [ ] .gitignore configured properly
- [ ] README updated with description
- [ ] GitHub repository is public
- [ ] App tested locally (`streamlit run web_app.py`)

---

## 🎉 Success!

Once deployed, your dashboard will be accessible 24/7 from anywhere in the world!

**Expected URL format:**
```
https://YOUR-USERNAME-hyderabad-nbs-dashboard.streamlit.app
```

**Share it with:**
- Urban planners
- City officials
- Environmental scientists
- Community groups
- Academic researchers
- Policy makers

---

**Need help?** Check the Streamlit Community forum or open an issue on GitHub!

---

*Last Updated: December 1, 2025*
*Streamlit Cloud: Free Tier*
*Deployment Time: ~5 minutes*

