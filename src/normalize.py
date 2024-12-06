class Normalizer:
    pass



# Multiprocessing functions

def get_iterable():
    pass

def worker_init():
    pass

def worker():
    pass

# Main entry point

def normalize_jsonl(inpath: list[str], outpath: str):
    """Normalize text stored in .jsonl files"""
    normalizer = Normalizer()
    normalizer.logger.info(f"Started normalizing {}")
