# **Edu.AI – AI-Powered Chatbot for Course Recommendation & Learning Path Generator (RAG System)**  

Edu.AI is an intelligent student advisory assistant that generates personalized learning paths, recommends courses, and continues natural conversation using a **Retrieval-Augmented Generation (RAG)** pipeline.

The system uses:

- **Qdrant (Vector Database)** for semantic search  
- **Sentence Transformers** for generating embeddings  
- **Groq LLM (Llama 3.3-70B)** for structured learning path generation  
- **Streamlit** for the UI  
- **Docker** for containerized deployment  

---

## 🚀 **Features**

### 🔍 **RAG-based Course Recommendations**
- Extracts course metadata from a curated dataset  
- Embeds course descriptions using Sentence Transformers  
- Stores and retrieves vectors from Qdrant  
- Finds the most relevant courses based on user intent  

### 🎓 **AI-Generated Learning Paths**
- Creates structured, multi-step learning plans  
- Includes skills, URLs, course flow, duration, and outcomes  
- Tailored to user profile (field, experience, preferences, goals)

### 💬 **Conversation Memory**
- Continues the chat even after recommendations  
- Maintains profile & LLM history using `st.session_state`

### 📦 **Full Docker Support**
- Build once → run anywhere  
- Suitable for cloud deployment (Render, Oracle Cloud, Railway, Fly.io)

---

## 🧠 **Architecture Overview**

Edu.AI follows a **10-phase pipeline**:

1. **Data Collection**  
2. **Preprocessing**  
3. **Text Chunking**  
4. **Embedding Generation**  
5. **Vector DB Ingestion (Qdrant)**  
6. **Semantic Retrieval**  
7. **Prompt Engineering**  
8. **LLM Generation (Groq)**  
9. **Streamlit UI**  
10. **Dockerization & Deployment**

---

## 🛠 **Tech Stack**

| Layer | Technology |
|-------|------------|
| Language | Python |
| UI | Streamlit |
| Embeddings | Sentence Transformers (all-MiniLM-L6-v2) |
| Vector DB | Qdrant Cloud |
| LLM | Groq (Llama-3.3-70B) |
| Deployment | Docker |
| Others | Pandas, Requests, python-dotenv |

---




## 🐳 **Docker Usage**

### **Build the image**
  ```
docker build -t eduai-app .
```

Run the container
```
docker run -p 8501:8501 --env-file .env eduai-app
```
App will be available at:
```
👉 'https://eduai-app-production.up.railway.app/'
```

---

☁️ Deployment Notes
You can deploy Edu.AI on:

Deployed on Railway.app

---

🤝 Contributing
Pull requests are welcome!
Please open an issue to discuss major changes before submitting.

---

📜 License
MIT License.

---

⭐ Show Your Support
If you found this helpful, please ⭐ the repository!

