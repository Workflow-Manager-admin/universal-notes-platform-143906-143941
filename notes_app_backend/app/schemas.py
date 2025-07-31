from marshmallow import Schema, fields, validate

# PUBLIC_INTERFACE
class UserRegisterSchema(Schema):
    """Schema for user registration input."""
    username = fields.Str(required=True, validate=validate.Length(min=3, max=120), description="Username of the user")
    email = fields.Email(required=True, description="User's email address")
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=6), description="User's password")


# PUBLIC_INTERFACE
class UserLoginSchema(Schema):
    """Schema for user login input."""
    email = fields.Email(required=True, description="User's email address")
    password = fields.Str(required=True, load_only=True, description="User's password")


# PUBLIC_INTERFACE
class UserOutSchema(Schema):
    """Schema for outputting user information."""
    id = fields.Integer()
    username = fields.String()
    email = fields.Email()


# PUBLIC_INTERFACE
class NoteCreateSchema(Schema):
    """Schema for creating a note."""
    title = fields.Str(required=True, validate=validate.Length(min=1, max=255), description="Title of the note")
    content = fields.Str(required=False, allow_none=True, description="Content body of the note")
    category = fields.Str(required=False, allow_none=True, description="Category/tag of the note")


# PUBLIC_INTERFACE
class NoteUpdateSchema(Schema):
    """Schema for updating a note."""
    title = fields.Str(required=False, validate=validate.Length(min=1, max=255))
    content = fields.Str(required=False, allow_none=True)
    category = fields.Str(required=False, allow_none=True)


# PUBLIC_INTERFACE
class NoteOutSchema(Schema):
    """Schema for outputting a note."""
    id = fields.Int()
    title = fields.Str()
    content = fields.Str()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    user_id = fields.Int()
    category = fields.Str()

# Helper for paginated responses
class PaginatedNotesSchema(Schema):
    """Schema for paginated notes output."""
    items = fields.List(fields.Nested(NoteOutSchema))
    total = fields.Int()
    total_pages = fields.Int()
    page = fields.Int()
    next_page = fields.Int(allow_none=True)
    previous_page = fields.Int(allow_none=True)
