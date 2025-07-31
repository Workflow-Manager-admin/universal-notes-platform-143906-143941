from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request
from sqlalchemy import or_, desc
from ..models import Note, db
from ..schemas import (
    NoteCreateSchema,
    NoteUpdateSchema,
    NoteOutSchema,
    PaginatedNotesSchema,
)
from ..auth import jwt_required

blp = Blueprint(
    "Notes",
    "notes",
    url_prefix="/notes",
    description="CRUD and search operations for notes"
)

def get_pagination():
    """Helper for extracting pagination params from request."""
    try:
        page = int(request.args.get("page", "1"))
        per_page = min(int(request.args.get("per_page", "10")), 50)
        return page, per_page
    except Exception:
        return 1, 10

def notes_query_base(user_id):
    """Base query for notes with filter by user."""
    return Note.query.filter_by(user_id=user_id)

@blp.route("/")
class NotesListCreate(MethodView):
    """Create a note or get notes (with filter, search, pagination)."""
    @jwt_required
    @blp.arguments(NoteCreateSchema)
    @blp.response(201, NoteOutSchema)
    def post(self, data):
        """
        PUBLIC_INTERFACE
        Create a new note for the authenticated user.
        """
        user_id = request.user_id
        note = Note(
            title=data["title"],
            content=data.get("content", ""),
            category=data.get("category"),
            user_id=user_id,
        )
        db.session.add(note)
        db.session.commit()
        return note

    @jwt_required
    @blp.response(200, PaginatedNotesSchema)
    def get(self):
        """
        PUBLIC_INTERFACE
        List all notes for the authenticated user (with optional filters and pagination).

        Query params:
            - q: search query for title/content
            - category: filter by category/tag
            - page: int, results page (default 1)
            - per_page: int, results per page (default 10, max 50)
        """
        user_id = request.user_id
        q = request.args.get("q")
        category = request.args.get("category")
        sort = request.args.get("sort", "updated_at") # default sort
        desc_order = request.args.get("desc", "true") == "true"

        query = notes_query_base(user_id)
        if q:
            query = query.filter(or_(
                Note.title.ilike(f"%{q}%"),
                Note.content.ilike(f"%{q}%")
            ))
        if category:
            query = query.filter_by(category=category)
        # Sorting
        if sort in ["created_at", "updated_at", "title", "category"]:
            col = getattr(Note, sort)
            query = query.order_by(desc(col) if desc_order else col)
        page, per_page = get_pagination()
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return {
            "items": [NoteOutSchema().dump(note) for note in pagination.items],
            "total": pagination.total,
            "total_pages": pagination.pages,
            "page": page,
            "previous_page": pagination.prev_num if pagination.has_prev else None,
            "next_page": pagination.next_num if pagination.has_next else None,
        }

@blp.route("/<int:note_id>")
class NoteDetail(MethodView):
    """Get, update, or delete a specific note."""
    @jwt_required
    @blp.response(200, NoteOutSchema)
    def get(self, note_id):
        """
        PUBLIC_INTERFACE
        Get details of a specific note (must be owned by user).
        """
        user_id = request.user_id
        note = Note.query.filter_by(id=note_id, user_id=user_id).first_or_404()
        return note

    @jwt_required
    @blp.arguments(NoteUpdateSchema)
    @blp.response(200, NoteOutSchema)
    def put(self, update_data, note_id):
        """
        PUBLIC_INTERFACE
        Update a note (must be owned by user).
        """
        user_id = request.user_id
        note = Note.query.filter_by(id=note_id, user_id=user_id).first_or_404()
        for field in ["title", "content", "category"]:
            if field in update_data and update_data[field] is not None:
                setattr(note, field, update_data[field])
        db.session.commit()
        return note

    @jwt_required
    def delete(self, note_id):
        """
        PUBLIC_INTERFACE
        Delete a note (must be owned by user).
        """
        user_id = request.user_id
        note = Note.query.filter_by(id=note_id, user_id=user_id).first_or_404()
        db.session.delete(note)
        db.session.commit()
        return {"message": "Note deleted successfully."}
