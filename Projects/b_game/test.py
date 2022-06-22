# def big_function(num1: int, num2: int) -> int:
#     """
#     This function adds the two arguments
#     Args:
#         num1: First number
#         num2: Second number
#
#     Returns:
#         Sum of ''num1'' and ''num2''
#     """
#     return num1 + num2

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ba = np.around(np.random.normal(70, 7, 20000))

pd.Series(ba).hist()