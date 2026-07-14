import os, json, urllib.request, urllib.error, random
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder=None)

PORT = int(os.environ.get("PORT", 5000))
DIR = os.path.dirname(os.path.abspath(__file__))

WORDS = [
    "Cool","Unique","Old","Okay","No","Roblox","Banana","Times","Hola","Happy","Lucky","Fast","Brave","Smart",
    "Wild","Calm","Dark","Gold","Ice","Fire","Star","Moon","Sun","Sky","Blue","Red","Big","Small","Hot","Cold",
    "New","Fresh","Bold","Kind","Pure","Sharp","Sweet","Soft","Warm","Crisp","Royal","Noble","Epic","Super",
    "Ultra","Mega","Alpha","Beta","Delta","Sigma","Omega","Pixel","Neon","Cyber","Hyper","Solar","Lunar","Nova",
    "Blaze","Storm","Thunder","Lightning","Crystal","Shadow","Spirit","Thunder","Eagle","Tiger","Wolf","Falcon",
    "Quest","Ridge","Peak","Valley","Forest","River","Stone","Steel","Iron","Copper","Silver","Diamond","Platinum"
]

sessions = {}
used_phrases = set()

def get_user_id(username):
    req = urllib.request.Request("https://users.roblox.com/v1/usernames/users")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "BloxyMe/1.0")
    data = json.dumps({"usernames": [username]}).encode()
    with urllib.request.urlopen(req, data, timeout=15) as r:
        resp = json.loads(r.read())
    if resp.get("data"):
        return resp["data"][0]["id"]
    req2 = urllib.request.Request(f"https://api.roblox.com/users/get-by-username?username={username}")
    req2.add_header("User-Agent", "BloxyMe/1.0")
    with urllib.request.urlopen(req2, timeout=15) as r2:
        resp2 = json.loads(r2.read())
    if resp2.get("Id"):
        return resp2["Id"]
    return None

def get_bio(user_id):
    req = urllib.request.Request(f"https://users.roblox.com/v1/users/{user_id}")
    req.add_header("User-Agent", "BloxyMe/1.0")
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())
    return data.get("description", "")

def get_avatar(user_id):
    req = urllib.request.Request(
        f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size=150x150&format=Png&isCircular=false")
    req.add_header("User-Agent", "BloxyMe/1.0")
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())
    if data.get("data"):
        return data["data"][0].get("imageUrl", "")
    return ""

@app.route("/")
def index():
    return send_from_directory(DIR, "index.html")

@app.route("/api/generate", methods=["POST"])
def api_generate():
    username = request.json.get("username", "").strip()
    if not username:
        return jsonify({"ok": False, "error": "No username"})
    uid = get_user_id(username)
    if not uid:
        return jsonify({"ok": False, "error": "User not found"})
    random.seed(str(random.random()) + username + str(random.random()))
    phrase = " ".join(random.choices(WORDS, k=8))
    while phrase in used_phrases:
        phrase = " ".join(random.choices(WORDS, k=8))
    used_phrases.add(phrase)
    sessions[uid] = {"phrase": phrase, "username": username}
    print(f"[+] {username} ({uid}): {phrase}")
    return jsonify({"ok": True, "phrase": phrase, "userId": uid})

@app.route("/api/verify", methods=["POST"])
def api_verify():
    uid = request.json.get("userId")
    if not uid or uid not in sessions:
        return jsonify({"ok": False, "error": "No phrase generated yet. Start again."})
    session = sessions[uid]
    try:
        bio = get_bio(uid)
    except Exception as e:
        return jsonify({"ok": False, "error": f"Could not fetch bio: {str(e)}"})
    if session["phrase"] in bio:
        avatar = get_avatar(uid)
        del sessions[uid]
        return jsonify({"ok": True, "user": {"id": uid, "username": session["username"], "avatar": avatar}})
    else:
        return jsonify({"ok": False, "error": "Phrase not found in your bio. Make sure you saved it!"})

@app.route("/api/logout", methods=["POST"])
def api_logout():
    return jsonify({"ok": True})

@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(DIR, filename)

if __name__ == "__main__":
    print(f"BloxyMe Server auf Port {PORT}")
    app.run(host="0.0.0.0", port=PORT)