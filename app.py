from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import logging
from typing import Optional, List

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu-clave-secreta-mas-segura-aqui'  # Cambiar en producción
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vehiculos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_recycle': 300,
    'pool_pre_ping': True
}

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Modelos mejorados
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    vehiculos = db.relationship('Vehiculo', backref='propietario', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Vehiculo(db.Model):
    __tablename__ = 'vehiculos'
    
    id = db.Column(db.Integer, primary_key=True)
    marca = db.Column(db.String(100), nullable=False, index=True)
    modelo = db.Column(db.String(100), nullable=False, index=True)
    año = db.Column(db.Integer, nullable=False, index=True)
    color = db.Column(db.String(50))
    placa = db.Column(db.String(20), unique=True, index=True)
    fecha_compra = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Índices compuestos para búsquedas comunes
    __table_args__ = (
        db.Index('idx_marca_modelo', 'marca', 'modelo'),
        db.Index('idx_user_año', 'user_id', 'año'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'marca': self.marca,
            'modelo': self.modelo,
            'año': self.año,
            'color': self.color,
            'placa': self.placa,
            'fecha_compra': self.fecha_compra.isoformat() if self.fecha_compra else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Context processor para datos comunes
@app.context_processor
def inject_user():
    return dict(current_user=current_user)

# Manejo de errores
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# Rutas de autenticación
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            
            if User.query.filter_by(username=username).first():
                flash('El nombre de usuario ya existe', 'error')
                return render_template('register.html')
            
            if User.query.filter_by(email=email).first():
                flash('El email ya está registrado', 'error')
                return render_template('register.html')
            
            user = User(username=username, email=email)
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registro exitoso. Por favor inicia sesión.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error en registro: {str(e)}")
            flash('Error en el registro. Intenta nuevamente.', 'error')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                login_user(user)
                next_page = request.args.get('next')
                flash('Inicio de sesión exitoso.', 'success')
                return redirect(next_page or url_for('index'))
            else:
                flash('Usuario o contraseña incorrectos', 'error')
                
        except Exception as e:
            logger.error(f"Error en login: {str(e)}")
            flash('Error en el inicio de sesión.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada exitosamente.', 'success')
    return redirect(url_for('index'))

# Rutas principales
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        # Paginación para mejor rendimiento con muchos vehículos
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        vehiculos = Vehiculo.query.filter_by(user_id=current_user.id)\
            .order_by(Vehiculo.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return render_template('dashboard.html', vehiculos=vehiculos)
    except Exception as e:
        logger.error(f"Error en dashboard: {str(e)}")
        flash('Error al cargar el dashboard.', 'error')
        return redirect(url_for('index'))

# API endpoints para AJAX
@app.route('/api/vehiculos')
@login_required
def api_vehiculos():
    try:
        vehiculos = Vehiculo.query.filter_by(user_id=current_user.id).all()
        return jsonify([v.to_dict() for v in vehiculos])
    except Exception as e:
        logger.error(f"Error en API vehiculos: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/agregar_vehiculo', methods=['GET', 'POST'])
@login_required
def agregar_vehiculo():
    if request.method == 'POST':
        try:
            marca = request.form['marca']
            modelo = request.form['modelo']
            año = request.form['año']
            color = request.form['color']
            placa = request.form['placa']
            fecha_compra = request.form['fecha_compra']
            
            # Validaciones
            if Vehiculo.query.filter_by(placa=placa).first():
                flash('La placa ya existe', 'error')
                return render_template('agregar_vehiculo.html')
            
            if fecha_compra:
                fecha_compra = datetime.strptime(fecha_compra, '%Y-%m-%d').date()
            
            vehiculo = Vehiculo(
                marca=marca,
                modelo=modelo,
                año=int(año),
                color=color,
                placa=placa,
                fecha_compra=fecha_compra,
                user_id=current_user.id
            )
            
            db.session.add(vehiculo)
            db.session.commit()
            
            flash('Vehículo agregado exitosamente.', 'success')
            return redirect(url_for('dashboard'))
            
        except ValueError as e:
            flash('Error en los datos ingresados. Verifica el formato.', 'error')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error al agregar vehículo: {str(e)}")
            flash('Error al agregar el vehículo.', 'error')
    
    return render_template('agregar_vehiculo.html')

@app.route('/editar_vehiculo/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_vehiculo(id):
    try:
        vehiculo = Vehiculo.query.filter_by(id=id, user_id=current_user.id).first_or_404()
        
        if request.method == 'POST':
            vehiculo.marca = request.form['marca']
            vehiculo.modelo = request.form['modelo']
            vehiculo.año = int(request.form['año'])
            vehiculo.color = request.form['color']
            vehiculo.placa = request.form['placa']
            
            if request.form['fecha_compra']:
                vehiculo.fecha_compra = datetime.strptime(request.form['fecha_compra'], '%Y-%m-%d').date()
            else:
                vehiculo.fecha_compra = None
            
            # Verificar si la placa ya existe en otro vehículo
            existing = Vehiculo.query.filter(
                Vehiculo.placa == vehiculo.placa,
                Vehiculo.id != id
            ).first()
            
            if existing:
                flash('La placa ya existe en otro vehículo', 'error')
                return render_template('editar_vehiculo.html', vehiculo=vehiculo)
            
            db.session.commit()
            flash('Vehículo actualizado exitosamente.', 'success')
            return redirect(url_for('dashboard'))
        
        return render_template('editar_vehiculo.html', vehiculo=vehiculo)
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al editar vehículo {id}: {str(e)}")
        flash('Error al editar el vehículo.', 'error')
        return redirect(url_for('dashboard'))

@app.route('/eliminar_vehiculo/<int:id>')
@login_required
def eliminar_vehiculo(id):
    try:
        vehiculo = Vehiculo.query.filter_by(id=id, user_id=current_user.id).first_or_404()
        db.session.delete(vehiculo)
        db.session.commit()
        flash('Vehículo eliminado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al eliminar vehículo {id}: {str(e)}")
        flash('Error al eliminar el vehículo.', 'error')
    
    return redirect(url_for('dashboard'))

# Health check para Render
@app.route('/health')
def health_check():
    try:
        # Verificar que la base de datos funciona
        db.session.execute('SELECT 1')
        return jsonify({'status': 'healthy', 'database': 'connected'})
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({'status': 'unhealthy', 'database': 'disconnected'}), 500

# Inicialización de la base de datos
def init_db():
    try:
        db.create_all()
        logger.info("Base de datos inicializada correctamente")
    except Exception as e:
        logger.error(f"Error al inicializar la base de datos: {str(e)}")

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=False, host='0.0.0.0', port=5000)
