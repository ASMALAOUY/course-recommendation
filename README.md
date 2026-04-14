# 🎓 Course Recommendation System

A web-based application that recommends courses to users based on their preferences using Machine Learning and user interaction data.

---

## 🚀 Features

*  User registration and login
*  Like and save courses
*  Course recommendation using ML model
*  Personalized suggestions based on user behavior
*  Web interface with Flask (HTML, CSS, Bootstrap)

---

## 🛠️ Technologies Used

* **Backend:** Python, Flask
* **Frontend:** HTML, CSS, Bootstrap
* **Database:** MySQL
* **Machine Learning:** Scikit-learn, Pandas
* **Version Control:** Git & GitHub

---

## 📁 Project Structure

```


























course-recommendation/
│
├── app.py                # Main Flask application
├── recommender.py       # Recommendation logic
├── model/               # Saved ML models
├── data/                # Dataset
├── templates/           # HTML pages
├── static/              # CSS / JS files
├── courses_db.sql       # Database file
└── README.md
```

---



###  Install dependencies

```bash
pip install -r requirements.txt
```

If not available:

```bash
pip install flask pandas scikit-learn mysql-connector-python
```

---

## Codes SQL
Voici les requêtes SQL pour créer les tables et insérer des données :
### Création des tables
```sql
CREATE DATABASE IF NOT EXISTS courses_db CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE courses_db;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  full_name VARCHAR(255) NOT NULL,
  phone VARCHAR(50),
  email VARCHAR(255) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS liked_courses (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  course_id INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY unique_like (user_id, course_id),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

```

---

###  Configure Database Connection

In `app.py`, update:

```python
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="courses_db"
)
```

---

###  Run the application

```bash
python app.py
```

---

## 🌐 Demo








---





##  Future Improvements

*  Password encryption
*  Deploy online (Render / Railway)
*  Responsive design improvement
*  Advanced recommendation algorithms

---



---

## 📄 License

This project is for educational purposes.

---
