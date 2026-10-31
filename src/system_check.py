import sys
import numpy as np
import pandas as pd
import sklearn
import fastapi

print("=" * 50)
print("       WORLDCORE INITIALIZATION")
print("=" * 50)

print("Python:", sys.version.split()[0])
print("NumPy:", np.__version__)
print("Pandas:", pd.__version__)
print("Scikit-learn:", sklearn.__version__)
print("FastAPI:", fastapi.__version__)

print("\nWORLDCORE ENVIRONMENT READY!")
print("=" * 50)