# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

This is a Course Materials RAG (Retrieval-Augmented Generation) system built with:
- **Backend**: FastAPI application serving both API endpoints and static frontend files
- **Frontend**: Vanilla HTML/CSS/JavaScript single-page application
- **Vector Database**: ChromaDB for semantic search of course content
- **AI Integration**: Anthropic Claude for response generation
- **Session Management**: Built-in conversation history tracking

### Core Components

- `backend/rag_system.py`: Main orchestrator class that coordinates all components
- `backend/vector_store.py`: ChromaDB integration for storing and searching course content
- `backend/document_processor.py`: Handles parsing and chunking of course documents
- `backend/ai_generator.py`: Anthropic API integration for response generation
- `backend/session_manager.py`: Manages conversation sessions and history
- `backend/search_tools.py`: Tool-based search system for course content
- `backend/app.py`: FastAPI application with API endpoints and static file serving

## Development Commands

### Running the Application
```bash
# Quick start (recommended)
./run.sh

# Manual start
cd backend && uv run uvicorn app:app --reload --port 8000
```

### Code Quality
```bash
# Format code (black + isort)
./scripts/format.sh

# Run linting checks (flake8)
./scripts/lint.sh

# Run all quality checks (format + lint)
./scripts/quality.sh

# Manual commands
uv run black .          # Format with black
uv run isort .          # Sort imports
uv run flake8 backend/  # Lint specific directory
```

### Package Management
```bash
# Install dependencies
uv sync

# Add new dependency
uv add <package_name>
```

### Environment Setup
Create `.env` file in root with:
```
ANTHROPIC_API_KEY=your_api_key_here
```

## Key Features

- **Document Processing**: Automatically processes `.txt` files in `docs/` folder on startup
- **Semantic Search**: Uses sentence transformers for embedding-based search
- **Session Management**: Maintains conversation context across queries
- **Tool-Based Architecture**: Extensible search tool system
- **CORS Enabled**: Configured for development with wildcard origins

## API Endpoints

- `POST /api/query`: Process user queries with optional session_id
- `GET /api/courses`: Get course statistics and analytics
- `GET /`: Serves the frontend application

## File Structure Notes

- Course documents are expected in `docs/` folder as `.txt` files
- Frontend assets are in `frontend/` and served at root path
- Vector database is stored in ChromaDB persistent storage
- No build step required - runs directly with uv/uvicorn