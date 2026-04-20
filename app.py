import html
import os
import warnings
from typing import Any

import requests
import streamlit as st

# =============================
# CONFIG
# =============================
API_BASE = os.getenv("MOVIE_API_BASE", "https://movie-rec-466x.onrender.com")
TMDB_IMG = "https://image.tmdb.org/t/p/w500"
HOME_CATEGORIES = ["trending", "popular", "top_rated", "now_playing", "upcoming"]
HOME_LIMIT = 24
SEARCH_LIMIT = 24

# Keep output clean if older warnings appear from cached environments.
warnings.filterwarnings("ignore", message=".*use_column_width.*")

st.set_page_config(layout="wide", page_title="Movie Recommendation System")


# =============================
# STYLES
# =============================
def inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Manrope:wght@400;600;700;800&display=swap');

        :root {
            --bg-main: #0b0b0f;
            --bg-elevated: #151520;
            --bg-soft: #1e1e2c;
            --accent: #e50914;
            --accent-hover: #ff2530;
            --text-main: #f7f7fa;
            --text-muted: #b6b6c8;
            --border: rgba(255, 255, 255, 0.09);
            --card-shadow: 0 18px 40px rgba(0, 0, 0, 0.45);
            --radius-lg: 18px;
            --radius-md: 12px;
        }

        .stApp {
            background:
                radial-gradient(1200px 450px at 8% -10%, rgba(229, 9, 20, 0.20), transparent 45%),
                radial-gradient(800px 350px at 100% 0%, rgba(58, 40, 123, 0.25), transparent 45%),
                var(--bg-main);
            color: var(--text-main);
            font-family: "Manrope", "Segoe UI", sans-serif;
        }

        .block-container {
            max-width: 1350px;
            padding-top: clamp(4.6rem, 7vh, 6.2rem);
            padding-bottom: 2rem;
        }

        h1, h2, h3 {
            color: var(--text-main);
        }

        .hero-title {
            font-family: "Bebas Neue", sans-serif;
            letter-spacing: 0.04em;
            font-size: 3.1rem;
            margin-bottom: 0.2rem;
            margin-top: 0.2rem;
            line-height: 1.12;
        }

        .hero-subtitle {
            color: var(--text-muted);
            font-size: 0.98rem;
            margin-bottom: 0.8rem;
        }

        .panel {
            background: linear-gradient(160deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02));
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 1rem 1.1rem;
            box-shadow: var(--card-shadow);
            backdrop-filter: blur(6px);
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            background: linear-gradient(160deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02));
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            box-shadow: var(--card-shadow);
            backdrop-filter: blur(6px);
        }

        .poster-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 1rem;
            margin-top: 0.55rem;
            margin-bottom: 0.4rem;
        }

        @media (max-width: 1080px) {
            .poster-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }

        @media (max-width: 680px) {
            .poster-grid {
                grid-template-columns: repeat(1, minmax(0, 1fr));
            }
        }

        .movie-card {
            background: linear-gradient(170deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02));
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            overflow: hidden;
            box-shadow: var(--card-shadow);
            transition: transform 0.22s ease, border-color 0.22s ease, box-shadow 0.22s ease;
            min-height: 100%;
        }

        .movie-card:hover {
            transform: translateY(-4px);
            border-color: rgba(229, 9, 20, 0.50);
            box-shadow: 0 22px 46px rgba(229, 9, 20, 0.18);
        }

        .poster-shell {
            aspect-ratio: 2 / 3;
            width: 100%;
            background: #111118;
            overflow: hidden;
            border-bottom: 1px solid var(--border);
        }

        .poster-shell img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
        }

        .poster-fallback {
            width: 100%;
            height: 100%;
            display: grid;
            place-items: center;
            color: var(--text-muted);
            font-size: 0.9rem;
            padding: 0.8rem;
            text-align: center;
        }

        .movie-meta {
            padding: 0.8rem;
            display: grid;
            gap: 0.7rem;
        }

        .movie-title {
            color: var(--text-main);
            font-weight: 700;
            line-height: 1.25;
            min-height: 2.5rem;
            overflow: hidden;
            font-size: 0.97rem;
        }

        .movie-open-button {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            text-decoration: none;
            color: #ffffff !important;
            background: linear-gradient(140deg, var(--accent), #b80710);
            border: 1px solid rgba(255, 255, 255, 0.16);
            border-radius: 10px;
            height: 2.35rem;
            padding: 0 0.9rem;
            font-size: 0.9rem;
            font-weight: 700;
            transition: filter 0.18s ease, transform 0.18s ease;
        }

        .movie-open-button:hover {
            filter: brightness(1.08);
            transform: translateY(-1px);
        }

        .section-label {
            margin-top: 0.4rem;
            margin-bottom: 0.2rem;
            font-weight: 800;
            color: var(--text-main);
            font-size: 1.05rem;
            letter-spacing: 0.01em;
        }

        .meta-row {
            color: var(--text-muted);
            margin-bottom: 0.3rem;
            font-size: 0.96rem;
        }

        .stButton > button {
            width: 100%;
            height: 2.45rem;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.14);
            background: linear-gradient(140deg, var(--accent), #b80710);
            color: #fff;
            font-weight: 700;
            transition: transform 0.16s ease, filter 0.16s ease;
        }

        .stButton > button:hover {
            filter: brightness(1.08);
            transform: translateY(-1px);
            border-color: rgba(255, 255, 255, 0.25);
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(17, 17, 25, 0.92), rgba(14, 14, 20, 0.95));
            border-right: 1px solid var(--border);
        }

        [data-testid="stSelectbox"] > div,
        [data-testid="stTextInput"] > div,
        [data-testid="stTextInput"] input {
            background-color: rgba(255, 255, 255, 0.04) !important;
            color: var(--text-main) !important;
            border-radius: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# =============================
# STATE + ROUTING
# =============================
def init_state() -> None:
    if "view" not in st.session_state:
        st.session_state.view = "home"
    if "selected_tmdb_id" not in st.session_state:
        st.session_state.selected_tmdb_id = None

    qp_view = st.query_params.get("view")
    qp_id = st.query_params.get("id")

    if qp_view in {"home", "details"}:
        st.session_state.view = qp_view

    if qp_id:
        try:
            st.session_state.selected_tmdb_id = int(qp_id)
            st.session_state.view = "details"
        except (TypeError, ValueError):
            pass


def goto_home() -> None:
    st.session_state.view = "home"
    st.session_state.selected_tmdb_id = None
    st.query_params["view"] = "home"
    if "id" in st.query_params:
        del st.query_params["id"]
    st.rerun()


def goto_details(tmdb_id: int) -> None:
    st.session_state.view = "details"
    st.session_state.selected_tmdb_id = int(tmdb_id)
    st.query_params["view"] = "details"
    st.query_params["id"] = str(int(tmdb_id))
    st.rerun()


# =============================
# API HELPERS
# =============================
@st.cache_data(ttl=30)
def api_get_json(path: str, params: dict[str, Any] | None = None) -> tuple[Any, str | None]:
    try:
        response = requests.get(f"{API_BASE}{path}", params=params, timeout=25)
        if response.status_code >= 400:
            return None, f"HTTP {response.status_code}: {response.text[:300]}"
        return response.json(), None
    except requests.RequestException as exc:
        return None, f"Request failed: {exc}"


def to_cards_from_tfidf_items(tfidf_items: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for item in tfidf_items or []:
        tmdb_data = item.get("tmdb") or {}
        tmdb_id = tmdb_data.get("tmdb_id")
        if not tmdb_id:
            continue
        cards.append(
            {
                "tmdb_id": tmdb_id,
                "title": tmdb_data.get("title") or item.get("title") or "Untitled",
                "poster_url": tmdb_data.get("poster_url"),
            }
        )
    return cards


def parse_tmdb_search_to_cards(
    data: Any, keyword: str, limit: int = SEARCH_LIMIT
) -> tuple[list[tuple[str, int]], list[dict[str, Any]]]:
    keyword_l = keyword.strip().lower()

    if isinstance(data, dict) and "results" in data:
        raw_items: list[dict[str, Any]] = []
        for movie in data.get("results") or []:
            title = (movie.get("title") or "").strip()
            tmdb_id = movie.get("id")
            poster_path = movie.get("poster_path")
            if not title or not tmdb_id:
                continue
            raw_items.append(
                {
                    "tmdb_id": int(tmdb_id),
                    "title": title,
                    "poster_url": f"{TMDB_IMG}{poster_path}" if poster_path else None,
                    "release_date": movie.get("release_date", ""),
                }
            )
    elif isinstance(data, list):
        raw_items = []
        for movie in data:
            tmdb_id = movie.get("tmdb_id") or movie.get("id")
            title = (movie.get("title") or "").strip()
            if not title or not tmdb_id:
                continue
            raw_items.append(
                {
                    "tmdb_id": int(tmdb_id),
                    "title": title,
                    "poster_url": movie.get("poster_url"),
                    "release_date": movie.get("release_date", ""),
                }
            )
    else:
        return [], []

    matched = [item for item in raw_items if keyword_l in item["title"].lower()]
    final_list = matched if matched else raw_items

    suggestions: list[tuple[str, int]] = []
    for item in final_list[:10]:
        year = (item.get("release_date") or "")[:4]
        label = f"{item['title']} ({year})" if year else item["title"]
        suggestions.append((label, int(item["tmdb_id"])))

    cards = [
        {
            "tmdb_id": int(item["tmdb_id"]),
            "title": item["title"],
            "poster_url": item.get("poster_url"),
        }
        for item in final_list[:limit]
    ]
    return suggestions, cards


# =============================
# RENDER HELPERS
# =============================
def render_header() -> None:
    st.markdown("<div class='hero-title'>Movie Recommendation System</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='hero-subtitle'>Search any movie, open details, and discover similar films instantly.</div>",
        unsafe_allow_html=True,
    )
    st.divider()


def render_sidebar() -> str:
    with st.sidebar:
        st.markdown("## Navigation")
        if st.button("Home", key="btn_home"):
            goto_home()

        st.markdown("---")
        st.markdown("### Home Feed")
        category = st.selectbox(
            "Category",
            HOME_CATEGORIES,
            index=0,
            help="Pick a category for the homepage recommendations.",
        )

    return category


def build_movie_card_html(card: dict[str, Any]) -> str:
    title = html.escape(str(card.get("title") or "Untitled"))
    tmdb_id = card.get("tmdb_id")
    poster_url = card.get("poster_url")

    if poster_url:
        poster_markup = (
            f"<img src='{html.escape(str(poster_url), quote=True)}' alt='{title} poster' loading='lazy' />"
        )
    else:
        poster_markup = "<div class='poster-fallback'>Poster not available</div>"

    if tmdb_id:
        open_control = (
            f"<a class='movie-open-button' href='?view=details&id={int(tmdb_id)}'>Open Details</a>"
        )
    else:
        open_control = "<span class='movie-open-button' style='pointer-events:none;opacity:0.6;'>Unavailable</span>"

    return (
        "<article class='movie-card'>"
        f"<div class='poster-shell'>{poster_markup}</div>"
        "<div class='movie-meta'>"
        f"<div class='movie-title'>{title}</div>"
        f"{open_control}"
        "</div>"
        "</article>"
    )


def poster_grid(cards: list[dict[str, Any]]) -> None:
    if not cards:
        st.info("No movies to show.")
        return

    cards_html = "".join(build_movie_card_html(card) for card in cards)
    st.markdown(f"<section class='poster-grid'>{cards_html}</section>", unsafe_allow_html=True)


def render_home(category: str) -> None:
    typed = st.text_input(
        "Search by movie title",
        placeholder="Try: avenger, batman, matrix...",
    )

    st.divider()

    if typed.strip():
        if len(typed.strip()) < 2:
            st.caption("Type at least 2 characters for suggestions.")
            return

        data, err = api_get_json("/tmdb/search", params={"query": typed.strip()})
        if err or data is None:
            st.error(f"Search failed: {err}")
            return

        suggestions, cards = parse_tmdb_search_to_cards(data, typed.strip(), limit=SEARCH_LIMIT)

        if suggestions:
            labels = ["-- Select a movie --"] + [label for label, _ in suggestions]
            selected_label = st.selectbox("Suggestions", labels, index=0, key="search_suggestions")
            if selected_label != "-- Select a movie --":
                label_to_id = {label: tmdb_id for label, tmdb_id in suggestions}
                goto_details(label_to_id[selected_label])
        else:
            st.info("No suggestions found. Try another keyword.")

        st.markdown("<div class='section-label'>Results</div>", unsafe_allow_html=True)
        poster_grid(cards)
        return

    st.markdown(
        f"<div class='section-label'>Home - {category.replace('_', ' ').title()}</div>",
        unsafe_allow_html=True,
    )

    home_cards, err = api_get_json("/home", params={"category": category, "limit": HOME_LIMIT})
    if err or not home_cards:
        st.error(f"Home feed failed: {err or 'Unknown error'}")
        return

    poster_grid(home_cards)


def render_details() -> None:
    tmdb_id = st.session_state.selected_tmdb_id
    if not tmdb_id:
        st.warning("No movie selected.")
        if st.button("Back to Home", key="details_back_empty"):
            goto_home()
        return

    left_head, right_head = st.columns([3, 1])
    with left_head:
        st.markdown("### Movie Details")
    with right_head:
        if st.button("Back to Home", key="details_back"):
            goto_home()

    data, err = api_get_json(f"/movie/id/{tmdb_id}")
    if err or not data:
        st.error(f"Could not load details: {err or 'Unknown error'}")
        return

    left_col, right_col = st.columns([1, 2.25], gap="large")

    with left_col:
        with st.container(border=True):
            if data.get("poster_url"):
                st.image(data["poster_url"], width="stretch")
            else:
                st.markdown("<div class='poster-fallback'>Poster not available</div>", unsafe_allow_html=True)

    with right_col:
        with st.container(border=True):
            st.markdown(f"## {html.escape(data.get('title') or '')}")
            release = data.get("release_date") or "-"
            genres = ", ".join(g.get("name", "") for g in data.get("genres", [])) or "-"
            st.markdown(f"<div class='meta-row'><strong>Release:</strong> {html.escape(release)}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='meta-row'><strong>Genres:</strong> {html.escape(genres)}</div>", unsafe_allow_html=True)
            st.markdown("---")
            st.markdown("### Overview")
            st.write(data.get("overview") or "No overview available.")

    if data.get("backdrop_url"):
        st.markdown("#### Backdrop")
        st.image(data["backdrop_url"], width="stretch")

    st.divider()
    st.markdown("### Recommendations")

    title = (data.get("title") or "").strip()
    if not title:
        st.warning("No title available to compute recommendations.")
        return

    bundle, err2 = api_get_json(
        "/movie/search",
        params={"query": title, "tfidf_top_n": 12, "genre_limit": 12},
    )

    if not err2 and bundle:
        st.markdown("<div class='section-label'>Similar Movies (TF-IDF)</div>", unsafe_allow_html=True)
        poster_grid(to_cards_from_tfidf_items(bundle.get("tfidf_recommendations")))

        st.markdown("<div class='section-label'>More Like This (Genre)</div>", unsafe_allow_html=True)
        poster_grid(bundle.get("genre_recommendations", []))
        return

    st.info("Showing genre recommendations (fallback).")
    genre_only, err3 = api_get_json("/recommend/genre", params={"tmdb_id": tmdb_id, "limit": 18})
    if not err3 and genre_only:
        poster_grid(genre_only)
    else:
        st.warning("No recommendations available right now.")


def main() -> None:
    inject_styles()
    init_state()
    home_category = render_sidebar()
    render_header()

    if st.session_state.view == "home":
        render_home(home_category)
    elif st.session_state.view == "details":
        render_details()


if __name__ == "__main__":
    main()
