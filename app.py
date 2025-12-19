import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session, abort, jsonify
from recommender import df, recommend_by_id, recommend_for_user

app = Flask(__name__)
app.secret_key = "change_me"   # à changer en prod


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
# LOGIN - CORRIGÉ
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
            session["full_name"] = user["full_name"]  # ✅ AJOUTER
            session["email"] = user["email"]           # ✅ AJOUTER
            session["phone"] = user["phone"]           # ✅ AJOUTER
            # après login → page des cours
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
# HOMEPAGE / COURSES (protégée)
# URL : /home  mais endpoint = "index" (comme avant)
# =====================================================
@app.route("/home")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))

    cols = ["id", "title", "avg_rating", "num_subscribers", "price_detail__amount"]
    courses = df[cols].head(100).to_dict(orient="records")
    return render_template("index.html", courses=courses)


# =====================================================
# COURSE PAGE (protégée)
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
# FAVORITES PAGE (profil utilisateur)
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
        liked_courses = df[df["id"].isin(liked_ids)].to_dict(orient="records")

    recommendations = []
    if liked_ids:
        recommendations = recommend_for_user(liked_ids, top_n=10)

    return render_template(
        "favorites.html",
        liked_courses=liked_courses,
        recommendations=recommendations
    )


# =====================================================
# UPDATE PROFILE - CORRIGÉ
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
    
    # Validation
    if not full_name or not email or not phone:
        return jsonify({'success': False, 'message': 'Tous les champs sont obligatoires'}), 400
    
    try:
        conn = get_db()
        cur = conn.cursor()
        
        # Mise à jour en base de données
        cur.execute(
            "UPDATE users SET full_name=%s, email=%s, phone=%s WHERE id=%s",
            (full_name, email, phone, user_id)
        )
        conn.commit()
        conn.close()
        
        # Mise à jour de la session
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