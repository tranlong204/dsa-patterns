# DSA Patterns Backend API

FastAPI backend for the DSA Patterns application with Supabase integration.

## Features

- **CRUD Operations** for LeetCode problems
- **User Progress Tracking** - Mark problems as solved/unsolved
- **Statistics API** - Get solved counts by difficulty
- **Calendar Data** - Track daily problem-solving activity
- **Supabase Integration** - Persistent data storage

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
```

### 3. Set Up Supabase Database

1. Create a new Supabase project at https://supabase.com
2. Go to SQL Editor in your Supabase dashboard
3. Run the SQL from `app/database_init.py` to create tables

### 4. Import Problems Data

```bash
python import_data.py
```

This will import all 1,432 problems from `data.js` into your Supabase database.

### 5. Run the Server

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Problems

- `GET /api/problems/` - Get all problems
- `GET /api/problems/{problem_id}` - Get a specific problem
- `POST /api/problems/` - Create a new problem
- `PUT /api/problems/{problem_id}` - Update a problem
- `DELETE /api/problems/{problem_id}` - Delete a problem
- `GET /api/problems/by-category/{category}` - Get problems by category

### User Progress

- `GET /api/user/{user_id}/solved` - Get solved problem IDs
- `POST /api/user/{user_id}/solved/{problem_id}` - Mark problem as solved
- `DELETE /api/user/{user_id}/solved/{problem_id}` - Mark problem as unsolved
- `GET /api/user/{user_id}/stats` - Get progress statistics
- `GET /api/user/{user_id}/calendar` - Get calendar activity data

### Health Check

- `GET /` - API information
- `GET /health` - Health check endpoint

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Database Schema

### problems table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| number | INTEGER | Problem number |
| title | TEXT | Problem title |
| difficulty | VARCHAR | Easy/Medium/Hard |
| topics | JSONB | Array of categories |
| link | TEXT | Problem URL |
| subtopic | TEXT | Subcategory name |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Last update time |

### user_progress table

| Column | Type | Description |
|--------|------|-------------|
| id | BIGINT | Primary key |
| user_id | VARCHAR | User identifier |
| problem_id | INTEGER | Reference to problems.id |
| solved | BOOLEAN | Solved status |
| solved_at | DATE | Date solved |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Last update time |

## Testing

You can test the API using curl or any API client:

```bash
# Get all problems
curl http://localhost:8000/api/problems/

# Get user stats
curl http://localhost:8000/api/user/my_user_id/stats

# Mark problem as solved
curl -X POST http://localhost:8000/api/user/my_user_id/solved/1
```

