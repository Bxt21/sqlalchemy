from flask import Flask, render_template, url_for, redirect, request, flash
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"

DB_TYPE = "postgresql" 
DB_USER = "postgres"
DB_PASSWORD = "schnitzel1229"
DB_HOST = "localhost"
DB_NAME = "genshin"

if DB_TYPE == "postgresql":
    DB_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
elif DB_TYPE == "mysql":
    DB_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
else:
    raise ValueError("Unsupported database type. Use 'postgresql' or 'mysql'.")

app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

bootstrap = Bootstrap5(app)
db = SQLAlchemy(app)

class Region(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, unique=True)
    name: Mapped[str] = mapped_column(unique=True)
    characters = relationship("Character", back_populates="region")

    def __repr__(self):
        return self.name

class Character(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, unique=True)
    name: Mapped[str]
    element: Mapped[str]
    weapon: Mapped[str]
    region_id: Mapped[int] = mapped_column(ForeignKey("region.id"))
    region = relationship("Region", back_populates="characters")

    def __repr__(self):
        return self.name

@app.route("/")
def home():
    characters = Character.query.all()
    return render_template("home.html", characters=characters)

@app.route("/view/<int:id>")
def read(id):
    character = Character.query.get(id)
    return render_template("read.html", character=character)

@app.route("/new", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        name = request.form["name"]
        element = request.form["element"]
        weapon = request.form["weapon"]
        region_id = request.form["region"]
        character = Character(name=name, element=element, weapon=weapon, region_id=region_id)
        db.session.add(character)
        db.session.commit()
        flash(f"{name} added successfully")
    regions = Region.query.all()
    return render_template("create.html", regions=regions)

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def update(id):
    character = Character.query.get(id)
    if request.method == "POST":
        character.name = request.form["name"]
        character.element = request.form["element"]
        character.weapon = request.form["weapon"]
        character.region_id = request.form["region"]
        db.session.commit()
        flash(f"{character.name} edited successfully")
    regions = Region.query.all()
    return render_template("update.html", character=character, regions=regions)

@app.route("/delete/<int:id>")
def remove(id):
    Character.query.filter_by(id=id).delete()
    db.session.commit()
    flash("Deleted successfully")
    return redirect(url_for("home"))

@app.route("/regions")
def list_regions():
    regions = Region.query.all()
    return render_template("regions.html", regions=regions)

@app.route("/regions/new", methods=["GET", "POST"])
def create_region():
    if request.method == "POST":
        name = request.form["name"]
        region = Region(name=name)
        db.session.add(region)
        db.session.commit()
        flash(f"Region {name} added successfully")
    return render_template("create_region.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
