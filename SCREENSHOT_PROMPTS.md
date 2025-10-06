# Screenshot Prompts for README

## 🎯 Goal: Show users how the system works in 30 seconds

**Design Style:** Terminal window with dark theme (like macOS Terminal)
**Format:** `👤 You ▶` for user input, `🤖 AI ▶` for responses
**Language:** English only
**NO QUOTES:** Commands without quotation marks (important feature!)

---

## 📸 Screenshot 1: SAVE - Store Personal Data Locally

```
👤 You ▶ remember my email is john@example.com locally
🤖 AI  ▶ 💾 Saved securely!
```

**Key Point:** Shows 💾 icon - proves data went to local DB, NOT OpenAI cloud

---

## 📸 Screenshot 2: RETRIEVE - Get Stored Data

```
👤 You ▶ whats my email?
🤖 AI  ▶ 🔍 Found in DB: john@example.com
```

**Key Point:** Shows 🔍 icon - proves data comes from local DB

---

## 📸 Screenshot 3: LIST - Show All Stored Data

```
👤 You ▶ what do you know about me?
🤖 AI  ▶ 📦 Your data (3):
         1. [email] john@example.com
         2. [phone] +1-555-0123
         3. [address] 123 Main St, NYC
```

**Key Point:** Shows 📦 icon and numbered list

---

## 📸 Screenshot 4: DELETE - Remove Data

```
👤 You ▶ forget my phone number
🤖 AI  ▶ 🗑️ Deleted! (1 entry removed)
```

**Key Point:** Shows 🗑️ icon with deletion count

---

## 📸 Screenshot 5: Normal OpenAI Query (No Icon = Cloud)

```
👤 You ▶ capital of france?
🤖 AI  ▶ The capital of France is Paris.
```

**Key Point:** NO icon - shows this went to OpenAI cloud, not local DB

---

## 📸 Screenshot 6: Privacy Comparison (Side-by-Side)

**Left Side (Local DB - Private):**
```
👤 You ▶ whats my API key?
🤖 AI  ▶ 🔍 From DB: sk-abc123xyz
```

**Right Side (OpenAI Cloud - General):**
```
👤 You ▶ how to sort files by size?
🤖 AI  ▶ Use: ls -lhS
```

**Key Point:** Icon 🔍 = Local DB (private), No icon = OpenAI (cloud)

---

## ✨ Copy-Paste Commands (NO QUOTES!)

### SAVE Operations:
```bash
chat save my phone +1-555-0123 locally
chat remember my birthday is May 15, 1990 locally
chat keep my address: 123 Main St, NYC
chat I live in London, remember that locally
```

### RETRIEVE Operations:
```bash
chat whats my phone number?
chat whens my birthday?
chat what address do you have?
chat get my API key from db
```

### LIST Operations:
```bash
chat list all my data
chat what do you know about me?
chat show everything stored
chat what data do you have?
```

### DELETE Operations:
```bash
chat forget my phone
chat delete my birthday
chat remove my address
chat clear my API key
```

### NORMAL Operations (OpenAI Cloud):
```bash
chat capital of france?
chat explain quantum computing
chat write a haiku about AI
chat how to reverse a string in python?
```

---

## 🎨 Screenshot Best Practices

1. **Terminal Design:** Dark theme with light text (like macOS Terminal)
2. **Header:** Show `/config = Settings | ESC/quit = Exit` at top
3. **Prompt Format:** `👤 You ▶` and `🤖 AI ▶` with proper spacing
4. **NO QUOTES:** Commands without quotation marks
5. **Icon Visibility:** Make sure 💾/🔍/🗑️/📦 icons are clearly visible
6. **Contrast:** Show LOCAL (with icons) vs OPENAI (no icons)
7. **Real Data:** Use realistic examples (emails, phones, addresses)
8. **Keep Short:** 1-2 lines max for responses

---

## 🎬 Recommended Screenshot Order for README

1. **Hero Shot:** SAVE operation with 💾 icon
2. **Retrieval:** RETRIEVE with 🔍 icon showing data from DB
3. **Comparison:** Side-by-side LOCAL (🔍) vs OPENAI (no icon)
4. **List:** LIST operation showing 3-4 items with 📦 icon
5. **Delete:** DELETE with 🗑️ icon and count

---

## 🔑 Key Messages to Communicate

1. **Privacy First:** Icons show when data stays local (never touches OpenAI)
2. **No Quotes Needed:** Natural language without quotation marks
3. **Smart Routing:** System automatically decides local DB vs OpenAI cloud
4. **Multilingual:** Works in English, German, Spanish, French, Italian, Portuguese
5. **Encrypted:** Local data protected with AES-256 encryption

---

## 📋 Example Screenshot Session (Complete Flow)

```
👤 You ▶ save my API key sk-test-abc123 locally
🤖 AI  ▶ 💾 Saved securely!

👤 You ▶ whats my API key?
🤖 AI  ▶ 🔍 Got it: sk-test-abc123

👤 You ▶ what do you know about me?
🤖 AI  ▶ 📦 Your data (1):
         1. [api_key] sk-test-abc123

👤 You ▶ capital of france?
🤖 AI  ▶ The capital of France is Paris.

👤 You ▶ forget my API key
🤖 AI  ▶ 🗑️ Deleted! (1 entry removed)
```

**This shows:**
- ✅ SAVE with 💾 icon
- ✅ RETRIEVE with 🔍 icon
- ✅ LIST with 📦 icon
- ✅ Normal OpenAI query (no icon)
- ✅ DELETE with 🗑️ icon
