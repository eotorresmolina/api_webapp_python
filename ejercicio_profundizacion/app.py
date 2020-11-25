__author__ = "Emmanuel Oscar Torres Molina"
__email__ = "emmaotm@gmail.com"
__version__ = "1.1"


import os
import traceback
import io
from flask import Flask, request, render_template, jsonify, Response
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib import pyplot as plt
from config import config
import insight


script_path = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(script_path, 'config.ini')

endpoints = config('endpoints', config_path)
server = config('server', config_path)

templates = config('templates', config_path)


def bar_plot(x, y, title=None, color='darkblue', x_label=None, y_label=None):
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.set_title = (title)
    ax.bar(x, y, color=color)
    ax.set_xlabel(x_label, fontsize=15)
    ax.set_ylabel(y_label, fontsize=15)
    ax.set_facecolor('lightyellow')
    plt.grid(True)

    return fig


app = Flask(__name__)

@app.route(endpoints['index'])
def index():
    try:
        return render_template(templates['welcome'])
    
    except:
        jsonify({'trace': traceback.format_exc()})


@app.route(endpoints['graph_temperat'])
def graph_temperat():
    try:
        data = insight.report(graph=True, name_table='atm_temperat')

        x = [sol[0] for sol in data]
        y = [abs(value[1]) if (value[1] is not None) else 0 for value in data]

        title = 'Average Atmospheric Temperature [°C]'
        labels = ['Number of days (or sols, on Mars)', 'Negative Temperature Value']

        figure = bar_plot(x, y, title, color='darkgreen', 
                    x_label=labels[0], y_label=labels[1])

        output = io.BytesIO()
        FigureCanvas(figure).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')

    except:
        return jsonify({'trace': traceback.format_exc()})


@app.route(endpoints['graph_pressure'])
def graph_pressure():
    try:
        data = insight.report(graph=True, name_table='atm_pressure')

        x = [sol[0] for sol in data]
        y = [value[1] if (value[1] is not None) else 0 for value in data]

        title = 'Average Atmospheric Pressure [Pa]'
        labels = ['Number of days (or sols, on Mars)', '[Pa]']

        figure = bar_plot(x, y, title, color='darkblue', 
                    x_label=labels[0], y_label=labels[1])

        output = io.BytesIO()
        FigureCanvas(figure).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')

    except:
        return jsonify({'trace': traceback.format_exc()})


@app.route(endpoints['table_temperat'])
def table_temperat():
    try:
        data = insight.report(graph=False, name_table='atm_temperat')

        x = [sol[0] for sol in data]
        y = [value[1] for value in data]

        return render_template(templates['table_temperat'], row=zip(x,y))

    except:
        return jsonify({'trace': traceback.format_exc()})


@app.route(endpoints['table_pressure'])
def table_pressure():
    try:
        data = insight.report(graph=False, name_table='atm_pressure')

        x = [sol[0] for sol in data]
        y = [value[1] for value in data]

        return render_template(templates['table_pressure'], row=zip(x,y))

    except:
        return jsonify({'trace': traceback.format_exc()})
    
    

if __name__ == "__main__":
    # Creamos la DB:
    insight.create_schema()

    # Cargamos la DB:
    insight.fill(table='temperature')
    insight.fill(table='pressure')

    #Corremos el Server:
    app.run(host=server['host'],
            port=server['port'],
            debug='True')
    
    