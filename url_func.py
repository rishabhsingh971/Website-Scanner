import requests
import validators
# import socket
import whois
from tld import get_tld

# import time

CONNECTION_OK = "connected to internet"
CONNECTION_NA = "not connected to internet"


# def check_connection2(url='www.google.com/'):
#     # noinspection PyBroadException
#     try:
#         # see if we can resolve the host name -- tells us if there is
#         # a DNS listening
#         host = socket.gethostbyname(url)
#         # connect to the host -- tells us if the host is actually
#         # reachable
#         socket.create_connection((host, 80), 2)
#         return CONNECTION_OK
#     except:
#         pass
#     return CONNECTION_NA


def check_connection(url='http://www.google.com/', timeout=5):
    try:
        req = requests.get(url, timeout=timeout)
        # HTTP errors are not raised by default, this statement does that
        req.raise_for_status()
        # logger.info('-> Connection Status : '+CONNECTION_OK)
        return CONNECTION_OK
    except requests.HTTPError as e:
        rs = "Http Error, status code {0}.".format(e.response.status_code)
        # logger.info('-> Connection Status : '+rs)
        return rs
    except requests.ConnectionError:
        # logger.info('-> Connection Status : '+CONNECTION_NA)
        return CONNECTION_NA
    except requests.RequestException:
        return None


def check_url_syntax(url):
    rv = True
    # noinspection PyBroadException
    try:
        if not validators.url(str(url)):
            rv = False
    except:
        rv = False
    return rv


def return_tld(url):
    return get_tld(url, fail_silently=True)


def get_domain_info(domain):
    return whois.whois(domain)
