# PhotoShare

PhotoShare is a web application that allows users to upload, manage, and share their photos. The platform supports multiple roles, including regular users, moderators, and administrators, each with specific access rights. Users can upload photos, apply transformations, add tags, comment on photos, and rate them. The application also includes an admin dashboard for managing users and content.

## Features

### Authentication and Authorization
- **JWT-Based Authentication**: Secure authentication using JSON Web Tokens (JWT).
- **Role-Based Access Control**: Users are assigned one of three roles: Regular User, Moderator, or Administrator.
- **Automatic Role Assignment**: The first user to register is automatically assigned the Administrator role.

### User Capabilities
- **Photo Upload**: Users can upload photos with optional descriptions.
- **Photo Management**: Users can edit descriptions, delete photos, and view photos via unique URLs.
- **Tagging System**: Users can add up to 5 unique tags per photo. Tags are managed centrally, and existing tags are reused where applicable.
- **Photo Transformations**: Users can resize photos or apply filters using Cloudinary's image transformation services.
- **QR Code Generation**: Users can generate a QR code for any photo, which can be scanned to view the image.
- **Rating System**: Users can rate photos from 1 to 5 stars, with an average rating calculated from all users' ratings. Users can only rate each photo once and cannot rate their own photos.

### Commenting System
- **Commenting**: Users can comment on any photo. 
- **Comment Editing**: Users can edit their comments but cannot delete them.
- **Comment Moderation**: Moderators and administrators can delete comments.
- **Timestamping**: Comments are timestamped with their creation and last edited times.

### User Profiles
- **Profile Pages**: Each user has a profile page accessible via their unique username. The profile includes information such as the user’s name, registration date, and the number of uploaded photos.

### Administrative Capabilities
- **User Management**: Administrators can deactivate (ban) users. Inactive users cannot log in to the application.
- **Comment and Rating Management**: Moderators and administrators can view and delete user comments and ratings.

### Additional Features
- **Logout and Token Blacklisting**: Users can log out, and their access tokens are added to a blacklist for the remainder of their validity period.
- **Responsive Frontend**: Built using Jinja templates with HTML, CSS, and minimal JavaScript.
- **Admin Dashboard**: Separate dashboard for administrators to execute administrative tasks.
- **Frontend Role-Based Access**: Frontend options are protected based on user roles, and development routes are also secured.

## Deployment
The application is deployed using [Koyeb](https://app.koyeb.com/auth/signin), ensuring that it is accessible globally with robust cloud infrastructure.

## Tech Stack
- **Backend**: FastAPI, Python
- **Frontend**: Jinja2 (HTML, CSS, minimal JavaScript)
- **Database**: PostgreSQL
- **Image Handling**: Cloudinary
- **QR Code Generation**: Python `qrcode` package
- **Authentication**: JWT
- **Deployment**: Koyeb 

## Installation

### Prerequisites
- Python 3.11
- PostgreSQL
- Cloudinary Account

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/elgatoafk/photoshare.git
   cd photoshare
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables, like (the list of variables required is in app.src.config.config.py:
   - `DATABASE_URL`: Your PostgreSQL database URL.
   - `CLOUDINARY_URL`: Your Cloudinary API key.
   - `SECRET_KEY`: A secret key for JWT token generation.

5. Run migrations:
   ```bash
   alembic upgrade head
   ```

6. Start the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## Usage
1. **Register a new user**: The first registered user will be assigned the Administrator role.
2. **Log in**: Use your credentials to receive a JWT token.
3. **Upload a photo**: Navigate to the upload section and upload a photo with optional tags and a description.
4. **Manage photos**: Edit or delete your photos as needed.
5. **Rate and comment**: Interact with other users' photos by rating and commenting.
6. **Admin Dashboard**: Administrators can manage users, photos, comments, and ratings from the admin dashboard.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request for any enhancements, bug fixes, or new features.

## License
This project is licensed under the MIT License. This allows others to use, modify, and distribute the software freely as long as the original license is included.

---
