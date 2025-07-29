from app import app

# Import routes after app creation to avoid circular imports
with app.app_context():
    import routes  # noqa: F401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
