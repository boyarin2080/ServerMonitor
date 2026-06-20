from flask import Flask, jsonify, render_template_string
import psutil
import platform

app = Flask(__name__)


def get_cpu_temp():
    # Проверяем, поддерживает ли текущая ОС датчики температуры в psutil
    if not hasattr(psutil, "sensors_temperatures"):
        return "N/A"  # Для Windows вернет N/A без вылета ошибки

    try:
        temps = psutil.sensors_temperatures()
        if 'coretemp' in temps and temps['coretemp']:
            return temps['coretemp'][0].current
        elif 'cpu_thermal' in temps and temps['cpu_thermal']:  # Для Raspberry Pi
            return temps['cpu_thermal'][0].current
        return "N/A"
    except:
        return "N/A"


def get_cpu_model():
    """Получаем модель процессора"""
    try:
        # Для Linux/Unix систем
        if platform.system() == "Linux":
            try:
                with open('/proc/cpuinfo', 'r') as f:
                    for line in f:
                        if line.startswith('model name'):
                            return line.split(':')[1].strip()
            except:
                pass
        
        # Альтернативный вариант через platform
        return platform.processor() or platform.machine()
    except:
        return "Unknown"


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Server Monitor</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: sans-serif; background: #121212; color: #fff; text-align: center; padding: 50px; }
        .container { display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; }
        .card { background: #1e1e1e; padding: 20px; border-radius: 10px; min-width: 150px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        h1 { color: #00adb5; }
        .value { font-size: 24px; font-weight: bold; margin-top: 10px; color: #eeeeee; }
        .cpu-model { 
            font-size: 16px; 
            color: #a0a0a0; 
            margin-top: 20px; 
            padding: 10px; 
            background: #2a2a2a; 
            border-radius: 5px; 
            max-width: 600px; 
            margin-left: auto; 
            margin-right: auto;
        }
    </style>
</head>
<body>
    <h1>Домашний сервер</h1>
    <div class="container">
        <div class="card"><h3>CPU Загрузка</h3><div class="value" id="cpu">0%</div></div>
        <div class="card"><h3>ОЗУ (занято / всего)</h3><div class="value" id="ram">0 / 0 GB</div></div>
        <div class="card"><h3>Температура CPU</h3><div class="value" id="temp">0°C</div></div>
    </div>
    <div class="cpu-model" id="cpu_model">Загрузка модели процессора...</div>
    <script>
        async function updateStats() {
            try {
                const res = await fetch('/api/stats');
                const data = await res.json();
                document.getElementById('cpu').innerText = data.cpu + '%';
                document.getElementById('ram').innerText = data.ram_used + ' / ' + data.ram_total + ' GB';
                document.getElementById('temp').innerText = data.cpu_temp === 'N/A' ? 'N/A' : data.cpu_temp + '°C';
                document.getElementById('cpu_model').innerText = data.cpu_model || 'Unknown';
            } catch (e) { console.error("Ошибка обновления:", e); }
        }
        setInterval(updateStats, 2000);
        updateStats();
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/stats')
def stats():
    # Контейнеру нужен доступ к хостовому /proc и /sys через psutil
    vm = psutil.virtual_memory()
    return jsonify({
        'cpu': psutil.cpu_percent(interval=None),
        'ram_used': round(vm.used / (1024 ** 3), 2),
        'ram_total': round(vm.total / (1024 ** 3), 2),
        'cpu_temp': get_cpu_temp(),
        'cpu_model': get_cpu_model()
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)