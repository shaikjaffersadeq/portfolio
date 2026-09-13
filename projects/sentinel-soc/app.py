from flask import Flask, render_template, request, jsonify
import sqlite3
import math
import re
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

DATABASE = "database/security_lab.db"


# ============================================================
# DEFENSE SETTINGS
# ============================================================

DEFAULT_RATE_LIMIT = 3
RATE_LIMIT_WINDOW = 10

BRUTE_FORCE_THRESHOLD = 5
BRUTE_FORCE_WINDOW = 60

LOCKOUT_DURATION = 60


# ============================================================
# COMMON PASSWORDS
# ============================================================

COMMON_PASSWORDS = {
    "password",
    "password123",
    "123456",
    "123456789",
    "12345678",
    "qwerty",
    "qwerty123",
    "admin",
    "admin123",
    "welcome",
    "welcome123",
    "letmein",
    "iloveyou",
    "abc123",
    "monkey",
    "dragon",
    "football",
    "master",
    "login"
}


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db_connection():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def initialize_database():

    connection = get_db_connection()

    cursor = connection.cursor()

    # --------------------------------------------------------
    # USERS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lab_users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT UNIQUE NOT NULL,

            password_hash TEXT NOT NULL,

            created_at TEXT NOT NULL

        )
    """)

    # --------------------------------------------------------
    # AUTHENTICATION EVENTS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS auth_events (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT NOT NULL,

            event_type TEXT NOT NULL,

            success INTEGER NOT NULL,

            timestamp TEXT NOT NULL

        )
    """)

    # --------------------------------------------------------
    # SECURITY ALERTS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS security_alerts (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            alert_type TEXT NOT NULL,

            severity TEXT NOT NULL,

            username TEXT NOT NULL,

            description TEXT NOT NULL,

            event_count INTEGER NOT NULL,

            timestamp TEXT NOT NULL,

            status TEXT NOT NULL

        )
    """)

    # --------------------------------------------------------
    # DEFENSE EVENTS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS defense_events (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT NOT NULL,

            defense_type TEXT NOT NULL,

            action TEXT NOT NULL,

            reason TEXT NOT NULL,

            timestamp TEXT NOT NULL

        )
    """)

    # --------------------------------------------------------
    # ACCOUNT SECURITY
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS account_security (

            username TEXT PRIMARY KEY,

            locked_until TEXT,

            failed_attempts INTEGER DEFAULT 0

        )
    """)

    # --------------------------------------------------------
    # DEFENSE SETTINGS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS defense_settings (

            id INTEGER PRIMARY KEY,

            rate_limiting INTEGER NOT NULL DEFAULT 1,

            account_lockout INTEGER NOT NULL DEFAULT 1

        )
    """)

    # --------------------------------------------------------
    # INCIDENTS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidents (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            alert_id INTEGER,

            incident_type TEXT NOT NULL,

            severity TEXT NOT NULL,

            username TEXT NOT NULL,

            description TEXT NOT NULL,

            event_count INTEGER NOT NULL,

            status TEXT NOT NULL,

            analyst_notes TEXT,

            response_action TEXT,

            created_at TEXT NOT NULL,

            updated_at TEXT NOT NULL,

            resolved_at TEXT,

            resolution_summary TEXT,

            closed_at TEXT,

            closure_reason TEXT

        )
    """)

    # --------------------------------------------------------
    # INCIDENT TIMELINE
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incident_timeline (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            incident_id INTEGER NOT NULL,

            action TEXT NOT NULL,

            details TEXT NOT NULL,

            timestamp TEXT NOT NULL

        )
    """)

    # --------------------------------------------------------
    # DATABASE MIGRATION
    # --------------------------------------------------------
    # Existing databases created by the previous version will
    # not automatically receive the new resolution/closure
    # columns. These ALTER TABLE statements safely add them
    # when necessary.
    # --------------------------------------------------------

    cursor.execute("""
        PRAGMA table_info(incidents)
    """)

    existing_columns = {
        row["name"]
        for row in cursor.fetchall()
    }

    if "resolution_summary" not in existing_columns:

        cursor.execute("""
            ALTER TABLE incidents
            ADD COLUMN resolution_summary TEXT
        """)

    if "closed_at" not in existing_columns:

        cursor.execute("""
            ALTER TABLE incidents
            ADD COLUMN closed_at TEXT
        """)

    if "closure_reason" not in existing_columns:

        cursor.execute("""
            ALTER TABLE incidents
            ADD COLUMN closure_reason TEXT
        """)

    # --------------------------------------------------------
    # DEFAULT DEFENSE SETTINGS
    # --------------------------------------------------------

    cursor.execute("""
        INSERT OR IGNORE INTO defense_settings
        (
            id,
            rate_limiting,
            account_lockout
        )

        VALUES (1, 1, 1)
    """)

    # --------------------------------------------------------
    # DEFAULT LAB USER
    # --------------------------------------------------------

    cursor.execute(
        "SELECT id FROM lab_users WHERE username = ?",
        ("lab_user",)
    )

    user = cursor.fetchone()

    if user is None:

        password_hash = generate_password_hash(
            "LabPass@123"
        )

        cursor.execute("""
            INSERT INTO lab_users
            (
                username,
                password_hash,
                created_at
            )

            VALUES (?, ?, ?)
        """, (
            "lab_user",
            password_hash,
            datetime.now().isoformat(
                timespec="seconds"
            )
        ))

    # --------------------------------------------------------
    # ACCOUNT SECURITY RECORD
    # --------------------------------------------------------

    cursor.execute("""
        INSERT OR IGNORE INTO account_security
        (
            username,
            locked_until,
            failed_attempts
        )

        VALUES (?, NULL, 0)
    """, ("lab_user",))

    connection.commit()

    connection.close()


# ============================================================
# PASSWORD ANALYSIS
# ============================================================

def contains_sequential_pattern(password):

    if len(password) < 3:

        return False

    for i in range(len(password) - 2):

        part = password[i:i + 3]

        if part.isdigit():

            values = [
                int(character)
                for character in part
            ]

            if (
                values[1] == values[0] + 1
                and values[2] == values[1] + 1
            ):

                return True

            if (
                values[1] == values[0] - 1
                and values[2] == values[1] - 1
            ):

                return True

        if part.isalpha():

            values = [
                ord(character.lower())
                for character in part
            ]

            if (
                values[1] == values[0] + 1
                and values[2] == values[1] + 1
            ):

                return True

            if (
                values[1] == values[0] - 1
                and values[2] == values[1] - 1
            ):

                return True

    return False


def contains_repeated_characters(password):

    return bool(
        re.search(r"(.)\1\1", password)
    )


def calculate_entropy(password, character_pool):

    if not password or character_pool == 0:

        return 0

    return len(password) * math.log2(
        character_pool
    )


def analyze_password(password):

    if not password:

        return {
            "score": 0,
            "strength": "EMPTY",
            "risk": "HIGH",
            "entropy": 0,
            "length": 0,
            "checks": {
                "length": False,
                "lowercase": False,
                "uppercase": False,
                "numbers": False,
                "special": False,
                "common": False,
                "sequential": False,
                "repeated": False
            },
            "recommendations": [
                "Enter a password to begin the security analysis."
            ]
        }

    length = len(password)

    has_lowercase = bool(
        re.search(r"[a-z]", password)
    )

    has_uppercase = bool(
        re.search(r"[A-Z]", password)
    )

    has_numbers = bool(
        re.search(r"[0-9]", password)
    )

    has_special = bool(
        re.search(r"[^A-Za-z0-9]", password)
    )

    normalized = password.lower()

    is_common = (
        normalized in COMMON_PASSWORDS
    )

    sequential = contains_sequential_pattern(
        password
    )

    repeated = contains_repeated_characters(
        password
    )

    character_pool = 0

    if has_lowercase:

        character_pool += 26

    if has_uppercase:

        character_pool += 26

    if has_numbers:

        character_pool += 10

    if has_special:

        character_pool += 32

    entropy = calculate_entropy(
        password,
        character_pool
    )

    score = 0

    if length >= 8:

        score += 15

    if length >= 12:

        score += 15

    if length >= 16:

        score += 10

    if has_lowercase:

        score += 10

    if has_uppercase:

        score += 10

    if has_numbers:

        score += 10

    if has_special:

        score += 10

    if entropy >= 40:

        score += 5

    if entropy >= 60:

        score += 5

    if is_common:

        score -= 35

    if sequential:

        score -= 10

    if repeated:

        score -= 10

    score = max(
        0,
        min(100, score)
    )

    if score < 30:

        strength = "WEAK"

        risk = "HIGH"

    elif score < 55:

        strength = "MODERATE"

        risk = "MEDIUM"

    elif score < 75:

        strength = "STRONG"

        risk = "LOW"

    else:

        strength = "VERY STRONG"

        risk = "LOW"

    recommendations = []

    if length < 12:

        recommendations.append(
            "Use at least 12 characters."
        )

    if not has_lowercase:

        recommendations.append(
            "Add lowercase letters."
        )

    if not has_uppercase:

        recommendations.append(
            "Add uppercase letters."
        )

    if not has_numbers:

        recommendations.append(
            "Add numbers."
        )

    if not has_special:

        recommendations.append(
            "Add special characters."
        )

    if is_common:

        recommendations.append(
            "Avoid commonly used passwords."
        )

    if sequential:

        recommendations.append(
            "Avoid sequential patterns."
        )

    if repeated:

        recommendations.append(
            "Avoid repeated characters."
        )

    if not recommendations:

        recommendations.append(
            "Password has good complexity characteristics."
        )

    return {

        "score": score,

        "strength": strength,

        "risk": risk,

        "entropy": round(
            entropy,
            1
        ),

        "length": length,

        "checks": {

            "length":
                length >= 12,

            "lowercase":
                has_lowercase,

            "uppercase":
                has_uppercase,

            "numbers":
                has_numbers,

            "special":
                has_special,

            "common":
                not is_common,

            "sequential":
                not sequential,

            "repeated":
                not repeated
        },

        "recommendations":
            recommendations
    }


# ============================================================
# DEFENSE SETTINGS
# ============================================================

def get_defense_settings():

    connection = get_db_connection()

    settings = connection.execute("""
        SELECT
            rate_limiting,
            account_lockout

        FROM defense_settings

        WHERE id = 1
    """).fetchone()

    connection.close()

    return {

        "rate_limiting":
            bool(settings["rate_limiting"]),

        "account_lockout":
            bool(settings["account_lockout"])
    }


# ============================================================
# RECORD DEFENSE EVENT
# ============================================================

def record_defense_event(
    username,
    defense_type,
    action,
    reason
):

    connection = get_db_connection()

    connection.execute("""
        INSERT INTO defense_events
        (
            username,
            defense_type,
            action,
            reason,
            timestamp
        )

        VALUES (?, ?, ?, ?, ?)
    """, (

        username,

        defense_type,

        action,

        reason,

        datetime.now().isoformat(
            timespec="seconds"
        )
    ))

    connection.commit()

    connection.close()


# ============================================================
# RATE LIMIT
# ============================================================

def check_rate_limit(username):

    settings = get_defense_settings()

    if not settings["rate_limiting"]:

        return {
            "allowed": True,
            "count": 0
        }

    connection = get_db_connection()

    cutoff = (
        datetime.now()
        - timedelta(
            seconds=RATE_LIMIT_WINDOW
        )
    ).isoformat(
        timespec="seconds"
    )

    result = connection.execute("""
        SELECT COUNT(*) AS count

        FROM auth_events

        WHERE username = ?

        AND timestamp >= ?
    """, (

        username,

        cutoff

    )).fetchone()

    connection.close()

    count = result["count"]

    if count >= DEFAULT_RATE_LIMIT:

        record_defense_event(

            username,

            "RATE_LIMIT",

            "BLOCK",

            (
                f"More than "
                f"{DEFAULT_RATE_LIMIT} "
                "authentication attempts "
                f"occurred within "
                f"{RATE_LIMIT_WINDOW} seconds."
            )
        )

        return {

            "allowed": False,

            "count": count
        }

    return {

        "allowed": True,

        "count": count
    }


# ============================================================
# ACCOUNT LOCK CHECK
# ============================================================

def check_account_lock(username):

    settings = get_defense_settings()

    if not settings["account_lockout"]:

        return {

            "locked": False,

            "locked_until": None
        }

    connection = get_db_connection()

    security = connection.execute("""
        SELECT
            locked_until

        FROM account_security

        WHERE username = ?
    """, (
        username,
    )).fetchone()

    if not security:

        connection.close()

        return {

            "locked": False,

            "locked_until": None
        }

    locked_until = security[
        "locked_until"
    ]

    if locked_until:

        lock_time = datetime.fromisoformat(
            locked_until
        )

        if datetime.now() < lock_time:

            connection.close()

            return {

                "locked": True,

                "locked_until":
                    locked_until
            }

        connection.execute("""
            UPDATE account_security

            SET locked_until = NULL,

                failed_attempts = 0

            WHERE username = ?
        """, (
            username,
        ))

        connection.commit()

    connection.close()

    return {

        "locked": False,

        "locked_until": None
    }


# ============================================================
# FAILED ATTEMPT
# ============================================================

def register_failed_attempt(username):

    connection = get_db_connection()

    security = connection.execute("""
        SELECT
            failed_attempts

        FROM account_security

        WHERE username = ?
    """, (
        username,
    )).fetchone()

    if security:

        failed_attempts = (
            security["failed_attempts"] + 1
        )

        connection.execute("""
            UPDATE account_security

            SET failed_attempts = ?

            WHERE username = ?
        """, (

            failed_attempts,

            username
        ))

    else:

        failed_attempts = 1

        connection.execute("""
            INSERT INTO account_security
            (
                username,
                locked_until,
                failed_attempts
            )

            VALUES (?, NULL, ?)
        """, (

            username,

            failed_attempts
        ))

    connection.commit()

    connection.close()

    return failed_attempts


# ============================================================
# APPLY LOCKOUT
# ============================================================

def apply_lockout(
    username,
    failed_attempts
):

    settings = get_defense_settings()

    if not settings["account_lockout"]:

        return False

    if failed_attempts < BRUTE_FORCE_THRESHOLD:

        return False

    locked_until = (

        datetime.now()

        + timedelta(
            seconds=LOCKOUT_DURATION
        )

    ).isoformat(
        timespec="seconds"
    )

    connection = get_db_connection()

    connection.execute("""
        UPDATE account_security

        SET locked_until = ?,

            failed_attempts = 0

        WHERE username = ?
    """, (

        locked_until,

        username
    ))

    connection.commit()

    connection.close()

    record_defense_event(

        username,

        "ACCOUNT_LOCKOUT",

        "LOCK",

        (
            f"{failed_attempts} failed "
            "authentication attempts "
            f"triggered a "
            f"{LOCKOUT_DURATION}-second "
            "account lockout."
        )
    )

    return True


# ============================================================
# BRUTE FORCE DETECTION
# ============================================================

def detect_bruteforce(username):

    connection = get_db_connection()

    cutoff = (

        datetime.now()

        - timedelta(
            seconds=BRUTE_FORCE_WINDOW
        )

    ).isoformat(
        timespec="seconds"
    )

    failed_events = connection.execute("""
        SELECT COUNT(*) AS count

        FROM auth_events

        WHERE username = ?

        AND event_type = 'LOGIN_FAILURE'

        AND timestamp >= ?
    """, (

        username,

        cutoff

    )).fetchone()

    failure_count = failed_events[
        "count"
    ]

    alert_created = False

    alert_id = None

    if failure_count >= BRUTE_FORCE_THRESHOLD:

        existing_alert = connection.execute("""
            SELECT id

            FROM security_alerts

            WHERE username = ?

            AND alert_type = 'BRUTE_FORCE_PATTERN'

            AND timestamp >= ?

            ORDER BY id DESC

            LIMIT 1
        """, (

            username,

            cutoff

        )).fetchone()

        if existing_alert is None:

            description = (

                f"{failure_count} failed "

                "authentication attempts "

                "detected within 60 seconds."
            )

            cursor = connection.execute("""
                INSERT INTO security_alerts
                (
                    alert_type,
                    severity,
                    username,
                    description,
                    event_count,
                    timestamp,
                    status
                )

                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (

                "BRUTE_FORCE_PATTERN",

                "HIGH",

                username,

                description,

                failure_count,

                datetime.now().isoformat(
                    timespec="seconds"
                ),

                "OPEN"
            ))

            alert_id = cursor.lastrowid

            alert_created = True

    connection.commit()

    connection.close()

    return {

        "detected":
            failure_count >=
            BRUTE_FORCE_THRESHOLD,

        "failure_count":
            failure_count,

        "alert_created":
            alert_created,

        "alert_id":
            alert_id
    }


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ============================================================
# LOGIN PAGE
# ============================================================

@app.route("/login")
def login_page():

    return render_template(
        "login.html"
    )


# ============================================================
# ATTACK PAGE
# ============================================================

@app.route("/attack")
def attack_page():

    return render_template(
        "attack.html"
    )


# ============================================================
# DEFENSE PAGE
# ============================================================

@app.route("/defense")
def defense_page():

    return render_template(
        "defense.html"
    )


# ============================================================
# SOC DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard_page():

    return render_template(
        "dashboard.html"
    )


# ============================================================
# INCIDENT RESPONSE PAGE
# ============================================================

@app.route("/incidents")
def incidents_page():

    return render_template(
        "incidents.html"
    )


# ============================================================
# PASSWORD ANALYZER API
# ============================================================

@app.route(
    "/api/analyze-password",
    methods=["POST"]
)
def analyze_password_api():

    data = request.get_json(
        silent=True
    )

    if not data or "password" not in data:

        return jsonify({
            "error":
                "Password field is required."
        }), 400

    password = data.get(
        "password",
        ""
    )

    if not isinstance(
        password,
        str
    ):

        return jsonify({
            "error":
                "Password must be text."
        }), 400

    if len(password) > 256:

        return jsonify({
            "error":
                "Password is too long."
        }), 400

    return jsonify(
        analyze_password(password)
    )


# ============================================================
# LAB LOGIN API
# ============================================================

@app.route(
    "/api/lab-login",
    methods=["POST"]
)
def lab_login():

    data = request.get_json(
        silent=True
    )

    if not data:

        return jsonify({
            "error":
                "Invalid request."
        }), 400

    username = data.get(
        "username",
        ""
    )

    password = data.get(
        "password",
        ""
    )

    if not username or not password:

        return jsonify({
            "error":
                "Username and password are required."
        }), 400

    # --------------------------------------------------------
    # ACCOUNT LOCK
    # --------------------------------------------------------

    lock_status = check_account_lock(
        username
    )

    if lock_status["locked"]:

        return jsonify({

            "success": False,

            "blocked": True,

            "reason":
                "ACCOUNT_LOCKED",

            "message":
                "Authentication blocked. "
                "Laboratory account is currently locked.",

            "locked_until":
                lock_status[
                    "locked_until"
                ]

        }), 423

    # --------------------------------------------------------
    # RATE LIMIT
    # --------------------------------------------------------

    rate_status = check_rate_limit(
        username
    )

    if not rate_status["allowed"]:

        return jsonify({

            "success": False,

            "blocked": True,

            "reason":
                "RATE_LIMITED",

            "message":
                "Authentication request blocked "
                "by the laboratory rate limiter.",

            "attempts_in_window":
                rate_status["count"]

        }), 429

    # --------------------------------------------------------
    # VERIFY USER
    # --------------------------------------------------------

    connection = get_db_connection()

    user = connection.execute("""
        SELECT *

        FROM lab_users

        WHERE username = ?
    """, (
        username,
    )).fetchone()

    success = False

    if user:

        success = check_password_hash(

            user["password_hash"],

            password
        )

    if success:

        event_type = "LOGIN_SUCCESS"

    else:

        event_type = "LOGIN_FAILURE"

    # --------------------------------------------------------
    # RECORD EVENT
    # --------------------------------------------------------

    connection.execute("""
        INSERT INTO auth_events
        (
            username,
            event_type,
            success,
            timestamp
        )

        VALUES (?, ?, ?, ?)
    """, (

        username,

        event_type,

        1 if success else 0,

        datetime.now().isoformat(
            timespec="seconds"
        )
    ))

    connection.commit()

    connection.close()

    # --------------------------------------------------------
    # SUCCESS
    # --------------------------------------------------------

    if success:

        return jsonify({

            "success": True,

            "blocked": False,

            "message":
                "Laboratory authentication successful.",

            "event":
                event_type
        })

    # --------------------------------------------------------
    # FAILURE
    # --------------------------------------------------------

    failed_attempts = (
        register_failed_attempt(
            username
        )
    )

    detection = detect_bruteforce(
        username
    )

    locked = apply_lockout(

        username,

        failed_attempts
    )

    if locked:

        return jsonify({

            "success": False,

            "blocked": True,

            "reason":
                "ACCOUNT_LOCKED",

            "message":
                "Brute-force threshold reached. "
                "Laboratory account has been locked.",

            "failed_attempts":
                failed_attempts,

            "detection":
                detection

        }), 423

    return jsonify({

        "success": False,

        "blocked": False,

        "message":
            "Authentication failed.",

        "event":
            event_type,

        "failed_attempts":
            failed_attempts,

        "detection":
            detection
    })


# ============================================================
# AUTH EVENTS API
# ============================================================

@app.route("/api/auth-events")
def auth_events():

    connection = get_db_connection()

    events = connection.execute("""
        SELECT
            id,
            username,
            event_type,
            success,
            timestamp

        FROM auth_events

        ORDER BY id DESC

        LIMIT 50
    """).fetchall()

    connection.close()

    return jsonify([
        dict(event)
        for event in events
    ])


# ============================================================
# SECURITY ALERTS API
# ============================================================

@app.route("/api/security-alerts")
def security_alerts():

    connection = get_db_connection()

    alerts = connection.execute("""
        SELECT
            id,
            alert_type,
            severity,
            username,
            description,
            event_count,
            timestamp,
            status

        FROM security_alerts

        ORDER BY id DESC

        LIMIT 50
    """).fetchall()

    connection.close()

    return jsonify([
        dict(alert)
        for alert in alerts
    ])


# ============================================================
# DETECTION STATUS API
# ============================================================

@app.route("/api/detection-status")
def detection_status():

    connection = get_db_connection()

    total_events = connection.execute("""
        SELECT COUNT(*) AS count

        FROM auth_events
    """).fetchone()["count"]

    failed_events = connection.execute("""
        SELECT COUNT(*) AS count

        FROM auth_events

        WHERE event_type = 'LOGIN_FAILURE'
    """).fetchone()["count"]

    successful_events = connection.execute("""
        SELECT COUNT(*) AS count

        FROM auth_events

        WHERE event_type = 'LOGIN_SUCCESS'
    """).fetchone()["count"]

    total_alerts = connection.execute("""
        SELECT COUNT(*) AS count

        FROM security_alerts
    """).fetchone()["count"]

    open_alerts = connection.execute("""
        SELECT COUNT(*) AS count

        FROM security_alerts

        WHERE status = 'OPEN'
    """).fetchone()["count"]

    connection.close()

    return jsonify({

        "total_events":
            total_events,

        "failed_events":
            failed_events,

        "successful_events":
            successful_events,

        "total_alerts":
            total_alerts,

        "open_alerts":
            open_alerts
    })


# ============================================================
# DEFENSE SETTINGS API
# ============================================================

@app.route("/api/defense-settings")
def defense_settings():

    return jsonify(
        get_defense_settings()
    )


@app.route(
    "/api/defense-settings",
    methods=["POST"]
)
def update_defense_settings():

    data = request.get_json(
        silent=True
    )

    if not data:

        return jsonify({
            "error":
                "Invalid request."
        }), 400

    rate_limiting = bool(
        data.get(
            "rate_limiting",
            True
        )
    )

    account_lockout = bool(
        data.get(
            "account_lockout",
            True
        )
    )

    connection = get_db_connection()

    connection.execute("""
        UPDATE defense_settings

        SET rate_limiting = ?,

            account_lockout = ?

        WHERE id = 1
    """, (

        1 if rate_limiting else 0,

        1 if account_lockout else 0
    ))

    connection.commit()

    connection.close()

    return jsonify({

        "success": True,

        "rate_limiting":
            rate_limiting,

        "account_lockout":
            account_lockout
    })


# ============================================================
# DEFENSE EVENTS API
# ============================================================

@app.route("/api/defense-events")
def defense_events():

    connection = get_db_connection()

    events = connection.execute("""
        SELECT
            id,
            username,
            defense_type,
            action,
            reason,
            timestamp

        FROM defense_events

        ORDER BY id DESC

        LIMIT 50
    """).fetchall()

    connection.close()

    return jsonify([
        dict(event)
        for event in events
    ])


# ============================================================
# ACCOUNT SECURITY API
# ============================================================

@app.route(
    "/api/account-security/<username>"
)
def account_security(username):

    connection = get_db_connection()

    security = connection.execute("""
        SELECT
            username,
            locked_until,
            failed_attempts

        FROM account_security

        WHERE username = ?
    """, (
        username,
    )).fetchone()

    connection.close()

    if not security:

        return jsonify({

            "error":
                "Account not found."

        }), 404

    locked = False

    locked_until = security[
        "locked_until"
    ]

    if locked_until:

        try:

            locked = (

                datetime.now()

                < datetime.fromisoformat(
                    locked_until
                )
            )

        except ValueError:

            locked = False

    return jsonify({

        "username":
            security["username"],

        "locked":
            locked,

        "locked_until":
            locked_until,

        "failed_attempts":
            security["failed_attempts"]
    })


# ============================================================
# INCIDENT API — LIST INCIDENTS
# ============================================================

@app.route("/api/incidents")
def get_incidents():

    connection = get_db_connection()

    incidents = connection.execute("""
        SELECT
            id,
            alert_id,
            incident_type,
            severity,
            username,
            description,
            event_count,
            status,
            analyst_notes,
            response_action,
            created_at,
            updated_at,
            resolved_at,
            resolution_summary,
            closed_at,
            closure_reason

        FROM incidents

        ORDER BY id DESC

        LIMIT 100
    """).fetchall()

    connection.close()

    return jsonify([
        dict(incident)
        for incident in incidents
    ])


# ============================================================
# INCIDENT API — CREATE INCIDENT FROM ALERT
# ============================================================

@app.route(
    "/api/incidents",
    methods=["POST"]
)
def create_incident():

    data = request.get_json(
        silent=True
    )

    if not data:

        return jsonify({
            "error":
                "Invalid request."
        }), 400

    alert_id = data.get(
        "alert_id"
    )

    if not alert_id:

        return jsonify({
            "error":
                "alert_id is required."
        }), 400

    connection = get_db_connection()

    alert = connection.execute("""
        SELECT *

        FROM security_alerts

        WHERE id = ?
    """, (
        alert_id,
    )).fetchone()

    if not alert:

        connection.close()

        return jsonify({
            "error":
                "Security alert not found."
        }), 404

    # --------------------------------------------------------
    # PREVENT DUPLICATE INCIDENT
    # --------------------------------------------------------

    existing = connection.execute("""
        SELECT id

        FROM incidents

        WHERE alert_id = ?

        LIMIT 1
    """, (
        alert_id,
    )).fetchone()

    if existing:

        connection.close()

        return jsonify({

            "success": True,

            "message":
                "Incident already exists.",

            "incident_id":
                existing["id"]
        })


    now = datetime.now().isoformat(
        timespec="seconds"
    )

    # --------------------------------------------------------
    # CREATE INCIDENT
    # --------------------------------------------------------

    cursor = connection.execute("""
        INSERT INTO incidents
        (
            alert_id,
            incident_type,
            severity,
            username,
            description,
            event_count,
            status,
            analyst_notes,
            response_action,
            created_at,
            updated_at,
            resolved_at,
            resolution_summary,
            closed_at,
            closure_reason
        )

        VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?
        )
    """, (

        alert["id"],

        alert["alert_type"],

        alert["severity"],

        alert["username"],

        alert["description"],

        alert["event_count"],

        "OPEN",

        "",

        "",

        now,

        now,

        None,

        "",

        None,

        ""
    ))

    incident_id = cursor.lastrowid

    # --------------------------------------------------------
    # TIMELINE ENTRY
    # --------------------------------------------------------

    connection.execute("""
        INSERT INTO incident_timeline
        (
            incident_id,
            action,
            details,
            timestamp
        )

        VALUES (?, ?, ?, ?)
    """, (

        incident_id,

        "INCIDENT_CREATED",

        (
            "Incident created from "
            f"security alert #{alert['id']}."
        ),

        now
    ))

    # --------------------------------------------------------
    # UPDATE ALERT STATUS
    # --------------------------------------------------------

    connection.execute("""
        UPDATE security_alerts

        SET status = 'INCIDENT_CREATED'

        WHERE id = ?
    """, (
        alert_id,
    ))

    connection.commit()

    connection.close()

    return jsonify({

        "success": True,

        "message":
            "Incident created successfully.",

        "incident_id":
            incident_id

    }), 201


# ============================================================
# INCIDENT API — UPDATE INCIDENT
# ============================================================

@app.route(
    "/api/incidents/<int:incident_id>",
    methods=["PUT"]
)
def update_incident(incident_id):

    data = request.get_json(
        silent=True
    )

    if not data:

        return jsonify({
            "error":
                "Invalid request."
        }), 400

    connection = get_db_connection()

    incident = connection.execute("""
        SELECT *

        FROM incidents

        WHERE id = ?
    """, (
        incident_id,
    )).fetchone()

    if not incident:

        connection.close()

        return jsonify({
            "error":
                "Incident not found."
        }), 404

    old_status = incident[
        "status"
    ]

    status = data.get(
        "status",
        old_status
    )

    allowed_statuses = {
        "OPEN",
        "INVESTIGATING",
        "RESOLVED",
        "CLOSED"
    }

    if status not in allowed_statuses:

        connection.close()

        return jsonify({

            "error":
                "Invalid incident status."

        }), 400

    severity = data.get(
        "severity",
        incident["severity"]
    )

    allowed_severities = {
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL"
    }

    if severity not in allowed_severities:

        connection.close()

        return jsonify({

            "error":
                "Invalid severity."

        }), 400

    analyst_notes = data.get(
        "analyst_notes",
        incident["analyst_notes"] or ""
    )

    response_action = data.get(
        "response_action",
        incident["response_action"] or ""
    )

    resolution_summary = data.get(
        "resolution_summary",
        incident["resolution_summary"] or ""
    )

    closure_reason = data.get(
        "closure_reason",
        incident["closure_reason"] or ""
    )

    now = datetime.now().isoformat(
        timespec="seconds"
    )

    resolved_at = incident[
        "resolved_at"
    ]

    closed_at = incident[
        "closed_at"
    ]

    # --------------------------------------------------------
    # RESOLUTION
    # --------------------------------------------------------

    if status == "RESOLVED":

        if not resolution_summary.strip():

            connection.close()

            return jsonify({

                "error":
                    "Resolution summary is required "
                    "before resolving the incident."

            }), 400

        if not resolved_at:

            resolved_at = now

        closed_at = None

    # --------------------------------------------------------
    # CLOSURE
    # --------------------------------------------------------

    elif status == "CLOSED":

        if old_status != "RESOLVED" and not resolved_at:

            connection.close()

            return jsonify({

                "error":
                    "Incident must be resolved "
                    "before it can be closed."

            }), 400

        if not closure_reason.strip():

            connection.close()

            return jsonify({

                "error":
                    "Closure reason is required "
                    "before closing the incident."

            }), 400

        if not resolved_at:

            resolved_at = now

        if not closed_at:

            closed_at = now

    else:

        resolved_at = None

        closed_at = None

    # --------------------------------------------------------
    # UPDATE DATABASE
    # --------------------------------------------------------

    connection.execute("""
        UPDATE incidents

        SET severity = ?,

            status = ?,

            analyst_notes = ?,

            response_action = ?,

            updated_at = ?,

            resolved_at = ?,

            resolution_summary = ?,

            closed_at = ?,

            closure_reason = ?

        WHERE id = ?
    """, (

        severity,

        status,

        analyst_notes,

        response_action,

        now,

        resolved_at,

        resolution_summary,

        closed_at,

        closure_reason,

        incident_id
    ))

    # --------------------------------------------------------
    # TIMELINE — STATUS CHANGE
    # --------------------------------------------------------

    if status != old_status:

        connection.execute("""
            INSERT INTO incident_timeline
            (
                incident_id,
                action,
                details,
                timestamp
            )

            VALUES (?, ?, ?, ?)
        """, (

            incident_id,

            "STATUS_CHANGED",

            (
                f"Incident status changed "
                f"from {old_status} "
                f"to {status}."
            ),

            now
        ))

    # --------------------------------------------------------
    # TIMELINE — ANALYST NOTES
    # --------------------------------------------------------

    if analyst_notes:

        connection.execute("""
            INSERT INTO incident_timeline
            (
                incident_id,
                action,
                details,
                timestamp
            )

            VALUES (?, ?, ?, ?)
        """, (

            incident_id,

            "ANALYST_NOTE",

            analyst_notes,

            now
        ))

    # --------------------------------------------------------
    # TIMELINE — RESPONSE
    # --------------------------------------------------------

    if response_action:

        connection.execute("""
            INSERT INTO incident_timeline
            (
                incident_id,
                action,
                details,
                timestamp
            )

            VALUES (?, ?, ?, ?)
        """, (

            incident_id,

            "RESPONSE_ACTION",

            response_action,

            now
        ))

    # --------------------------------------------------------
    # TIMELINE — RESOLUTION
    # --------------------------------------------------------

    if (
        status == "RESOLVED"
        and resolution_summary
    ):

        connection.execute("""
            INSERT INTO incident_timeline
            (
                incident_id,
                action,
                details,
                timestamp
            )

            VALUES (?, ?, ?, ?)
        """, (

            incident_id,

            "INCIDENT_RESOLVED",

            resolution_summary,

            now
        ))

    # --------------------------------------------------------
    # TIMELINE — CLOSURE
    # --------------------------------------------------------

    if (
        status == "CLOSED"
        and closure_reason
    ):

        connection.execute("""
            INSERT INTO incident_timeline
            (
                incident_id,
                action,
                details,
                timestamp
            )

            VALUES (?, ?, ?, ?)
        """, (

            incident_id,

            "INCIDENT_CLOSED",

            closure_reason,

            now
        ))

    connection.commit()

    connection.close()

    return jsonify({

        "success": True,

        "message":
            "Incident updated successfully.",

        "incident_id":
            incident_id,

        "status":
            status,

        "resolved_at":
            resolved_at,

        "closed_at":
            closed_at
    })


# ============================================================
# INCIDENT TIMELINE API
# ============================================================

@app.route(
    "/api/incidents/<int:incident_id>/timeline"
)
def incident_timeline(incident_id):

    connection = get_db_connection()

    incident = connection.execute("""
        SELECT id

        FROM incidents

        WHERE id = ?
    """, (
        incident_id,
    )).fetchone()

    if not incident:

        connection.close()

        return jsonify({
            "error":
                "Incident not found."
        }), 404

    timeline = connection.execute("""
        SELECT
            id,
            incident_id,
            action,
            details,
            timestamp

        FROM incident_timeline

        WHERE incident_id = ?

        ORDER BY id ASC
    """, (
        incident_id,
    )).fetchall()

    connection.close()

    return jsonify([
        dict(event)
        for event in timeline
    ])

# ============================================================
# APPLICATION INFORMATION API
# ============================================================

@app.route("/api/application-info")
def application_info():

    return jsonify({

        "application":
            "SENTINEL SOC",

        "version":
            "2.0",

        "description":
            "Security Operations Center and "
            "Incident Response Laboratory",

        "modules": [

            "Authentication Monitoring",

            "Brute Force Detection",

            "Security Alert Generation",

            "Defense Controls",

            "Incident Management",

            "Incident Investigation",

            "Incident Response",

            "Incident Resolution",

            "Incident Closure",

            "Incident Timeline and Audit History"

        ]

    })


# ============================================================
# INCIDENT STATISTICS API
# ============================================================

@app.route("/api/incident-statistics")
def incident_statistics():

    connection = get_db_connection()

    total = connection.execute("""
        SELECT COUNT(*) AS count
        FROM incidents
    """).fetchone()["count"]

    open_count = connection.execute("""
        SELECT COUNT(*) AS count
        FROM incidents
        WHERE status = 'OPEN'
    """).fetchone()["count"]

    investigating = connection.execute("""
        SELECT COUNT(*) AS count
        FROM incidents
        WHERE status = 'INVESTIGATING'
    """).fetchone()["count"]

    resolved = connection.execute("""
        SELECT COUNT(*) AS count
        FROM incidents
        WHERE status = 'RESOLVED'
    """).fetchone()["count"]

    closed = connection.execute("""
        SELECT COUNT(*) AS count
        FROM incidents
        WHERE status = 'CLOSED'
    """).fetchone()["count"]

    high_severity = connection.execute("""
        SELECT COUNT(*) AS count
        FROM incidents
        WHERE severity IN ('HIGH', 'CRITICAL')
    """).fetchone()["count"]

    connection.close()

    return jsonify({

        "total":
            total,

        "open":
            open_count,

        "investigating":
            investigating,

        "resolved":
            resolved,

        "closed":
            closed,

        "high_severity":
            high_severity

    })


# ============================================================
# RESOLVED INCIDENTS API
# ============================================================

@app.route("/api/incidents/resolved")
def resolved_incidents():

    connection = get_db_connection()

    incidents = connection.execute("""
        SELECT
            id,
            alert_id,
            incident_type,
            severity,
            username,
            description,
            event_count,
            status,
            analyst_notes,
            response_action,
            created_at,
            updated_at,
            resolved_at,
            resolution_summary,
            closed_at,
            closure_reason

        FROM incidents

        WHERE status = 'RESOLVED'

        ORDER BY resolved_at DESC
    """).fetchall()

    connection.close()

    return jsonify([
        dict(incident)
        for incident in incidents
    ])


# ============================================================
# CLOSED INCIDENTS API
# ============================================================

@app.route("/api/incidents/closed")
def closed_incidents():

    connection = get_db_connection()

    incidents = connection.execute("""
        SELECT
            id,
            alert_id,
            incident_type,
            severity,
            username,
            description,
            event_count,
            status,
            analyst_notes,
            response_action,
            created_at,
            updated_at,
            resolved_at,
            resolution_summary,
            closed_at,
            closure_reason

        FROM incidents

        WHERE status = 'CLOSED'

        ORDER BY closed_at DESC
    """).fetchall()

    connection.close()

    return jsonify([
        dict(incident)
        for incident in incidents
    ])


# ============================================================
# SINGLE INCIDENT API
# ============================================================

@app.route(
    "/api/incidents/<int:incident_id>",
    methods=["GET"]
)
def get_single_incident(incident_id):

    connection = get_db_connection()

    incident = connection.execute("""
        SELECT
            id,
            alert_id,
            incident_type,
            severity,
            username,
            description,
            event_count,
            status,
            analyst_notes,
            response_action,
            created_at,
            updated_at,
            resolved_at,
            resolution_summary,
            closed_at,
            closure_reason

        FROM incidents

        WHERE id = ?
    """, (
        incident_id,
    )).fetchone()

    connection.close()

    if not incident:

        return jsonify({

            "error":
                "Incident not found."

        }), 404

    return jsonify(
        dict(incident)
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/api/health")
def health_check():

    try:

        connection = get_db_connection()

        connection.execute(
            "SELECT 1"
        ).fetchone()

        connection.close()

        return jsonify({

            "status":
                "healthy",

            "database":
                "connected",

            "timestamp":
                datetime.now().isoformat(
                    timespec="seconds"
                )

        })

    except Exception as error:

        return jsonify({

            "status":
                "unhealthy",

            "database":
                "error",

            "error":
                str(error)

        }), 500


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

initialize_database()


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )