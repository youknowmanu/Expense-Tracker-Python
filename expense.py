from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import matplotlib.pyplot as plt
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<Expense {self.id}>'

# Define routes and views
@app.route('/')
def index():
    expenses = Expense.query.all()
    return render_template('index.html', expenses=expenses)

@app.route('/add', methods=['POST'])
def add_expense():
    amount = float(request.form['amount'])
    category = request.form['category']
    new_expense = Expense(amount=amount, category=category)
    db.session.add(new_expense)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    db.session.delete(expense)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/chart')
def chart():
    categories = db.session.query(Expense.category).distinct()
    category_expenses = {}
    for category in categories:
        total = db.session.query(db.func.sum(Expense.amount)).filter(Expense.category == category[0]).scalar()
        if total:
            category_expenses[category[0]] = total
    labels = category_expenses.keys()
    values = category_expenses.values()
    explode = [0.1] * len(labels)  # Explode all slices for better visibility
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0']  # Custom colors
    plt.figure(figsize=(10, 7))
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140, explode=explode, colors=colors)
    plt.title('Expense Distribution by Category')
    plt.axis('equal')
    chart_path = os.path.join(app.root_path, 'static', 'chart.png')
    plt.savefig(chart_path, transparent=True)
    return render_template('chart.html')

if __name__ == '__main__':
    app.run(debug=True)
