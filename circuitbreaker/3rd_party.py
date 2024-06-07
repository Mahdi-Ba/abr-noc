from abc import ABC, abstractmethod
import requests
import pybreaker
import redis
import logging

# Set up the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up the redis
redis = redis.StrictRedis()
# redis = redis.StrictRedis(host='redis', port=6379, db=0)
# server_info = redis.info()
# print("Redis Server Version:", server_info['redis_version'])


class ThirdPartyService(ABC):
    def __init__(self, service_name, login_url, user, password, method, service_url, payload=None, retry=1, timeout=5):
        self.service_name = service_name
        self.login_url = login_url
        self.method = method
        self.service_url = service_url
        self.user = user
        self.password = password
        self.payload = payload
        self.timeout = timeout
        self.token = None
        self.retry = retry

    @abstractmethod
    def get_token(self):
        error = None
        for _ in range(self.retry):
            try:
                response = requests.post(self.login_url, json={'user': self.user, 'password': self.password},
                                         timeout=self.timeout)
                response.raise_for_status()
                self.token = response.json().get('token')
                return self.token
            except Exception as e:
                error = e
        raise error

    @abstractmethod
    def make_request(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        error = None
        for _ in range(self.retry):
            try:
                response = requests.request(self.method, self.service_url, json=self.payload, headers=headers,
                                            timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                error = e
        raise error

    def calculate_sla(self):
        pass


    def calculate_cost(self):
        pass


class MyService(ThirdPartyService):
    def get_token(self):
        super().get_token()

    def make_request(self):
        super().make_request()


class NotifyListener(pybreaker.CircuitBreakerListener):
    def state_change(self, cb, old_state, new_state):
        if old_state.name == 'closed' and new_state.name == 'open':
            logger.info('notify %s', cb.name)


breaker = pybreaker.CircuitBreaker(name='test', fail_max=3, reset_timeout=5, listeners=[NotifyListener()],
                                   state_storage=pybreaker.CircuitRedisStorage(pybreaker.STATE_CLOSED, redis,
                                                                               namespace='test'))


@breaker
def test(**kwargs):
    service = MyService("test", "https://example.com/login", "user123", "password456", "POST`",
                        "https://example.com/", )
    service.get_token()
    service.make_request()


# try:
#     test()
# except pybreaker.CircuitBreakerError as e:
#     print("test CircuitBreakerError: The circuit is open. Operation aborted.")
# except Exception as e:
#     print(f"Exception occurred: {e}")
#
breaker_test = pybreaker.CircuitBreaker(name='simple_third_party', fail_max=3, reset_timeout=2, listeners=[NotifyListener()],
                                        state_storage=pybreaker.CircuitRedisStorage(pybreaker.STATE_CLOSED, redis,
                                                                                    namespace='simple_third_party'))


@breaker_test
def simple_third_party(**kwargs):
    service = MyService("test", "https://example.com/login", "user123", "password456", "POST`",
                        "https://example.com/", )
    service.get_token()
    service.make_request()


# try:
#     simple_third_party()
# except pybreaker.CircuitBreakerError as e:
#     print("simple_third_party CircuitBreakerError: The circuit is open. Operation aborted.")
# except Exception as e:
#     print(f"Exception occurred: {e}")


def wrapper_third_party(*function_names, **kwargs):
    for funct in function_names:
        try:
            funct(**kwargs)
            return 'success'
        except pybreaker.CircuitBreakerError as e:
            logger.error(
                f"CircuitBreakerError: The circuit is open. Operation aborted. Function name: {funct.__name__}")
            continue
        except Exception as e:
            logger.error(f"Exception occurred: {e}, Function name: {funct.__name__}")
            continue
    return 'fail'


result = wrapper_third_party(simple_third_party, test, name='reza')
if result == 'fail':
    logger.warning('wrong')
else:
    logger.info('healthy')
