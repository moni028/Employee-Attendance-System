from flask_wtf import FlaskForm
from wtforms import PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Length, Optional, Regexp, ValidationError

from app.models.enums import LeaveType


class EmployeeForm(FlaskForm):
    employee_code = StringField("Employee code", validators=[DataRequired(), Length(max=50)])
    username = StringField("Login username", validators=[DataRequired(), Length(max=80)])
    email = StringField("Email", validators=[DataRequired(), Regexp(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", message="Enter a valid email address."), Length(max=255)])
    first_name = StringField("First name", validators=[DataRequired(), Length(max=100)])
    last_name = StringField("Last name", validators=[DataRequired(), Length(max=100)])
    phone = StringField("Phone", validators=[Optional(), Length(max=30)])
    designation = StringField("Designation", validators=[Optional(), Length(max=120)])
    department_id = SelectField("Department", coerce=int, validators=[DataRequired()])
    joining_date = DateField("Joining date", validators=[DataRequired()], format="%Y-%m-%d")
    password = PasswordField("Initial password", validators=[DataRequired(), Length(min=8, max=128)])
    submit = SubmitField("Create employee")


class EmployeeUpdateForm(FlaskForm):
    employee_code = StringField("Employee code", validators=[DataRequired(), Length(max=50)])
    username = StringField("Login username", validators=[DataRequired(), Length(max=80)])
    email = StringField("Email", validators=[DataRequired(), Regexp(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", message="Enter a valid email address."), Length(max=255)])
    first_name = StringField("First name", validators=[DataRequired(), Length(max=100)])
    last_name = StringField("Last name", validators=[DataRequired(), Length(max=100)])
    phone = StringField("Phone", validators=[Optional(), Length(max=30)])
    designation = StringField("Designation", validators=[Optional(), Length(max=120)])
    department_id = SelectField("Department", coerce=int, validators=[DataRequired()])
    joining_date = DateField("Joining date", validators=[DataRequired()], format="%Y-%m-%d")
    submit = SubmitField("Save changes")


class LeaveRequestForm(FlaskForm):
    leave_type = SelectField("Leave type", choices=[(item.value, item.value.title()) for item in LeaveType], validators=[DataRequired()])
    start_date = DateField("Start date", validators=[DataRequired()], format="%Y-%m-%d")
    end_date = DateField("End date", validators=[DataRequired()], format="%Y-%m-%d")
    reason = TextAreaField("Reason", validators=[DataRequired(), Length(max=2000)])
    submit = SubmitField("Apply for leave")

    def validate_end_date(self, field):
        if self.start_date.data and field.data and field.data < self.start_date.data:
            raise ValidationError("End date must be on or after the start date.")
