# Project Setup Guide - Indian Railways Journey Planner
## 📋 Prerequisites Installation

### 1. Install Python (3.11 preferred)

**Windows:**
1. Download Python from [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Run the installer
3. ✅ **IMPORTANT:** Check "Add Python to PATH" during installation
4. Click "Install Now"
5. Verify installation:
   ```bash
   python --version
   ```
   Should show: `Python 3.11.x` or higher

***

### 2. Install Node.js and npm (v18 or higher)

**Windows:**
1. Download Node.js LTS from [https://nodejs.org/](https://nodejs.org/)
2. Run the installer (includes npm automatically)
3. Verify installation:
   ```bash
   node --version
   npm --version
   ```
   Should show: `v23.x.x` or higher for Node, `11.7.x` or higher for npm

***


### 3. Install Visual Studio Code Extensions

**Recommended VS Code Extensions:**
1. Python (by Microsoft)
2. Vue (Official) (for Vue 3)
3. Postman (for API testing) - *installation steps below*

***

## 🚀 Project Setup

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd <project-folder-name>
```

***

## 🐍 Backend Setup (Flask)

### Step 1: Navigate to Backend Directory
```bash
cd backend
```

### Step 2: Create Python Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

✅ Your terminal prompt should now show `(venv)` at the beginning

### Step 3: Install Python Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- Flask (web framework)
- Flask-CORS (cross-origin support)
- supabase (database client)
- python-dateutil (date handling)

### Step 4: Create Environment File (IGNORE THIS STEP FOR NOW)

Create a file named `.env` in the `backend/` directory:

**Windows:**
```bash
type nul > .env
notepad .env
```

**macOS/Linux:**
```bash
touch .env
nano .env
```

Add the following content (get actual credentials from team lead):
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
FLASK_ENV=development
```

Save and close the file.

### Step 5: Run the Backend Server
```bash
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

✅ **Backend is now running on port 5000**[1]

**Keep this terminal open and running!**

***

## 🎨 Frontend Setup (Vue 3)

### Step 1: Open a NEW Terminal
Don't close the backend terminal! Open a new terminal window/tab.

### Step 2: Navigate to Frontend Directory
```bash
cd frontend
```
(If you were in `backend/`, do `cd ../frontend`)

### Step 3: Install Node Dependencies
```bash
npm install
```

This will take 2-3 minutes to download all packages.

### Step 4: Run the Development Server
```bash
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

✅ **Frontend is now running on port 5173**[2]

### Step 5: Open in Browser
Open your browser and go to:
```
http://localhost:5173
```

You should see the Vue app homepage!

***

## 🧪 Testing the Setup

### Test 1: Backend Health Check with Postman Extension

#### Install Postman Extension in VS Code[3]

1. Open VS Code
2. Click the **Extensions** icon in the left sidebar (or press `Ctrl+Shift+X` / `Cmd+Shift+X`)
3. Search for **"Postman"**
4. Click **Install** on "Postman" by Postman Inc. (with verified badge)
5. After installation, you may need to **reload VS Code**
6. Sign in with your Postman account when prompted (create free account at [postman.com](https://www.postman.com/) if needed)

#### Send GET Request to Health Endpoint

1. In VS Code, click the **Postman icon** in the left sidebar (P icon)
2. Click **"New Request"** or **"+"** to create a new request
3. Set request type to **GET** (dropdown)
4. Enter URL:
   ```
   http://127.0.0.1:5000/api/health
   ```
5. Click **"Send"**

**Expected Response:**
```json
{
  "status": "healthy"
}
```

✅ If you see this, backend is working correctly!

#### Test Root Endpoint

Create another request:
- Method: **GET**
- URL: `http://127.0.0.1:5000/`
- Click **Send**

**Expected Response:**
```json
{
  "status": "ok",
  "message": "TRAIN JOURNEY DISCOVERY API"
}
```

***

### Test 2: Frontend Display

1. Make sure frontend is running (`npm run dev` in `frontend/` directory)
2. Open browser to `http://localhost:5173`
3. You should see the default Vue welcome page with Vue logo

✅ Frontend is working!

***

## 📁 Project Structure Overview

```
project-root/
├── backend/
│   ├── app.py              ← Flask server entry point
│   ├── requirements.txt    ← Python dependencies
│   ├── .env               ← Your credentials (NOT committed to git)
│   └── venv/              ← Virtual environment (NOT committed)
├── frontend/
│   ├── src/
│   │   ├── App.vue        ← Main Vue component
│   │   └── main.js        ← Vue app entry point
│   ├── package.json       ← Node dependencies
│   └── node_modules/      ← Installed packages (NOT committed)
└── data/
    └── README.md          ← Data documentation
```

***

## 🔧 Common Issues & Solutions

### Issue 1: "Python not found" or "command not found"

**Solution:** 
- Windows: Reinstall Python and check "Add to PATH"
- Mac/Linux: Use `python3` instead of `python`

### Issue 2: "Port 5000 already in use"

**Solution:**
Either kill the process using port 5000, or change Flask port in `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Changed to 5001
```

### Issue 3: "Port 5173 already in use" (Frontend)

**Solution:**
Vite will automatically use next available port (5174, 5175, etc.)[2]

### Issue 4: "Module not found" errors

**Solution:**

Backend:
```bash
cd backend
pip install -r requirements.txt
```

Frontend:
```bash
cd frontend
npm install
```

### Issue 5: Virtual environment not activating

**Windows PowerShell may block scripts:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then retry:
```bash
venv\Scripts\activate
```

***

## 🎯 Daily Workflow

**Every time you start working:**

1. **Start Backend:**
   ```bash
   cd backend
   source venv/bin/activate  # Mac/Linux
   # OR
   venv\Scripts\activate     # Windows
   python app.py
   ```

2. **Start Frontend (in new terminal):**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open browser:** `http://localhost:5173`

4. **Test API with Postman** in VS Code as needed

**Before committing code:**
```bash
git status
git add .
git commit -m "Descriptive message"
git push origin main
```

***