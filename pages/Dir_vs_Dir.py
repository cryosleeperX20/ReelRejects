import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()
TMDB_KEY = os.getenv("TMDB_API_KEY")

st.set_page_config(page_title="Dir vs Dir", page_icon="🆚", layout="wide", initial_sidebar_state="expanded")

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
def search_director(name):
    data = tmdb_get("search/person", {"query": name})
    results = data.get("results", [])
    for r in results:
        if r.get("known_for_department") == "Directing":
            return r
    return results[0] if results else None

@st.cache_data(ttl=3600)
def get_director_movies(person_id):
    data = tmdb_get(f"person/{person_id}/movie_credits")
    crew = data.get("crew", [])
    movies = [m for m in crew if m.get("job") == "Director" and m.get("vote_count", 0) > 100]
    return sorted(movies, key=lambda x: x.get("vote_count", 0), reverse=True)[:30]

def get_stats(movies):
    if not movies:
        return 0, 0, 0, 0, None, None
    hits = [m for m in movies if m.get("vote_average", 0) >= 6.5]
    hit_rate = round(len(hits) / len(movies) * 100, 1)
    avg_rating = round(sum(m.get("vote_average", 0) for m in movies) / len(movies), 2)
    best = max(movies, key=lambda x: x.get("vote_average", 0))
    worst = min(movies, key=lambda x: x.get("vote_average", 0))
    return hit_rate, len(hits), len(movies), avg_rating, best, worst

# header
st.markdown("<div class='hero-title'>🆚 DIR<span class='red-accent'> VS </span>DIR</div>", unsafe_allow_html=True)
st.markdown("<div style='color:#888; font-size:0.9rem; letter-spacing:3px; text-transform:uppercase; margin-top:0.5rem'>Head to head director showdown — who wins at the box office?</div>", unsafe_allow_html=True)
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# two inputs side by side
left_input, vs_col, right_input = st.columns([2, 0.5, 2])
with left_input:
    st.markdown("<div class='section-title'>— Director 1</div>", unsafe_allow_html=True)
    dir1_name = st.text_input("Director 1", placeholder="e.g. Christopher Nolan", label_visibility="collapsed")
with vs_col:
    st.markdown("<div style='font-family:Bebas Neue; font-size:3rem; color:#A01830; text-align:center; padding-top:1rem'>VS</div>", unsafe_allow_html=True)
with right_input:
    st.markdown("<div class='section-title'>— Director 2</div>", unsafe_allow_html=True)
    dir2_name = st.text_input("Director 2", placeholder="e.g. James Cameron", label_visibility="collapsed")

st.markdown("<br>", unsafe_allow_html=True)
compare_btn = st.button("COMPARE")

if compare_btn and dir1_name and dir2_name:
    with st.spinner("Loading records..."):
        p1 = search_director(dir1_name)
        p2 = search_director(dir2_name)

    if not p1 or not p2:
        st.markdown("<div style='color:#A01830'>Could not find one or both directors.</div>", unsafe_allow_html=True)
    else:
        m1 = get_director_movies(p1["id"])
        m2 = get_director_movies(p2["id"])

        hr1, hits1, total1, avg1, best1, worst1 = get_stats(m1)
        hr2, hits2, total2, avg2, best2, worst2 = get_stats(m2)

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

        # winner banner
        if hr1 > hr2:
            winner = p1.get("name", dir1_name)
            win_color = "#00ff00"
        elif hr2 > hr1:
            winner = p2.get("name", dir2_name)
            win_color = "#00ff00"
        else:
            winner = "IT'S A TIE"
            win_color = "#ffaa00"

        st.markdown(f"""
        <div style='text-align:center; padding:1.5rem 0'>
            <div style='font-size:0.7rem; color:#666; letter-spacing:3px'>WINNER BY HIT RATE</div>
            <div style='font-family:Bebas Neue; font-size:3.5rem; color:{win_color}; letter-spacing:4px'>{winner}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # side by side stats
        col1, divider_col, col2 = st.columns([2, 0.1, 2])

        def render_director_card(person, movies, hit_rate, hits, total, avg_rating, best, worst):
            profile = person.get("profile_path")
            pc1, pc2 = st.columns([1, 2])
            with pc1:
                if profile:
                    st.image(f"https://image.tmdb.org/t/p/w200{profile}", use_container_width=True)
                else:
                    st.markdown("<div style='background:#1a1a1a; height:120px; display:flex; align-items:center; justify-content:center; color:#444; font-size:2rem'>🎬</div>", unsafe_allow_html=True)
            with pc2:
                st.markdown(f"<div style='font-family:Bebas Neue; font-size:1.5rem; color:#fff'>{person.get('name','')}</div>", unsafe_allow_html=True)
                color = "#00ff00" if hit_rate >= 60 else "#A01830"
                st.markdown(f"<div style='font-family:Bebas Neue; font-size:2.5rem; color:{color}'>{hit_rate}%</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-size:0.7rem; color:#666'>HIT RATE</div>", unsafe_allow_html=True)

            s1, s2, s3 = st.columns(3)
            with s1:
                st.markdown(f"<div class='stat-card'><div class='stat-number'>{total}</div><div class='stat-label'>Movies</div></div>", unsafe_allow_html=True)
            with s2:
                st.markdown(f"<div class='stat-card'><div class='stat-number'>{hits}</div><div class='stat-label'>Hits</div></div>", unsafe_allow_html=True)
            with s3:
                st.markdown(f"<div class='stat-card'><div class='stat-number'>{avg_rating}</div><div class='stat-label'>Avg Rating</div></div>", unsafe_allow_html=True)

            # hit rate bar
            bar_color = "#00ff00" if hit_rate >= 60 else "#A01830"
            st.markdown(f"""
            <div class='prob-bar-container' style='height:10px'>
                <div class='prob-bar-fill' style='width:{hit_rate}%; background:{bar_color}'></div>
            </div>
            """, unsafe_allow_html=True)

            if best and worst:
                st.markdown(f"""
                <div style='margin-top:1rem'>
                    <div style='font-size:0.65rem; color:#00ff00; letter-spacing:2px'>BEST</div>
                    <div style='font-size:0.9rem; color:#fff'>{best.get('title','')} <span style='color:#666'>({best.get('release_date','')[:4]})</span> ⭐ {best.get('vote_average','')}</div>
                    <div style='font-size:0.65rem; color:#A01830; letter-spacing:2px; margin-top:0.5rem'>WORST</div>
                    <div style='font-size:0.9rem; color:#fff'>{worst.get('title','')} <span style='color:#666'>({worst.get('release_date','')[:4]})</span> ⭐ {worst.get('vote_average','')}</div>
                </div>
                """, unsafe_allow_html=True)

            # filmography strip -- top 6
            st.markdown("<div style='font-size:0.65rem; color:#444; letter-spacing:2px; margin-top:1rem; margin-bottom:0.5rem'>TOP FILMS</div>", unsafe_allow_html=True)
            film_cols = st.columns(6)
            for i, movie in enumerate(movies[:6]):
                with film_cols[i]:
                    poster = movie.get("poster_path")
                    if poster:
                        st.image(f"https://image.tmdb.org/t/p/w92{poster}", use_container_width=True)
                    r = movie.get("vote_average", 0)
                    c = "#00ff00" if r >= 6.5 else "#A01830"
                    st.markdown(f"<div style='font-size:0.6rem; color:{c}; text-align:center'>⭐{r}</div>", unsafe_allow_html=True)

        with col1:
            render_director_card(p1, m1, hr1, hits1, total1, avg1, best1, worst1)

        with divider_col:
            st.markdown("<div style='width:1px; background:#1a1a1a; height:100%'></div>", unsafe_allow_html=True)

        with col2:
            render_director_card(p2, m2, hr2, hits2, total2, avg2, best2, worst2)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center; color:#333; font-size:0.7rem; letter-spacing:2px'>REELREJECTS — ML POWERED MOVIE PREDICTION</div>", unsafe_allow_html=True)