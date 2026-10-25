let currentGrade = 'Grade 5';
let currentTopic = 'Fractions';
let quizData = [];
let currentQuestionIndex = 0;
let score = 0;
let currentDifficulty = 'medium';

const topicsData = {
    "Grade 5": [
        { title: "Fractions", desc: "Understand numerators, denominators, and equivalent fractions.", icon: "pie-chart", time: "15 mins" },
        { title: "Decimals", desc: "Read, write, and compare decimals to thousandths.", icon: "hash", time: "20 mins" },
        { title: "Basic ratios", desc: "Introduction to proportional relationships and scaling.", icon: "percent", time: "15 mins" },
        { title: "Geometry", desc: "Classify polygons and coordinate plane plotting.", icon: "box", time: "25 mins" },
        { title: "Measurement", desc: "Convert units within customary and metric systems.", icon: "ruler", time: "15 mins" }
    ],
    "Grade 6": [
        { title: "Fractions & Operations", desc: "Divide fractions by fractions and solve word problems.", icon: "divide", time: "20 mins" },
        { title: "Decimals & Percentages", desc: "Master percentage calculations and real-world discounts.", icon: "badge-percent", time: "20 mins" },
        { title: "Ratios & Rates", desc: "Solve unit rate and proportional word problems.", icon: "scale", time: "25 mins" },
        { title: "Geometry & Area", desc: "Calculate area of polygons, surface area, and volume.", icon: "triangle", time: "30 mins" },
        { title: "Expressions & Equations", desc: "Write and evaluate algebraic expressions with variables.", icon: "cpu", time: "25 mins" }
    ]
};

const achievementsData = [
    { title: "First Steps", desc: "Complete your very first math quiz.", icon: "footprints", unlocked: true },
    { title: "Fraction Master", desc: "Score 100% on a Fractions quiz.", icon: "award", unlocked: true },
    { title: "Streak Champion", desc: "Maintain a 5-day learning streak.", icon: "flame", unlocked: true },
    { title: "AI Explorer", desc: "Generate 5 explanations with the AI Tutor.", icon: "bot", unlocked: false },
    { title: "Speed Demon", desc: "Answer 5 questions correctly in under 60 seconds.", icon: "zap", unlocked: false },
    { title: "Math Wizard", desc: "Complete all topics for Grade 5 and 6.", icon: "sparkles", unlocked: false }
];

function switchTab(tabId) {
    document.querySelectorAll('.view-section').forEach(el => el.classList.add('hidden'));
    document.querySelectorAll('.sidebar-btn').forEach(el => el.classList.remove('active'));

    document.getElementById(`view-${tabId}`).classList.remove('hidden');
    const navBtn = document.getElementById(`nav-${tabId}`);
    if (navBtn) navBtn.classList.add('active');

    if (tabId === 'explorer') renderExplorer();
    if (tabId === 'achievements') renderAchievements();
    lucide.createIcons();
}

function setGrade(grade) {
    currentGrade = grade;
    document.getElementById('current-grade-label').innerText = grade;
    if (grade === 'Grade 5') {
        document.getElementById('g5-btn').className = "px-4 py-1.5 text-xs font-bold rounded-full bg-primary text-white shadow-sm";
        document.getElementById('g6-btn').className = "px-4 py-1.5 text-xs font-bold rounded-full text-mutedtext hover:text-slate-900";
    } else {
        document.getElementById('g6-btn').className = "px-4 py-1.5 text-xs font-bold rounded-full bg-primary text-white shadow-sm";
        document.getElementById('g5-btn').className = "px-4 py-1.5 text-xs font-bold rounded-full text-mutedtext hover:text-slate-900";
    }
    renderExplorer();
}

function renderExplorer() {
    const grid = document.getElementById('topic-grid');
    const topics = topicsData[currentGrade];
    grid.innerHTML = topics.map(t => `
        <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm card-hover flex flex-col justify-between">
            <div>
                <div class="w-12 h-12 rounded-2xl bg-indigo-50 flex items-center justify-center text-primary mb-4">
                    <i data-lucide="${t.icon}" class="w-6 h-6"></i>
                </div>
                <span class="text-xs font-bold text-primary uppercase">${currentGrade}</span>
                <h3 class="text-lg font-extrabold text-slate-800 mt-1">${t.title}</h3>
                <p class="text-sm text-mutedtext mt-2">${t.desc}</p>
            </div>
            <div class="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between">
                <span class="text-xs font-semibold text-slate-400 flex items-center"><i data-lucide="clock" class="w-3.5 h-3.5 mr-1"></i>${t.time}</span>
                <button onclick="launchTopicTutor('${t.title}')" class="bg-indigo-50 text-primary font-bold px-4 py-2 rounded-xl text-xs hover:bg-primary hover:text-white transition-all">Start Lesson</button>
            </div>
        </div>
    `).join('');
    lucide.createIcons();
}

function launchTopicTutor(topicName) {
    currentTopic = topicName;
    document.getElementById('tutor-topic-select').value = topicName;
    switchTab('tutor');
    fetchAiTutor();
}

async function fetchAiTutor() {
    const topic = document.getElementById('tutor-topic-select').value;
    const container = document.getElementById('tutor-content');
    container.innerHTML = `
        <div class="p-12 text-center">
            <i data-lucide="loader-2" class="w-10 h-10 text-primary mx-auto animate-spin mb-3"></i>
            <p class="text-sm font-semibold text-slate-600">Generating Gemini AI explanation for ${topic}...</p>
        </div>
    `;
    lucide.createIcons();

    try {
        const response = await fetch('/api/tutor', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic: topic, grade: currentGrade })
        });
        const res = await response.json();
        const data = res.data;

        container.innerHTML = `
            <div class="space-y-6">
                <div class="p-6 bg-indigo-50/60 rounded-2xl border border-indigo-100">
                    <h3 class="font-extrabold text-primary text-base mb-2">Core Explanation</h3>
                    <p class="text-slate-700 text-sm leading-relaxed">${data.explanation}</p>
                </div>
                <div class="p-6 bg-slate-50 rounded-2xl border border-slate-200">
                    <h3 class="font-extrabold text-slate-800 text-base mb-3">Step-by-Step Breakdown</h3>
                    <ul class="space-y-2">
                        ${data.steps.map((step, idx) => `<li class="flex items-start text-sm text-slate-700"><span class="w-6 h-6 rounded-full bg-primary text-white font-bold flex items-center justify-center text-xs mr-3 flex-shrink-0">${idx+1}</span><span>${step}</span></li>`).join('')}
                    </ul>
                </div>
                <div class="p-6 bg-teal-50/60 rounded-2xl border border-teal-100 flex items-start space-x-4">
                    <div class="w-10 h-10 rounded-xl bg-teal-500 text-white flex items-center justify-center flex-shrink-0">
                        <i data-lucide="lightbulb" class="w-5 h-5"></i>
                    </div>
                    <div>
                        <h4 class="font-extrabold text-teal-800 text-sm">Real-World Example</h4>
                        <p class="text-teal-900 text-sm mt-1">${data.real_world}</p>
                    </div>
                </div>
                <div class="flex justify-end space-x-4 pt-4">
                    <button onclick="switchTab('quiz')" class="bg-secondary text-white font-bold px-6 py-3 rounded-xl shadow-md hover:bg-teal-600 transition-all flex items-center space-x-2">
                        <span>Take Practice Quiz</span>
                        <i data-lucide="arrow-right" class="w-4 h-4"></i>
                    </button>
                </div>
            </div>
        `;
    } catch (err) {
        container.innerHTML = `<div class="p-6 bg-rose-50 text-rose-700 rounded-2xl">Error connecting to AI service. Please try again.</div>`;
    }
    lucide.createIcons();
}

async function startQuiz() {
    const container = document.getElementById('quiz-container');
    container.innerHTML = `
        <div class="text-center py-12">
            <i data-lucide="loader-2" class="w-10 h-10 text-primary mx-auto animate-spin mb-3"></i>
            <p class="text-sm font-semibold text-slate-600">Generating adaptive quiz questions...</p>
        </div>
    `;
    lucide.createIcons();

    try {
        const response = await fetch('/api/quiz', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic: currentTopic, difficulty: currentDifficulty, grade: currentGrade })
        });
        const res = await response.json();
        quizData = res.questions || [];
        currentQuestionIndex = 0;
        score = 0;
        renderQuestion();
    } catch (err) {
        container.innerHTML = `<div class="p-6 bg-rose-50 text-rose-700 rounded-2xl">Failed to load quiz. Please check your connection.</div>`;
    }
}

function renderQuestion() {
    if (currentQuestionIndex >= quizData.length) {
        document.getElementById('quiz-container').innerHTML = `
            <div class="text-center py-12 space-y-4">
                <div class="w-16 h-16 bg-amber-100 text-amber-600 rounded-full flex items-center justify-center mx-auto">
                    <i data-lucide="trophy" class="w-8 h-8"></i>
                </div>
                <h3 class="text-2xl font-extrabold text-slate-900">Quiz Completed!</h3>
                <p class="text-slate-600 text-sm">You scored ${score} out of ${quizData.length} correct.</p>
                <button onclick="startQuiz()" class="bg-primary text-white font-bold px-8 py-3 rounded-2xl shadow-lg hover:bg-indigo-700 transition-all">Try Again</button>
            </div>
        `;
        lucide.createIcons();
        return;
    }

    const q = quizData[currentQuestionIndex];
    const container = document.getElementById('quiz-container');
    container.innerHTML = `
        <div class="space-y-6">
            <div class="flex justify-between items-center text-xs font-bold text-mutedtotal uppercase">
                <span>Question ${currentQuestionIndex + 1} of ${quizData.length}</span>
                <span>Score: ${score}</span>
            </div>
            <h3 class="text-lg font-bold text-slate-900">${q.question}</h3>
            <div class="space-y-3" id="options-list">
                ${q.options.map(opt => `
                    <button onclick="submitAnswer(this, '${opt}', '${q.correct}', '${q.explanation.replace(/'/g, "\\'")}')" class="w-full text-left p-4 rounded-2xl border border-slate-200 bg-slate-50 font-semibold text-slate-700 hover:bg-indigo-50 hover:border-primary transition-all option-btn">
                        ${opt}
                    </button>
                `).join('')}
            </div>
            <div id="explanation-box" class="hidden p-4 rounded-2xl bg-indigo-50 border border-indigo-100 text-sm text-indigo-900"></div>
        </div>
    `;
    lucide.createIcons();
}

function submitAnswer(btn, selected, correct, explanation) {
    document.querySelectorAll('.option-btn').forEach(b => b.disabled = true);
    const expBox = document.getElementById('explanation-box');
    expBox.classList.remove('hidden');

    if (selected === correct) {
        btn.classList.add('bg-emerald-100', 'border-emerald-500', 'text-emerald-800');
        expBox.innerHTML = `<strong>Correct! 🎉</strong> ${explanation}`;
        score++;
    } else {
        btn.classList.add('bg-rose-100', 'border-rose-500', 'text-rose-800');
        expBox.innerHTML = `<strong>Incorrect.</strong> The correct answer is <strong>${correct}</strong>. ${explanation}`;
    }

    setTimeout(() => {
        currentQuestionIndex++;
        renderQuestion();
    }, 3500);
}

function renderAchievements() {
    const grid = document.getElementById('achievements-grid');
    grid.innerHTML = achievementsData.map(a => `
        <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm flex items-center space-x-4 ${a.unlocked ? '' : 'opacity-60 grayscale'}">
            <div class="w-14 h-14 rounded-2xl ${a.unlocked ? 'bg-amber-100 text-amber-600' : 'bg-slate-100 text-slate-400'} flex items-center justify-center flex-shrink-0">
                <i data-lucide="${a.icon}" class="w-7 h-7"></i>
            </div>
            <div>
                <div class="flex items-center space-x-2">
                    <h3 class="font-extrabold text-slate-900">${a.title}</h3>
                    ${a.unlocked ? '<span class="bg-emerald-100 text-emerald-700 text-[10px] font-bold px-2 py-0.5 rounded-full">Unlocked</span>' : '<span class="bg-slate-100 text-slate-500 text-[10px] font-bold px-2 py-0.5 rounded-full">Locked</span>'}
                </div>
                <p class="text-xs text-mutedtext mt-1">${a.desc}</p>
            </div>
        </div>
    `).join('');
    lucide.createIcons();
}