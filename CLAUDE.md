# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Retrieval-Augmented Generation (RAG) system built with FastAPI, ChromaDB, and Anthropic's Claude API. The system enables semantic search and question-answering over course materials stored in text format.

**Key Technologies:**
- **Backend**: FastAPI with async support
- **Vector Store**: ChromaDB with persistent storage
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **AI Model**: Claude Sonnet 4 (claude-sonnet-4-20250514)
- **Frontend**: Vanilla JavaScript with HTML/CSS

## Development Commands

### Environment Setup
```bash
# Install dependencies
uv sync

# Install dev dependencies
uv sync --extra dev

# Set up environment variables
cp .env.example .env
# Then edit .env to add your ANTHROPIC_API_KEY
```

### Running the Application
```bash
# Quick start (from project root)
./run.sh

# Manual start (from project root)
cd backend && uv run uvicorn app:app --reload --port 8000

# The application runs on:
# - Web UI: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### Testing
```bash
# Run all tests
cd backend && uv run pytest

# Run specific test file
cd backend && uv run pytest test_file.py

# Run with verbose output
cd backend && uv run pytest -v

# Run with coverage
cd backend && uv run pytest --cov=.
```

## Architecture

### Data Flow

1. **Document Ingestion** (`document_processor.py`)
   - Reads course documents from `docs/` folder on startup
   - Expected format: First 3 lines contain metadata (Course Title, Link, Instructor)
   - Parses lessons marked as "Lesson N: Title" followed by optional "Lesson Link:"
   - Chunks text into ~800 character segments with 100 character overlap
   - Each chunk gets prepended with context (course title + lesson number)

2. **Vector Storage** (`vector_store.py`)
   - **Two ChromaDB collections**:
     - `course_catalog`: Stores course metadata (titles, instructors, links, lessons)
     - `course_content`: Stores chunked lesson content with metadata
   - Semantic course name resolution: Partial course names are matched via vector similarity
   - Filtering: Supports filtering by exact course title and/or lesson number

3. **Query Processing** (`rag_system.py`)
   - **Tool-based architecture**: Claude uses the `search_course_content` tool to query the vector store
   - AI decides when to search vs. use general knowledge
   - Session-based conversation history (last 2 exchanges retained)
   - Returns response + sources array

4. **AI Generation** (`ai_generator.py`)
   - Uses Claude API with tool calling
   - Single-pass tool execution: AI calls search tool → receives results → generates response
   - System prompt emphasizes brevity and one search per query
   - Temperature: 0 (deterministic), Max tokens: 800

### Key Components

**`RAGSystem`** (rag_system.py): Main orchestrator
- Coordinates document_processor, vector_store, ai_generator, session_manager, and tools
- `add_course_folder()`: Bulk import from docs folder with duplicate detection
- `query()`: Processes user questions with tool-based search

**`VectorStore`** (vector_store.py):
- `search()`: Unified interface with optional course_name and lesson_number filters
- `_resolve_course_name()`: Fuzzy matches course names via vector similarity
- Lessons metadata stored as JSON string in ChromaDB (ChromaDB limitation workaround)

**`CourseSearchTool`** (search_tools.py):
- Implements Tool interface for Anthropic tool calling
- Tracks `last_sources` for UI display
- Returns formatted results with course/lesson context headers

**`SessionManager`** (session_manager.py):
- Manages conversation history per session ID
- Retains last MAX_HISTORY (2) exchanges to control token usage

### Data Models

**Core Models** (models.py):
- `Course`: title (unique ID), course_link, instructor, lessons[]
- `Lesson`: lesson_number, title, lesson_link
- `CourseChunk`: content, course_title, lesson_number, chunk_index

**API Models** (app.py):
- `QueryRequest`: query, session_id (optional)
- `QueryResponse`: answer, sources[], session_id
- `CourseStats`: total_courses, course_titles[]

### Configuration

All settings in `backend/config.py`:
- `ANTHROPIC_MODEL`: "claude-sonnet-4-20250514"
- `EMBEDDING_MODEL`: "all-MiniLM-L6-v2"
- `CHUNK_SIZE`: 800 characters
- `CHUNK_OVERLAP`: 100 characters
- `MAX_RESULTS`: 5 search results
- `MAX_HISTORY`: 2 conversation exchanges
- `CHROMA_PATH`: "./chroma_db"

## Important Implementation Details

### Course Document Format
Documents in `docs/` must follow this structure:
```
Course Title: [title]
Course Link: [url]
Course Instructor: [name]

Lesson 0: [lesson title]
Lesson Link: [url]
[lesson content...]

Lesson 1: [lesson title]
Lesson Link: [url]
[lesson content...]
```

### Chunk Context Injection
The system prepends context to chunks for better retrieval:
- First chunk of lesson: `"Lesson {N} content: {chunk}"`
- Other chunks: `"Course {title} Lesson {N} content: {chunk}"`
- This ensures chunks contain identifiable information even in isolation

### Tool Calling Pattern
The AI generator uses a single-turn tool pattern:
1. User message → AI decides to call `search_course_content` tool
2. Tool executes → Results returned in new user message
3. AI synthesizes final answer (no tools in second call)

This prevents infinite tool loops and keeps responses fast.

### Duplicate Prevention
`add_course_folder()` checks existing course titles before ingestion:
- Retrieves all IDs from `course_catalog` collection
- Skips files that would produce duplicate course titles
- Set `clear_existing=True` to rebuild from scratch

### Session Management
- Session IDs created on first query if not provided
- History stored as formatted string: `"User: {query}\nAssistant: {response}"`
- Older messages dropped when MAX_HISTORY exceeded
- No persistence - sessions lost on server restart

## Common Development Patterns

### Adding New Search Capabilities
1. Create new Tool class inheriting from `Tool` (search_tools.py)
2. Implement `get_tool_definition()` and `execute()`
3. Register with ToolManager in RAGSystem.__init__()
4. Tool becomes available to AI automatically

### Modifying AI Behavior
Edit `SYSTEM_PROMPT` in ai_generator.py. Current prompt emphasizes:
- Use search only for course-specific questions
- One search maximum per query
- Brief, direct responses (no meta-commentary)
- No mention of "based on search results"

### Working with ChromaDB Collections
- Collections auto-create on first access
- IDs must be unique within collection (course titles used as IDs in catalog)
- Metadata must be JSON-serializable primitives (use json.dumps for complex types)
- Filters use MongoDB-like syntax: `{"$and": [{...}, {...}]}`

### Frontend-Backend Contract
- Frontend expects `sources` array of strings in format: `"{course} - Lesson {N}"`
- Session ID returned in response, client should include in subsequent requests
- CORS configured for `allow_origins=["*"]` (restrict in production)
