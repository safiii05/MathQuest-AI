import os
import json
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

app = Flask(__name__)
app.secret_key = "mathquest_secret_key_change_me"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mathquest.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(100))
    grade = db.Column(db.String(20), default="Grade 5")
    xp = db.Column(db.Integer, default=520)
    streak = db.Column(db.Integer, default=6)
    lessons_completed = db.Column(db.Integer, default=14)
    current_difficulty = db.Column(db.String(20), default="medium")
    consecutive_correct = db.Column(db.Integer, default=0)
    consecutive_incorrect = db.Column(db.Integer, default=0)

class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(255))
    icon = db.Column(db.String(50))
    unlocked = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()
    if not User.query.filter_by(email="safikul@mathquest.ai").first():
        default_user = User(
            name="S Safikul Farinaz",
            email="safikul@mathquest.ai",
            password="password123",
            grade="Grade 5",
            xp=520,
            streak=6
        )
        db.session.add(default_user)
        db.session.commit()
    
    initial_achievements = [
        ("First Steps", "Complete your first quiz or lesson.", "footprints", True),
        ("Fraction Master", "Score high on a fractions module.", "pie-chart", True),
        ("Streak Champion", "Maintain a 5-day learning streak.", "flame", True),
        ("AI Explorer", "Generate 5 AI tutor explanations.", "bot", True),
        ("Speed Demon", "Answer 5 questions correctly.", "zap", False)
    ]
    for title, desc, icon, unlocked in initial_achievements:
        if not Achievement.query.filter_by(title=title).first():
            db.session.add(Achievement(title=title, description=desc, icon=icon, unlocked=unlocked))
    db.session.commit()

# Initialize Gemini client securely
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

FALLBACK_LESSONS = {
    "Grade 5": {
        "Fractions": {
            "explanation": "Grade 5 Fractions: Add and subtract fractions with unlike denominators using common multiples.",
            "steps": ["Find LCM of denominators.", "Convert to equivalent fractions.", "Add numerators."],
            "real_world": "Combining fractional measurements in a recipe."
        },
        "Decimals": {
            "explanation": "Grade 5 Decimals: Read, write, and compare decimals to thousandths place.",
            "steps": ["Align decimal points.", "Compare place values sequentially."],
            "real_world": "Comparing monetary prices at a grocery store."
        },
        "Geometry": {
            "explanation": "Grade 5 Geometry: Coordinate grid plotting and polygon classification.",
            "steps": ["Identify x and y coordinates.", "Classify triangles by angles."],
            "real_world": "Navigating grid coordinates on a map."
        }
    },
    "Grade 6": {
        "Fractions": {
            "explanation": "Grade 6 Fractions: Master division of fractions by fractions using reciprocal algorithms.",
            "steps": ["Keep first fraction.", "Change division to multiplication.", "Flip second fraction."],
            "real_world": "Dividing ribbon lengths into equal segments."
        },
        "Ratios": {
            "explanation": "Grade 6 Ratios: Understand ratio relationships, tape diagrams, and unit rates.",
            "steps": ["Write comparison as a fraction or colon.", "Calculate unit rates."],
            "real_world": "Scaling ingredients for a cooking recipe."
        },
        "Expressions": {
            "explanation": "Grade 6 Expressions: Write and evaluate algebraic expressions with variables.",
            "steps": ["Substitute numbers for variables.", "Apply order of operations."],
            "real_world": "Calculating earnings based on hourly wage and fixed bonus."
        }
    }
}

GRADE_TOPIC_QUESTIONS = {
    "Grade 5": {
        "Fractions": [
            {"question": "What is 1/4 + 2/4 in simplest form?", "options": ["3/8", "3/4", "1/2", "1"], "correct": "3/4", "explanation": "Add numerators: 1 + 2 = 3 over common denominator 4."},
            {"question": "What is 3/5 - 1/5?", "options": ["2/5", "2/10", "4/5", "1/5"], "correct": "2/5", "explanation": "Subtract numerators: 3 - 1 = 2 over 5."},
            {"question": "Convert the improper fraction 9/4 into a mixed number.", "options": ["2 1/4", "1 3/4", "2 3/4", "3 1/4"], "correct": "2 1/4", "explanation": "4 goes into 9 twice (8) with 1 left over, giving 2 1/4."},
            {"question": "What is 1/2 + 1/3?", "options": ["2/5", "5/6", "1/6", "3/5"], "correct": "5/6", "explanation": "Common denominator is 6. 3/6 + 2/6 = 5/6."},
            {"question": "What is 3/4 multiplied by 8?", "options": ["6", "4", "8", "12"], "correct": "6", "explanation": "3 × 8 = 24, and 24 ÷ 4 = 6."},
            {"question": "Which fraction is equivalent to 3/5?", "options": ["6/10", "4/10", "5/8", "3/10"], "correct": "6/10", "explanation": "Multiply top and bottom by 2 to get 6/10."},
            {"question": "What is 7/8 - 1/4?", "options": ["5/8", "3/8", "6/8", "1/2"], "correct": "5/8", "explanation": "Convert 1/4 to 2/8. 7/8 - 2/8 = 5/8."},
            {"question": "If you eat 2 slices out of a 6-slice pizza, what fraction remains?", "options": ["2/6", "4/6", "1/3", "Both B and C"], "correct": "Both B and C", "explanation": "4/6 remains, which simplifies to 2/3."},
            {"question": "What is 2/3 of 15?", "options": ["10", "5", "12", "9"], "correct": "10", "explanation": "15 ÷ 3 = 5, and 5 × 2 = 10."},
            {"question": "Which is greater: 2/3 or 3/5?", "options": ["2/3", "3/5", "They are equal", "Cannot determine"], "correct": "2/3", "explanation": "2/3 = 10/15 and 3/5 = 9/15. 10/15 is greater."}
        ],
        "Decimals": [
            {"question": "What is 0.3 + 0.4?", "options": ["0.7", "0.07", "0.34", "7.0"], "correct": "0.7", "explanation": "Line up tenths: 3 + 4 = 7 tenths (0.7)."},
            {"question": "Which decimal is greater: 0.45 or 0.5?", "options": ["0.45", "0.5", "Equal", "Cannot tell"], "correct": "0.5", "explanation": "0.5 is equivalent to 0.50, which is greater than 0.45."},
            {"question": "What is 2.5 + 1.25?", "options": ["3.75", "3.50", "2.75", "4.00"], "correct": "3.75", "explanation": "Align decimals: 2.50 + 1.25 = 3.75."},
            {"question": "Subtract 1.2 from 4.6.", "options": ["3.4", "3.2", "4.4", "2.4"], "correct": "3.4", "explanation": "4.6 - 1.2 = 3.4."},
            {"question": "What is 0.2 × 0.3?", "options": ["0.6", "0.06", "0.006", "6.0"], "correct": "0.06", "explanation": "2 × 3 = 6 with two decimal places = 0.06."},
            {"question": "Express 3/4 as a decimal.", "options": ["0.25", "0.50", "0.75", "0.80"], "correct": "0.75", "explanation": "3 divided by 4 equals 0.75."},
            {"question": "Round 14.678 to the nearest tenth.", "options": ["14.6", "14.7", "14.0", "15.0"], "correct": "14.7", "explanation": "The hundredth digit is 7 (>=5), so round up to 14.7."},
            {"question": "What is 5.4 divided by 2?", "options": ["2.7", "2.2", "3.1", "2.5"], "correct": "2.7", "explanation": "5.4 ÷ 2 = 2.7."},
            {"question": "Which is the smallest decimal?", "options": ["0.08", "0.8", "0.008", "0.88"], "correct": "0.008", "explanation": "Thousandths place value makes 0.008 the smallest."},
            {"question": "What is $10.00 - $3.45?", "options": ["$6.55", "$7.55", "$6.45", "$7.45"], "correct": "$6.55", "explanation": "Standard subtraction: 10.00 - 3.45 = 6.55."}
        ],
        "Geometry": [
            {"question": "How many degrees are in a triangle's interior angles?", "options": ["90°", "180°", "360°", "270°"], "correct": "180°", "explanation": "Interior angles of any triangle always sum to 180°."},
            {"question": "A polygon with 4 equal sides and 4 right angles is a:", "options": ["Rectangle", "Square", "Trapezoid", "Pentagon"], "correct": "Square", "explanation": "Squares have 4 equal sides and 90-degree right angles."},
            {"question": "What is the area of a rectangle with length 5 cm and width 3 cm?", "options": ["15 cm²", "16 cm²", "8 cm²", "30 cm²"], "correct": "15 cm²", "explanation": "Area = length × width = 5 × 3 = 15 cm²."},
            {"question": "How many sides does a pentagon have?", "options": ["5", "6", "7", "8"], "correct": "5", "explanation": "A pentagon is a five-sided polygon."},
            {"question": "What angle measures exactly 90 degrees?", "options": ["Acute", "Right", "Obtuse", "Straight"], "correct": "Right", "explanation": "A right angle measures exactly 90°."},
            {"question": "What is the perimeter of a square with side length 6 inches?", "options": ["24 inches", "36 inches", "12 inches", "18 inches"], "correct": "24 inches", "explanation": "Perimeter = 4 × side = 4 × 6 = 24 inches."},
            {"question": "Parallel lines are lines that...", "options": ["Intersects at 90°", "Never intersect", "Cross each other", "Form a circle"], "correct": "Never intersect", "explanation": "Parallel lines always maintain the same distance and never cross."},
            {"question": "What type of triangle has all three sides of equal length?", "options": ["Scalene", "Isosceles", "Equilateral", "Right"], "correct": "Equilateral", "explanation": "Equilateral triangles have 3 equal sides and 3 equal angles."},
            {"question": "On a coordinate plane, the horizontal axis is called the...", "options": ["y-axis", "x-axis", "Origin", "Quadrant"], "correct": "x-axis", "explanation": "The horizontal number line is the x-axis."},
            {"question": "What is the volume of a rectangular prism with length 3, width 2, and height 4?", "options": ["24", "12", "9", "18"], "correct": "24", "explanation": "Volume = L × W × H = 3 × 2 × 4 = 24."}
        ]
    },
    "Grade 6": {
        "Fractions": [
            {"question": "What is 2/3 ÷ 1/4?", "options": ["2/12", "8/3", "3/8", "6/4"], "correct": "8/3", "explanation": "Multiply by reciprocal: (2/3) × (4/1) = 8/3."},
            {"question": "What is 1 1/2 × 2/3?", "options": ["1", "3/2", "2", "3/4"], "correct": "1", "explanation": "Convert to improper fraction: (3/2) × (2/3) = 6/6 = 1 whole."},
            {"question": "Divide 5/8 by 1/2.", "options": ["5/4", "5/16", "4/5", "10/8"], "correct": "5/4", "explanation": "(5/8) × (2/1) = 10/8 = 5/4."},
            {"question": "What is 3/4 of 2 2/3?", "options": ["2", "1", "3", "1 1/2"], "correct": "2", "explanation": "(3/4) × (8/3) = 24/12 = 2."},
            {"question": "Simplify the complex fraction (1/2) / (3/4).", "options": ["2/3", "3/8", "4/6", "1/3"], "correct": "2/3", "explanation": "(1/2) × (4/3) = 4/6 = 2/3."},
            {"question": "What is 4 1/2 ÷ 1 1/2?", "options": ["3", "4", "2", "6"], "correct": "3", "explanation": "(9/2) ÷ (3/2) = (9/2) × (2/3) = 18/6 = 3."},
            {"question": "Subtract 1/6 from 5/6 and simplify.", "options": ["2/3", "4/6", "1/2", "3/4"], "correct": "2/3", "explanation": "5/6 - 1/6 = 4/6 = 2/3."},
            {"question": "What is 2/5 + 1/3?", "options": ["11/15", "3/8", "2/15", "7/15"], "correct": "11/15", "explanation": "Common denominator is 15. 6/15 + 5/15 = 11/15."},
            {"question": "Multiply 7/8 by 4/7.", "options": ["1/2", "28/56", "4/8", "Both A and C"], "correct": "Both A and C", "explanation": "(7/8) × (4/7) = 28/56 = 1/2 (4/8). Both A and C are correct."},
            {"question": "What is the reciprocal of 3 3/4?", "options": ["4/15", "15/4", "3/4", "4/3"], "correct": "4/15", "explanation": "3 3/4 = 15/4. Its reciprocal is 4/15."}
        ],
        "Ratios": [
            {"question": "If boys to girls is 3:2 and there are 15 boys, how many girls?", "options": ["10", "12", "18", "20"], "correct": "10", "explanation": "Multiplier is 5 (15 ÷ 3), so 2 × 5 = 10 girls."},
            {"question": "What is the unit rate if a runner covers 15 miles in 3 hours?", "options": ["3 mph", "5 mph", "6 mph", "45 mph"], "correct": "5 mph", "explanation": "Divide total distance by hours: 15 ÷ 3 = 5 miles per hour."},
            {"question": "Express the ratio 18:24 in simplest form.", "options": ["3:4", "2:3", "4:5", "6:8"], "correct": "3:4", "explanation": "Divide both numbers by their Greatest Common Divisor, which is 6."},
            {"question": "If 4 markers cost $6, what is the cost of 10 markers at the same unit rate?", "options": ["$15", "$12", "$18", "$20"], "correct": "$15", "explanation": "Unit rate is $1.50 per marker. 10 × $1.50 = $15."},
            {"question": "A recipe uses 3 cups of flour for every 2 cups of sugar. What is the ratio of sugar to total ingredients?", "options": ["2:5", "3:5", "2:3", "5:2"], "correct": "2:5", "explanation": "Total ingredients = 3 + 2 = 5. Ratio of sugar (2) to total (5) is 2:5."},
            {"question": "If 7 inches on a map represent 210 actual miles, what does 1 inch represent?", "options": ["30 miles", "20 miles", "35 miles", "15 miles"], "correct": "30 miles", "explanation": "210 ÷ 7 = 30 miles per inch."},
            {"question": "What is 20% expressed as a ratio of part to whole in simplest form?", "options": ["1:5", "1:4", "2:10", "20:100"], "correct": "1:5", "explanation": "20% = 20/100 = 1/5 (1:5)."},
            {"question": "If the ratio of cats to dogs is 5:7 and there are 60 total animals, how many dogs are there?", "options": ["35", "25", "42", "30"], "correct": "35", "explanation": "Total parts = 5 + 7 = 12. Each part = 60 ÷ 12 = 5. Dogs = 7 × 5 = 35."},
            {"question": "Which of these ratios is equivalent to 4:7?", "options": ["12:21", "8:15", "16:25", "20:30"], "correct": "12:21", "explanation": "Multiply both numbers in 4:7 by 3 to get 12:21."},
            {"question": "A car uses 4 gallons of gas for 140 miles. How far can it travel on 7 gallons?", "options": ["245 miles", "210 miles", "280 miles", "220 miles"], "correct": "245 miles", "explanation": "Unit rate is 35 mpg. 35 × 7 = 245 miles."}
        ],
        "Expressions": [
            {"question": "Evaluate 4x + 3 when x = 5.", "options": ["23", "20", "35", "12"], "correct": "23", "explanation": "Substitute 5: 4(5) + 3 = 20 + 3 = 23."},
            {"question": "Simplify the expression: 6y + 2 - 2y + 5", "options": ["8y + 7", "4y + 7", "6y + 7", "4y + 3"], "correct": "4y + 7", "explanation": "Combine like terms: (6y - 2y) + (2 + 5) = 4y + 7."},
            {"question": "What is the coefficient in the expression 7x - 9?", "options": ["7", "x", "-9", "4"], "correct": "7", "explanation": "The coefficient is the number multiplied by the variable (7)."},
            {"question": "Evaluate 2(a + 6) when a = 4.", "options": ["20", "14", "16", "22"], "correct": "20", "explanation": "Parentheses first: (4 + 6) = 10. Then 2 × 10 = 20."},
            {"question": "Write an algebraic expression for '5 less than twice a number n'.", "options": ["2n - 5", "5 - 2n", "2(n - 5)", "n/2 - 5"], "correct": "2n - 5", "explanation": "Twice a number is 2n. 5 less than that is 2n - 5."},
            {"question": "Which expression is equivalent to 3(x + 4)?", "options": ["3x + 12", "3x + 4", "x + 12", "3x + 7"], "correct": "3x + 12", "explanation": "Distribute the 3: 3(x) + 3(4) = 3x + 12."},
            {"question": "Evaluate x² + 5 when x = 3.", "options": ["14", "11", "9", "16"], "correct": "14", "explanation": "3² = 9, and 9 + 5 = 14."},
            {"question": "Combine like terms: 5a + 3b + 2a - b", "options": ["7a + 2b", "7a + 4b", "6ab", "5a + 2b"], "correct": "7a + 2b", "explanation": "(5a + 2a) + (3b - b) = 7a + 2b."},
            {"question": "What is the value of 3³?", "options": ["27", "9", "6", "81"], "correct": "27", "explanation": "3 × 3 × 3 = 27."},
            {"question": "Solve for x: x + 8 = 15", "options": ["7", "8", "23", "5"], "correct": "7", "explanation": "Subtract 8 from both sides: x = 15 - 8 = 7."}
        ]
    }
}

@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("auth_page"))
    user = db.session.get(User, session["user_id"])
    return render_template("index.html", user=user)

@app.route("/auth")
def auth_page():
    return render_template("auth.html")

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    user = User.query.filter_by(email=data.get("email"), password=data.get("password")).first()
    if user:
        session["user_id"] = user.id
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Invalid email or password."}), 401

@app.route("/api/signup", methods=["POST"])
def api_signup():
    data = request.get_json() or {}
    if User.query.filter_by(email=data.get("email")).first():
        return jsonify({"success": False, "message": "Email already registered."}), 400
    new_user = User(name=data.get("name"), email=data.get("email"), password=data.get("password"), grade="Grade 5", xp=100, streak=1)
    db.session.add(new_user)
    db.session.commit()
    session["user_id"] = new_user.id
    return jsonify({"success": True})

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("auth_page"))

@app.route("/api/tutor", methods=["POST"])
def ai_tutor():
    data = request.get_json() or {}
    topic = data.get("topic", "Fractions")
    grade = data.get("grade", "Grade 5")
    
    grade_fallbacks = FALLBACK_LESSONS.get(grade, FALLBACK_LESSONS["Grade 5"])
    default_lesson = grade_fallbacks.get(topic, {"explanation": f"Concept guide for {topic}.", "steps": ["Review rules."], "real_world": "Everyday math."})

    if not client:
        return jsonify({"source": "fallback", "data": default_lesson})
    
    try:
        prompt = f"Explain '{topic}' for a {grade} student aligned with Georgia standards. Return valid JSON with keys: 'explanation' (string), 'steps' (array of strings), 'real_world' (string)."
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return jsonify({"source": "gemini", "data": json.loads(response.text)})
    except Exception:
        return jsonify({"source": "fallback_error", "data": default_lesson})

@app.route("/api/infographic", methods=["POST"])
def ai_infographic():
    data = request.get_json() or {}
    topic = data.get("topic", "Fractions")
    svg_visual = f'<svg viewBox="0 0 300 80" class="w-full max-w-md h-20 mx-auto"><rect x="10" y="10" width="280" height="60" rx="12" fill="#6C4CF1" opacity="0.15"/><text x="150" y="45" text-anchor="middle" fill="#6C4CF1" font-weight="bold" font-size="16">Infographic Model: {topic}</text></svg>'
    return jsonify({"type": "svg", "content": svg_visual})

@app.route("/api/solver", methods=["POST"])
def ai_solver():
    data = request.get_json() or {}
    query = data.get("query", "")
    if not client:
        return jsonify({"solution": f"AI Solver: Break down '{query}' step by step."})
    try:
        response = client.models.generate_content(model="gemini-2.5-flash", contents=f"Provide a step-by-step math solution for: '{query}'")
        return jsonify({"solution": response.text})
    except Exception:
        return jsonify({"solution": "Review your numbers and verify operations."})

@app.route("/api/quiz_questions", methods=["POST"])
def get_quiz_questions():
    data = request.get_json() or {}
    topic = data.get("topic", "Fractions")
    grade = data.get("grade", "Grade 5")
    
    user = db.session.get(User, session.get("user_id", 1))
    diff = user.current_difficulty if user else "medium"

    grade_pool = GRADE_TOPIC_QUESTIONS.get(grade, GRADE_TOPIC_QUESTIONS["Grade 5"])
    questions_pool = grade_pool.get(topic, grade_pool.get("Fractions", []))

    if not client:
        return jsonify({"questions": questions_pool, "difficulty": diff})

    try:
        prompt = f"Generate 5 multiple-choice math quiz questions on '{topic}' for {grade} at '{diff}' difficulty level. Return valid JSON as an array of objects with keys: 'question', 'options' (array of 4 strings), 'correct' (exact string matching one option), 'explanation'."
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return jsonify({"questions": json.loads(response.text), "difficulty": diff})
    except Exception:
        return jsonify({"questions": questions_pool, "difficulty": diff})

@app.route("/api/submit_answer", methods=["POST"])
def submit_answer():
    data = request.get_json() or {}
    user = db.session.get(User, session.get("user_id", 1))
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
        
    if data.get("is_correct", False):
        user.xp += 25
        user.consecutive_correct += 1
        user.consecutive_incorrect = 0
        if user.consecutive_correct >= 2 and user.current_difficulty == "easy":
            user.current_difficulty = "medium"
            user.consecutive_correct = 0
        elif user.consecutive_correct >= 2 and user.current_difficulty == "medium":
            user.current_difficulty = "hard"
            user.consecutive_correct = 0
    else:
        user.consecutive_incorrect += 1
        user.consecutive_correct = 0
        if user.consecutive_incorrect >= 2 and user.current_difficulty == "hard":
            user.current_difficulty = "medium"
            user.consecutive_incorrect = 0
        elif user.consecutive_incorrect >= 2 and user.current_difficulty == "medium":
            user.current_difficulty = "easy"
            user.consecutive_incorrect = 0
            
    db.session.commit()
    return jsonify({"xp": user.xp, "difficulty": user.current_difficulty})

@app.route("/api/achievements", methods=["GET"])
def get_achievements():
    return jsonify([{ "title": a.title, "description": a.description, "icon": a.icon, "unlocked": a.unlocked } for a in Achievement.query.all()])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)