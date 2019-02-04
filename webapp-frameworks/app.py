import os
import subprocess
import flask
import json


app = flask.Flask(__name__, template_folder='templates')
app.secret_key = 'secret_key'


@app.route('/frameworks/<framework>', methods=['PUT'])
def start_tests(framework):
    # check if there's a test still running
    pid_filename = f'/tmp/{framework}.pid'
    if os.path.exists(pid_filename):
        return json.dumps(dict(message='Tests still running', category='WARNING'))

    script = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        '../scripts/run_framework.sh'
    ))
    try:
        # TODO: parse arguments from website
        # WRK arguments
        env = os.environ.copy()
        env['TEST_HTTP_SERVER'] = '0.0.0.0'
        env['TEST_HTTP_PORT'] = '5000'
        p = subprocess.Popen([
            '/bin/bash', script, framework
        ], env=env)
        out, err = p.communicate()
        return json.dumps(dict(message=f'Successfully started {framework}', stdout=out, stderr=err, category='INFO'))
    except subprocess.CalledProcessError as e:
        return json.dumps(dict(message=f'Encountered error when attempting to start {framework}', stderr=e, category='ERROR'))


@app.route('/frameworks/<framework>', methods=['GET'])
def status(framework):
    pid_filename = f'/tmp/{framework}.pid'
    if not os.path.exists(pid_filename):
        return json.dumps(dict(message='Framework is not running', category='WARNING'))

    with open(pid_filename, 'r') as f:
        pid = f.read().strip()

    return json.dumps(dict(message=f'Framework running in PID: {pid}', category='WARNING'))


@app.route('/frameworks/<framework>', methods=['DELETE'])
def stop(framework):
    pid_filename = f'/tmp/{framework}.pid'
    if not os.path.exists(pid_filename):
        return json.dumps(dict(message='Framework is not running', category='WARNING'))

    script = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        '../scripts/stop_framework.sh'
    ))
    try:
        p = subprocess.Popen([
            '/bin/bash', script, framework
        ])
        out, err = p.communicate()
        return json.dumps(dict(message=f'Successfully stopped {framework}', stdout=out, stderr=err, cagegory='INFO'))
    except subprocess.CalledProcessError as e:
        return json.dumps(dict(message=f'Encountered error when attempting to stop {framework}', stderr=e, category='ERROR'))


if __name__ == '__main__':
    app.run(
        '0.0.0.0',
        port=5000,
        debug=True
    )
