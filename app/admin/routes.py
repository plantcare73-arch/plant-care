"""
Admin routes.
"""
from flask import render_template, session, request, redirect, url_for, flash
from . import admin_bp
from ..utils.decorators import admin_required
from .services import AdminService

@admin_bp.route('/')
@admin_required
def dashboard():
    """Admin dashboard with stats, users, and recent audit logs."""
    stats = AdminService.get_dashboard_stats()
    users = AdminService.get_all_users()
    audit_logs = AdminService.get_audit_logs(limit=15)
    return render_template('admin/dashboard.html', stats=stats, users=users, audit_logs=audit_logs)

@admin_bp.route('/suspend/<user_id>', methods=['POST'])
@admin_required
def suspend_user(user_id):
    AdminService.suspend_user(user_id)
    AdminService.log_action(
        user_id=session.get('user_id'),
        action='toggle_suspend_user',
        target_type='user',
        target_id=user_id
    )
    return {}, 200

@admin_bp.route('/diseases', methods=['GET'])
@admin_required
def diseases():
    """Disease and Treatment Management."""
    diseases = AdminService.get_all_diseases()
    treatments = AdminService.get_all_treatments()
    
    # Map treatments to diseases for easy rendering
    t_map = {}
    for t in treatments:
        if '_id' in t:
            t['_id'] = str(t['_id'])
        t_map[t['disease_class']] = t

    for d in diseases:
        if '_id' in d:
            d['_id'] = str(d['_id'])
        d['treatment'] = t_map.get(d['class_name'], {})
        
    return render_template('admin/diseases.html', diseases=diseases)

@admin_bp.route('/diseases/update', methods=['POST'])
@admin_required
def update_disease():
    class_name = request.form.get('class_name')
    if class_name:
        AdminService.update_disease(class_name, {
            "name": request.form.get('name'),
            "crop": request.form.get('crop'),
            "description": request.form.get('description'),
            "symptoms": [s.strip() for s in request.form.get('symptoms', '').split('\n') if s.strip()]
        })
        AdminService.update_treatment(class_name, {
            "crop": request.form.get('crop'),
            "prevention": [s.strip() for s in request.form.get('prevention', '').split('\n') if s.strip()],
            "chemical_control": [s.strip() for s in request.form.get('chemical_control', '').split('\n') if s.strip()],
            "biological_control": [s.strip() for s in request.form.get('biological_control', '').split('\n') if s.strip()]
        })
        AdminService.log_action(
            user_id=session.get('user_id'),
            action='update_disease_and_treatment',
            target_type='disease',
            target_id=class_name
        )
        flash('Disease & Treatment updated successfully.', 'success')
    return redirect(url_for('admin.diseases'))

@admin_bp.route('/risk_rules', methods=['GET'])
@admin_required
def risk_rules():
    """Risk Rules Management."""
    rules = AdminService.get_all_risk_rules()
    for r in rules:
        if '_id' in r:
            r['_id'] = str(r['_id'])
    return render_template('admin/risk_rules.html', rules=rules)

@admin_bp.route('/risk_rules/update', methods=['POST'])
@admin_required
def update_risk_rule():
    disease_class = request.form.get('disease_class')
    crop = request.form.get('crop')
    AdminService.add_or_update_risk_rule({
        "disease_class": disease_class,
        "crop": crop,
        "min_temp": float(request.form.get('min_temp') or 0),
        "max_temp": float(request.form.get('max_temp') or 50),
        "min_humidity": float(request.form.get('min_humidity') or 0),
        "max_humidity": float(request.form.get('max_humidity') or 100),
        "condition": request.form.get('condition')
    })
    AdminService.log_action(
        user_id=session.get('user_id'),
        action='update_risk_rule',
        target_type='risk_rule',
        target_id=f"{crop}_{disease_class}"
    )
    flash('Risk Rule updated successfully.', 'success')
    return redirect(url_for('admin.risk_rules'))

@admin_bp.route('/risk_rules/delete', methods=['POST'])
@admin_required
def delete_risk_rule():
    disease_class = request.form.get('disease_class')
    crop = request.form.get('crop')
    AdminService.delete_risk_rule(disease_class, crop)
    AdminService.log_action(
        user_id=session.get('user_id'),
        action='delete_risk_rule',
        target_type='risk_rule',
        target_id=f"{crop}_{disease_class}"
    )
    flash('Risk Rule deleted successfully.', 'success')
    return redirect(url_for('admin.risk_rules'))
