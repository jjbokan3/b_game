from main import *

local_session = Session(bind=engine)

user_to_update = local_session.query(Batter).filter(Batter.name.like("Joseph%")).all()

# user_to_update.username = 'johnathon'
#
# user_to_update.email = 'this' + ' this email'
#
# local_session.commit()

for batter in user_to_update:
    try:
        print(f"Power: {batter.attributes['power']}")

    except KeyError:
        print(f"Movement: {batter.attributes['movement']}")

# user_to_update[0].username = 'meredith'
# user_to_update[1].email = 'thisISCOOL@aol.com'
#
# local_session.commit()