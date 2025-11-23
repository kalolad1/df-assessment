# Deerfield Assessment - Medical Document API

A FastAPI backend application for document management with LLM-powered medical note summarization.

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
   make build
   ```
  
3. **Start the Services**

   ```bash
   make up
   ```

   The API will be available at `http://localhost:8000`

4. **Stop the Services**

   ```bash
   make down
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