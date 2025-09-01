Lab Report System
Overview
This is a web-based Lab Report System designed to streamline the process of submitting, grading, and managing lab reports for students, lecturers, and administrators within an educational institution. The application features a clean, responsive front-end built with HTML and JavaScript, styled using Tailwind CSS.

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

Getting Started
This project is the front-end client for the Lab Report System. To run this application, you will need a corresponding backend server that provides the necessary API endpoints.

Technologies Used
HTML: For the structure of the web pages.

Tailwind CSS: For all styling, providing a utility-first approach.

JavaScript: For all client-side logic and making requests to the backend API.

How to Run
Ensure you have a compatible backend server running locally or hosted somewhere.

Open the index.html file in your web browser.

The application will automatically attempt to connect to the backend running on the same domain.

Note: The front-end code is set up to interact with a backend that handles user authentication and data management. It will not function correctly without a server providing the required API endpoints.