import requests
import time
import mimetypes

class HttpLib:
    max_retries = 3
    sleep_duration = 3
    num_calls_per_second = 5  # can run five times per second at most (at 100/20 rate limit)

    def _rate_limited(maxPerSecond):
        minInterval = 1.0 / float(maxPerSecond)
        def decorate(func):
            lastTimeCalled = [0.0]
            def rateLimitedFunction(*args,**kargs):
                elapsed = time.clock() - lastTimeCalled[0]
                leftToWait = minInterval - elapsed
                if leftToWait>0:
                    time.sleep(leftToWait)
                ret = func(*args,**kargs)
                lastTimeCalled[0] = time.clock()
                return ret
            return rateLimitedFunction
        return decorate

    @_rate_limited(num_calls_per_second)
    def get(self, endpoint, args=None, mode=None):
        retries = 1
        while True:
            if retries > self.max_retries:
                return None
            try:
                headers = {'Accept-Encoding': 'gzip'}
                r = requests.get(endpoint, params=args, headers=headers)
                if mode is 'nojson':
                    return r
                else:
                    r_json = r.json()
                    # if we still hit the rate limiter, do not return anything so the call will be retried
                    if 'success' in r_json:  # this is for all normal API calls (but not the access token call)
                        if r_json['success'] == False:
                            print('error from http_lib.py: ' + str(r_json['errors'][0]))
                            if r_json['errors'][0]['code'] in ('606', '615', '604'):
                                # this handles Marketo exceptions; HTTP response is still 200, but error is in the JSON
                                error_code = r_json['errors'][0]['code']
                                error_description = {
                                    '606': 'rate limiter',
                                    '615': 'concurrent call limit',
                                    '604': 'timeout'}
                                if retries < self.max_retries:
                                    print('Attempt %s. Error %s, %s. Pausing, then trying again.' % (retries, error_code, error_description[error_code]))
                                else:
                                    print('Attempt %s. Error %s, %s. This was the final attempt.' % (retries, error_code, error_description[error_code]))
                                time.sleep(self.sleep_duration)
                                retries += 1
                            else:
                                # fatal exceptions will still error out; exceptions caught above may be recoverable
                                return r_json
                        else:
                            return r_json
                    else:
                        return r_json  # this is only for the access token call
            except Exception as e:
                print("HTTP Get Exception! Retrying.....")
                time.sleep(self.sleep_duration)
                retries += 1

    @_rate_limited(num_calls_per_second)
    def post(self, endpoint, args, data=None, files=None, filename=None, mode=None):
        retries = 1
        while True:
            if retries > self.max_retries:
                return None
            try:
                if mode is 'nojsondumps':
                    r = requests.post(endpoint, params=args, data=data)
                elif files is None:
                    headers = {'Content-type': 'application/json'}
                    r = requests.post(endpoint, params=args, json=data, headers=headers)
                elif files is not None:
                    mimetype = mimetypes.guess_type(files)[0]
                    file = {filename: (files, open(files, 'rb'), mimetype)}
                    r = requests.post(endpoint, params=args, json=data, files=file)
                r_json = r.json()
                # if we still hit the rate limiter, do not return anything so the call will be retried
                if 'success' in r_json:  # this is for all normal API calls (but not the access token call)
                    if r_json['success'] == False:
                        print('error from http_lib.py: ' + str(r_json['errors'][0]))
                        if r_json['errors'][0]['code'] in ('606', '615', '604'):
                            # this handles Marketo exceptions; HTTP response is still 200, but error is in the JSON
                            error_code = r_json['errors'][0]['code']
                            error_description = {
                                '606': 'rate limiter',
                                '615': 'concurrent call limit',
                                '604': 'timeout'}
                            if retries < self.max_retries:
                                print('Attempt %s. Error %s, %s. Pausing, then trying again.' % (
                                retries, error_code, error_description[error_code]))
                            else:
                                print('Attempt %s. Error %s, %s. This was the final attempt.' % (
                                retries, error_code, error_description[error_code]))
                            time.sleep(self.sleep_duration)
                            retries += 1
                        else:
                            # fatal exceptions will still error out; exceptions caught above may be recoverable
                            return r_json
                    else:
                        return r_json
                else:
                    return r_json
            except Exception as e:
                print("HTTP Post Exception! Retrying....."+ str(e))
                time.sleep(self.sleep_duration)
                retries += 1

    @_rate_limited(num_calls_per_second)
    def delete(self, endpoint, args, data):
        retries = 0
        while True:
            if retries > self.max_retries:
                return None
            try:
                headers = {'Content-type': 'application/json'}
                r = requests.delete(endpoint, params=args, json=data, headers=headers)
                return r.json()
            except Exception as e:
                print("HTTP Delete Exception! Retrying....."+ str(e))
                time.sleep(self.sleep_duration)
                retries += 1
