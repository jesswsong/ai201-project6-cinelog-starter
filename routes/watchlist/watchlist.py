"""
routes/watchlist.py — CineLog (feature/watchlist branch)

Endpoints for the watchlist feature.
"""

from flask import Blueprint, jsonify, request
from services.watchlist_service import (
    add_to_watchlist,
    get_watchlist,
    AlreadyInWatchlistError,
)
from services.collection_service import FilmNotFoundError

watchlist_bp = Blueprint("watchlist", __name__)


@watchlist_bp.route("/<user_id>", methods=["GET"])
def view_watchlist(user_id):
    """GET /watchlist/<user_id> — Return the user's watchlist."""
    films = get_watchlist(user_id)
    return jsonify(films)


@watchlist_bp.route("/<user_id>/add", methods=["POST"])
def add_film(user_id):
    """
    POST /watchlist/<user_id>/add

<<<<<<< HEAD
    Body: { "film_id": "<uuid>" }
=======
    Body: { "film_id": <int> }
>>>>>>> 8e20142b6033149e7d03bad177f4f298cec9ba46
    """
    data = request.get_json()
    if not data or "film_id" not in data:
        return jsonify({"error": "film_id is required"}), 400

    try:
        entry = add_to_watchlist(user_id=user_id, film_id=data["film_id"])
        return jsonify(entry.to_dict()), 201
    except FilmNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except AlreadyInWatchlistError as e:
        return jsonify({"error": str(e)}), 409
