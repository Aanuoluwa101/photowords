groups = ['a','b', 'c']

# idx = next((idx for idx, value in enumerate(groups) if value == 'c'), None)
# print(idx)


import random

print(random.sample(groups, 4))