# PeakPrep 🎯

PeakPrep is a JEE preparation website built with Python Flask.
It provides student accounts, mock tests for JEE Main and JEE Advanced,
and test-result tracking.

## Features

- Student registration and login
- Password-based authentication
- JEE Main mock-test interface
- JEE Advanced mock-test interface
- Physics, Chemistry and Mathematics questions
- Countdown timer and answer navigation
- Automatic test scoring
- Student dashboard and result history
- Lavender and mint user interface
- SQLite database for storing results

## Technology Stack

- Python
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-WTF
- SQLite
- HTML and CSS
- JavaScript

## Project Structure

```text
CodeQuest-web/
├── app.py
├── question_bank.py
├── requirements.txt
├── README.md
├── instance/
│   └── peakprep.db
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── mock_test.html
│   └── result.html
└── static/
    └── style.css
```

The database file is created by the application when configured to do so.
You do not need to create it manually.

## Requirements

- Python 3.10 or newer
- Visual Studio Code or another code editor
- Internet connection for installing Python packages

## Installation

### 1. Open the project folder

Open `CodeQuest-web` in VS Code.

### 2. Create a virtual environment

**Windows:**

```bash
py -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

**macOS or Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure the secret key

Set a strong, private `SECRET_KEY` environment variable before running
the application. Do not commit secret keys or passwords to GitHub.

For a local Windows PowerShell session:

```powershell
$env:SECRET_KEY = "replace-with-a-long-random-secret"
```

For macOS or Linux:

```bash
export SECRET_KEY="replace-with-a-long-random-secret"
```

The application must be configured to read this variable.

### 5. Run the application

```bash
python app.py
```

Open the local address shown in the terminal, usually:

http://127.0.0.1:5000

## How to Use

1. Open PeakPrep in your browser.
2. Create a student account.
3. Log in with your account.
4. Open the dashboard.
5. Select a JEE Main or JEE Advanced mock test.
6. Answer questions and submit the test.
7. Review your score and previous results.

## Security Notes

- Keep your secret key private.
- Never store plaintext passwords.
- Validate submitted answers and test deadlines on the server.
- Use Flask's debug mode only for local development.
- Configure secure cookies and HTTPS before deployment.

## Development Status

This project is a learning and development project.
Verify the question bank, scoring rules, database operations and routes
before using it for actual exam preparation or deploying it publicly.

## License

Add your chosen license before distributing the project