# Secure Backend Setup

## Installation

1. Create virtual environment:

**Windows:**
```bash
py -3.12 -m venv venv
```

**macOS:**
```bash
python3.12 -m venv venv
```

2. Activate virtual environment:

**Windows:**
```bash
source venv/Scripts/activate
```

**macOS:**
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

```bash
python app.py
```

Server runs on http://localhost:5000

## Deployment

For production, use a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Docker

### Build and Run
```bash
docker-compose up --build
```

Runs on http://localhost:5001

## Environment Variables

All secrets are stored in `.env` file (never commit this file).
See `.env.example` for required variables.
