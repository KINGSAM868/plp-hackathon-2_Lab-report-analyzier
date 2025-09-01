Lab Report System
Overview
This is a web-based Lab Report System designed to streamline the process of submitting, grading, and managing lab reports for students, lecturers, and administrators within an educational institution. The application features a clean, responsive front-end built with HTML and JavaScript, styled using Tailwind CSS, and a Python-based backend that handles all data processing and API requests.

The project includes a detailed MySQL database schema (Lab_reportsdb.sql) to manage user data, lab templates, submissions, and analytics, ensuring data integrity and efficient operations.

Features
The system provides a clear separation of roles, with dedicated dashboards for each user type:

User Authentication
Registration: Allows new users to sign up with a specific role (Student, Lecturer, or Admin).

Login: Authenticates users and directs them to their respective dashboards based on their role.

Student Dashboard
Submit Report: Students can select from available lab report templates and submit their reports.

My Submissions: Students can view a history of their submitted reports, including their current status, grade, and feedback.

Lecturer Dashboard
Create Template: Lecturers can create new lab report templates with custom fields for students to use.

Submissions to Grade: Lecturers can view and grade reports submitted by their students, providing a grade and feedback.

Admin Dashboard
User Management: Administrators can view a list of all users in the system.

Institution Management: Admins have the ability to create new institutions within the system.

Technical Stack
Front-end:

HTML: For the structure of the web pages.

Tailwind CSS: For all styling, providing a utility-first approach.

JavaScript: For all client-side logic and making requests to the backend API.

Back-end:

Python: The core language for the backend server logic.

Flask: A micro-framework for building the RESTful API endpoints.

Database:

MySQL: The relational database for persistent storage. The schema is provided in Lab_reportsdb.sql.

Getting Started
To get the full system running, you need to set up both the backend server and the database.

1. Database Setup
The database schema is provided in the Lab_reportsdb.sql file. You can import this file into your MySQL database to create all the necessary tables, views, and triggers.

2. Backend Server
The backend is written in Python using Flask. You can run the server from your terminal.

Install Dependencies:

pip install Flask

Run the server:
Assuming your main server file is named app.py, run the following command from your terminal:

flask run

If your file has a different name, for example server.py, use:

flask --app server run

3. Front-end
Simply open the index.html file in your web browser. The front-end is configured to communicate with the backend running on the same domain.
