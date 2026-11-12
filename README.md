# AcadTrack

A web-based academic management platform built with **Django** and **SQLite3** to create an environment for students, faculties and admins to have a seamless academic management experience.


## ✨ Features

- **Attendance Tracking** — Record and view lecture-wise attendance
- **Assignment Management** — Create, submit, and grade assignments with feedback
- **Examination System** — Schedule exams and enter marks
- **Semester Results** — Auto-generated semester performance with SGPA
- **Academic History** — Preserved records across multiple courses and batches
- **Graduation Records** — Final CGPA and graduation status
- **Role-Based Access** — Separate dashboards for students, faculty, and admins


## 👥 Users

### 🎓 Student
View attendance, submit assignments, check exam results, and track semester performance.

### 👨‍🏫 Faculty
Schedule lectures, mark attendance, create and grade assignments, enter exam marks.

### 🛡️ Admin
Manage users, departments, courses, batches, semesters, subjects, and academic records.


## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django |
| Database | SQLite3 |
| Frontend | HTML, CSS, JavaScript |


## ⚡ Quick Start (Local)

### 1. Clone & Setup

```bash
git clone https://github.com/Altaf-7/AcadTrack.git
uv venv
.venv\Scripts\activate
uv pip install -r requirements.txt
cd AcadTrack
```

### 2. Initialize Database

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```
**Note** : The superuser is the admin of the website. It will allow you to create new users, faculty, admins, departments, courses, batches, semesters, subjects, and academic records. And also login as admin and manage the website.

### 3. Run

```bash
python manage.py runserver
```
Open [http://localhost:8000/](http://localhost:8000/)


## 🐳 Quick Start (Docker)

### 1. Pull & Run

```bash
docker pull altaf700/acadtrack:1.0
docker run -d -p 8000:8000 --name acadtrack acadtrack
```

### 2. Create Admin User

```bash
docker exec -it acadtrack python manage.py createsuperuser
```
Open [http://localhost:8000/](http://localhost:8000/)


## Future Scope

- CGPA calculation & transcript generation
- Performance analytics & graphical dashboards
- Attendance shortage & deadline alerts
- Email notifications & PDF reports
- Mobile application support


## License

This project is developed for academic and educational purposes.
