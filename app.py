import mysql.connector
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session, abort, jsonify
from recommender import df, recommend_by_id, recommend_for_user

app = Flask(__name__)
app.secret_key = "change_me"   # à changer en prod


# =====================================================
# GÉNÉRER DES IMAGES POUR LES COURS
# =====================================================
# Remplacez la fonction add_course_images par celle-ci :
def add_course_images(df):
    """Ajoute une colonne image_url au DataFrame avec TOUS les mots-clés possibles"""
    
    # Images de haute qualité
    images_map = {
        # Programmation & Web
        'python': 'https://images.unsplash.com/photo-1526374965328-7f5ae4e8cfb6?w=400&h=200&fit=crop',
        'java': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=400&h=200&fit=crop',
        'javascript': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=400&h=200&fit=crop',
        'web': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=400&h=200&fit=crop',
        'node': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=400&h=200&fit=crop',
        'react': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=400&h=200&fit=crop',
        'code': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=400&h=200&fit=crop',
        'blockchain': 'https://images.unsplash.com/photo-1526374965328-7f5ae4e8cfb6?w=400&h=200&fit=crop',
        
        # Data & Analytics
        'sql': 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=400&h=200&fit=crop',
        'data': 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=400&h=200&fit=crop',
        'tableau': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=400&h=200&fit=crop',
        'excel': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=200&fit=crop',
        'power': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=200&fit=crop',
        'mysql': 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=400&h=200&fit=crop',
        'analytics': 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=400&h=200&fit=crop',
        'hadoop': 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=400&h=200&fit=crop',
        'numpy': 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=400&h=200&fit=crop',
        'intelligence': 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=400&h=200&fit=crop',
        'google': 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=400&h=200&fit=crop',
        'crash': 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=400&h=200&fit=crop',
        'weekend': 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=400&h=200&fit=crop',
        'fundamentals': 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=400&h=200&fit=crop',
        'finance': 'https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=400&h=200&fit=crop',
        
        # AI & Machine Learning
        'machine': 'https://images.unsplash.com/photo-1677442d019cecf8caa46caf6fe43ca63a65a6bd8?w=400&h=200&fit=crop',
        'ai': 'https://images.unsplash.com/photo-1677442d019cecf8caa46caf6fe43ca63a65a6bd8?w=400&h=200&fit=crop',
        'deep': 'https://images.unsplash.com/photo-1677442d019cecf8caa46caf6fe43ca63a65a6bd8?w=400&h=200&fit=crop',
        'learning': 'https://images.unsplash.com/photo-1677442d019cecf8caa46caf6fe43ca63a65a6bd8?w=400&h=200&fit=crop',
        'neural': 'https://images.unsplash.com/photo-1677442d019cecf8caa46caf6fe43ca63a65a6bd8?w=400&h=200&fit=crop',
        'robotic': 'https://images.unsplash.com/photo-1677442d019cecf8caa46caf6fe43ca63a65a6bd8?w=400&h=200&fit=crop',
        'rpa': 'https://images.unsplash.com/photo-1677442d019cecf8caa46caf6fe43ca63a65a6bd8?w=400&h=200&fit=crop',
        'automation': 'https://images.unsplash.com/photo-1677442d019cecf8caa46caf6fe43ca63a65a6bd8?w=400&h=200&fit=crop',
        'prerequisites': 'https://images.unsplash.com/photo-1677442d019cecf8caa46caf6fe43ca63a65a6bd8?w=400&h=200&fit=crop',
        
        # Business & Finance
        'business': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop',
        'analyst': 'https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=400&h=200&fit=crop',
        'accounting': 'https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=400&h=200&fit=crop',
        'trading': 'https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=400&h=200&fit=crop',
        'investment': 'https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=400&h=200&fit=crop',
        'banking': 'https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=400&h=200&fit=crop',
        'forex': 'https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=400&h=200&fit=crop',
        'stock': 'https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=400&h=200&fit=crop',
        'mba': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop',
        'crypto': 'https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=400&h=200&fit=crop',
        'real': 'https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=400&h=200&fit=crop',
        'valuation': 'https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=400&h=200&fit=crop',
        'modeling': 'https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=400&h=200&fit=crop',
        
        # Marketing & Sales
        'marketing': 'https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop',
        'sales': 'https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop',
        'seo': 'https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop',
        'email': 'https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop',
        'writing': 'https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop',
        'copywriting': 'https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop',
        'customer': 'https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop',
        'service': 'https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop',
        'digital': 'https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop',
        'etiquette': 'https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop',
        'tactics': 'https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop',
        'communication': 'https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop',
        'smarter': 'https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop',
        'better': 'https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop',
        'techniques': 'https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop',
        'practical': 'https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop',
        
        # Management & Leadership
        'management': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop',
        'leadership': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop',
        'project': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop',
        'pmi': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop',
        'agile': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop',
        'scrum': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop',
        'kanban': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop',
        
        # Skills & Communication
        'skill': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop',
        'team': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop',
        'speaking': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop',
        'emotional': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop',
        'listening': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop',
        'presentation': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop',
        'exceptional': 'https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop',
        'flair': 'https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop',
        
        # Design & Creative
        'design': 'https://images.unsplash.com/photo-1561070791-2526d30994b5?w=400&h=200&fit=crop',
        'ui': 'https://images.unsplash.com/photo-1561070791-2526d30994b5?w=400&h=200&fit=crop',
        'ux': 'https://images.unsplash.com/photo-1561070791-2526d30994b5?w=400&h=200&fit=crop',
        'graphic': 'https://images.unsplash.com/photo-1561070791-2526d30994b5?w=400&h=200&fit=crop',
        
        # E-commerce & Entrepreneurship
        'ecommerce': 'https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop',
        'shopify': 'https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop',
        'dropship': 'https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop',
        'ebay': 'https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop',
        'amazon': 'https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop',
        'entrepreneur': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop',
        'freelancer': 'https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop',
        'fba': 'https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop',
        
        # Certifications & Exams
        'exam': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop',
        'certification': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop',
        'prep': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop',
        'sigma': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop',
        'belt': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop',
        'course': 'https://images.unsplash.com/photo-1677442d019cecf8caa46caf6fe43ca63a65a6bd8?w=400&h=200&fit=crop',
        'training': 'https://images.unsplash.com/photo-1677442d019cecf8caa46caf6fe43ca63a65a6bd8?w=400&h=200&fit=crop',
        'seminar': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop',
        'pmbok': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop',
        'capm': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop',
        
        # Security & IT
        'security': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop',
        'awareness': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop',
        'it': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop',
        
        # Général
        'complete': 'https://images.unsplash.com/photo-1677442d019cecf8caa46caf6fe43ca63a65a6bd8?w=400&h=200&fit=crop',
        'ultimate': 'https://images.unsplash.com/photo-1677442d019cecf8caa46caf6fe43ca63a65a6bd8?w=400&h=200&fit=crop',
        'master': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop',
        'beginner': 'https://images.unsplash.com/photo-1677442d019cecf8caa46caf6fe43ca63a65a6bd8?w=400&h=200&fit=crop',
        'hands': 'https://images.unsplash.com/photo-1677442d019cecf8caa46caf6fe43ca63a65a6bd8?w=400&h=200&fit=crop',
    }
    
    default_image = 'https://images.unsplash.com/photo-1516321318423-f06f70504504?w=400&h=200&fit=crop'
    
    def get_image_url(title):
        title_lower = str(title).lower()
        # Chercher le premier mot-clé qui correspond
        for key, url in images_map.items():
            if key in title_lower:
                return url
        return default_image
    
    df['image_url'] = df['title'].apply(get_image_url)
    return df


# Ajouter les images au chargement
df = add_course_images(df)
# =====================================================
# Connexion MySQL
# =====================================================
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="courses_db"
    )


# =====================================================
# RACINE → toujours vers login
# =====================================================
@app.route("/")
def root():
    return redirect(url_for("login"))


# =====================================================
# LOGIN
# =====================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )
        user = cur.fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["full_name"]
            session["full_name"] = user["full_name"]
            session["email"] = user["email"]
            session["phone"] = user["phone"]
            return redirect(url_for("index"))
        else:
            error = "Email ou mot de passe incorrect."

    return render_template("login.html", error=error)


# =====================================================
# SIGN UP
# =====================================================
@app.route("/register", methods=["POST"])
def register():
    full_name = request.form["full_name"]
    phone = request.form.get("phone")
    email = request.form["email"]
    password = request.form["password"]

    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO users (full_name, phone, email, password) VALUES (%s, %s, %s, %s)",
            (full_name, phone, email, password)
        )
        conn.commit()
    except mysql.connector.Error:
        conn.close()
        return render_template("login.html", error="Cet email est déjà utilisé.")

    conn.close()
    return redirect(url_for("login"))


# =====================================================
# LOGOUT
# =====================================================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# =====================================================
# HOMEPAGE / COURSES
# =====================================================
@app.route("/home")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))

    cols = ["id", "title", "avg_rating", "num_subscribers", "price_detail__amount", "image_url"]
    courses = df[cols].head(100).to_dict(orient="records")
    
    return render_template("index.html", courses=courses)


# =====================================================
# COURSE PAGE
# =====================================================
@app.route("/course/<int:course_id>")
def course_page(course_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    course_row = df[df["id"] == course_id]
    if course_row.empty:
        abort(404)

    course = course_row.iloc[0].to_dict()
    recommendations = recommend_by_id(course_id, top_n=6)
    
    # Ajouter image_url aux recommandations
    for rec in recommendations:
        rec['image_url'] = df[df['id'] == rec['id']]['image_url'].values[0] if len(df[df['id'] == rec['id']]) > 0 else 'https://images.unsplash.com/photo-1516321318423-f06f70504504?w=400&h=200&fit=crop'

    return render_template(
        "course.html",
        course=course,
        recommendations=recommendations
    )


# =====================================================
# LIKE A COURSE
# =====================================================
@app.route("/like/<int:course_id>")
def like_course(course_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT IGNORE INTO liked_courses (user_id, course_id) VALUES (%s, %s)",
        (user_id, course_id)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("my_favorites"))


# =====================================================
# UNLIKE A COURSE
# =====================================================
@app.route("/unlike/<int:course_id>")
def unlike_course(course_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM liked_courses WHERE user_id=%s AND course_id=%s",
        (user_id, course_id)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("my_favorites"))


# =====================================================
# FAVORITES PAGE
# =====================================================
@app.route("/my_favorites")
def my_favorites():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT course_id FROM liked_courses WHERE user_id=%s", (user_id,))
    rows = cur.fetchall()
    conn.close()

    liked_ids = [r["course_id"] for r in rows]

    liked_courses = []
    if liked_ids:
        cols = ["id", "title", "avg_rating", "num_subscribers", "price_detail__amount", "image_url"]
        liked_courses = df[df["id"].isin(liked_ids)][cols].to_dict(orient="records")

    recommendations = []
    if liked_ids:
        recommendations = recommend_for_user(liked_ids, top_n=10)
        # Ajouter image_url aux recommandations
        for rec in recommendations:
            rec['image_url'] = df[df['id'] == rec['id']]['image_url'].values[0] if len(df[df['id'] == rec['id']]) > 0 else 'https://images.unsplash.com/photo-1516321318423-f06f70504504?w=400&h=200&fit=crop'

    return render_template(
        "favorites.html",
        liked_courses=liked_courses,
        recommendations=recommendations
    )


# =====================================================
# UPDATE PROFILE
# =====================================================
@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Non authentifié'}), 401
    
    data = request.get_json()
    user_id = session['user_id']
    
    full_name = data.get('full_name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    
    if not full_name or not email or not phone:
        return jsonify({'success': False, 'message': 'Tous les champs sont obligatoires'}), 400
    
    try:
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute(
            "UPDATE users SET full_name=%s, email=%s, phone=%s WHERE id=%s",
            (full_name, email, phone, user_id)
        )
        conn.commit()
        conn.close()
        
        session['full_name'] = full_name
        session['email'] = email
        session['phone'] = phone
        session['username'] = full_name
        
        return jsonify({'success': True, 'message': 'Profil mis à jour avec succès'})
    
    except mysql.connector.Error as err:
        return jsonify({'success': False, 'message': f'Erreur BD: {err}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# =====================================================
# RUN
# =====================================================
if __name__ == "__main__":
    app.run(debug=True)