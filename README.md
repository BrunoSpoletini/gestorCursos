# 📚 Course Manager

#### Table of Contents  
- [Description](#description)
- [Usage](#usage)
- [Features](#features)
- [Business Rules](#-business-rules)
- [Models Used](#️-models-used)
- [Authentication](#-autentication)
- [Endpoints](#-endpoints)
- [Improvements in progress](#-improvements-in-progress)

## Description

RESTful API with Django built to manage an online course system, student enrollments, and instructor grading.
For now, the focus is on the backend logic, with plans to implement a frontend in the future.

The goal is to demonstrate solid knowledge of:
- Django
- Django REST Framework
- PostgreSQL
- JWT Authentication
- ORM and relationships
- Data modeling
- Access control and roles
- Code best practices

## Usage

1. Clone the repository:

   ```bash
   git clone https://github.com/BrunoSpoletini/gestorCursos.git
   cd gestorCursos
   ```

2. Create and enter your virtual enviroment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate (*linux) or .venv\Scripts\activate (*Windows)
   cp .env_template .env
   ```
Then complete the .env file with your PosgreSQL database parameters.

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create database and apply migrations:

   ```bash
   python dbSetup.py
   cd gestor
   python manage.py makemigrations
   python manage.py migrate
   ```
   
5. Run the server:
   ```bash
   python manage.py runserver
   ```
   And check the available endpoints on the [API Schema](http://localhost:8000/) once the server is up and running.
7. To run Unit Tests, stop the server and type:
   ```bash
   pytest
   ```
8. You can also test the API endpoints using tools like Postman or the API_requests.http file with the Rest Client VsCode extension.


### Features:
- Registration and login with JWT
- User roles: `student`, `instructor`, `admin`
- Course, enrollment, and grading models
- Role-based permissions
- Organized REST endpoints
- Access restricted according to business logic
---

## 🧠 Business Rules

- A **user** can have one of the following roles:
  - `student`: can enroll in courses, view their grades
  - `instructor`: can create courses and grade enrolled students
  - `admin`: can view and modify everything

- An **instructor** can only grade students enrolled in their own courses.

- A **student** can only view their own grades.

---

## 🗃️ Models Used

### 🔹 User
- Inherits from `AbstractUser`
- Extra field: `role` (`student`, `instructor`, `admin`)

### 🔹 Course
- `name`: CharField
- `description`: TextField
- `created_by`: ForeignKey → User (only  `instructor`)

### 🔹 Enrollment
- `user`: ForeignKey → User (only  `student`)
- `course`: ForeignKey → Course
- `created_at`: DateTime

### 🔹 Grade
- `enrollment`: ForeignKey → Enrollment
- `score`: FloatField (0.0 - 10.0)
- `comment`: TextField
- `created_at`: DateTime

---

## 🔐 Autentication

- JWT usage (`djangorestframework-simplejwt`)
- Flow:
  1. POST `/api/register/` → creates a user and assigns a role
  2. POST `/api/token/` → gets  `access` and `refresh`
  3. Uso de `Authorization: Bearer <token>` for all protected endpoints
     
---

## 📡 Endpoints

### 👤 Users
| Method | Path                 | Role       | Description                       |
|--------|----------------------|------------|-----------------------------------|
| POST   | `/api/register/`     | Público    | 	User registration with role      |
| POST   | `/api/token/`        | Público    | 	Login and get tokens             |
| GET    | `/api/users/`        | Admin      | 	List all users                   |

---

### 📘 Courses
| Method | Path                 | Role       | Description                       |
|--------|----------------------|------------|-----------------------------------|
| GET    | `/api/courses/`      | Todos      | List all public courses           |
| POST   | `/api/courses/`      | Instructor | 	Create a new course              |
| GET    | `/api/courses/<id>/` | Todos      | 	View course details              |

---

### 🎓 Enrollments
| Method | Path                  | Role    | Description                          |
|--------|-----------------------|---------|--------------------------------------|
| POST   | `/api/enroll/`        | Student | 	Enroll in a course                  |
| GET    | `/api/my-enrollments/`| Student | List courses the student is in       |

---

### 📝 Grades
| Method | Path                    | Role       | Description                          |
|--------|-------------------------|------------|--------------------------------------|
| POST   | `/api/grades/`          | Instructor | Grade an enrolled student            |
| GET    | `/api/my-grades/`       | Student    | View own grades                      |
| GET    | `/api/grades/course/<id>/` | Instructor | 	View grades for their course     |

---

## 🧪 Improvements in progress
- Consider Docker usage
- Frontend using react


---


