import sys
from django.conf import settings
from django import http

from iberian.basic.utils import ErrHandle
from iberian.basic.models import Address


class BlockedIpMiddleware(object):

    bot_list = ['googlebot', 'bot.htm', 'bot.com', '/petalbot', 'crawler.com', 'robot', 'crawler',
                'semrush', 'bingbot' ]
    debug_level = 1

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        oErr = ErrHandle()
        if self.debug_level > 1:
            oErr.Status("BlockedIpMiddleware: __call__")

        # First double-check if this is okay...
        response = self.process_request(request)

        if response == None:
            # No problem: we can do what we want
            # oErr.Status("Honoring request")
            response = self.get_response(request)
        else:
            oErr.Status("Denying request")

        return response

    def process_request(self, request):
        oErr = ErrHandle()

        try:
            remote_host = self.get_host(request)
            remote_ip = self.get_client_ip(request)
            path = request.path            

            if self.debug_level > 0 and remote_ip != "127.0.0.1":
                oErr.Status("BlockedIpMiddleware: remote addr = [{}]".format(remote_ip))

            # Check for blocked IP
            if Address.is_blocked(remote_ip, request):
                # Reject this IP address
                oErr.Status("Blocked IP: {}".format(remote_ip))
                return http.HttpResponseForbidden('<h1>Forbidden</h1>')

            bHostOkay = (remote_host in settings.ALLOWED_HOSTS)
            if bHostOkay:
                # CUrrent debugging
                if self.debug_level > 1: 
                    oErr.Status("Host: [{}]".format(remote_host))
            else:
                # Rejecting this host
                oErr.Status("Rejecting host: [{}]".format(remote_host))
                return http.HttpResponseForbidden('<h1>Forbidden</h1>')

            if remote_ip in settings.BLOCKED_IPS:
                oErr.Status("Blocking IP: {}".format(remote_ip))
                return http.HttpResponseForbidden('<h1>Forbidden</h1>')
            else:
                # Try the IP addresses the other way around
                for block_ip in settings.BLOCKED_IPS:
                    if block_ip in remote_ip:
                        oErr.Status("Blocking IP: {}".format(remote_ip))
                        return http.HttpResponseForbidden('<h1>Forbidden</h1>')
                # Get the user agent
                user_agent = request.META.get('HTTP_USER_AGENT')

                if self.debug_level > 1:
                    oErr.Status("BlockedIpMiddleware: http user agent = [{}]".format(user_agent))

                if user_agent == None or user_agent == "":
                    # This is forbidden...
                    oErr.Status("Blocking empty user agent")
                    return http.HttpResponseForbidden('<h1>Forbidden</h1>')
                else:
                    # Check what the user agent is...
                    user_agent = user_agent.lower()
                    for bot in self.bot_list:
                        if bot in user_agent:
                            ip = request.META.get('REMOTE_ADDR')
                            # Print it for logging
                            msg = "blocking bot: [{}] {}: {}".format(ip, bot, user_agent)
                            print(msg, file=sys.stderr)
                            return http.HttpResponseForbidden('<h1>Forbidden</h1>')
        except:
            msg = oErr.get_error_message()
            oErr.DoError("BlockedIpMiddleware/process_request")
        return None

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[-1].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_host(self, request):
        """
        Return the HTTP host using the environment or request headers. Skip
        allowed hosts protection, so may return an insecure host.
        """
        # We try three options, in order of decreasing preference.
        if settings.USE_X_FORWARDED_HOST and (
                'HTTP_X_FORWARDED_HOST' in self.META):
            host = request.META['HTTP_X_FORWARDED_HOST']
        elif 'HTTP_HOST' in request.META:
            host = request.META['HTTP_HOST']
        else:
            # Reconstruct the host, taking the part before a possible colon
            host = request.META['SERVER_NAME']

        # Strip off any colon
        host = host.split(":")[0]
        return host

    def get_port(self, request):
        """Return the port number for the request as a string."""
        if settings.USE_X_FORWARDED_PORT and 'HTTP_X_FORWARDED_PORT' in request.META:
            port = request.META['HTTP_X_FORWARDED_PORT']
        else:
            port = request.META['SERVER_PORT']
        return str(port)

