# 🤖 Customer Support Chatbot for Internal Documentation

An AI-powered customer support chatbot that leverages **semantic search + LLMs** to retrieve accurate answers from internal knowledge Base. The system intelligently **escalates low-confidence queries to human agents**, ensuring reliability and scalability.

---

## 📌 Problem Statement

Organizations face repeated queries regarding:

- Internal policies  
- IT procedures  
- Product usage  
- Troubleshooting steps  

---

## 🎯 Solution Overview

This system introduces an **AI-driven support assistant** that:

- Understands natural language queries  
- Retrieves relevant internal documents  
- Generates context-aware responses  
- Computes confidence scores  
- Escalates unresolved queries automatically via email.

---

## 🧠 System Architecture

```
User Query (React UI)
        ↓
Django REST API
        ↓
Embedding Model (Gemini)
        ↓
Vector Search (Pinecone)
        ↓
Relevant Context Retrieval
        ↓
LLM Response Generation (Gemini)
        ↓
Confidence Scoring
   ↓            ↓
High Confidence  Low Confidence
   ↓            ↓
Show Answer     Escalate to Human
```

---

## 🚀 Features

### 1️⃣ Query Submission
- React-based chatbot UI  
- Text input + optional attachments  
- Input validation  
- Conversation logging  

---

### 2️⃣ AI-Based Query Understanding
- Text embedding generation  
- Semantic similarity search (Vector DB)  
- Context retrieval  
- LLM-based response generation  
- Confidence scoring  

---

### 3️⃣ High-Confidence Handling
- AI-generated response  
- Source document references  
- Confidence score display  

---

### 4️⃣ Low-Confidence Escalation
- Detects uncertain responses  
- Sends escalation email to human agents  
- Includes:
  - User query  
  - Conversation history  
  - Retrieved context   

---

## 🛠️ Tech Stack

### Frontend
- React.js  
- Tailwind CSS  
- Axios  
- Lucide Icons  

### Backend
- Django  
- Django REST Framework  
- JWT Authentication  

### Database
- PostgreSQL  

### Vector Database
- Pinecone  

### AI Models
- Gemini Embedding Model  
- Gemini LLM  

---

## 🔐 Authentication

- JWT-based authentication  
- Access & refresh tokens  
- Secure endpoints  

---

## 📡 API Documentation

Full OpenAPI schema available in the project (`Support Chatbot API Documentation.yaml`)

---

## 📌 Key API Endpoints

### 🔑 Authentication

| Endpoint | Method | Description |
|--------|--------|------------|
| `/api/register/` | POST | Register user |
| `/api/login/` | POST | Login user |
| `/api/logout/` | POST | Logout |
| `/api/refresh/` | POST | Refresh token |
| `/api/verify-token/` | GET | Verify JWT |

---

### 💬 Conversations

| Endpoint | Method | Description |
|--------|--------|------------|
| `/api/chatbot/create/conversation` | POST | Create conversation |
| `/api/chatbot/fetch/conversations` | GET | Get user conversations |
| `/api/chatbot/delete/conversation/{id}` | DELETE | Delete conversation |

---

### 🧾 Messages

| Endpoint | Method | Description |
|--------|--------|------------|
| `/api/chatbot/create/message` | POST | Send message + get AI response |
| `/api/chatbot/fetch/message-history` | POST | Get chat history |

---

### 🚨 Escalation

| Endpoint | Method | Description |
|--------|--------|------------|
| `/api/chatbot/send/email` | POST | Escalate to human agent |

---

### 🧩 Widget API

| Endpoint | Method | Description |
|--------|--------|------------|
| `/api/chatbot/widget/response` | POST | Stateless chatbot response |

---

## ⚙️ Installation & Setup

### 1️⃣ Clone Repository

```bash
git clone https://gitlab.com/nueve/internship/pavan-sai-porapu.git
cd customer-support-chatbot
```

---

### 2️⃣ Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

---

### 3️⃣ Environment Variables

Create `.env` file in backend folder:

```env
DB_URI=postgresql://URL

PINECONE_API_KEY=your_pincone_api_key

EMAIL_API_KEY=your_email_service_api_key

GOOGLE_API_KEY=your_api_key
GEMINI_API_KEY=your_api_key

REDIS_LOCATION=redis_url

ALLOWED_HOSTS=str

CORS_ALLOWED_ORIGINS=str

DJANGO_SECRET_KEY=django_screte_key

```
Create `.env` file in frontend folder:

```env
VITE_API_URL=endpoint_url

```
---

### 4️⃣ Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

### 5️⃣ Run Server

```bash
python manage.py runserver
```

---

### 6️⃣ Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 API Testing

- Swagger UI: `/docs/`  
- Redoc UI: `/redoc/`  
- Schema: `/schema/`  

---


---

## 🔄 Escalation Workflow

1. Detect low-confidence response  
2. Package:
   - Query  
   - Chat history  
3. Send email to support agent  
4. Agent respond to user

---


## 📜 License

MIT License

---

## 👨‍💻 Author

**Sai Pawan**    