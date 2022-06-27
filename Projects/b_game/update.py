from main import *

local_session = Session(bind=engine)

user_to_update = local_session.query(Batter).filter(Batter.name.like("Joseph%")).all()

# user_to_update.username = 'johnathon'
#
# user_to_update.email = 'this' + ' this email'
#
# local_session.commit()

# user_to_update[2].main_rating = 32
# print(user_to_update[2].main_rating)
user_to_update.sort(key=lambda x: x.main_rating, reverse=True)

user_to_update[0].main_rating = 102

print(user_to_update)

# for user in user_to_update:
#     print(user.name, user.main_rating)

# user_to_update[0].username = 'meredith'
# user_to_update[1].email = 'thisISCOOL@aol.com'
#
local_session.commit()

# Joseph Luciano 71