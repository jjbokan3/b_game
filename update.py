from main import *

local_session = Session(bind=engine)

players = local_session.query(Batter.id).all()

print(len(players)

# Joseph Luciano 71