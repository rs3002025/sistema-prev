from flask import render_template, url_for, flash, redirect, request
from flask import render_template, url_for, flash, redirect, request
from flask import render_template, url_for, flash, redirect, request, abort, Response
from weasyprint import HTML
from datetime import datetime
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, SimulationForm, FactorForm
from app import User, Simulation, CorrectionFactor, SalaryContribution
from flask_login import login_user, current_user, logout_user, login_required
from app.decorators import admin_required

@app.route("/")
@app.route("/dashboard")
@login_required
def dashboard():
    simulations = Simulation.query.filter_by(author=current_user).order_by(Simulation.created_at.desc()).all()
    return render_template('dashboard.html', simulations=simulations)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/simulation/new", methods=['GET', 'POST'])
@login_required
def create_simulation():
    form = SimulationForm()
    if form.validate_on_submit():
        simulation = Simulation(server_name=form.server_name.data,
                                dob=form.dob.data,
                                benefit_type=form.benefit_type.data,
                                gender=form.gender.data,
                                author=current_user)
        db.session.add(simulation)
        db.session.commit()
        flash('Simulation created! Please enter the salary contributions below.', 'success')
        return redirect(url_for('enter_salaries', simulation_id=simulation.id))
    return render_template('create_simulation.html', title='New Simulation', form=form)

@app.route("/simulation/<int:simulation_id>/salaries", methods=['GET'])
@login_required
def enter_salaries(simulation_id):
    simulation = Simulation.query.get_or_404(simulation_id)
    if simulation.author != current_user:
        abort(403)

    factors = CorrectionFactor.query.order_by(CorrectionFactor.id).all()

    existing_salaries_query = SalaryContribution.query.filter_by(simulation_id=simulation.id).all()
    existing_salaries = {s.month_year: s.amount for s in existing_salaries_query}

    return render_template('enter_salaries.html',
                           title='Enter Salaries',
                           simulation=simulation,
                           factors=factors,
                           existing_salaries=existing_salaries)

@app.route("/simulation/<int:simulation_id>/calculate", methods=['POST'])
@login_required
def calculate_salaries(simulation_id):
    simulation = Simulation.query.get_or_404(simulation_id)
    if simulation.author != current_user:
        abort(403)

    # Clear old salary contributions for this simulation
    SalaryContribution.query.filter_by(simulation_id=simulation.id).delete()

    # Add new salary contributions from the form
    new_salaries = []
    for key, value in request.form.items():
        if key.startswith('salary_') and value:
            try:
                amount = float(value)
                if amount > 0:
                    month_year = key.replace('salary_', '')
                    sc = SalaryContribution(simulation_id=simulation.id,
                                            month_year=month_year,
                                            amount=amount)
                    new_salaries.append(sc)
            except (ValueError, TypeError):
                # Ignore non-numeric values
                continue

    if not new_salaries:
        flash('No salary data provided. Calculation aborted.', 'warning')
        return redirect(url_for('enter_salaries', simulation_id=simulation.id))

    db.session.bulk_save_objects(new_salaries)

    # --- Perform the 90% calculation ---
    all_factors = {f.month_year: f.value for f in CorrectionFactor.query.all()}

    adjusted_salaries = []
    for salary in new_salaries:
        factor = all_factors.get(salary.month_year, 1.0)
        adjusted_salaries.append(salary.amount * factor)

    adjusted_salaries.sort(reverse=True)

    # Calculate how many values are 90%
    count_90_percent = int(len(adjusted_salaries) * 0.9)
    if count_90_percent < 1:
        count_90_percent = 1 if adjusted_salaries else 0

    top_90_percent_salaries = adjusted_salaries[:count_90_percent]

    if top_90_percent_salaries:
        average = sum(top_90_percent_salaries) / len(top_90_percent_salaries)
        simulation.result = average
    else:
        simulation.result = 0

    db.session.commit()

    flash('Calculation complete! The result has been updated.', 'success')
    return redirect(url_for('dashboard'))

# --- Admin Routes ---
@app.route("/admin/factors")
@admin_required
def manage_factors():
    form = FactorForm()
    factors = CorrectionFactor.query.order_by(CorrectionFactor.id.desc()).all()
    return render_template('admin_factors.html', title='Manage Factors', form=form, factors=factors)

@app.route("/admin/factor/add", methods=['POST'])
@admin_required
def add_factor():
    form = FactorForm()
    if form.validate_on_submit():
        factor = CorrectionFactor(month_year=form.month_year.data, value=form.value.data)
        db.session.add(factor)
        db.session.commit()
        flash('Factor has been added!', 'success')
    # Redirect back to the management page, which will display errors if any
    return redirect(url_for('manage_factors'))

@app.route("/admin/factor/<int:factor_id>/edit", methods=['GET', 'POST'])
@admin_required
def edit_factor(factor_id):
    factor = CorrectionFactor.query.get_or_404(factor_id)
    form = FactorForm()
    # Bypass the unique validation when editing
    form.editing = True

    if form.validate_on_submit():
        factor.month_year = form.month_year.data
        factor.value = form.value.data
        db.session.commit()
        flash('Factor has been updated!', 'success')
        return redirect(url_for('manage_factors'))
    elif request.method == 'GET':
        form.month_year.data = factor.month_year
        form.value.data = factor.value

    # We render a different template for editing to have a dedicated page
    return render_template('edit_factor.html', title='Edit Factor', form=form, factor=factor)

@app.route("/admin/factor/<int:factor_id>/delete", methods=['POST', 'GET']) # Allow GET for simple link-based deletion
@admin_required
def delete_factor(factor_id):
    factor = CorrectionFactor.query.get_or_404(factor_id)
    db.session.delete(factor)
    db.session.commit()
    flash('Factor has been deleted!', 'success')
    return redirect(url_for('manage_factors'))

@app.route("/simulation/<int:simulation_id>/pdf")
@login_required
def generate_pdf(simulation_id):
    simulation = Simulation.query.get_or_404(simulation_id)
    if simulation.author != current_user:
        abort(403)

    # --- Re-gather all data needed for the report ---
    all_factors = CorrectionFactor.query.order_by(CorrectionFactor.id).all()
    user_salaries = {s.month_year: s.amount for s in simulation.salaries}

    report_data = []
    adjusted_salaries_for_calc = []
    total_adjusted = 0

    for factor in all_factors:
        salary = user_salaries.get(factor.month_year)
        adjusted = None
        if salary:
            adjusted = salary * factor.value
            adjusted_salaries_for_calc.append(adjusted)
            total_adjusted += adjusted

        report_data.append({
            'month_year': factor.month_year,
            'salary': salary,
            'factor': factor.value,
            'adjusted': adjusted,
        })

    # --- Re-calculate summary numbers ---
    adjusted_salaries_for_calc.sort(reverse=True)
    count_90_percent = int(len(adjusted_salaries_for_calc) * 0.9)
    if count_90_percent < 1:
        count_90_percent = 1 if adjusted_salaries_for_calc else 0

    top_90_percent_salaries = adjusted_salaries_for_calc[:count_90_percent]
    sum_top_90 = sum(top_90_percent_salaries)

    # Render the HTML template for the PDF
    rendered_html = render_template('pdf_template.html',
                                    simulation=simulation,
                                    report_data=report_data,
                                    total_adjusted=total_adjusted,
                                    sum_top_90=sum_top_90,
                                    count_top_90=len(top_90_percent_salaries),
                                    today_date=datetime.utcnow().strftime('%d de %B de %Y'))

    # Generate PDF
    pdf = HTML(string=rendered_html).write_pdf()

    return Response(pdf, mimetype='application/pdf', headers={
        'Content-Disposition': f'attachment;filename=simulation_{simulation.id}.pdf'
    })

@app.route("/simulation/<int:simulation_id>/delete", methods=['POST', 'GET'])
@login_required
def delete_simulation(simulation_id):
    simulation = Simulation.query.get_or_404(simulation_id)
    if simulation.author != current_user:
        abort(403)
    db.session.delete(simulation)
    db.session.commit()
    flash('Simulation has been deleted!', 'success')
    return redirect(url_for('dashboard'))
