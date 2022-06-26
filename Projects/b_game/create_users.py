from main import *


local_session = Session(bind=engine)

# new_user = User(username='jona', email='jona@company.com')
#
# local_session.add(new_user)
#
# local_session.commit()

df = create_player_df()
df_dict = df.to_dict('records')

for p in df_dict:
    new_user = Batter(p['name'], p['parent_position'], p['position'], p['main_rating'], p['handed'], p['attributes'], False, None, True)

    local_session.add(new_user)

    local_session.commit()

    print(f"Added {p['name']}")