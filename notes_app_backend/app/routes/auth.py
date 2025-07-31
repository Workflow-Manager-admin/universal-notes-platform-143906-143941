from flask_smorest import Blueprint
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
from ..models import User, db
from ..schemas import UserRegisterSchema, UserLoginSchema, UserOutSchema
from ..auth import create_access_token

blp = Blueprint(
    "Auth",
    "auth",
    url_prefix="/auth",
    description="User registration, login, and authentication"
)

@blp.route("/register")
class Register(MethodView):
    """Register a new user."""
    @blp.arguments(UserRegisterSchema)
    @blp.response(201, UserOutSchema)
    def post(self, user_data):
        """
        PUBLIC_INTERFACE
        Register a new user.

        Args:
            user_data (dict): Username, email, password

        Returns:
            UserOutSchema
        """
        if User.query.filter((User.username == user_data['username']) | (User.email == user_data['email'])).first():
            blp.abort(409, message="Username or email already exists.")
        user = User(
            username=user_data['username'],
            email=user_data['email']
        )
        user.set_password(user_data['password'])
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            blp.abort(409, message="Username or email already exists.")
        return user

@blp.route("/login")
class Login(MethodView):
    """User login and JWT issuance."""
    @blp.arguments(UserLoginSchema)
    def post(self, credentials):
        """
        PUBLIC_INTERFACE
        Log in a user and receive a JWT access token.

        Args:
            credentials (dict): email, password

        Returns:
            dict: { token, user info }
        """
        user = User.query.filter_by(email=credentials["email"]).first()
        if user and user.check_password(credentials["password"]):
            token = create_access_token(user.id)
            return {
                "access_token": token,
                "user": UserOutSchema().dump(user)
            }
        blp.abort(401, message="Invalid email or password.")
