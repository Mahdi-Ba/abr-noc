# tasks.py
from celery import Celery

app = Celery('tasks')
app.config_from_object('celeryconfig')

@app.task
def calculate_fuel_cost_task(distance, altitude, air_temperature):
    # Placeholder calculation logic
    fuel_cost = (distance * 0.05) + (altitude * 0.03) + (air_temperature * 0.02)
    return fuel_cost
