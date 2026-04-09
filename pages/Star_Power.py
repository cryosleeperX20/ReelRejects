import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()
TMDB_KEY = os.getenv("TMDB_API_KEY")

st.set_page_config(page_title="Star Power", page_icon="⭐", layout="wide", initial_sidebar_state="expanded")

with st.sidebar:
    st.markdown("<div style='height:1px; background:linear-gradient(to right, transparent, #A01830, transparent); margin-bottom:1.5rem; margin-top:1rem'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.6rem; color:#333; letter-spacing:2px; margin-bottom:0.8rem; padding-left:1rem'>NAVIGATION</div>", unsafe_allow_html=True)
    st.page_link("app.py", label="🎬  PREDICT")
    st.page_link("pages/Director_Intel.py", label="🎭  DIRECTOR INTEL")
    st.page_link("pages/Actor_Intel.py", label="⭐  ACTOR INTEL")
    st.page_link("pages/Star_Power.py", label="💪  STAR POWER")
    st.page_link("pages/Dir_vs_Dir.py", label="🆚  DIR VS DIR")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;600&display=swap');
    html, body, [class*="css"] { background-color: #0a0a0a; color: #ffffff; font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0a0a0a; }
    .block-container { padding: 2rem 3rem; max-width: 1200px; }
    .hero-title { font-family: 'Bebas Neue', cursive; font-size: 3.5rem; color: #ffffff; letter-spacing: 6px; line-height: 1; margin: 0; }
    .red-accent { color: #A01830; }
    .divider { height: 2px; background: linear-gradient(to right, #A01830, transparent); margin: 1.5rem 0; }
    .stat-card { background: #111111; border: 1px solid #1f1f1f; border-left: 3px solid #A01830; padding: 1.2rem 1.5rem; border-radius: 4px; margin-bottom: 1rem; }
    .stat-number { font-family: 'Bebas Neue', cursive; font-size: 2.5rem; color: #A01830; line-height: 1; }
    .stat-label { font-size: 0.7rem; color: #666666; letter-spacing: 2px; text-transform: uppercase; margin-top: 0.2rem; }
    .section-title { font-family: 'Bebas Neue', cursive; font-size: 1.2rem; color: #A01830; letter-spacing: 3px; margin-bottom: 1rem; }
    .insight-row { display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #1a1a1a; font-size: 0.85rem; }
    .insight-label { color: #666666; }
    .insight-value { color: #ffffff; font-weight: 600; }
    .prob-bar-container { background: #1a1a1a; border-radius: 2px; height: 6px; margin: 0.5rem 0; overflow: hidden; }
    .prob-bar-fill { height: 100%; border-radius: 2px; }
    .stButton > button { background-color: #A01830 !important; color: white !important; border: none !important; font-family: 'Bebas Neue', cursive !important; font-size: 1.2rem !important; letter-spacing: 3px !important; padding: 0.8rem 3rem !important; border-radius: 2px !important; width: 100% !important; }
    .stTextInput input { background-color: #1a1a1a !important; border: 1px solid #2a2a2a !important; color: #ffffff !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    section[data-testid="stSidebar"] { background-color: #0a0a0a !important; border-right: 2px solid #1a1a1a !important; }
    [data-testid="stPageLink"] a { font-family: 'Bebas Neue', cursive !important; font-size: 1.1rem !important; letter-spacing: 3px !important; color: #444444 !important; text-decoration: none !important; padding: 0.7rem 1rem !important; display: block !important; border-radius: 3px !important; border-left: 3px solid transparent !important; }
    [data-testid="stPageLink"] a:hover { color: #ffffff !important; background: #111111 !important; border-left: 3px solid #A01830 !important; }
    [data-testid="stPageLink-active"] a { color: #ffffff !important; background: #150508 !important; border-left: 3px solid #A01830 !important; }
    footer { display: none; }
    #MainMenu { visibility: hidden; }
    header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

def tmdb_get(endpoint, params={}):
    base = "https://api.themoviedb.org/3"
    params["api_key"] = TMDB_KEY
    r = requests.get(f"{base}/{endpoint}", params=params)
    return r.json() if r.ok else {}

@st.cache_data(ttl=3600)
def search_person(name):
    data = tmdb_get("search/person", {"query": name})
    results = data.get("results", [])
    return results[0] if results else None

@st.cache_data(ttl=3600)
def get_person_movies(person_id):
    data = tmdb_get(f"person/{person_id}/movie_credits")
    cast = data.get("cast", [])
    movies = [m for m in cast if m.get("vote_count", 0) > 200]
    return sorted(movies, key=lambda x: x.get("vote_count", 0), reverse=True)[:20]

def calc_star_score(movies):
    if not movies:
        return 0
    hits = [m for m in movies if m.get("vote_average", 0) >= 6.5]
    hit_rate = len(hits) / len(movies)
    avg_pop = sum(m.get("popularity", 0) for m in movies) / len(movies)
    # score out of 100 -- hit rate weighted more than popularity
    score = (hit_rate * 70) + min(avg_pop / 50 * 30, 30)
    return round(score, 1)

def get_star_badge(score):
    if score >= 75:
        return "💎 A-LIST", "#00ff00"
    elif score >= 60:
        return "⭐ RELIABLE", "#88ff88"
    elif score >= 45:
        return "⚠️ RISKY", "#ffaa00"
    else:
        return "☠️ BOX OFFICE POISON", "#A01830"

# header
st.markdown("<div class='hero-title'>⭐ STAR<span class='red-accent'> POWER</span></div>", unsafe_allow_html=True)
st.markdown("<div style='color:#888; font-size:0.9rem; letter-spacing:3px; text-transform:uppercase; margin-top:0.5rem'>Build your cast — calculate combined star power score</div>", unsafe_allow_html=True)
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

st.markdown("<div class='section-title'>— Add Your Cast</div>", unsafe_allow_html=True)
st.markdown("<div style='color:#666; font-size:0.8rem; margin-bottom:1rem'>Add up to 5 cast members. Score updates as you add more.</div>", unsafe_allow_html=True)

# 5 actor inputs
cast_names = []
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    cast_names.append(st.text_input("Actor 1", placeholder="e.g. Tom Hanks"))
with c2:
    cast_names.append(st.text_input("Actor 2", placeholder="e.g. Meryl Streep"))
with c3:
    cast_names.append(st.text_input("Actor 3", placeholder="e.g. Leonardo DiCaprio"))
with c4:
    cast_names.append(st.text_input("Actor 4", placeholder="Optional"))
with c5:
    cast_names.append(st.text_input("Actor 5", placeholder="Optional"))

# director input
st.markdown("<div class='section-title' style='margin-top:1rem'>— Add Director</div>", unsafe_allow_html=True)
director_name = st.text_input("Director", placeholder="e.g. Christopher Nolan")

calculate_btn = st.button("CALCULATE STAR POWER")

if calculate_btn:
    all_names = [n for n in cast_names if n.strip()] + ([director_name] if director_name.strip() else [])

    if not all_names:
        st.markdown("<div style='color:#A01830'>Add at least one name.</div>", unsafe_allow_html=True)
    else:
        scores = []
        profiles = []

        with st.spinner("Crunching star power..."):
            for name in all_names:
                person = search_person(name)
                if person:
                    movies = get_person_movies(person["id"])
                    score = calc_star_score(movies)
                    scores.append(score)
                    profiles.append({
                        "name": person.get("name", name),
                        "photo": person.get("profile_path"),
                        "score": score,
                        "movies": len(movies),
                        "badge": get_star_badge(score)
                    })

        if not profiles:
            st.markdown("<div style='color:#666'>Could not find any of these people on TMDB.</div>", unsafe_allow_html=True)
        else:
            # combined score -- average weighted slightly toward highest scorer
            combined = round((sum(scores) / len(scores)) * 0.7 + max(scores) * 0.3, 1)
            badge, badge_color = get_star_badge(combined)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

            # big combined score
            score_color = "#00ff00" if combined >= 60 else "#ffaa00" if combined >= 45 else "#A01830"
            st.markdown(f"""
            <div style='text-align:center; padding:2rem 0'>
                <div style='font-size:0.8rem; color:#666; letter-spacing:3px; margin-bottom:0.5rem'>COMBINED STAR POWER SCORE</div>
                <div style='font-family:Bebas Neue; font-size:6rem; color:{score_color}; line-height:1'>{combined}</div>
                <div style='font-size:1.2rem; color:{badge_color}; font-weight:600; margin-top:0.5rem'>{badge}</div>
                <div style='font-size:0.75rem; color:#444; margin-top:0.5rem'>Based on {len(profiles)} people · hit rates + popularity weighted</div>
            </div>
            """, unsafe_allow_html=True)

            # score bar
            st.markdown(f"""
            <div class='prob-bar-container' style='height:16px; margin: 0 auto; max-width:600px'>
                <div class='prob-bar-fill' style='width:{combined}%; background:{score_color}'></div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>— Individual Scores</div>", unsafe_allow_html=True)

            # individual cards
            cols = st.columns(len(profiles))
            for i, p in enumerate(profiles):
                with cols[i]:
                    if p["photo"]:
                        st.image(f"https://image.tmdb.org/t/p/w200{p['photo']}", use_container_width=True)
                    else:
                        st.markdown("<div style='background:#1a1a1a; height:150px; display:flex; align-items:center; justify-content:center; color:#444; font-size:2rem'>👤</div>", unsafe_allow_html=True)

                    s_color = "#00ff00" if p["score"] >= 60 else "#ffaa00" if p["score"] >= 45 else "#A01830"
                    b_label, b_color = p["badge"]
                    st.markdown(f"""
                    <div style='margin-top:0.5rem; text-align:center'>
                        <div style='font-size:0.85rem; font-weight:600; color:#fff'>{p['name']}</div>
                        <div style='font-family:Bebas Neue; font-size:2rem; color:{s_color}'>{p['score']}</div>
                        <div style='font-size:0.65rem; color:{b_color}'>{b_label}</div>
                        <div style='font-size:0.6rem; color:#444'>{p['movies']} movies analyzed</div>
                    </div>
                    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center; color:#333; font-size:0.7rem; letter-spacing:2px'>REELREJECTS — ML POWERED MOVIE PREDICTION</div>", unsafe_allow_html=True)