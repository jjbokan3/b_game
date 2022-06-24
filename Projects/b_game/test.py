from main import *

player_list = []

df1 = create_player_df()
print(df1.head())

df1_dict = df1.to_dict('records')

for player in df1_dict:
    temp = Player(player['id'], player['name'], player['position'], player['sec_position'], player['main_rating'], player['handed'], player['attributes'])
    player_list.append(temp)


# with open("player_list.txt", "wb") as t:
#     pickle.dump(player_list, t)
# with open("player_list.txt", "rb") as t:
#     list2 = pickle.load(t)

print(player_list[0].__dict__)
