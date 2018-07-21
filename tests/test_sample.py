# content of test_sample.py
from analyser.main import main 
def func(x):
    return x + 1

def test_answer():
    assert func(3) == 4
