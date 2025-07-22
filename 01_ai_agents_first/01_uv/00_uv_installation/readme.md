# **UV Installation:**

# 💻 Python Installation (Step-by-Step for All OS)

---

## 💻 Windows

### ✅ Step 1: Download Python

- Go to: https://www.python.org/downloads/windows/
- Click **"Download Python 3.x.x"** (latest version)

### ✅ Step 2: Run Installer

- Double-click the `.exe` file
- **Important**: Check ✅ **"Add Python to PATH"**
- Click **Install Now**

### ✅ Step 3: Verify Installation

Open **Command Prompt** and type:

```bash
python --version
```

---

## 🍎 macOS

### ✅ Step 1: Use Homebrew (Recommended)

First, install Homebrew (if not already):

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Then install Python:

```bash
brew install python
```

### ✅ Step 2: Verify Installation

```bash
python3 --version
```

---

## 🐧 Linux (Ubuntu/Debian-based)

### ✅ Step 1: Update System

```bash
sudo apt update
```

### ✅ Step 2: Install Python

```bash
sudo apt install python3 python3-pip -y
```

### ✅ Step 3: Verify Installation

```bash
python3 --version
pip3 --version
```

---

# 🚀 UV Package Manager Installation (All OS)

---

## 💻 Windows

### ✅ Step 1: Open PowerShell as Admin

### ✅ Step 2: Run Installation Script

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### ✅ Step 3: Verify

```powershell
uv --version
```

---

## 🍎 macOS

### ✅ Option 1: Install via Homebrew

```bash
brew install uv
```

### ✅ Option 2: Install via Script

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### ✅ Step 3: Verify

```bash
uv --version

```

---

## 🐧 Linux

### ✅ Step 1: Install via Curl

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### ✅ Optional: If Needed, Add to PATH

```bash
export PATH="$HOME/.local/bin:$PATH"
```

### ✅ Step 2: Verify
```bash
uv --version
```