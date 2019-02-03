import os
import subprocess
import flask


app = flask.Flask(__name__, template_folder='templates')
app.secret_key = 'secret_key'
report_directory = os.path.join(os.path.dirname(__file__), '../reports')
frameworks_directory = os.path.join(os.path.dirname(__file__), '../frameworks')
pid_filename = os.path.join(os.path.dirname(__file__), '../__.pid')


@app.route('/')
def home():
    _list = []
    for framework in sorted(filter(
            lambda x: os.path.isdir(x),
            map(lambda x: os.path.join(frameworks_directory, x), os.listdir(frameworks_directory))
    )):
        try:
            size = subprocess.check_output([
                'du', '-s', os.path.abspath(os.path.join(framework, 'lib'))
            ]).split()[0].decode('utf-8')
        except subprocess.CalledProcessError as e:
            size = 0

        try:
            last_run = open(os.path.join(
                framework,
                'last_run.txt'
            )).read()
        except FileNotFoundError as e:
            last_run = None

        _list.append(dict(
            name=os.path.basename(framework),
            size=size,
            last_run=last_run
        ))

    return flask.render_template('template.html', frameworks=_list)


def is_process_running(pid):
    try:
        p = subprocess.check_output([
            'ls', '-l', f'/proc/{pid.decode("utf-8")}/exe'
        ], stderr=subprocess.STDOUT, timeout=3)
        # TODO: verify it exists?
        return True
    except subprocess.CalledProcessError as e:
        if e.output.decode('utf-8').startswith(f'ls: /proc/{pid}/exe: No such file or directory'):
            return False
        else:
            raise e


def is_process_running_ps(pid):
    proc1 = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE)
    proc2 = subprocess.Popen(['grep', pid.decode('utf-8')], stdin=proc1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # proc3 = subprocess.Popen(['awk', "'{print $2}'"], stdin=proc2.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Allow proc1 to receive a SIGPIPE if proc2 exits.
    proc1.stdout.close()
    out, err = proc2.communicate()
    is_running = len(pid) > 0 and pid in out
    return is_running


@app.route('/start/', methods=['POST'])
def start_tests():
    # check if there's a test still running
    try:
        pid = open(pid_filename, 'rb').read()
        if is_process_running(pid):
            flask.flash(message='Tests still running', category='WARNING')
            return flask.redirect(flask.url_for('home'))
    except FileNotFoundError:
        pass


    script = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        '../scripts/launch_framework_test.sh'
        # '../scripts/test.sh'
    ))
    try:
        # TODO: parse arguments from website
        # WRK arguments
        env = os.environ.copy()
        env['DURATION'] = '20'
        env['CONNECTIONS'] = '200'
        env['THREADS'] = '10'
        env['TIMEOUT'] = '10'
        p = subprocess.Popen([
            '/bin/bash', script
        ], env=env)
        with open(pid_filename, 'wb') as f:
            print(f"Launched Process: {p.pid}")
            f.write(bytes(str(p.pid), encoding='utf-8'))

        flask.flash(message='Tests initiated', category='INFO')
    except subprocess.CalledProcessError as e:
        flask.flash(message='', category='ERROR')

    return flask.redirect(flask.url_for('home'))


@app.route('/download/<filename>')
def download(filename):
    filename = filename or 'results.csv'
    return flask.send_from_directory(directory=report_directory, filename=filename)


if __name__ == '__main__':
    app.run(
        '0.0.0.0',
        port=5000,
        debug=True
    )
