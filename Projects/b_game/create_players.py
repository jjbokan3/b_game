from main import *
import time
local_session = Session(bind=engine)

# new_user = User(username='jona', email='jona@company.com')
#
# local_session.add(new_user)
#
# local_session.commit()

df = create_player_df()
df_dict = df.to_dict('records')

for p in df_dict:
    if p['parent_position'] == 'B':
        new_user = Batter(p['name'], p['parent_position'], p['position'], p['main_rating'], p['handed'], p['attributes'], False, None, True, None)

    else:
        new_user = Pitcher(p['name'], p['parent_position'], p['position'], p['main_rating'], p['handed'], p['attributes'], False, None, 5, None)

    local_session.add(new_user)

    local_session.commit()

    # print(f"Added {p['name']}")
