from flask import Flask, render_template, request, jsonify
import stripe
import pybreaker
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from prometheus_flask_exporter import PrometheusMetrics


app = Flask(__name__)

metrics = PrometheusMetrics(app)

# Stripe API keys
public_key = "pk_test_51Ot6a6F30zvOkJGCS0GTYbkzirFVbRJqPMnkfaH3XsTpniIdmxZhnwm48qqJtzjrSY7u366FkNCjcHQlZWk0FSC100euMGM77q"
stripe.api_key = "sk_test_51Ot6a6F30zvOkJGCDY4QY6ALBOPTj64ixOAU90fXk7OyZycdhmEefT3PnEGUaOAOqw8ILFqelBqtwJnvdYiI0JfH00hWl1rbXq"

# Initialize Flask-Limiter with key_func specified correctly from https://flask-limiter.readthedocs.io/en/stable/
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# Circuit breaker for Stripe API calls
stripe_cb = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=60)

@app.route('/')
def index():
    # Pass the public key to your template
    return render_template('index.html', public_key=public_key)

@app.route('/charge', methods=['POST'])
@limiter.limit("2 per day")
def charge():
    amount = 500  # Assume some amount for demonstration

    def create_charge():
        customer = stripe.Customer.create(
            email=request.form['stripeEmail'],
            source=request.form['stripeToken']
        )
        return stripe.Charge.create(
            customer=customer.id,
            amount=amount,
            currency='usd',
            description='Flask Charge'
        )

    try:
        charge = stripe_cb.call(create_charge)
        return render_template('charge.html', amount=amount)
    except pybreaker.CircuitBreakerError:
        return "Service temporarily unavailable, please try again later.", 503
    except Exception as e:
        return str(e), 500

@app.route('/health')
def health_check():
    # Liveness probe
    return jsonify({"status": "UP"}), 200

@app.route('/ready')
def readiness_check():
    # Readiness probe
    return jsonify({"status": "Ready to serve requests"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
