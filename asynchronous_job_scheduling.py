from talon import cron

class AsynchronousJobHandler:
    def __init__(self):
        self.job = None
    
    def start_job(self, job_function, time_between_calls_in_milliseconds: int):
        self.job = cron.interval(f'{time_between_calls_in_milliseconds}ms', job_function)

    def stop_job(self):
        if self.job:
            cron.cancel(self.job)
        self.job = None
