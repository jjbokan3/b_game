from main import *
import time
import random
# facts = open('fun_facts.txt', 'r').read().split('\n')
#
# random.shuffle(facts)
#
# for fact in facts:
#     print(fact)
#     time.sleep(5)


local_session = Session(bind=engine)


# Aggregares each players stats for a given year
from collections import defaultdict
bgs = local_session.query(BatterGameStats).filter(BatterGameStats.batter.has(current_team=26)).all()


groups = defaultdict(list)
for obj in bgs:
    groups[obj.batter_id].append(obj)
df = pd.DataFrame([sum(list1).to_dict() for list1 in groups.values()])
df.sort_values('ops', ascending=False, inplace=True)
print(df.head(20))

# TODO: Display the players name instead of id
