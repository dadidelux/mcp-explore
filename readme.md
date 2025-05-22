# Meme Generator Web App

This repository contains a cross-platform meme generator web application built with both Flask and Django. It allows users to create memes using popular templates and custom text, with a modern Bootstrap-based UI.

## Features
- **Web-based Meme Generator**: Create memes by selecting templates and entering top/bottom text.
- **Multiple Frameworks**: Includes both a Flask app and a Django app for flexibility.
- **Bootstrap UI**: Clean, responsive interface for easy meme creation.
- **Environment Variable Security**: Sensitive credentials (e.g., Imgflip API) are stored in a `.env` file.
- **Cross-Platform Startup Scripts**: Easy-to-use scripts for both Windows (`.ps1`) and Linux (`.sh`).
- **Extensible**: Easily add more meme templates or extend functionality.

## Project Structure
```
├── src/
│   ├── meme_web_app.py         # Flask app
│   └── django_app/            # Django project
│       ├── manage.py
│       ├── mysite/
│       └── meme_generator/
├── start_django.ps1           # Windows script for Django
├── start_django.sh            # Linux script for Django
├── start_meme_app.ps1         # Windows script for Flask
├── start_meme_app.sh          # Linux script for Flask
├── .env                       # Environment variables (not committed)
├── requirements.txt           # Python dependencies
└── readme.md                  # This file
```

## Setup Instructions

### 1. Clone the Repository
```powershell
git clone <repo-url>
cd mcp_explore
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory with the following content:
```ini
# Imgflip API credentials
IMGFLIP_USERNAME=your_username
IMGFLIP_PASSWORD=your_password

# Django settings
DJANGO_SECRET_KEY=your_django_secret_key
DJANGO_DEBUG=True
```

### 4. Run the Applications
#### Flask Meme Generator
- **Windows:**
  ```powershell
  .\start_meme_app.ps1
  ```
- **Linux:**
  ```bash
  ./start_meme_app.sh
  ```
- Access at: [http://127.0.0.1:5000](http://127.0.0.1:5000)

#### Django Meme Generator
- **Windows:**
  ```powershell
  .\start_django.ps1
  ```
- **Linux:**
  ```bash
  ./start_django.sh
  ```
- Access at: [http://127.0.0.1:8000](http://127.0.0.1:8000)

## Adding Meme Templates
To add more meme templates, edit the `TEMPLATES` list in either `src/meme_web_app.py` (Flask) or `src/django_app/meme_generator/views.py` (Django).

## Security Note
- **Never commit your `.env` file or credentials to version control.**
- This project is for educational/demo purposes. For production, use a secure deployment and secret management strategy.

## License
MIT License

---
Enjoy making memes!