import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "segredo-local")

def get_conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"), sslmode='require')