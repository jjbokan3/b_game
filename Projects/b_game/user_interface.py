import time
import random
facts = open('fun_facts.txt', 'r').read().split('\n')

random.shuffle(facts)

for fact in facts:
    print(fact)
    time.sleep(5)