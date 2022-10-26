from locust import task, HttpUser, events
from locust.runners import STATE_STOPPING, STATE_STOPPED, STATE_CLEANUP, WorkerRunner
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
import time
import gevent
disable_warnings(InsecureRequestWarning)

routes = [
    'register/',
    'login',
    'resetting/request',
    'news',
    'kb',
    'voting',
    'trade',
    'coin/MINTME/BTC',
    'coin/MINTME/ETH',
    'coin/MINTME/USDC',
    'coin/MINTME/BNB'
    ]
total_reqs = len(routes)

class GeneralModules(HttpUser):

    @task
    def register(self):
        for route in routes:
            with self.client.get(route, verify=False, catch_response=True) as response:
                if response.elapsed.total_seconds() > 60:
                    response.failure("Request took too long: "+str(response.elapsed.total_seconds()))
                elif response.status_code != 200:
                    response.failure("Code: "+str(response.status_code))

def checker(environment):
    while not environment.runner.state in [STATE_STOPPING, STATE_STOPPED, STATE_CLEANUP]:
        time.sleep(1)
        if environment.runner.stats.num_requests == total_reqs:
            environment.runner.quit()
            return

@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    if not isinstance(environment.runner, WorkerRunner):
        gevent.spawn(checker, environment)