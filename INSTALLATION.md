# Installation Guide for Cognivault AI Business Analyst Agent

## ⚠️ Important Notes

1. **Disk Space Issue**: You encountered a "No space left on device" error. Please free up some disk space before proceeding.
2. **ElevenLabs API Updated**: The code has been updated to work with ElevenLabs v1.x API.

## 📋 Step-by-Step Installation

### Step 1: Free Up Disk Space

Before installing, ensure you have at least **2-3 GB** of free space on your C: drive.

### Step 2: Install Core Dependencies First

Install the essential packages in stages to avoid overwhelming your disk:

```bash
# Stage 1: Core framework
pip install streamlit python-dotenv

# Stage 2: AI APIs
pip install groq elevenlabs

# Stage 3: Document processing
pip install PyPDF2 pdfplumber python-docx python-pptx

# Stage 4: Data analysis (essential)
pip install pandas numpy matplotlib seaborn plotly scikit-learn

# Stage 5: Vector database & embeddings
pip install chromadb sentence-transformers

# Stage 6: Utilities
pip install openpyxl requests
```

### Step 3: Verify Installation

Test if the app can start:

```bash
streamlit run app.py
```

### Step 4: Set Up API Keys

Edit the `.env` file and add your API keys:

```env
GROQ_API_KEY=your_groq_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
```

## 🔧 Alternative: Minimal Installation

If you're still facing disk space issues, you can run with minimal features:

```bash
# Absolute minimum (Business Consulting + Voice only)
pip install streamlit groq elevenlabs python-dotenv requests
```

**Note**: With minimal installation:
- ✅ Business Consulting will work
- ✅ Voice Generation will work  
- ❌ RAG Documents will NOT work (needs chromadb, sentence-transformers)
- ❌ Data Analysis will NOT work (needs pandas, numpy, matplotlib)

## 🚀 Quick Start (After Installation)

1. Make sure your `.env` file has valid API keys
2. Run: `streamlit run app.py`
3. Open browser to: `http://localhost:8501`
4. Start with **Business Consulting** mode (works with minimal install)

## 💡 Troubleshooting

### If you get "ModuleNotFoundError"
Install the missing module:
```bash
pip install <module-name>
```

### If ElevenLabs gives errors
The code has been updated for v1.x API. Make sure you have the latest version:
```bash
pip install --upgrade elevenlabs
```

### If ChromaDB fails to install
This is a large package. You can skip it and use only Business Consulting + Voice modes:
```bash
# Skip chromadb - RAG mode won't work but other modes will
```

## 📊 What Works with Minimal Install

| Mode | Requires | Works with Minimal? |
|------|----------|---------------------|
| 🎯 Business Consulting | groq | ✅ Yes |
| 📄 RAG Documents | chromadb, sentence-transformers, document parsers | ❌ No |
| 📊 Data Analysis | pandas, numpy, matplotlib, seaborn | ❌ No |
| 🔊 Voice Generation | elevenlabs | ✅ Yes |

## 🎯 Recommended Approach

1. **Start Minimal**: Install just `streamlit`, `groq`, `elevenlabs`, `python-dotenv`
2. **Test**: Run the app and test Business Consulting + Voice
3. **Add Features**: Gradually install more packages as needed:
   - For Documents: `pip install chromadb sentence-transformers PyPDF2 pdfplumber python-docx python-pptx`
   - For Data Analysis: `pip install pandas numpy matplotlib seaborn plotly scikit-learn openpyxl`

## ✅ Verification

After installation, verify each component:

```python
# Test in Python
import streamlit  # Core
import groq  # Business consulting
import elevenlabs  # Voice
# import chromadb  # RAG (optional)
# import pandas  # Data analysis (optional)

print("✅ All required modules installed!")
```

## 🆘 Need Help?

If you continue to face issues:
1. Check available disk space: `dir C:\` (look at "bytes free")
2. Clear pip cache: `pip cache purge`
3. Use a virtual environment to isolate dependencies
4. Consider installing on a different drive if C: is full

---

**Ready to proceed?** Free up disk space, then run the installation commands above!
