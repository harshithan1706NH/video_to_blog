from flask import Flask, request, jsonify, session
from flask_cors import CORS
from db import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import subprocess
import os
import uuid

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY", "development-secret-key")

CORS(app, supports_credentials=True)

FFMPEG_PATH = "ffmpeg"
FFPROBE_PATH = "ffprobe"

MAX_VIDEO_DURATION = 30 * 60


@app.route("/")
def home():
    return "Backend is running!"


@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No registration data received"
        }), 400

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name:
        return jsonify({
            "success": False,
            "message": "Name is required"
        }), 400

    if not email:
        return jsonify({
            "success": False,
            "message": "Email is required"
        }), 400

    if not password:
        return jsonify({
            "success": False,
            "message": "Password is required"
        }), 400

    if len(password) < 6:
        return jsonify({
            "success": False,
            "message": "Password must be at least 6 characters long"
        }), 400

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT user_id FROM users WHERE email = %s",
            (email,)
        )

        if cursor.fetchone():
            return jsonify({
                "success": False,
                "message": "An account with this email already exists"
            }), 409

        password_hash = generate_password_hash(password)

        cursor.execute("""
            INSERT INTO users
            (name, email, password_hash)
            VALUES (%s, %s, %s)
            RETURNING user_id
        """, (name, email, password_hash))

        user_id = cursor.fetchone()[0]

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Registration successful",
            "user_id": user_id
        }), 201

    except Exception as e:
        if connection:
            connection.rollback()

        return jsonify({
            "success": False,
            "message": "Registration failed",
            "error": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No login data received"
        }), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Email and password are required"
        }), 400

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT user_id, name, email, password_hash
            FROM users
            WHERE email = %s
        """, (email,))

        user = cursor.fetchone()

        if not user:
            return jsonify({
                "success": False,
                "message": "Invalid email or password"
            }), 401

        user_id, name, stored_email, password_hash = user

        if not check_password_hash(password_hash, password):
            return jsonify({
                "success": False,
                "message": "Invalid email or password"
            }), 401

        session["user_id"] = user_id
        session["user_name"] = name
        session["user_email"] = stored_email

        return jsonify({
            "success": True,
            "message": "Login successful",
            "user": {
                "user_id": user_id,
                "name": name,
                "email": stored_email
            }
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Login failed",
            "error": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


@app.route("/session", methods=["GET"])
def get_session():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "success": False,
            "authenticated": False
        }), 401

    return jsonify({
        "success": True,
        "authenticated": True,
        "user": {
            "user_id": session.get("user_id"),
            "name": session.get("user_name"),
            "email": session.get("user_email")
        }
    }), 200


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()

    return jsonify({
        "success": True,
        "message": "Logged out successfully"
    }), 200


def get_video_duration(video_path):
    command = [
        FFPROBE_PATH,
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        video_path
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise Exception("Could not determine video duration")

    return float(result.stdout.strip())


def extract_audio(video_path, output_path):
    command = [
        FFMPEG_PATH,
        "-y",
        "-i",
        video_path,
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ar",
        "16000",
        "-ac",
        "1",
        output_path
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise Exception(
            f"Audio extraction failed: {result.stderr}"
        )


@app.route("/upload", methods=["POST"])
def upload_video():
    if not session.get("user_id"):
        return jsonify({
            "success": False,
            "message": "Please log in before uploading a video"
        }), 401

    if "video" not in request.files:
        return jsonify({
            "success": False,
            "message": "No video file received"
        }), 400

    video = request.files["video"]

    if video.filename == "":
        return jsonify({
            "success": False,
            "message": "No video file selected"
        }), 400

    filename = video.filename

    if not filename.lower().endswith(".mp4"):
        return jsonify({
            "success": False,
            "message": "Only MP4 videos are supported"
        }), 400

    backend_folder = os.path.dirname(os.path.abspath(__file__))

    upload_folder = os.path.join(
        backend_folder,
        "uploads"
    )

    processing_folder = os.path.join(
        backend_folder,
        "processing"
    )

    os.makedirs(upload_folder, exist_ok=True)
    os.makedirs(processing_folder, exist_ok=True)

    unique_id = str(uuid.uuid4())

    temp_path = os.path.join(
        upload_folder,
        f"{unique_id}.mp4"
    )

    audio_path = os.path.join(
        processing_folder,
        f"{unique_id}.wav"
    )

    connection = None
    cursor = None

    try:
        video.save(temp_path)

        duration = get_video_duration(temp_path)
        duration_seconds = int(round(duration))

        if duration_seconds > MAX_VIDEO_DURATION:
            os.remove(temp_path)

            return jsonify({
                "success": False,
                "message": "Video duration must not exceed 30 minutes",
                "duration_seconds": duration_seconds
            }), 400

        cloudinary_result = cloudinary.uploader.upload(
            temp_path,
            resource_type="video",
            folder="blog_videos"
        )

        video_url = cloudinary_result.get("secure_url")

        extract_audio(
            temp_path,
            audio_path
        )

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO videos
            (
                user_id,
                filename,
                format,
                duration_seconds,
                cloudinary_url
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING video_id, uploaded_at
        """, (
            session.get("user_id"),
            filename,
            "mp4",
            duration_seconds,
            video_url
        ))

        video_id, uploaded_at = cursor.fetchone()

        connection.commit()

        os.remove(temp_path)

        return jsonify({
            "success": True,
            "message": "Video uploaded and audio extracted successfully",
            "video": {
                "video_id": video_id,
                "filename": filename,
                "format": "mp4",
                "duration_seconds": duration_seconds,
                "cloudinary_url": video_url,
                "uploaded_at": uploaded_at.isoformat()
            },
            "audio_path": audio_path
        }), 200

    except Exception as e:
        if connection:
            connection.rollback()

        if os.path.exists(temp_path):
            os.remove(temp_path)

        if os.path.exists(audio_path):
            os.remove(audio_path)

        return jsonify({
            "success": False,
            "message": "Video processing failed",
            "error": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


if __name__ == "__main__":
    app.run(debug=True, port=5000)