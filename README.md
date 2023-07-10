# webtronics-social-network
Test task for webtronics, backend project based on FastAPI with PostgreSQL + Redis.
## Features
- JWT auth and registration
- User can register and log in
- User can create, edit, delete and view posts
- User can like or dislike other user's posts but not my own
- UI Documentation (Swagger UI + ReDoc)
## Deploy
1. To start working on project install dependencies ```pip install -r requirements.txt```
2. Create env file from example ```cp .env.example .env```
3. Run databases PostgreSQL and Redis
4. Up migrations ```alembic upgrade head```
5. Run backend server ```python -m webtronics_social_network.server```