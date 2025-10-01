from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import git
from datetime import datetime

app = Flask(__name__)
CORS(app)

ENTRIES_FOLDER = "entries"
if not os.path.exists(ENTRIES_FOLDER):
    os.makedirs(ENTRIES_FOLDER)

# Initialize repo
repo = git.Repo.init(ENTRIES_FOLDER)

# Route to get all entries
@app.route("/api/entries", methods=["GET"])
def get_entries():
    entries = []
    for filename in sorted(os.listdir(ENTRIES_FOLDER), reverse=True):
        if filename.endswith(".txt"):
            with open(os.path.join(ENTRIES_FOLDER, filename), "r") as f:
                content = f.read()
            entries.append({
                "filename": filename,
                "preview": content[:100] + ("..." if len(content) > 100 else "")
            })
    return jsonify(entries)

# Route to save a new entry
@app.route("/api/entry", methods=["POST"])
def save_entry():
    data = request.get_json()
    title = data.get("title", "Untitled")
    content = data.get("content", "")
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{now}_{title}.txt"
    filepath = os.path.join(ENTRIES_FOLDER, filename)
    with open(filepath, "w") as f:
        f.write(content)

    # Create a new branch for this entry
    branch_name = f"entry_{now}"
    if branch_name not in repo.branches:
        repo.git.checkout("-b", branch_name)

    # Commit
    repo.index.add([filepath])
    repo.index.commit(f"Journal Entry: {title} ({now})")

    # Switch back to main
    repo.git.checkout("main")

    return jsonify({"commit": f"Journal Entry: {title} saved on branch {branch_name}!"})

# Route to delete an entry
@app.route("/api/entry/<filename>", methods=["DELETE"])
def delete_entry(filename):
    filepath = os.path.join(ENTRIES_FOLDER, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        # Commit deletion
        repo.index.remove([filepath])
        repo.index.commit(f"Deleted entry: {filename}")
        return jsonify({"message": f"{filename} deleted!"})
    else:
        return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
