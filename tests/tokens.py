from locust import task, HttpUser, events
from locust.runners import STATE_STOPPING, STATE_STOPPED, STATE_CLEANUP, WorkerRunner
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
import requests
import argparse
import time
import gevent
disable_warnings(InsecureRequestWarning)

parser = argparse.ArgumentParser()
parser.add_argument('-H', '--host')
args, unknown = parser.parse_known_args()
url = str(args.host)+'dev/api/v2/open/assets/'
response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, verify=False)
tokens = response.json()
total_reqs = len(tokens)

class GeneralModules(HttpUser):

    @task
    def tokens(self):
        for token in tokens.keys():
            if token == 'MINTME' or token == 'BTC' or token == 'ETH' or token == 'USDC' or token == 'BNB':
                continue
            with self.client.get('token/'+token, verify=False, catch_response=True) as response:
                if response.elapsed.total_seconds() > 60:
                    response.failure("Request took too long: "+str(response.elapsed.total_seconds()))
                elif response.status_code != 200:
                    response.failure("Code: "+str(response.status_code))

def checker(environment):
    while not environment.runner.state in [STATE_STOPPING, STATE_STOPPED, STATE_CLEANUP]:
        time.sleep(1)
        if environment.runner.stats.num_requests > total_reqs:
            environment.runner.quit()
            return

@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    if not isinstance(environment.runner, WorkerRunner):
        gevent.spawn(checker, environment)