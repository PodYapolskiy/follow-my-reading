from rq.worker import Worker
from core.models import load_models


class ModelsWorker(Worker):
    def __init__(self, *args, **kwargs):
        load_models()
        super().__init__(*args, **kwargs)
