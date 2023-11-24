# Twitter-Like API Project

# Deployment

The Twitter-Like API is deployed on Google Cloud Platform (GCP) and can be accessed at:

🔗 [Swagger UI for Twitter-Like API](http://34.126.153.135/swagger)

This deployment is containerized using Docker and hosted on a GCP.

This brief section directs users to the deployed application and succinctly informs them about the deployment method.

## Overview
This project is a Flask-based API that mimics basic functionalities of Twitter. It allows users to register, login, post tweets, follow/unfollow users, and view user profiles. Additionally, it introduces Role-Based Access Control (RBAC) with a special role for Twitter Moderators, who can flag tweets as spam and suspend user accounts.


## Features
- **User Authentication**: Registration and login functionalities.
- **Tweet Management**: Users can post and view tweets.
- **User Relationships**: Users can follow and unfollow each other.
- **User Profiles**: Retrieve user profiles with tweets and follow statistics.
- **Feed Generation**: Users can view a feed of tweets from users they follow.
- **Moderation**: Twitter Moderators can flag tweets as spam and suspend user accounts.

## Technologies Used
- Flask, SQLAlchemy, Marshmallow, JWT, PostgreSQL

## Setup and Installation
1. **Clone the repository:**
   ```
   git clone https://github.com/RevoU-FSSE-2/Week-21-m-istighfar
   ```
2. **Navigate to the project directory:**
   ```
   cd revou-flask-api-main
   ```
3. **Install dependencies using pipenv:**
   ```
   pipenv install
   pipenv shell
   ```
4. **Set up environment variables:**
   - Copy `.env.example` to a new file named `.env` in the `src` directory.
   - Modify the `.env` file with your specific configurations.

5. **Run the application:**
   ```
   flask run
   ```

## API Endpoints

The following table outlines the available API endpoints along with their respective request methods and descriptions:

| Endpoint                  | Method | Description                                                  |
|---------------------------|--------|--------------------------------------------------------------|
| `/auth/registration`      | POST   | User registration, including optional role assignment.       |
| `/auth/login`             | POST   | User login, with handling for suspended accounts.            |
| `/user/profile`                   | GET    | Fetches the profile of the logged-in user.                   |
| `/tweet`                  | POST   | Allows users to post a tweet.                                |
| `/following`              | POST   | Enables users to follow/unfollow other users.                |
| `/user/feed`              | GET    | Generates a feed based on the users followed by the requester. |
| `/moderation/tweet`       | POST   | Allows Twitter Moderators to flag tweets as spam.            |
| `/moderation/user`        | POST   | Enables Twitter Moderators to suspend user accounts.         |