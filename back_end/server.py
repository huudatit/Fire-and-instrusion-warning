from waitress import serve
from app import app  # ⚠️ Đảm bảo tên app trùng với Flask instance trong app.py

if __name__ == "__main__":
    print(" Production server running at http://0.0.0.0:5000")
    serve(app, host="0.0.0.0", port=5000)
