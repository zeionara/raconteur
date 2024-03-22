from time import sleep


def retry(times: int, delay: float = None):
    def retry_(fn):
        def fn_wrapper(*args, **kwargs):
            i = 1

            while True:
                try:
                    return fn(*args, **kwargs)
                except:
                    if i >= times:
                        raise

                i += 1

                if delay is not None:
                    sleep(delay)

        return fn_wrapper
    return retry_
