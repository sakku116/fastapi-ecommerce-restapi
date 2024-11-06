import unittest
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv(override=True)

    loader = unittest.TestLoader()
    suite = loader.discover('tests')

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)