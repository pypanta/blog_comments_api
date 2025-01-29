# Blog Comments API

A RESTful API built with Flask and SQLAlchemy for managing my personal
blog post comments.

## Features

- CRUD operations for comments and replies
- Nested comment structure with parent-child relationships
- Authentication with token-based access (JWT)

## Installation

### Clone the Repository

```sh
git clone https://github.com/pypanta/blog_comments_api.git
```

### Create a Virtual Environment

```sh
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### Install Dependencies

```sh
pip install -r requirements.txt
```

### Set Up Environment Variables

Create a .flaskenv file and define:

```sh
SECRET_KEY=your_secret_key
DATABASE=sqlite:///database.db
```

### Apply Database Migrations

```sh
flask db upgrade
```

### Run the Server

```sh
flask run
```

## API Endpoints

| Method   | Endpoint                   | Description                       | Authentication |
|----------|----------------------------|-----------------------------------|----------------|
| `POST`   | `/register`                | Register a new user               | ❌ No          |
| `POST`   | `/login`                   | Login and get JWT token           | ❌ No          |
| `GET`    | `/logout`                  | Logout and delete JWT token       | ✅ Yes         |
| `GET`    | `/`                        | Fetch all comments                | ✅ Yes         |
| `GET`    | `/<post_id>`               | Fetch post comments               | ❌ No          |
| `POST`   | `/new`                     | Create a new comment              | ❌ No          |
| `PUT`    | `/<comment_id>/update`     | Update an existing comment        | ✅ Yes         |
| `DELETE` | `/<comment_id>/delete`     | Delete a comment and its replies  | ✅ Yes         |
