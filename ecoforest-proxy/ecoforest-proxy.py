import sys, logging, datetime, urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, json, requests, urllib.parse

from os import curdir, sep
from http.server import BaseHTTPRequestHandler
from requests.auth import HTTPBasicAuth

# configuration
jdata = json.load(open('/data/options.json'))

DEBUG = bool(jdata['debug'])
DEFAULT_PORT = int(jdata['proxy_port'])
AQUECIMENTO_DHW = bool(jdata['domestic_hot_water'])

host = str(jdata['ecoforest_host'])
username = str(jdata['ecoforest_user'])
passwd = str(jdata['ecoforest_pass'])

ECOFOREST_URL = host + '/recepcion_datos_4.cgi'

if DEBUG:
    FORMAT = '%(asctime)-0s %(levelname)s %(message)s [at line %(lineno)d]'
    logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt='%Y-%m-%dT%I:%M:%S')
else:
    FORMAT = '%(asctime)-0s %(message)s'
    logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt='%Y-%m-%dT%I:%M:%S')

class EcoforestServer(BaseHTTPRequestHandler):

    def send(self, response):
        try:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        except:
            self.send_error(500, 'Something went wrong here on the server side.')


    def healthcheck(self):
        self.send({'status': 'ok'})


    def stats(self):
        if DEBUG: logging.debug('GET stats')
        stats = self.ecoforest_stats()
        if stats:
            self.send(stats)
        else:
            self.send_error(500, 'Something went wrong here on the server side.')

    def temps(self):
        if DEBUG: logging.debug('GET temps')
        temps = self.ecoforest_temps()
        if temps:
            self.send(temps)
        else:
            self.send_error(500, 'Something went wrong here on the server side.')

    def config_temps(self):
        if DEBUG: logging.debug('GET config temps')
        config_temps = self.ecoforest_config_temps()
        if config_temps:
            self.send(config_temps)
        else:
            self.send_error(500, 'Something went wrong here on the server side.')

    def operation_mode(self):
        if DEBUG: logging.debug('GET Operation Mode')
        operation_mode = self.ecoforest_get_operation_mode()
        if operation_mode:
            self.send(operation_mode)
        else:
            self.send_error(500, 'Something went wrong here on the server side getting operation mode.')

    def set_status(self, status):
        if DEBUG: logging.debug('SET STATUS: %s' % (status))
        stats = self.ecoforest_stats()

        # only if 'estado' is off send request to turn on
        if status == "on" and stats['state'] == "off":
            data = self.ecoforest_call('idOperacion=1013&on_off=1')

        # only if 'estado' is on send request to turn off
        if status == "off" and (stats['state'] in ["on", "stand by", "starting"]):
            data = self.ecoforest_call('idOperacion=1013&on_off=0')

        self.send(self.get_status())

    def get_current_operation_mode(self):
        operation_mode = self.ecoforest_get_operation_mode()
        self.send(operation_mode['CONTROL_CLIMA_INVIERNO'])

    def get_status(self):
        stats = self.ecoforest_stats()
        self.send(stats['state'])


    def set_temp(self, temp):
        if DEBUG: logging.debug('SET TEMP: %s' % (temp))
        if float(temp) < 12:
            temp = "12"
        if float(temp) > 40:
            temp = "30"
        # idOperacion=1019&temperatura
        data = self.ecoforest_call('idOperacion=1019&temperatura=' + temp)
        self.send(self.ecoforest_stats())

    def set_operation_mode(self, mode):
        if DEBUG: logging.debug('SET Operation Mode: %s' % (mode))
        if AQUECIMENTO_DHW:
            # check if mode is valid
            if int(mode) < 0 or int(mode) > 2:
                return
            stats = self.ecoforest_stats()
            # check if is turned off, otherwise do nothing
            if stats['state'] == "off":
                data = self.ecoforest_call('idOperacion=1152&CONTROL_CLIMA_INVIERNO=' + mode)
                print(data)
                self.send(self.ecoforest_get_operation_mode())

    def set_power(self, power):
        stats = self.ecoforest_call('idOperacion=1002')
        reply = dict(e.split('=') for e in stats.text.split('\n')[:-1]) # discard last line ?
        power_now = reply['consigna_potencia']
        power_now = int(power_now)
        logging.info('Power %s issued, stove power is at %s' % (power, power_now))

        if DEBUG: logging.debug('POWER: %s' % (power_now))
        if  power == "up":
            if power_now < 9:
                power_final = power_now + 1
                logging.info('Stove will change to %s' % power_final)
            else:
                if DEBUG: logging.debug('POWER at MAX: %s' % (power_now))
                power_final = power_now
                logging.info('Stove at MAX: %s' % power_final)
        if power == "down":
            if (power_now <= 9 and power_now > 1):
                power_final = power_now - 1
                logging.info('Stove will change to %s' % power_final)
            else:
                if DEBUG: logging.debug('POWER at MIN: %s' % (power_now))
                power_final = power_now
                logging.info('Stove at MIN: %s' % power_final)
        # idOperacion=1004&potencia=
        data = self.ecoforest_call('idOperacion=1004&potencia=' + str(power_final))
        print(data)
        self.send(self.ecoforest_stats())

    def ecoforest_temps(self):
        if AQUECIMENTO_DHW:
            if DEBUG: logging.debug('Get Operation Temps')
            temps = self.ecoforest_call('idOperacion=1129')
            reply = dict(e.split('=') for e in temps.text.split('\n')[:-1]) # discard last line ?
            return reply
        return

    def ecoforest_config_temps(self):
        if AQUECIMENTO_DHW:
            if DEBUG: logging.debug('Get Configuration Temps')
            config_temps = self.ecoforest_call('idOperacion=1130')
            reply = dict(e.split('=') for e in config_temps.text.split('\n')[:-1]) # discard last line ?
            return reply
        return

    def ecoforest_get_operation_mode(self):
        if AQUECIMENTO_DHW:
            if DEBUG: logging.debug('Get Operation Mode')
            current_operation_mode = self.ecoforest_call('idOperacion=1153')
            reply = dict(e.split('=') for e in current_operation_mode.text.split('\n')[:-1]) # discard last line ?
            states = {
                '0'  : 'aqs + heating',
                '1'  : 'aqs',
                '2'  : 'heating'
            }
            state = reply['CONTROL_CLIMA_INVIERNO']
            if state in states: 
                reply['state'] = states[state]
            else:
                reply['state'] = 'unknown'
                logging.debug('reply: %s', reply)

            return reply
        return

    def ecoforest_set_operation_mode(self, option):
        # 0 - AQS + Heating
        # 1 - AQS
        # 2 - Heating 
        if AQUECIMENTO_DHW:
            operation_mode = self.ecoforest_call('idOperacion=1152&CONTROL_CLIMA_INVIERNO=' + str(option))
            print(operation_mode)
            self.send(self.ecoforest_get_operation_mode())
            

    def ecoforest_stats(self):
        stats = self.ecoforest_call('idOperacion=1002')
        reply = dict(e.split('=') for e in stats.text.split('\n')[:-1]) # discard last line ?

        states = {
            '0'  : 'off',
            '1'  : 'off',
            '2'  : 'starting', 
            '3'  : 'starting', 
            '4'  : 'starting', 
            '5'  : 'starting', 
            '6'  : 'starting', 
            '10' : 'starting', 
            '7'  : 'on', 
            '8'  : 'shutting down', 
            '-2' : 'shutting down', 
            '9'  : 'shutting down', 
            '11' : 'shutting down', 
            '-3' : 'alarm',
            '-4' : 'alarm',
            '20' : 'stand by',
        }

        state = reply['estado']
        if state in states: 
            reply['state'] = states[state]
        else:
            reply['state'] = 'unknown'
            logging.debug('reply: %s', reply)

        return reply


    # queries the ecoforest server with the supplied contents and parses the results into JSON
    def ecoforest_call(self, body):
        if DEBUG: logging.debug('Request:\n%s' % (body))
        headers = { 'Content-Type': 'application/json' }
        try: 
            request = requests.post(ECOFOREST_URL, data=body, headers=headers, auth=HTTPBasicAuth(username, passwd), timeout=2.5)
            if DEBUG: logging.debug('Request:\n%s' %(request.url))
            if DEBUG: logging.debug('Result:\n%s' %(request.text))
            return request
        except requests.Timeout:
            pass


    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        args = dict()
        if parsed_path.query:
            args = dict(qc.split("=") for qc in parsed_path.query.split("&"))

        if DEBUG: logging.debug('GET: TARGET URL: %s, %s' % (parsed_path.path, parsed_path.query))
        content_len = int(self.headers.getheader('content-length', 0))
        post_body = self.rfile.read(content_len)

        dispatch = {
            '/ecoforest/status': self.set_status,
        }

        # API calls
        if parsed_path.path in dispatch:
            try:
                dispatch[parsed_path.path](post_body, **args)
            except:
                self.send_error(500, 'Something went wrong here on the server side.')
        else:
            self.send_error(404,'File Not Found: %s' % parsed_path.path)

        return


    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        args = dict()
        if parsed_path.query:
            args = dict(qc.split("=") for qc in parsed_path.query.split("&"))
        
        dispatch = {
            '/healthcheck': self.healthcheck,
            '/ecoforest/fullstats': self.stats,
            '/ecoforest/operationtemps': self.temps,
            '/ecoforest/configtemps': self.config_temps,
            '/ecoforest/operationmode': self.operation_mode,
            '/ecoforest/status': self.get_status,
            '/ecoforest/set_status': self.set_status,
            '/ecoforest/set_temp': self.set_temp,
            '/ecoforest/set_operationmode': self.set_operation_mode,
            '/ecoforest/set_power': self.set_power,
        }

        # API calls
        if parsed_path.path in dispatch:
            try:
                dispatch[parsed_path.path](**args)
            except:
                self.send_error(500, 'Something went wrong here on the server side.')
        else:
            self.send_error(404,'File Not Found: %s' % parsed_path.path)

        return


if __name__ == '__main__':
    try:
        from http.server import HTTPServer
        server = HTTPServer(('', DEFAULT_PORT), EcoforestServer)
        logging.info('Ecoforest proxy server has started.')
        server.serve_forever()
    except Exception as e:
        logging.error(e)
        sys.exit(2)
