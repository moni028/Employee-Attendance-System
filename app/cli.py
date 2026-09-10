import click
from flask import current_app
from flask.cli import with_appcontext

from app.extensions import db
from app.models import User
from app.models.enums import UserRole


@click.command("create-admin")
@click.option("--username", prompt=True, help="Admin username.")
@click.option("--email", prompt=True, help="Admin email address.")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
@with_appcontext
def create_admin(username, email, password):
    """Create the first administrator account for local development."""
    username = username.strip()
    email = email.strip().lower()

    if not username or not email or not password:
        raise click.ClickException("Username, email, and password are required.")
    if db.session.scalar(db.select(User).where(User.username == username)):
        raise click.ClickException("That username already exists.")
    if db.session.scalar(db.select(User).where(User.email == email)):
        raise click.ClickException("That email already exists.")

    user = User(username=username, email=email, role=UserRole.ADMIN)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    current_app.logger.info("Administrator account created: %s", username)
    click.echo(f"Administrator '{username}' created successfully.")
