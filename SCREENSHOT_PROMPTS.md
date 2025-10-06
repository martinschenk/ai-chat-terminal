# Screenshot Prompts for README

## 🎯 Goal: Show users how the system works in 30 seconds

### Screenshot 1: SAVE - Store Personal Data Locally
```bash
chat "remember my email is john@example.com locally"
```
**Expected:** 💾 Saved! ✅

---

### Screenshot 2: RETRIEVE - Get Stored Data
```bash
chat "what's my email?"
```
**Expected:** 🔍 Found in DB: john@example.com

---

### Screenshot 3: LIST - Show All Stored Data
```bash
chat "what data do you have about me?"
```
**Expected:**
```
📦 Your data (3):
  1. [email] john@example.com
  2. [phone] +1-555-0123
  3. [address] 123 Main St, NYC
```

---

### Screenshot 4: DELETE - Remove Data
```bash
chat "forget my phone number"
```
**Expected:** 🗑️ Deleted! (1 entry)

---

### Screenshot 5: Normal OpenAI Query (No Local DB)
```bash
chat "what's the capital of France?"
```
**Expected:** Paris is the capital of France.

---

### Screenshot 6: Complex Local Save
```bash
chat "I live in 123 Main Street, New York, NY 10001. Keep this locally."
```
**Expected:** 💾 Stored securely! 🔒

---

## 📝 Complete Demo Flow (5 Screenshots)

### Flow 1: Save & Retrieve
```bash
# Save
chat "save my API key sk-abc123 locally"
→ 💾 Saved!

# Retrieve
chat "what's my API key?"
→ 🔍 Got it: sk-abc123
```

### Flow 2: List & Delete
```bash
# List all
chat "show me everything you stored"
→ 📦 Your data (2):
  1. [api_key] sk-abc123
  2. [email] john@example.com

# Delete
chat "delete my API key"
→ 🗑️ Removed! ✨
```

### Flow 3: Normal vs Local
```bash
# Normal OpenAI query
chat "how do I sort files by size in bash?"
→ [OpenAI response with code]

# Local data query
chat "what's my stored email?"
→ 🔍 From DB: john@example.com
```

---

## 🎨 Best Practices for Screenshots

1. **Use short, clear prompts** (< 10 words)
2. **Show the icon** (💾/🔍/🗑️/📦) - proves it's from DB
3. **Keep responses SHORT** (1-2 lines max)
4. **Contrast**: Show LOCAL (with icons) vs OPENAI (no icons)
5. **Real-world data**: Email, phone, address, API keys

---

## 📸 Recommended Screenshot Order for README

1. **Hero shot**: `chat "remember my email is john@example.com locally"` → 💾 Saved!
2. **Retrieval**: `chat "what's my email?"` → 🔍 Found: john@example.com
3. **List all**: `chat "show me all my data"` → 📦 (with 3-4 items)
4. **Normal OpenAI**: `chat "what's 2+2?"` → 4 (no icon)
5. **Privacy**: Side-by-side showing LOCAL (with 🔍) vs OPENAI (no icon)

---

## ✨ One-Liner Prompts (Copy-Paste Ready)

**SAVE:**
- `chat "save my phone +1-555-0123 locally"`
- `chat "remember my birthday is May 15, 1990 locally"`
- `chat "keep my address: 123 Main St, NYC"`

**RETRIEVE:**
- `chat "what's my phone number?"`
- `chat "when's my birthday?"`
- `chat "what address do you have?"`

**LIST:**
- `chat "list all my data"`
- `chat "what do you know about me?"`
- `chat "show everything stored"`

**DELETE:**
- `chat "forget my phone"`
- `chat "delete my birthday"`
- `chat "remove my address"`

**NORMAL (OpenAI):**
- `chat "what's the weather in Paris?"`
- `chat "explain quantum computing"`
- `chat "write a haiku about AI"`
