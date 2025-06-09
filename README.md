# LIFE - Level Up Your Life

LIFE is a web application that helps you level up your life by tracking quests and habits. It uses RPG mechanics to make personal development more engaging and fun.

## Features

- **Quests**: Create and track one-time and recurring quests
- **Habits**: Build and maintain daily, weekly, or monthly habits
- **Experience Points**: Earn XP by completing quests and maintaining habits
- **Streaks**: Track your progress with habit streaks
- **User Authentication**: Secure login and registration system

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/life.git
cd life
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the dependencies:
```bash
pip install -r requirements.txt
```

4. Create a .env file in the project root with the following content:
```bash
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
```

5. Set up the database:
```bash
python manage.py setup
```

6. Run the development server:
```bash
python manage.py runserver
```

7. Visit http://localhost:8000 in your browser.

## Usage

### Admin Access

- URL: http://localhost:8000/admin
- Username: admin
- Password: admin

### Test User

- Username: test
- Password: test

## Development

### Available Management Commands

- `python manage.py setup`: Sets up the project by running all necessary commands
- `python manage.py resetdb`: Resets the database by dropping all tables and recreating them
- `python manage.py createsuperuser`: Creates a superuser
- `python manage.py createsampledata`: Creates sample data for testing

### Project Structure

```
life_dashboard/
├── dashboard/          # Main dashboard app
├── quests/            # Quests and habits app
├── templates/         # Project-wide templates
├── static/           # Project-wide static files
└── life_dashboard/   # Project settings
```

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
