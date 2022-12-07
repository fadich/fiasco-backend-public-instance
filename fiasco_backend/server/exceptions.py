
class RequestError(Exception):

    def __init__(self, *args, status: int = 500):
        self.status = status

        super().__init__(*args)
