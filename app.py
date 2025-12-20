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
# =====================================================
# GÉNÉRER DES IMAGES POUR LES COURS
# =====================================================
# Remplacez la fonction add_course_images par celle-ci :
def add_course_images(df):
    """Ajoute une colonne image_url au DataFrame - Gère les titres avec plusieurs mots-clés"""
    
    # Dictionnaire avec priorités
    images_map = {
        # Mots-clés CRITIQUES (priorité très haute)
        'sql': ('https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=400&h=200&fit=crop', 100),
        'python': ('https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=400&h=200&fit=crop', 100),
        'tableau': ('https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=400&h=200&fit=crop', 100),
        'hadoop': ('https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=400&h=200&fit=crop', 100),
        'blockchain': ('https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=400&h=200&fit=crop', 100),
        'shopify': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 100),
        'dropship': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 100),
        'amazon': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 100),
        'ebay': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 100),
        'splunk': ('https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=400&h=200&fit=crop', 100),
        'uipath': ('https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=200&fit=crop', 100),
        'powerpoint': ('https://images.unsplash.com/photo-1561070791-2526d30994b5?w=400&h=200&fit=crop', 100),
        
        # Mots-clés spécifiques (priorité haute)
        'rpa': ('https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=200&fit=crop', 95),
        'investment': ('https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=400&h=200&fit=crop', 95),
        'banking': ('https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=400&h=200&fit=crop', 95),
        'forex': ('https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=400&h=200&fit=crop', 95),
        'cryptocurrency': ('https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=400&h=200&fit=crop', 95),
        'trading': ('https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=400&h=200&fit=crop', 90),
        'pmp': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 95),
        'capm': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 95),
        'acp': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 95),
        'scrum': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 90),
        'kanban': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 90),
        'sigma': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 90),
        'agile': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 85),
        'scrum': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 85),
        
        # Catégories principales
        'machine': ('https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=200&fit=crop', 80),
        'deep': ('https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=200&fit=crop', 80),
        'learning': ('https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=200&fit=crop', 70),
        'ai': ('https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=200&fit=crop', 75),
        'data': ('https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=400&h=200&fit=crop', 70),
        'analytics': ('https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=400&h=200&fit=crop', 75),
        'analysis': ('https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=400&h=200&fit=crop', 70),
        'excel': ('https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=200&fit=crop', 80),
        'power': ('https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=200&fit=crop', 80),
        'mysql': ('https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=400&h=200&fit=crop', 85),
        'numpy': ('https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=400&h=200&fit=crop', 85),
        'finance': ('https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=400&h=200&fit=crop', 75),
        'stock': ('https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=400&h=200&fit=crop', 75),
        'accounting': ('https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=400&h=200&fit=crop', 75),
        'analyst': ('https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=400&h=200&fit=crop', 75),
        'business': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 70),
        'mba': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 75),
        'crypto': ('https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=400&h=200&fit=crop', 80),
        'real': ('https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=400&h=200&fit=crop', 70),
        'estate': ('https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=400&h=200&fit=crop', 70),
        
        # Marketing & Sales
        'marketing': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 75),
        'sales': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 75),
        'email': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 70),
        'seo': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 75),
        'customer': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 70),
        'service': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 70),
        'digital': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 70),
        'google': ('https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=400&h=200&fit=crop', 70),
        
        # Management & Leadership
        'management': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 75),
        'leadership': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 75),
        'project': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 75),
        'pmi': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 85),
        'management': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 75),
        'influence': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 70),
        'inspire': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 70),
        'impact': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 70),
        'virtual': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 65),
        
        # Skills & Communication
        'speaking': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 70),
        'public': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 70),
        'speech': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 70),
        'communication': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 70),
        'writing': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 70),
        'emotional': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 70),
        'intelligence': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 70),
        'listening': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 70),
        'presentation': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 70),
        'confidence': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 65),
        'ninja': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 60),
        'conscious': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 65),
        'powerful': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 65),
        'cross': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 65),
        'cultural': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 65),
        'brilliant': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 60),
        'flair': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 55),
        'exceptional': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 60),
        'mastery': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 60),
        'delight': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 55),
        
        # Design & Creative
        'design': ('https://images.unsplash.com/photo-1561070791-2526d30994b5?w=400&h=200&fit=crop', 75),
        'ui': ('https://images.unsplash.com/photo-1561070791-2526d30994b5?w=400&h=200&fit=crop', 80),
        'ux': ('https://images.unsplash.com/photo-1561070791-2526d30994b5?w=400&h=200&fit=crop', 80),
        'graphic': ('https://images.unsplash.com/photo-1561070791-2526d30994b5?w=400&h=200&fit=crop', 75),
        'creativity': ('https://images.unsplash.com/photo-1561070791-2526d30994b5?w=400&h=200&fit=crop', 75),
        'thinking': ('https://images.unsplash.com/photo-1561070791-2526d30994b5?w=400&h=200&fit=crop', 60),
        'innovation': ('https://images.unsplash.com/photo-1561070791-2526d30994b5?w=400&h=200&fit=crop', 75),
        
        # E-commerce & Entrepreneurship
        'entrepreneurship': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 70),
        'entrepreneur': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 70),
        'freelancer': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 65),
        'freelance': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 65),
        'empire': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 60),
        'aliexpress': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 80),
        'inventory': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 65),
        'budget': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 60),
        'fba': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 80),
        'ecommerce': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 75),
        
        # Certifications
        'exam': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 65),
        'certification': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 70),
        'certified': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 70),
        'prep': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 65),
        'belt': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 75),
        'yellow': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 75),
        'green': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 75),
        'white': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 70),
        'seminar': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 60),
        'pmbok': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 80),
        'contact': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 55),
        'hours': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 50),
        'accredited': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 60),
        'bko': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 60),
        
        # Security & IT
        'security': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 70),
        'awareness': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 65),
        'it': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 60),
        'internet': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 60),
        'employees': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 50),
        
        # Général (faible priorité)
        'bootcamp': ('https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=400&h=200&fit=crop', 60),
        'complete': ('https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=200&fit=crop', 30),
        'ultimate': ('https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=200&fit=crop', 30),
        'master': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 50),
        'beginner': ('https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=200&fit=crop', 30),
        'pro': ('https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=200&fit=crop', 40),
        'hands': ('https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=200&fit=crop', 40),
        'guide': ('https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=200&fit=crop', 40),
        'introduction': ('https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=200&fit=crop', 30),
        'brief': ('https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=200&fit=crop', 30),
        'fundamentals': ('https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=400&h=200&fit=crop', 50),
        'basics': ('https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=200&fit=crop', 30),
        'advanced': ('https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=200&fit=crop', 40),
        'course': ('https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=200&fit=crop', 20),
        'training': ('https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=200&fit=crop', 20),
        'class': ('https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=200&fit=crop', 25),
        'masterclass': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 50),
        'lessons': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 40),
        'skills': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 60),
        'skill': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 60),
        'team': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 60),
        'crash': ('https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=400&h=200&fit=crop', 50),
        'weekend': ('https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=400&h=200&fit=crop', 45),
        'story': ('https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=400&h=200&fit=crop', 50),
        'model': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 50),
        'process': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 55),
        'flowchart': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 55),
        'flowcharts': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 55),
        'mapping': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 55),
        'bundle': ('https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=200&fit=crop', 35),
        'personal': ('https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=400&h=200&fit=crop', 55),
        'product': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 60),
        'management': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 75),
        'solve': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 50),
        'solving': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 50),
        'consulting': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 70),
        'grow': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 50),
        'career': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 55),
        'certified': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 70),
        'essentials': ('https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=400&h=200&fit=crop', 40),
        'impress': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 55),
        'earn': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 45),
        'pdu': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 70),
        'get': ('https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=200&fit=crop', 20),
        'learn': ('https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=200&fit=crop', 25),
        'zero': ('https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=200&fit=crop', 30),
        'hero': ('https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=200&fit=crop', 30),
        'achieve': ('https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=400&h=200&fit=crop', 40),
        'wins': ('https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=400&h=200&fit=crop', 40),
        'blueprint': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 55),
        'proven': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 50),
        'mentor': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 65),
        'mentoring': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 65),
        'conflict': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 65),
        'differentiate': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 55),
        'understanding': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 50),
        'developing': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 50),
        'from': ('https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=200&fit=crop', 15),
        'chris': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 40),
        'seth': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 50),
        'start': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 40),
        'tight': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 35),
        'tame': ('https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=400&h=200&fit=crop', 40),
        'big': ('https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=400&h=200&fit=crop', 40),
        'examples': ('https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=400&h=200&fit=crop', 35),
        'live': ('https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=400&h=200&fit=crop', 35),
        'better': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 50),
        'work': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 35),
        'tactics': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 60),
        'smarter': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 40),
        'effective': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 45),
        'emails': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 65),
        'including': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 30),
        'four': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 30),
        'levels': ('https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=200&fit=crop', 35),
        'certified': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 70),
        'overview': ('https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=200&fit=crop', 35),
        'emotions': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 65),
        'work': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 40),
        'guide': ('https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=200&fit=crop', 40),
        'no': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 20),
        'home': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 35),
        'minutes': ('https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=200&fit=crop', 30),
        'build': ('https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=400&h=200&fit=crop', 50),
        'first': ('https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=200&fit=crop', 25),
        'analyzing': ('https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=400&h=200&fit=crop', 60),
        'investments': ('https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=400&h=200&fit=crop', 65),
        'communicate': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 65),
        'skills': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 60),
        'box': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 45),
        'lessons': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 50),
        'ceo': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 50),
        'full': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 30),
        'level': ('https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=200&fit=crop', 35),
        'empire': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 65),
        'scratch': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 50),
        'manage': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 55),
        'model': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 55),
        'introduction': ('https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=200&fit=crop', 30),
        'statement': ('https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=400&h=200&fit=crop', 70),
        'approach': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 55),
        'science': ('https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=400&h=200&fit=crop', 60),
        'strategies': ('https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=400&h=200&fit=crop', 60),
        'beginners': ('https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=200&fit=crop', 30),
        'deeply': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 40),
        'practical': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 55),
        'flex': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 50),
        'style': ('https://images.unsplash.com/photo-1561070791-2526d30994b5?w=400&h=200&fit=crop', 40),
        'delight': ('https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=200&fit=crop', 60),
        'understanding': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 50),
        'developing': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 50),
        'save': ('https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=400&h=200&fit=crop', 55),
        'protect': ('https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=400&h=200&fit=crop', 55),
        'make': ('https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=400&h=200&fit=crop', 40),
        '101': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 35),
        'bundle': ('https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=200&fit=crop', 40),
        'cert': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 65),
        'application': ('https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=200&fit=crop', 55),
        'bko': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 60),
        'accredited': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 65),
        'acumen': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 45),
        'presents': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 35),
        'anderson': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 40),
        'hours': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 55),
        'rep': ('https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', 60),
        

    }
    import re

    default_image = 'https://images.unsplash.com/photo-1516321318423-f06f70504504?w=400&h=200&fit=crop'
    
    def get_image_url(title):
        title_lower = str(title).lower()
        # Chercher TOUS les matches avec leurs priorités
        matches = []
        
        for key, (url, priority) in images_map.items():
            if key in title_lower:
                matches.append((priority, url))
        
        # Si on a des matches, retourner celui avec la priorité la plus élevée
        if matches:
            matches.sort(reverse=True, key=lambda x: x[0])
            return matches[0][1]
        
        # Par défaut
        return default_image
    images_map['investing'] = images_map['investment']   # pour "investing"
    images_map['financial'] = images_map['finance']      # pour "financial"
    images_map['analyst'] = images_map['analyst']        # déjà présent, mais à vérifierr des termes spécifiques 


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

    # Récupérer le paramètre de recherche
    query = request.args.get('q', '').strip()

    cols = ["id", "title", "avg_rating", "num_subscribers", "price_detail__amount", "image_url"]
    
    # Filtrer les cours selon la recherche
    if query:
        # Recherche dans le titre (insensible à la casse)
        filtered_df = df[df['title'].str.contains(query, case=False, na=False)]
        courses = filtered_df[cols].head(100).to_dict(orient="records")
    else:
        courses = df[cols].head(100).to_dict(orient="records")
    
    return render_template("index.html", courses=courses, query=query)

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