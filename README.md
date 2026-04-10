# 🤖 Customer Support Chatbot for Internal Documentation

An AI-powered customer support chatbot that retrieves answers from internal documentation using semantic search and Large Language Models (LLMs). The system automatically escalates low-confidence responses to human support agents.

---

## 📌 Problem Statement

In many organizations, employees and customers frequently ask questions about:

- Internal policies
- IT procedures
- Product usage
- Troubleshooting steps

These queries are often handled manually via email or ticketing systems, leading to:

- Delays
- Repetitive workload
- Inconsistent responses

This project builds an intelligent chatbot that:

- Understands user queries in natural language
- Retrieves relevant internal documentation
- Generates accurate AI-based responses
- Escalates unresolved or low-confidence queries

---

## 🚀 Features

### 1️⃣ Query Submission

- Web-based chatbot interface (React)
- Text-based question input
- Optional file/screenshot attachment
- Query validation and logging

---

### 2️⃣ AI-Based Query Understanding

- Text embedding generation
- Semantic similarity search (Vector DB)
- Retrieval of relevant document sections
- LLM-based response generation
- Confidence score calculation

---

### 3️⃣ High-Confidence Handling

- Displays AI-generated answer
- Shows source document references
- Displays response confidence score
- Provides contextual recommendations

---

### 4️⃣ Low-Confidence Escalation

- Detects low-confidence responses
- Escalates query to human support via email
- Includes:
  - User query
  - Conversation history
  - Retrieved context
- Stores agent response in knowledge base

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

- Gemini Text Embedding Model
- Gemini Large Language Model (LLM)

---
