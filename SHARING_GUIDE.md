# How to Share Your Journal Webapp

## Method 1: Local Network Sharing (Same WiFi)

### Steps:
1. **Start the Flask app:**
   ```bash
   cd c:\Users\HP\Desktop\journal_prototype1\journal
   python app.py
   ```

2. **Find your local IP address:**
   - Your IP addresses are shown below
   - Look for the one starting with 192.168.x.x or 10.x.x.x

3. **Share with your friend:**
   - If they're on the same WiFi: `http://YOUR_IP:5000`
   - Example: `http://192.168.1.100:5000`

### Important Notes:
- Only works when both on same WiFi network
- Your computer must stay running
- Firewall may block - you might need to allow port 5000

---

## Method 2: Public Internet Access (Using ngrok)

### One-time Setup:
1. **Download ngrok:**
   - Visit: https://ngrok.com/download
   - Download Windows version
   - Extract to a folder

2. **Sign up (free):**
   - Create account at https://ngrok.com
   - Get your authtoken from dashboard

3. **Configure ngrok:**
   ```bash
   ngrok config add-authtoken YOUR_AUTHTOKEN
   ```

### Every Time You Share:
1. **Start Flask app:**
   ```bash
   python app.py
   ```

2. **In a NEW terminal, start ngrok:**
   ```bash
   ngrok http 5000
   ```

3. **Copy the public URL:**
   - Look for "Forwarding" line
   - Example: `https://abc123.ngrok.io -> http://localhost:5000`
   - Share the `https://abc123.ngrok.io` link

### Ngrok Advantages:
✅ Works from anywhere in the world
✅ HTTPS by default (secure)
✅ No firewall configuration needed
✅ No port forwarding required

### Ngrok Limitations (Free Plan):
⚠️ URL changes every restart
⚠️ 2-hour session timeout
⚠️ Limited bandwidth

---

## Security Warning! ⚠️

**IMPORTANT:** Your app currently uses session-based authentication. When sharing:
- Each user needs their own Firebase account
- Don't share your personal login credentials
- Consider adding rate limiting for production use
- The ngrok URL is public - anyone with it can access your app

---

## Firewall Configuration (if needed)

If local network sharing doesn't work:

### Windows Firewall:
1. Open Windows Defender Firewall
2. Click "Advanced settings"
3. Click "Inbound Rules" > "New Rule"
4. Select "Port" > Next
5. Enter port `5000` > Next
6. Allow the connection > Next
7. Apply to all profiles > Next
8. Name it "Flask Journal App" > Finish
