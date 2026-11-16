"""Web app + JSON API for the chanting stand.   flask --app yocal_service.app run"""
from __future__ import annotations

import datetime as dt
import os

from flask import Flask, Response, abort, jsonify, request, send_from_directory

from . import compose, db, music
from yocal_rules import assemble

MAX_SCAN_DAYS = 400  # how far /api/adjacent looks for an in-scope date

STATIC = os.path.join(os.path.dirname(__file__), "static")


def create_app() -> Flask:
    app = Flask(__name__, static_folder=None)

    def _date(arg: str = "date") -> dt.date:
        v = request.args.get(arg)
        try:
            return dt.date.fromisoformat(v) if v else dt.date.today()
        except ValueError:
            abort(400, description=f"bad {arg}: expected YYYY-MM-DD")

    @app.get("/")
    def index():
        return send_from_directory(STATIC, "index.html")

    @app.get("/static/<path:p>")
    def static_files(p):
        return send_from_directory(STATIC, p)

    @app.get("/api/services")
    def services():
        return jsonify([{"id": k, "title": v} for k, v in compose.SERVICES.items()])

    @app.get("/api/adjacent")
    def adjacent():
        """Nearest date the service is served on. ?service= &date= &dir=next|prev &include=1 (accept the date itself)."""
        sid = request.args.get("service", "liturgy")
        if sid not in compose.SERVICES:
            abort(400, description=f"unknown service {sid!r}")
        d = _date()
        step = dt.timedelta(days=-1 if request.args.get("dir") == "prev" else 1)
        cur = d if request.args.get("include") == "1" else d + step
        for _ in range(MAX_SCAN_DAYS):
            if in_scope(sid, cur):
                return jsonify(service=sid, date=cur.isoformat())
            cur += step
        return jsonify(error=f"no {compose.SERVICES[sid]} within {MAX_SCAN_DAYS} days"), 404

    @app.get("/api/sundays")
    def sundays():
        """Upcoming (and recent) Sundays for the date selector."""
        start = next_sunday(_date("from") if request.args.get("from") else dt.date.today() - dt.timedelta(days=14))
        return jsonify([(start + dt.timedelta(weeks=i)).isoformat() for i in range(int(request.args.get("n", 12)))])

    @app.get("/api/service")
    def service():
        """The assembled service. ?date=YYYY-MM-DD (default: next Sunday) &service=liturgy &offline=1 &music=1 (also download scores)."""
        sid = request.args.get("service", "liturgy")
        d = _date()
        try:
            return jsonify(compose.compose(d, sid, offline=request.args.get("offline") == "1", fetch_music=request.args.get("music") == "1"))
        except ValueError as e:
            return jsonify(error=str(e)), 404
        except assemble.OutOfScope as e:
            return jsonify(error=str(e), nearest_date=nearest(sid, d)), 422
        except FileNotFoundError as e:
            return jsonify(error=str(e)), 503

    @app.post("/api/prefetch")
    def prefetch():
        """Download the music for a service into the cache (so it works without a network on Sunday). ?all=1 for every alternative."""
        d = _date()
        data = compose.compose(d, request.args.get("service", "liturgy"), fetch_music=True)
        con = db.connect()
        n = got = 0
        for sec in data["sections"]:
            for item in sec["music"]:
                for i, a in enumerate(item["assets"]):
                    if request.args.get("all") == "1" or i < music.MAX_PREFETCH:
                        n += 1
                        got += bool(music.fetch_asset(con, a["id"])["cached"])
        return jsonify(date=d.isoformat(), assets=n, cached=got)

    @app.get("/api/music/<int:aid>")
    def music_meta(aid):
        con = db.connect()
        try:
            return jsonify(music.fetch_asset(con, aid))
        except KeyError:
            abort(404)

    @app.get("/api/music/<int:aid>/file")
    def music_file(aid):
        con = db.connect()
        try:
            music.fetch_asset(con, aid)
        except KeyError:
            abort(404)
        data, mime = music.content(con, aid)
        if not data:
            abort(502, description="could not fetch from source")
        return Response(data, mimetype=mime or "application/octet-stream", headers={"Cache-Control": "public, max-age=86400"})

    @app.get("/api/music/<int:aid>/pages")
    def music_pages(aid):
        """Render (once) and count the pages of a score; the UI then loads /page/N.png."""
        con = db.connect()
        try:
            info = music.fetch_asset(con, aid)
        except KeyError:
            abort(404)
        if info["mime"] == "application/pdf":
            music.page_png(con, aid, 1)
        return jsonify(asset_id=aid, mime=info["mime"], pages=con.execute("SELECT COUNT(*) FROM music_page WHERE asset_id=?", (aid,)).fetchone()[0], error=info["error"])

    @app.get("/api/music/<int:aid>/page/<int:n>.png")
    def music_page(aid, n):
        png = music.page_png(db.connect(), aid, n)
        if not png:
            abort(404)
        return Response(png, mimetype="image/png", headers={"Cache-Control": "public, max-age=604800"})

    return app


def in_scope(sid: str, d: dt.date) -> bool:
    try:
        assemble.check_scope(sid, d)
        return True
    except assemble.OutOfScope:
        return False


def nearest(sid: str, d: dt.date) -> str | None:
    for i in range(MAX_SCAN_DAYS):
        if in_scope(sid, d + dt.timedelta(days=i)):
            return (d + dt.timedelta(days=i)).isoformat()
    return None


def next_sunday(d: dt.date | None = None) -> dt.date:
    d = d or dt.date.today()
    return d + dt.timedelta(days=(6 - d.weekday()) % 7)


app = create_app()
