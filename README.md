<img src="img1.png" alt="Legal Mind AI Icon" width="100%" style="display: block; margin: 0 auto;">

# Legal Mind AI ⚖️

An intelligent legal assistant platform focused on **MCP (Model Context Protocol)** server and client for legal document retrieval and analysis.

-----

## ✨ Features

### MCP Server (`server.py`)

  * **FastAPI-based** MCP server for legal document retrieval.
  * Supports **HTTP API** and **MCP protocol** for client communication.
  * **Real-time metrics dashboard** with ping and request rate monitoring.
  * **Tool:** `ask_legal_question` for answering legal questions using RAG (Retrieval-Augmented Generation).
  * **Endpoints:** `/mcp`, `/health`, `/query`, `/metrics`.

### MCP Client (`app.js`)

  * **Web-based chat interface** for interacting with the MCP server.
  * Minimal React Native **Expo app preview**.
  * Supports querying the server via the `/query` endpoint.
  * Stores server URL in `localStorage` for persistence.

-----

## 🔧 Requirements

  * **Python 3.9+** (Windows, macOS, Linux)
  * **Node.js** (for React Native client)

-----

## 💻 Setup

### First Time Setup (Install `uv` - One Time Only)

```bash
pip install uv
