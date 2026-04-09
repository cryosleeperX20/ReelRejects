import requests
from dotenv import load_dotenv
import streamlit as st
import pickle
import numpy as np
import os

TMDB_API_KEY = st.secrets.get("TMDB_API_KEY")

st.set_page_config(
    page_title="ReelRejects",
    page_icon="🎟️",
    layout="wide",
    initial_sidebar_state="expanded"
)
with st.sidebar:
    st.markdown("<div style='height:1px; background:linear-gradient(to right, transparent, #A01830, transparent); margin-bottom:1.5rem; margin-top:1rem'></div>", unsafe_allow_html=True)
    # nav links
    st.markdown("<div style='font-size:0.6rem; color:#333; letter-spacing:2px; margin-bottom:0.8rem; padding-left:1rem'>NAVIGATION</div>", unsafe_allow_html=True)
    st.page_link("app.py", label="🎬  PREDICT")
    st.page_link("pages/Director_Intel.py", label="🎭  DIRECTOR INTEL")
    st.page_link("pages/Actor_Intel.py", label="⭐  ACTOR INTEL")
    st.page_link("pages/Star_Power.py", label="💪  STAR POWER")
    st.page_link("pages/Dir_vs_Dir.py", label="🆚  DIR VS DIR")
    st.page_link("pages/Actor_vs_Actor.py", label="🥊  ACTOR VS ACTOR")


st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;600&display=swap');

    html, body, [class*="css"] {
        background-color: #0a0a0a;
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }

    .stApp { background-color: #0a0a0a; }

    section[data-testid="stSidebar"] { background-color: #0f0f0f; }

    .block-container {
        padding: 2rem 3rem;
        max-width: 1200px;
    }

    h1, h2, h3 {
        font-family: 'Bebas Neue', cursive;
        letter-spacing: 2px;
    }

    .hero-title {
        font-family: 'Bebas Neue', cursive;
        font-size: 5rem;
        color: #ffffff;
        letter-spacing: 6px;
        line-height: 1;
        margin: 0;
    }

    .hero-sub {
        font-size: 1rem;
        color: #888888;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-top: 0.5rem;
    }

    .red-accent { color: #A01830; }

    .divider {
        height: 2px;
        background: linear-gradient(to right, #A01830, transparent);
        margin: 1.5rem 0;
    }

    .stat-card {
        background: #111111;
        border: 1px solid #1f1f1f;
        border-left: 3px solid #A01830;
        padding: 1.2rem 1.5rem;
        border-radius: 4px;
        margin-bottom: 1rem;
    }

    .stat-number {
        font-family: 'Bebas Neue', cursive;
        font-size: 2.5rem;
        color: #A01830;
        line-height: 1;
    }

    .stat-label {
        font-size: 0.7rem;
        color: #666666;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-top: 0.2rem;
    }

    .result-hit {
        background: #0a1a0a;
        border: 2px solid #00ff00;
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
    }

    .result-flop {
        background: #1a0a0a;
        border: 2px solid #A01830;
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
    }

    .verdict-text {
        font-family: 'Bebas Neue', cursive;
        font-size: 5rem;
        letter-spacing: 8px;
        line-height: 1;
    }

    .verdict-hit { color: #00ff00; }
    .verdict-flop { color: #A01830; }

    .prob-bar-container {
        background: #1a1a1a;
        border-radius: 2px;
        height: 6px;
        margin: 0.5rem 0;
        overflow: hidden;
    }

    .prob-bar-fill {
        height: 100%;
        border-radius: 2px;
        transition: width 0.5s ease;
    }

    .input-section {
        background: #0f0f0f;
        border: 1px solid #1f1f1f;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }

    .section-title {
        font-family: 'Bebas Neue', cursive;
        font-size: 1.2rem;
        color: #A01830;
        letter-spacing: 3px;
        margin-bottom: 1rem;
    }

    div[data-testid="stSelectbox"] label,
    div[data-testid="stSlider"] label,
    div[data-testid="stNumberInput"] label {
        color: #888888 !important;
        font-size: 0.75rem !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
    }

    div[data-testid="stSelectbox"] > div > div {
        background-color: #1a1a1a !important;
        border: 1px solid #2a2a2a !important;
        color: #ffffff !important;
    }

    .stButton > button {
        background-color: #A01830 !important;
        color: white !important;
        border: none !important;
        font-family: 'Bebas Neue', cursive !important;
        font-size: 1.2rem !important;
        letter-spacing: 3px !important;
        padding: 0.8rem 3rem !important;
        border-radius: 2px !important;
        width: 100% !important;
        transition: all 0.2s !important;
    }

    .stButton > button:hover {
        background-color: #c0202a !important;
        transform: translateY(-1px) !important;
    }

    .genre-badge {
        display: inline-block;
        background: #1a1a1a;
        border: 1px solid #A01830;
        color: #A01830;
        padding: 0.2rem 0.6rem;
        border-radius: 2px;
        font-size: 0.7rem;
        letter-spacing: 1px;
        margin: 0.2rem;
    }

    .insight-row {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px solid #1a1a1a;
        font-size: 0.85rem;
    }

    .insight-label { color: #666666; }
    .insight-value { color: #ffffff; font-weight: 600; }

    footer { display: none; }
    #MainMenu { visibility: hidden; }
    header { visibility: hidden; }
    
    section[data-testid="stSidebar"] {
    background-color: #0a0a0a !important;
    border-right: 1px solid #1f1f1f !important;
    min-width: 220px !important;
}

[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }

section[data-testid="stSidebar"] {
    background-color: #0a0a0a !important;
    border-right: 2px solid #1a1a1a !important;
}

section[data-testid="stSidebar"] > div {
    padding: 2rem 1.2rem !important;
}

[data-testid="stPageLink"] {
    margin-bottom: 0.2rem !important;
}

[data-testid="stPageLink"] a {
    font-family: 'Bebas Neue', cursive !important;
    font-size: 1.1rem !important;
    letter-spacing: 3px !important;
    color: #444444 !important;
    text-decoration: none !important;
    padding: 0.7rem 1rem !important;
    display: block !important;
    border-radius: 3px !important;
    border-left: 3px solid transparent !important;
    transition: all 0.15s !important;
}

[data-testid="stPageLink"] a:hover {
    color: #ffffff !important;
    background: #111111 !important;
    border-left: 3px solid #A01830 !important;
}

[data-testid="stPageLink-active"] a {
    color: #ffffff !important;
    background: #150508 !important;
    border-left: 3px solid #A01830 !important;
}
</style>
""", unsafe_allow_html=True)


# ── Models ──────────────────────────────────────────────────────────────────
@st.cache_resource
def load_models():
    base = os.path.join(os.path.dirname(__file__), "models")
    with open(os.path.join(base, "reelrejects_model.pkl"), "rb") as f:
        model = pickle.load(f)
    with open(os.path.join(base, "genre_encoder.pkl"), "rb") as f:
        le = pickle.load(f)
    with open(os.path.join(base, "feature_cols.pkl"), "rb") as f:
        feature_cols = pickle.load(f)
    return model, le, feature_cols

model, le, feature_cols = load_models()


# ── Constants ────────────────────────────────────────────────────────────────
genre_defaults = {
    # genre_name: (runtime, popularity, rating, vote_count)
    'Action':           (116, 25.0, 6.4, 3000),
    'Adventure':        (120, 22.0, 6.6, 2500),
    'Animation':        (95,  18.0, 7.0, 2000),
    'Comedy':           (100, 18.0, 6.2, 2000),
    'Crime':            (112, 16.0, 6.8, 2000),
    'Documentary':      (90,  10.0, 7.0, 500),
    'Drama':            (107, 14.0, 6.8, 1500),
    'Family':           (100, 16.0, 6.4, 1500),
    'Fantasy':          (115, 20.0, 6.5, 2000),
    'History':          (120, 12.0, 7.0, 1000),
    'Horror':           (95,  15.0, 6.0, 1500),
    'Music':            (105, 12.0, 6.8, 800),
    'Mystery':          (105, 13.0, 6.8, 1500),
    'Romance':          (105, 14.0, 6.5, 1500),
    'Science Fiction':  (115, 22.0, 6.5, 2500),
    'Thriller':         (108, 16.0, 6.6, 2000),
    'War':              (120, 12.0, 7.0, 1000),
    'Western':          (115, 10.0, 6.8, 800),
}

genre_hit_rates = {
    'Fantasy': 73.6, 'Family': 70.3, 'Adventure': 67.1,
    'Action': 66.8, 'Science Fiction': 65.5, 'Comedy': 65.3,
    'Music': 64.7, 'Horror': 64.5, 'Romance': 64.3,
    'Western': 63.1, 'Crime': 61.9, 'Animation': 58.7,
    'Thriller': 58.5, 'Drama': 56.8, 'War': 56.5,
    'Mystery': 53.0, 'History': 50.0, 'Documentary': 48.1
}

month_names = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April',
    5: 'May', 6: 'June', 7: 'July', 8: 'August',
    9: 'September', 10: 'October', 11: 'November', 12: 'December'
}

month_hit_rates = {
    1: 60.1, 2: 62.4, 3: 63.2, 4: 61.4, 5: 61.5,
    6: 67.5, 7: 69.4, 8: 63.2, 9: 53.9, 10: 57.8,
    11: 62.0, 12: 66.4
}

genre_map = {
    28: 'Action', 12: 'Adventure', 16: 'Animation',
    35: 'Comedy', 80: 'Crime', 99: 'Documentary',
    18: 'Drama', 10751: 'Family', 14: 'Fantasy',
    36: 'History', 27: 'Horror', 10402: 'Music',
    9648: 'Mystery', 10749: 'Romance', 878: 'Science Fiction',
    53: 'Thriller', 10752: 'War', 37: 'Western'
}


# ── TMDB helpers ─────────────────────────────────────────────────────────────
def tmdb_get(endpoint, params={}):
    base = "https://api.themoviedb.org/3"
    params["api_key"] = TMDB_KEY
    r = requests.get(f"{base}/{endpoint}", params=params)
    return r.json() if r.ok else {}

@st.cache_data(ttl=3600)
def get_hall_of_fame():
    all_movies = []
    for page in range(1, 4):
        results = tmdb_get("discover/movie", {
            "sort_by": "revenue.desc",
            "vote_count.gte": 1000,
            "page": page
        })
        all_movies.extend(results.get("results", []))
        if len(all_movies) >= 30:
            break
    return all_movies[:30]


# ── ML helpers ────────────────────────────────────────────────────────────────
def predict_for_movie(movie):
    genre_ids = movie.get("genre_ids", [28])
    genre_name = next((genre_map[g] for g in genre_ids if g in genre_map), "Action")

    try:
        genre_encoded = le.transform([genre_name])[0]
    except:
        genre_encoded = 0

    release = movie.get("release_date", "2020-01-01")
    month = int(release.split("-")[1]) if release else 6
    year  = int(release.split("-")[0]) if release else 2020

    pop    = movie.get("popularity",    20.0)
    rating = movie.get("vote_average",   6.5)
    votes  = movie.get("vote_count",    1000)
    budget_actual = movie.get("budget",    0)

    d_runtime, d_pop, d_rating, d_votes = genre_defaults.get(genre_name, (110, 15.0, 6.5, 2000))
    budget_est = budget_actual if budget_actual > 0 else 50_000_000

    features = np.array([[
        np.log1p(budget_est),
        d_runtime,
        np.log1p(pop),
        rating,
        votes,
        month,
        year,
        genre_encoded
    ]])

    prob = model.predict_proba(features)[0]
    hit_prob = round(float(prob[1]) * 100, 1)
    return hit_prob, genre_name


def render_movie_grid(movies):
    for row in range(6):
        cols = st.columns(5)
        for col_idx in range(5):
            movie_idx = row * 5 + col_idx
            if movie_idx >= len(movies):
                break
            movie = movies[movie_idx]
            with cols[col_idx]:
                poster = movie.get("poster_path")
                if poster:
                    st.image(
                        f"https://image.tmdb.org/t/p/w300{poster}",
                        use_container_width=True
                    )
                else:
                    st.markdown(
                        "<div style='background:#1a1a1a;height:180px;display:flex;"
                        "align-items:center;justify-content:center;color:#444;font-size:2rem'>🎬</div>",
                        unsafe_allow_html=True
                    )

                hit_prob, genre_name = predict_for_movie(movie)
                verdict_color = "#00ff00" if hit_prob >= 50 else "#A01830"
                verdict       = "HIT"     if hit_prob >= 50 else "FLOP"

                st.markdown(f"""
                <div style='margin-top:0.5rem; margin-bottom:1.5rem'>
                    <div style='font-size:0.8rem;font-weight:600;color:#ffffff;margin-bottom:0.2rem'>
                        {movie.get('title','Unknown')[:22]}
                    </div>
                    <div style='font-size:0.65rem;color:#666'>{genre_name} · {movie.get('release_date','')[:4]}</div>
                    <div style='font-size:1.1rem;font-family:Bebas Neue;color:{verdict_color};margin-top:0.3rem'>
                        {verdict} · {hit_prob}%
                    </div>
                    <div style='font-size:0.65rem;color:#555'>
                        ⭐ {movie.get('vote_average',0)} · {movie.get('vote_count',0):,} votes
                    </div>
                </div>
                """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
#  UI
# ════════════════════════════════════════════════════════════════════════════

# Header
st.markdown("""
<div style='display:flex;align-items:center;justify-content:center;padding:1rem 0'>
    <div class='hero-title'>REEL<span class='red-accent'>REJECTS</span></div>
</div>
<div style='text-align:center'>
    <div class='hero-sub'>Movie Hit or Flop Predictor — ML Powered</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
# Top stats
s1, s2, s3, s4 = st.columns(4)
with s1:
    st.markdown("<div class='stat-card'><div class='stat-number'>73.4%</div><div class='stat-label'>Model Accuracy</div></div>", unsafe_allow_html=True)
with s2:
    st.markdown("<div class='stat-card'><div class='stat-number'>12K</div><div class='stat-label'>Movies Trained On</div></div>", unsafe_allow_html=True)
with s3:
    st.markdown("<div class='stat-card'><div class='stat-number'>4</div><div class='stat-label'>ML Models Evaluated</div></div>", unsafe_allow_html=True)
with s4:
    st.markdown("<div class='stat-card'><div class='stat-number'>XGB</div><div class='stat-label'>Deployed Model</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Main layout
left_col, right_col = st.columns([2, 1.5], gap="large")

with left_col:
    st.markdown("<div class='section-title'>— Movie Details</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        genre = st.selectbox("Primary Genre", options=sorted(list(le.classes_)))
    with c2:
        budget_millions = st.number_input("Budget ($M)", min_value=0.1, max_value=500.0,
                                  value=50.0, step=0.5)
    
    budget = budget_millions * 1_000_000

    c3, c4 = st.columns(2)
    with c3:
        release_month = st.selectbox("Release Month",
                                     options=list(month_names.keys()),
                                     format_func=lambda x: month_names[x],
                                     index=5)
    with c4:
        release_year = st.slider("Release Year", min_value=2020, max_value=2030, value=2025)

    # genre-based smart defaults -- avg values from training data
    genre_defaults = {
        'Action': (120, 25.0, 6.2, 3000),
        'Adventure': (115, 22.0, 6.4, 2800),
        'Animation': (95, 18.0, 6.8, 2000),
        'Comedy': (100, 15.0, 6.1, 2500),
        'Crime': (118, 14.0, 6.5, 2200),
        'Documentary': (90, 8.0, 7.0, 800),
        'Drama': (110, 12.0, 6.6, 2000),
        'Family': (100, 20.0, 6.3, 1800),
        'Fantasy': (118, 24.0, 6.5, 2600),
        'History': (130, 10.0, 6.7, 1200),
        'Horror': (95, 18.0, 5.8, 3500),
        'Music': (105, 12.0, 6.9, 1000),
        'Mystery': (105, 13.0, 6.4, 1800),
        'Romance': (105, 11.0, 6.3, 1500),
        'Science Fiction': (115, 28.0, 6.3, 2800),
        'Thriller': (110, 16.0, 6.2, 2400),
        'War': (130, 12.0, 6.8, 1400),
        'Western': (115, 9.0, 6.5, 1000),
    }

    d_runtime, d_pop, d_rating, d_votes = genre_defaults.get(genre, (110, 15.0, 6.5, 2000))

    c5, c6 = st.columns(2)
    with c5:
        runtime = st.slider("Runtime (mins)", min_value=60, max_value=240, value=d_runtime)
        vote_average = st.slider("Expected Rating (1-10)", min_value=1.0, max_value=10.0, value=float(d_rating), step=0.1)
    with c6:
        popularity = st.slider("Popularity Score", min_value=0.0, max_value=100.0, value=float(d_pop), step=0.5)
        vote_count = st.slider("Expected Vote Count", min_value=0, max_value=50000, value=d_votes, step=100)

    st.markdown("<br>", unsafe_allow_html=True)
    predict_btn = st.button("PREDICT")

with right_col:
    st.markdown("<div class='section-title'>— Genre Intelligence</div>", unsafe_allow_html=True)

    selected_hit_rate = genre_hit_rates.get(genre, 62.2)
    month_rate = month_hit_rates.get(release_month, 62.2)

    st.markdown(f"""
    <div class='stat-card'>
        <div class='stat-number'>{selected_hit_rate}%</div>
        <div class='stat-label'>{genre} Historical Hit Rate</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='stat-card'>
        <div class='stat-number'>{month_rate}%</div>
        <div class='stat-label'>{month_names[release_month]} Release Hit Rate</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='section-title' style='margin-top:1rem'>— Genre Rankings</div>", unsafe_allow_html=True)
    for g, rate in sorted(genre_hit_rates.items(), key=lambda x: x[1], reverse=True)[:8]:
        bar_color  = "#A01830" if g == genre else "#2a2a2a"
        text_color = "#ffffff" if g == genre else "#666666"
        st.markdown(f"""
        <div style='margin-bottom:0.4rem'>
            <div style='display:flex;justify-content:space-between;font-size:0.75rem;color:{text_color}'>
                <span>{g}</span><span>{rate}%</span>
            </div>
            <div class='prob-bar-container'>
                <div class='prob-bar-fill' style='width:{rate}%;background:{bar_color}'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# Prediction result
if predict_btn:
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>— Prediction Result</div>", unsafe_allow_html=True)

    genre_encoded = le.transform([genre])[0]
    features = np.array([[
        np.log1p(budget),
        runtime,
        np.log1p(popularity),
        vote_average,
        vote_count,
        release_month,
        release_year,
        genre_encoded
    ]])

    prob       = model.predict_proba(features)[0]
    prediction = model.predict(features)[0]
    hit_prob   = round(float(prob[1]) * 100, 1)
    flop_prob  = round(float(prob[0]) * 100, 1)
    confidence = round(float(max(prob)) * 100, 1)

    res_col, insight_col = st.columns([1.5, 1])

    with res_col:
        if prediction == 1:
            st.markdown(f"""
            <div class='result-hit'>
                <div class='verdict-text verdict-hit'>HIT</div>
                <div style='color:#00ff00;font-size:0.8rem;letter-spacing:2px;margin-top:0.5rem'>
                    PROJECTED TO BE PROFITABLE
                </div>
                <div style='font-size:3rem;font-family:Bebas Neue;color:#00ff00;margin-top:1rem'>
                    {hit_prob}%
                </div>
                <div style='color:#666;font-size:0.7rem;letter-spacing:2px'>HIT PROBABILITY</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='result-flop'>
                <div class='verdict-text verdict-flop'>FLOP</div>
                <div style='color:#A01830;font-size:0.8rem;letter-spacing:2px;margin-top:0.5rem'>
                    HIGH RISK OF LOSS
                </div>
                <div style='font-size:3rem;font-family:Bebas Neue;color:#A01830;margin-top:1rem'>
                    {flop_prob}%
                </div>
                <div style='color:#666;font-size:0.7rem;letter-spacing:2px'>FLOP PROBABILITY</div>
            </div>
            """, unsafe_allow_html=True)

    with insight_col:
        st.markdown("<div class='section-title'>— Breakdown</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='margin-bottom:1rem'>
            <div style='display:flex;justify-content:space-between;font-size:0.8rem;margin-bottom:0.3rem'>
                <span style='color:#00ff00'>HIT</span>
                <span style='color:#ffffff'>{hit_prob}%</span>
            </div>
            <div class='prob-bar-container'>
                <div class='prob-bar-fill' style='width:{hit_prob}%;background:#00ff00'></div>
            </div>
            <div style='display:flex;justify-content:space-between;font-size:0.8rem;margin-top:0.8rem;margin-bottom:0.3rem'>
                <span style='color:#A01830'>FLOP</span>
                <span style='color:#ffffff'>{flop_prob}%</span>
            </div>
            <div class='prob-bar-container'>
                <div class='prob-bar-fill' style='width:{flop_prob}%;background:#A01830'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class='insight-row'>
            <span class='insight-label'>Confidence</span>
            <span class='insight-value'>{confidence}%</span>
        </div>
        <div class='insight-row'>
            <span class='insight-label'>Genre avg hit rate</span>
            <span class='insight-value'>{selected_hit_rate}%</span>
        </div>
        <div class='insight-row'>
            <span class='insight-label'>Month avg hit rate</span>
            <span class='insight-value'>{month_rate}%</span>
        </div>
        <div class='insight-row'>
            <span class='insight-label'>Budget</span>
            <span class='insight-value'>${budget_millions:.1f}M</span>
        </div>
        <div class='insight-row'>
            <span class='insight-label'>Runtime</span>
            <span class='insight-value'>{runtime} mins</span>
        </div>
        <div class='insight-row'>
            <span class='insight-label'>Release</span>
            <span class='insight-value'>{month_names[release_month]} {release_year}</span>
        </div>
        """, unsafe_allow_html=True)


# Hall of Fame
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("<div style='color:#666;font-size:0.8rem;letter-spacing:2px;margin:1rem 0'>TOP GROSSING MOVIES OF ALL TIME — ML VERDICT</div>", unsafe_allow_html=True)

fame_movies = get_hall_of_fame()
if fame_movies:
    render_movie_grid(fame_movies)
else:
    st.markdown("<div style='color:#666'>Could not load movies. Check your TMDB API key.</div>", unsafe_allow_html=True)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center;color:#333;font-size:0.7rem;letter-spacing:2px'>REELREJECTS — ML POWERED MOVIE PREDICTION</div>", unsafe_allow_html=True)

