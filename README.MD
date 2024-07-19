# PhotoShare

PhotoShare is a photo-sharing application built with FastAPI. It allows users to upload, manage, and share photos, comment on photos, rate photos, and search for photos based on keywords and tags. The application uses JWT for authentication and role-based access control.

## Features

- User authentication with JWT
- Role-based access control (user, moderator, administrator)
- Photo upload, edit, delete, and transformation
- Comment on photos
- Rate photos
- Search and filter photos by keywords and tags

## Getting Started

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up the database (PostgreSQL is recommended)
4. Configure environment variables
5. Run the application: `uvicorn backend.main:app --reload`
