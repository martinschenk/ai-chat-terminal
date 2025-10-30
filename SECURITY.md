# Security Policy

## Supported Versions

AI Chat Terminal follows semantic versioning. Security updates are provided for the latest stable release.

| Version | Supported          |
| ------- | ------------------ |
| 11.6.x  | :white_check_mark: |
| 11.5.x  | :white_check_mark: |
| < 11.0  | :x:                |

---

## Security Model - Critical Disclaimer

⚠️ **AI Chat Terminal does NOT automatically protect you from sending sensitive data to OpenAI.**

**This is NOT a security filter.** This is an **alternative storage method** that YOU must actively use.

### How It Works

**❌ WITHOUT keywords** → Sent to OpenAI:
```bash
You: "My email is test@example.com"
→ ⚠️ Entire message sent to OpenAI
→ ⚠️ NO PROTECTION - you forgot the keyword!
```

**✅ WITH keywords** → Stored locally:
```bash
You: "save my email test@example.com"
→ ✅ Processed by local Qwen 2.5 Coder
→ ✅ Stored in encrypted SQLite
→ ✅ OpenAI NEVER sees this
```

**Key principle:** YOU control the switch. Keywords = Local AI ON. No keywords = OpenAI.

---

## Encryption

- **Method:** AES-256 via SQLCipher
- **Key Storage:** macOS Keychain
- **Scope:** `mydata` table (private data only)
- **Note:** `chat_history` is NOT encrypted (temporary context, auto-deleted)

---

## Reporting a Vulnerability

**Email:** security@martin-schenk.es

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Your suggested fix (if any)

**Response Time:** Within 48 hours
**Disclosure:** Coordinated disclosure after fix is released

---

## Security Best Practices

1. **Always use keywords** for sensitive data
2. **Never share your `.aichat/` directory** (contains encrypted data)
3. **Backup your encryption key** (stored in macOS Keychain)
4. **Review chat history** before sharing terminal output
5. **Update regularly** for security patches

---

**Last Updated:** 2025-10-27
