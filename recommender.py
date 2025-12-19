# recommender.py
# ---------------------------------------------------
# Chargement du modèle TF-IDF + fonctions de recommandation
# + plusieurs méthodes d'évaluation :
#   - show_example_recommendations (qualitative)
#   - precision_at_k / recall_at_k / avg_precision_at_k pour 1 cours
#   - evaluate_precision_at_k / evaluate_recall_at_k / evaluate_map_at_k
# ---------------------------------------------------

import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# ========= 1. Chargement des données =========
df = joblib.load("model/courses_df.pkl")
tfidf_matrix = joblib.load("model/tfidf_matrix.pkl")
vectorizer = joblib.load("model/tfidf_vectorizer.pkl")

print("Recommender : modeles PKL charges avec succes.")


# ========= 2. Détection de topic (pour l'évaluation) =========
def detect_topic(title: str) -> str:
    """
    Détecte un 'topic' simple à partir du titre du cours.
    Cette étiquette sera utilisée comme vérité terrain approximative
    pour l'évaluation (tous les cours d'un même topic sont 'pertinents').
    """
    t = str(title).lower()

    if "python" in t:
        return "python"
    if "sql" in t:
        return "sql"
    if "tableau" in t:
        return "tableau"
    if "excel" in t:
        return "excel"
    if "java" in t:
        return "java"
    if "javascript" in t or " js " in t:
        return "javascript"
    if "data science" in t or "data analysis" in t:
        return "data_science"
    if "machine learning" in t or " ml " in t:
        return "ml"

    return "other"


# Ajouter la colonne topic au DataFrame
df["topic"] = df["title"].astype(str).apply(detect_topic)


# ========= 3. Recommandation par ID =========
def recommend_by_id(course_id, top_n=5):
    """
    Retourne les top_n cours les plus similaires à partir de l'ID du cours.
    Utilise la similarité cosinus sur la matrice TF-IDF.
    """
    idx = df.index[df["id"] == course_id]
    if len(idx) == 0:
        print("ID non trouve :", course_id)
        return []

    idx = idx[0]

    # Similarité du cours avec tous les autres
    similarities = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()

    # tri décroissant, en sautant l'index du cours lui-même
    similar_idx = np.argsort(similarities)[::-1]
    similar_idx = [i for i in similar_idx if int(df.iloc[i]["id"]) != int(course_id)]
    similar_idx = similar_idx[:top_n]

    results = []
    for i in similar_idx:
        course = df.iloc[i]
        results.append({
            "id": int(course["id"]),
            "title": course.get("title", ""),
            "rating": float(course.get("avg_rating", 0)),
            "subscribers": int(course.get("num_subscribers", 0)),
            "price": float(course.get("price_detail__amount", 0)),
            "url": course.get("url", "#"),
            "score": float(similarities[i]),
        })

    return results


# ... ici tu as déjà df, tfidf_matrix, etc.

def recommend_for_user(liked_ids, top_n=6):
    """
    Recommande des cours en se basant sur TOUS les cours likés par l'utilisateur.
    On construit un 'profil utilisateur' = moyenne des vecteurs TF-IDF des cours likés,
    puis on cherche les cours les plus proches de ce profil.
    """

    if not liked_ids:
        return []

    # Récupérer les lignes des cours likés
    liked_rows = df[df["id"].isin(liked_ids)]
    if liked_rows.empty:
        return []

    liked_indices = liked_rows.index.tolist()

    # Profil utilisateur = moyenne des vecteurs TF-IDF des cours likés
    user_vector = tfidf_matrix[liked_indices].mean(axis=0)

    # ⚠️ convertir en array NumPy (ou dense) pour éviter np.matrix
    try:
        # si c'est un objet sparse (scipy), .A renvoie un ndarray
        user_vector = user_vector.A
    except AttributeError:
        # sinon, conversion classique
        user_vector = np.asarray(user_vector)

    # On s'assure que c'est bien 2D pour cosine_similarity
    if user_vector.ndim == 1:
        user_vector = user_vector.reshape(1, -1)

    # Similarité entre ce profil et tous les cours
    sims = cosine_similarity(user_vector, tfidf_matrix).ravel()

    # On évite de recommander les cours déjà likés
    sims[liked_indices] = -1

    # Top N indices
    top_indices = sims.argsort()[::-1][:top_n]

    recommendations = []
    for idx in top_indices:
        row = df.iloc[idx]
        recommendations.append({
            "id": int(row["id"]),
            "title": row["title"],
            "rating": float(row.get("avg_rating", 0) or 0),
            "subscribers": int(row.get("num_subscribers", 0) or 0),
            "price": float(row.get("price_detail__amount", 0) or 0),
        })

    return recommendations


# ========= 4. Évaluation qualitative =========
def show_example_recommendations(n_examples=5, top_n=5):
    """
    Affiche quelques exemples de recommandations pour vérifier
    qualitativement si la similarité a l'air cohérente.
    """
    n_examples = min(n_examples, len(df))
    indices = np.random.choice(len(df), size=n_examples, replace=False)

    for idx in indices:
        base_row = df.iloc[idx]
        base_id = int(base_row["id"])
        base_title = base_row.get("title", "")
        base_topic = base_row.get("topic", "other")

        print("=" * 80)
        print(f"Cours de base (id={base_id}) : {base_title}")
        print(f"Topic detecte        : {base_topic}")
        print("- Recommandations :")

        recs = recommend_by_id(base_id, top_n=top_n)
        for r in recs:
            r_topic = detect_topic(r["title"])
            print(f"  • {r['title']}")
            print(f"    topic={r_topic} | score={r['score']:.3f}")
        print()


# ========= 5. Métriques pour UN cours (Precision, Recall, MAP) =========
def precision_at_k_for_course(course_id, k=5):
    """
    Precision@K pour un cours :
    proportion de recommandations dans le top-K qui ont le même topic.
    """
    row = df[df["id"] == course_id]
    if row.empty:
        return None

    base_topic = row.iloc[0]["topic"]
    if base_topic == "other":
        # topic non informatif -> on ne calcule pas
        return None

    recs = recommend_by_id(course_id, top_n=k)
    if not recs:
        return 0.0

    same_topic = 0
    for r in recs:
        if detect_topic(r["title"]) == base_topic:
            same_topic += 1

    return same_topic / float(k)


def recall_at_k_for_course(course_id, k=5):
    """
    Recall@K pour un cours :
    (# reco pertinentes dans le top-K) / (# total de cours pertinents dans le dataset)
    où 'pertinent' = même topic que le cours de base.
    """
    row = df[df["id"] == course_id]
    if row.empty:
        return None

    base_topic = row.iloc[0]["topic"]
    if base_topic == "other":
        return None

    # Tous les cours de même topic (sauf le cours de base)
    same_topic_df = df[(df["topic"] == base_topic) & (df["id"] != course_id)]
    total_relevant = len(same_topic_df)
    if total_relevant == 0:
        # pas d'autres cours de ce topic -> recall non défini
        return None

    recs = recommend_by_id(course_id, top_n=k)
    if not recs:
        return 0.0

    same_topic = 0
    for r in recs:
        if detect_topic(r["title"]) == base_topic:
            same_topic += 1

    return same_topic / float(total_relevant)


def avg_precision_at_k_for_course(course_id, k=5):
    """
    Average Precision@K (AP@K) pour UN cours :
    AP@K = moyenne des precision@i aux positions où la reco est pertinente.

    On considère binaire :
    - 1 si le topic de la reco == topic du cours de base
    - 0 sinon
    """
    row = df[df["id"] == course_id]
    if row.empty:
        return None

    base_topic = row.iloc[0]["topic"]
    if base_topic == "other":
        return None

    recs = recommend_by_id(course_id, top_n=k)
    if not recs:
        return 0.0

    # liste de pertinence binaire par position
    relevances = [1 if detect_topic(r["title"]) == base_topic else 0 for r in recs]

    # nombre total de documents pertinents dans la reco (max K)
    num_relevant_in_recs = sum(relevances)
    if num_relevant_in_recs == 0:
        return 0.0

    precisions = []
    relevant_so_far = 0
    for i, rel in enumerate(relevances, start=1):
        if rel == 1:
            relevant_so_far += 1
            precisions.append(relevant_so_far / float(i))

    # AP@K
    return sum(precisions) / float(num_relevant_in_recs)


# ========= 6. Évaluation globale (moyennes sur plusieurs cours) =========
def _sample_courses_for_eval(max_courses=200):
    """
    Sélectionne un sous-échantillon de cours avec topic informatif
    pour l'évaluation globale.
    """
    mask = df["topic"] != "other"
    subset = df[mask]
    if max_courses is not None:
        subset = subset.sample(
            n=min(max_courses, len(subset)),
            random_state=42
        )
    return subset


def evaluate_precision_at_k(k=5, max_courses=200):
    """
    Calcule la Precision@K moyenne sur un échantillon de cours.
    """
    subset = _sample_courses_for_eval(max_courses)
    scores = []

    for _, row in subset.iterrows():
        c_id = int(row["id"])
        p = precision_at_k_for_course(c_id, k=k)
        if p is not None:
            scores.append(p)

    mean_p = float(np.mean(scores)) if scores else 0.0
    print(f"Precision@{k} moyenne = {mean_p:.3f} (sur {len(scores)} cours)")
    return scores


def evaluate_recall_at_k(k=5, max_courses=200):
    """
    Calcule la Recall@K moyenne sur un échantillon de cours.
    """
    subset = _sample_courses_for_eval(max_courses)
    scores = []

    for _, row in subset.iterrows():
        c_id = int(row["id"])
        r = recall_at_k_for_course(c_id, k=k)
        if r is not None:
            scores.append(r)

    mean_r = float(np.mean(scores)) if scores else 0.0
    print(f"Recall@{k} moyenne = {mean_r:.3f} (sur {len(scores)} cours)")
    return scores


def evaluate_map_at_k(k=5, max_courses=200):
    """
    Calcule la MAP@K (Mean Average Precision@K) sur un échantillon de cours.
    """
    subset = _sample_courses_for_eval(max_courses)
    scores = []

    for _, row in subset.iterrows():
        c_id = int(row["id"])
        ap = avg_precision_at_k_for_course(c_id, k=k)
        if ap is not None:
            scores.append(ap)

    mean_ap = float(np.mean(scores)) if scores else 0.0
    print(f"MAP@{k} (Mean Average Precision) = {mean_ap:.3f} (sur {len(scores)} cours)")
    return scores


# ========= 7. Tests si on lance ce fichier directement =========
if __name__ == "__main__":
    # 1) Évaluation qualitative
    print("=== Evaluation qualitative (exemples de reco) ===")
    show_example_recommendations(n_examples=3, top_n=5)

    # 2) Évaluation quantitative
    print("\n=== Evaluation quantitative (Precision/Recall/MAP @5) ===")
    evaluate_precision_at_k(k=5, max_courses=200)
    evaluate_recall_at_k(k=5, max_courses=200)
    evaluate_map_at_k(k=5, max_courses=200)
