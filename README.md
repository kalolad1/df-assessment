# Deerfield Assessment - Medical Document API

A FastAPI backend application for document management with LLM-powered medical note summarization.

## API Endpoints

### Health Check
```
GET /health
```
Returns the health status of the API.

### Document Management

**Create Document**
```
POST /documents
Content-Type: application/json

{
  "title": "Patient Visit Notes",
  "content": "Patient presents with..."
}
```

**Get All Documents**
```
GET /documents
```
Returns a list of all document IDs.

### LLM Summarization

**Summarize Medical Note**
```
POST /summarize_note
Content-Type: application/json

{
  "content": "Patient presents with persistent cough, fever, and chest discomfort. Physical examination reveals wheezing and crackling sounds in lungs. Diagnosed with acute bronchitis. Prescribed azithromycin 500mg daily for 5 days and advised bed rest."
}
```

**Response:**
```json
{
  "summary": "Patient diagnosed with acute bronchitis. Prescribed antibiotics and rest. Follow-up in 1 week.",
}
```

## Docker Deployment

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) 20.10+
- [Docker Compose](https://docs.docker.com/compose/install/) 2.0+

### Setup

1. **Configure Environment Variables**

   Copy the example environment file and add your API keys:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and replace the placeholder values with your actual API keys:
   ```bash
   # Database URLs
   ASYNC_DATABASE_URL=sqlite+aiosqlite:///./data/app.db
   SYNC_DATABASE_URL=sqlite:///./data/app.db
   
   # Required API keys
   PYDANTIC_AI_GATEWAY_API_KEY=your_actual_key_here
   OPENAI_API_KEY=your_actual_key_here
   ```

2. **Build the Docker Image**

   ```bash
   docker-compose build
   ```

   This will:
   - Use multi-stage build for optimized image size
   - Install all dependencies using UV package manager
   - Create a non-root user for security
   - Set up health checks

3. **Start the Services**

   ```bash
   docker-compose up
   ```

   Or run in detached mode:
   ```bash
   docker-compose up -d
   ```

   The API will be available at `http://localhost:8000`

4. **View Logs**

   ```bash
   docker-compose logs -f fastapi-app
   ```

5. **Stop the Services**

   ```bash
   docker-compose down
   ```

   To remove volumes as well:
   ```bash
   docker-compose down -v
   ```

### Testing the Deployment

Once the container is running, test the endpoints:

**Health Check:**
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy"}
```

**List Documents:**
```bash
curl http://localhost:8000/documents
```

**Create a Document:**
```bash
curl -X POST http://localhost:8000/documents \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Patient Visit Note",
    "content": "Patient presents with fever and cough."
  }'
```

**Summarize Medical Note:**
```bash
curl -X POST http://localhost:8000/summarize_note \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Patient presents with persistent cough, fever, and chest discomfort. Physical examination reveals wheezing and crackling sounds in lungs. Diagnosed with acute bronchitis. Prescribed azithromycin 500mg daily for 5 days and advised bed rest."
  }'
```

**Answer Medical Question:**
```bash
curl -X POST http://localhost:8000/answer_question \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the common side effects of azithromycin?"
  }'
```

**Extract Structured Data:**
```bash
curl -X POST http://localhost:8000/extract_structured \
  -H "Content-Type: application/json" \
  -d '{
    "data": "Patient: John Doe, Age: 45, Diagnosis: Type 2 Diabetes, Medication: Metformin 500mg twice daily"
  }'
```

**Convert to FHIR:**
```bash
curl -X POST http://localhost:8000/convert_to_fhir \
  -H "Content-Type: application/json" \
  -d '{
    "structured_data": {
      "name": "John Doe",
      "age": 45,
      "conditions": [],
      "diagnoses": [
        {
          "name": "Type 2 Diabetes",
          "icd_code": "E11.9"
        }
      ],
      "treatments": [],
      "medications": [
        {
          "name": "Metformin",
          "rx_norm_code": "860975"
        }
      ]
    }
  }'
```

### Database Persistence

The SQLite database is stored in the `./data` directory, which is mounted as a volume. This means:
- Database persists across container restarts
- Fixtures are loaded automatically on first run
- You can backup the database by copying the `./data` directory

## Development

### Code Quality

Format and lint code:
```bash
make lint
# or
uv run ruff format .
uv run ruff check --fix .
uv run pyright
```

### Testing

Run all tests:
```bash
make test
# or
uv run pytest -v
```

## Makefile Commands

```bash
make install    # Install all dependencies
make run        # Start development server
make test       # Run tests
make lint       # Format and lint code
make clean      # Remove cache and test databases
```