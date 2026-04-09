import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()
TMDB_KEY = os.getenv("TMDB_API_KEY")

st.set_page_config(page_title="Director Intel", page_icon="🎬", layout="wide")

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
    footer { display: none; }
    #MainMenu { visibility: hidden; }
    header { visibility: hidden; }
    section[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

def tmdb_get(endpoint, params={}):
    base = "https://api.themoviedb.org/3"
    params["api_key"] = TMDB_KEY
    r = requests.get(f"{base}/{endpoint}", params=params)
    return r.json() if r.ok else {}

@st.cache_data(ttl=3600)
def search_director(name):
    # search for person
    data = tmdb_get("search/person", {"query": name})
    results = data.get("results", [])
    # filter to directors only
    for r in results:
        if r.get("known_for_department") == "Directing":
            return r
    return results[0] if results else None

@st.cache_data(ttl=3600)
def get_director_movies(person_id):
    # get all movies they directed
    data = tmdb_get(f"person/{person_id}/movie_credits")
    crew = data.get("crew", [])
    # only directing credits with decent vote count
    movies = [m for m in crew if m.get("job") == "Director" and m.get("vote_count", 0) > 100]
    movies = sorted(movies, key=lambda x: x.get("vote_count", 0), reverse=True)
    return movies[:30]  # top 30 by popularity

def calc_hit_rate(movies):
    # using vote average as proxy -- 6.5+ is generally well received
    if not movies:
        return 0, 0, 0
    hits = [m for m in movies if m.get("vote_average", 0) >= 6.5]
    hit_rate = round(len(hits) / len(movies) * 100, 1)
    return hit_rate, len(hits), len(movies)

# header
st.markdown("<div class='hero-title'>🎬 DIRECTOR<span class='red-accent'> INTEL</span></div>", unsafe_allow_html=True)
st.markdown("<div style='color:#888; font-size:0.9rem; letter-spacing:3px; text-transform:uppercase; margin-top:0.5rem'>Career stats, hit rate, best and worst — powered by TMDB</div>", unsafe_allow_html=True)
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

director_name = st.text_input("Search Director", placeholder="e.g. Christopher Nolan, James Cameron...")
search_btn = st.button("SEARCH")

if search_btn and director_name:
    with st.spinner("Pulling records..."):
        person = search_director(director_name)

    if not person:
        st.markdown("<div style='color:#A01830; font-size:1rem'>Director not found. Try a different name.</div>", unsafe_allow_html=True)
    else:
        person_id = person["id"]
        movies = get_director_movies(person_id)

        if not movies:
            st.markdown("<div style='color:#666'>No directing credits found.</div>", unsafe_allow_html=True)
        else:
            hit_rate, hits, total = calc_hit_rate(movies)
            best = max(movies, key=lambda x: x.get("vote_average", 0))
            worst = min(movies, key=lambda x: x.get("vote_average", 0))
            avg_rating = round(sum(m.get("vote_average", 0) for m in movies) / len(movies), 2)

            st.markdown("<br>", unsafe_allow_html=True)

            # profile + stats
            left, right = st.columns([1, 3], gap="large")

            with left:
                profile = person.get("profile_path")
                if profile:
                    st.image(f"https://image.tmdb.org/t/p/w300{profile}", use_container_width=True)
                else:
                    st.markdown("<div style='background:#1a1a1a; height:200px; display:flex; align-items:center; justify-content:center; color:#444; font-size:3rem'>🎬</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-family:Bebas Neue; font-size:1.5rem; color:#fff; margin-top:0.5rem'>{person.get('name','')}</div>", unsafe_allow_html=True)

            with right:
                s1, s2, s3, s4 = st.columns(4)
                with s1:
                    st.markdown(f"<div class='stat-card'><div class='stat-number'>{hit_rate}%</div><div class='stat-label'>Hit Rate</div></div>", unsafe_allow_html=True)
                with s2:
                    st.markdown(f"<div class='stat-card'><div class='stat-number'>{total}</div><div class='stat-label'>Movies Directed</div></div>", unsafe_allow_html=True)
                with s3:
                    st.markdown(f"<div class='stat-card'><div class='stat-number'>{hits}</div><div class='stat-label'>Hits</div></div>", unsafe_allow_html=True)
                with s4:
                    st.markdown(f"<div class='stat-card'><div class='stat-number'>{avg_rating}</div><div class='stat-label'>Avg Rating</div></div>", unsafe_allow_html=True)

                # hit rate bar
                st.markdown("<div class='section-title' style='margin-top:1rem'>— Hit Rate</div>", unsafe_allow_html=True)
                bar_color = "#00ff00" if hit_rate >= 60 else "#A01830"
                st.markdown(f"""
                <div class='prob-bar-container' style='height:12px'>
                    <div class='prob-bar-fill' style='width:{hit_rate}%; background:{bar_color}'></div>
                </div>
                <div style='color:#666; font-size:0.7rem; margin-top:0.3rem'>{hits} hits out of {total} movies</div>
                """, unsafe_allow_html=True)

                # best and worst
                st.markdown("<div class='section-title' style='margin-top:1.5rem'>— Best & Worst</div>", unsafe_allow_html=True)
                b1, b2 = st.columns(2)
                with b1:
                    st.markdown(f"""
                    <div class='stat-card'>
                        <div style='font-size:0.65rem; color:#00ff00; letter-spacing:2px'>BEST RATED</div>
                        <div style='font-size:1rem; font-weight:600; margin-top:0.3rem'>{best.get('title','')}</div>
                        <div style='font-size:0.8rem; color:#888'>{best.get('release_date','')[:4]} · ⭐ {best.get('vote_average','')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with b2:
                    st.markdown(f"""
                    <div class='stat-card'>
                        <div style='font-size:0.65rem; color:#A01830; letter-spacing:2px'>WORST RATED</div>
                        <div style='font-size:1rem; font-weight:600; margin-top:0.3rem'>{worst.get('title','')}</div>
                        <div style='font-size:0.8rem; color:#888'>{worst.get('release_date','')[:4]} · ⭐ {worst.get('vote_average','')}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # filmography
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>— Filmography</div>", unsafe_allow_html=True)

            cols_per_row = 6
            for row in range(0, len(movies), cols_per_row):
                cols = st.columns(cols_per_row)
                for i, movie in enumerate(movies[row:row+cols_per_row]):
                    with cols[i]:
                        poster = movie.get("poster_path")
                        if poster:
                            st.image(f"https://image.tmdb.org/t/p/w200{poster}", use_container_width=True)
                        rating = movie.get("vote_average", 0)
                        color = "#00ff00" if rating >= 6.5 else "#A01830"
                        st.markdown(f"""
                        <div style='margin-top:0.3rem'>
                            <div style='font-size:0.7rem; color:#fff'>{movie.get('title','')[:18]}</div>
                            <div style='font-size:0.65rem; color:#666'>{movie.get('release_date','')[:4]}</div>
                            <div style='font-size:0.8rem; font-family:Bebas Neue; color:{color}'>⭐ {rating}</div>
                        </div>
                        """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center; color:#333; font-size:0.7rem; letter-spacing:2px'>REELREJECTS — ML POWERED MOVIE PREDICTION</div>", unsafe_allow_html=True)