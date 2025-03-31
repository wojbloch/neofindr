from typing import TypeVar, Any, Callable, Optional, cast, Dict, Type, Union
import http
from functools import wraps
import sys
import json
import time
import os
from django.db import connection
import logging
from logging.handlers import RotatingFileHandler
from django.http import HttpRequest, HttpResponse


F = TypeVar('F', bound=Callable[..., Any])


# log config

CONFIG_FILE = 'log_config.json'

def get_log_level(verbosity: str) -> int:
    if verbosity == '0':
        return logging.WARNING
    elif verbosity == 'v':
        return logging.INFO
    elif verbosity == 'vv':
        return logging.DEBUG
    else:
        return logging.INFO

def cfg_get_verbosity() -> Optional[str]:
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            return config.get('verbosity', 'v')
    return None

def cfg_set_verbosity(level: str) -> None:
    if level not in ['0', 'v', 'vv']:
        raise ValueError("verbosity must be '0', 'v', or 'vv'")
    config = {'verbosity': level}
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)


# logger

def logfunc(func: F) -> F:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any):
        if func.__name__ in CustomLogger.__dict__:
            return func(*args, **kwargs)
        logger = logging.getLogger('custom')
        level = get_log_level(cfg_get_verbosity())
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        if level <= logging.INFO:
            module_name = func.__module__
            func_name = func.__name__
            logger.log(level, f"[{module_name}:{func_name}] executed in {end_time - start_time:.6f}s")
        return result
    return cast(F, wrapper)


class LoggingMeta(type):
    def __new__(cls, name: str, bases: tuple, attrs: Dict[str, any]) -> Type:
        for attr_name, attr_value in attrs.items():
            if callable(attr_value) and not attr_name.startswith('__'):
                attrs[attr_name] = logfunc(attr_value)
        return super().__new__(cls, name, bases, attrs)


class CustomLogger(metaclass=LoggingMeta):
    _instance: Optional['CustomLogger'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CustomLogger, cls).__new__(cls)
            cls._instance.logger = logging.getLogger('custom')
        return cls._instance

    def set_verbosity(self, verbosity: str) -> None:
        if verbosity not in ['0', 'v', 'vv']:
            raise ValueError("verbosity must be '0', 'v', or 'vv'")
        cfg_set_verbosity(verbosity)
        level = get_log_level(verbosity)
        self.logger.setLevel(level)
        for handler in self.logger.handlers:
            handler.setLevel(level)

    def log_request(self, request: HttpRequest, duration: float) -> None:
        level = get_log_level(cfg_get_verbosity())
        if level <= logging.INFO:
            self.logger.info(f"{request.method}: {request.path} (processed in {duration:.6f}s)")
        if level <= logging.DEBUG:
            headers = ', '.join([f"{k}: {v}" for k, v in request.headers.items()])
            self.logger.debug(f"Body: {request.body.decode() if request.body else 'No body'}, Headers: {headers}")

    def log_query(self, query: str, duration: Union[str, float]) -> None:
        level = get_log_level(cfg_get_verbosity())
        if level <= logging.DEBUG:
            try:
                duration = float(duration)
                self.logger.debug(f"Query {query} executed in {duration:.6f}s")
            except ValueError:
                self.logger.error(f"value err {duration}")

    def log_exception(self, exc: Exception) -> None:
        self.logger.exception(f"exception {exc}")

    def log_error(self, status_code: int, method: str, path: str) -> None:
        error_message = http.client.responses.get(status_code, "Error")
        self.logger.warning(f"{error_message}: {method} {path}")


custom_logger = CustomLogger()

def handle_exception(exc_type: Type[BaseException], exc_value: BaseException, exc_traceback: Optional[Any]) -> None:
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    custom_logger.logger.error("stack trace", exc_info=(exc_type, exc_value, exc_traceback))
sys.excepthook = handle_exception


def startupcheck() -> None:
    verbo = cfg_get_verbosity()
    if verbo is None:
        cfg_set_verbosity('v')



# middlewares

class SafeRotatingFileHandler(RotatingFileHandler):
    def __init__(self, filename: str, mode: str = 'a', maxBytes: int =0, backupCount: int = 0, encoding: Optional[str] = None, delay: bool = False):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        logging.handlers.RotatingFileHandler.__init__(self, filename, mode, maxBytes, backupCount, encoding, delay)

class RequestLoggingMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time
        custom_logger.log_request(request, duration)
        return response

class QueryLoggingMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        if custom_logger.logger.level <= logging.DEBUG:
            for query in connection.queries:
                custom_logger.log_query(query['sql'], query['time'])
        return response

class ErrorLoggingMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        try:
            response = self.get_response(request)
            if response.status_code >= 400:
                custom_logger.log_error(response.status_code, request.method, request.path)
            return response
        except Exception as e:
            raise custom_logger.log_exception(e)
