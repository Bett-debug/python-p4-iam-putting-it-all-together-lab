from flask import Flask, request, session, make_response, jsonify
from flask_restful import Resource, Api
from models import db, User, Recipe

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "supersecretkey"

db.init_app(app)

with app.app_context():
    db.create_all()

api = Api(app)


# ----------- RESOURCES -----------

class Signup(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_user = User(
                username=data["username"],
                image_url=data.get("image_url", ""),
                bio=data.get("bio", "")
            )
            new_user.password_hash = data["password"]
            db.session.add(new_user)
            db.session.commit()

            session["user_id"] = new_user.id
            return new_user.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 422

class CheckSession(Resource):
    def get(self):
        user_id = session.get("user_id")
        if user_id:
            user = User.query.get(user_id)
            if user:
                return user.to_dict(), 200
        return {"error": "Unauthorized"}, 401

class Login(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(username=data.get("username")).first()
        if user and user.authenticate(data.get("password")):
            session["user_id"] = user.id
            return user.to_dict(), 200
        return {"error": "Invalid credentials"}, 401

class Logout(Resource):
    def delete(self):
        if session.get("user_id"):
            session.pop("user_id")
            return {}, 204
        return {"error": "Unauthorized"}, 401

class RecipeIndex(Resource):
    def get(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized"}, 401

        user = User.query.get(user_id)
        return [recipe.to_dict() for recipe in user.recipes], 200


    def post(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized"}, 401
        data = request.get_json()
        try:
            recipe = Recipe(
                title=data["title"],
                instructions=data["instructions"],
                minutes_to_complete=data["minutes_to_complete"],
                user_id=user_id
            )
            db.session.add(recipe)
            db.session.commit()
            return {
                "id": recipe.id,
                "title": recipe.title,
                "instructions": recipe.instructions,
                "minutes_to_complete": recipe.minutes_to_complete
            }, 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 422

# ----------- ROUTES -----------
api.add_resource(Signup, "/signup")
api.add_resource(CheckSession, "/check_session")
api.add_resource(Login, "/login")
api.add_resource(Logout, "/logout")
api.add_resource(RecipeIndex, "/recipes")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
