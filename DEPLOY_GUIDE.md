# 🚀 DEPLOY IN 5 MINUTES - NO CODING NEEDED!

## STEP 1: UPLOAD TO GITHUB (2 minutes)

1. Go to https://github.com/new
2. Repository name: `moass-terminal`
3. Click "Create repository"
4. Download the `moass-terminal` folder from Claude
5. Open terminal/command prompt in that folder
6. Run these commands:

```bash
git init
git add .
git commit -m "MOASS Terminal - Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/moass-terminal.git
git push -u origin main
```

✅ **Done!** Your code is on GitHub

---

## STEP 2: DEPLOY ON RENDER (3 minutes)

1. Go to https://render.com
2. Sign up (free) using your GitHub account
3. Click **"New +"** → **"Web Service"**
4. Select your `moass-terminal` repository
5. Fill in these settings:

```
Name: moass-terminal-api
Environment: Python 3
Build Command: pip install -r backend/requirements.txt
Start Command: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
Instance Type: Free
```

6. Click **"Advanced"** → **"Add Environment Variable"**:
```
API_HOST = 0.0.0.0
CORS_ORIGINS = *
ENVIRONMENT = production
```

7. Click **"Create Web Service"**

8. Wait 5-10 minutes (Render will build and deploy)

✅ **Done!** Your API is live!

---

## STEP 3: TEST IT (30 seconds)

Your app URL: `https://moass-terminal-api-XXXXX.onrender.com`

Open these URLs in your browser:

1. **Health Check:**
   `https://your-app.onrender.com/`

2. **GME Probability:**
   `https://your-app.onrender.com/api/gme/probability`

3. **Market Scanner:**
   `https://your-app.onrender.com/api/scanner/top`

4. **Any Ticker (example TSLA):**
   `https://your-app.onrender.com/api/universal/TSLA/probability`

✅ **Working?** You're done!

---

## 🎯 WHAT YOU JUST DEPLOYED:

✅ **Full API** calculating:
- GME MOASS probability with YOUR 214-day pattern
- T+35, 147-day, all your cycles
- GME warrants (59M @ $32) tracking
- AMC probability
- Universal calculator (any stock)
- Market scanner

✅ **Runs 24/7** (sleeps after 15min on free tier, wakes in <1min)

✅ **Completely FREE**

---

## 📱 USE IT:

### In Browser:
Just visit the URLs above

### In Code:
```python
import requests

# Get GME probability
response = requests.get('https://your-app.onrender.com/api/gme/probability')
data = response.json()
print(f"GME MOASS Probability: {data['probability']}%")
```

### From Pine Script:
Set webhook URL in TradingView alerts to:
`https://your-app.onrender.com/api/webhook/cycle`

---

## 🔥 THAT'S IT!

**You deployed a full squeeze probability API with:**
- Your custom GME cycles
- Market scanner
- Universal calculator
- Everything you asked for

**All you did:**
1. Upload to GitHub
2. Click deploy on Render
3. Done!

**Want to upgrade?**
- Add frontend dashboard ($0 on Vercel)
- Keep API always-on ($7/month)
- Add more data sources (free or paid APIs)

---

## 💡 NEXT STEPS:

1. **Test all endpoints** - Make sure everything works
2. **Bookmark your URL** - Save it somewhere
3. **Set up alerts** - Configure TradingView webhooks
4. **Share with apes** - Show the community!

---

## ❓ PROBLEMS?

### App not starting?
- Check Render logs in dashboard
- Verify environment variables
- Wait full 10 minutes for first deploy

### Getting errors?
- Make sure you used the exact commands above
- Check GitHub repo has all files
- Try redeploying on Render

### Need help?
**Just ask me!** I'm here to help troubleshoot! 🚀

---

**🎉 CONGRATS - YOU'RE LIVE!** 💎🙌
