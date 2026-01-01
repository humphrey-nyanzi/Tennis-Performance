import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns

# Title of the dashboard
st.title("Tennis Player Performance Dashboard")
 
# Load the datasets
@st.cache_data
def load_data_1():
    return pd.read_csv('mod_players.csv')  

@st.cache_data
def load_data_2():
    return pd.read_csv('players_yearly_perfomance.csv')  

@st.cache_data
def load_data_3():
    return pd.read_csv('matches.csv')

@st.cache_data
def load_data_4():
    return pd.read_csv('tournaments.csv')

ply_data = load_data_1()
#select only players with more than 50 matches
ply_data = ply_data[ply_data['total_matches'] >= 50]

perf_data = load_data_2()
match_data = load_data_3()
tourn_data = load_data_4()

col_1,col_2,col_3 = st.columns([1,3,1])

def win_loss_data(col):
    '''This function returns a dataframe of the win loss ratio of a player for the different categories of a specified column name'''
    w_stats = match_data.groupby(['w_name', col]).size().reset_index(name='wins')
    w_stats = w_stats.rename({'w_name':'name'},axis = 1)

    l_stats = match_data.groupby(['l_name', col]).size().reset_index(name='losses')
    l_stats = l_stats.rename({'l_name':'name'},axis = 1)

    player_stats = pd.merge(w_stats, l_stats, left_on=['name', col], right_on=['name', col], how='outer')

    # Fill NaN values with 0 (players who haven't lost or won on a particular surface)
    player_stats[['losses','wins']] = player_stats[['losses','wins']].fillna(0)

    # Calculate the total matches played by each player
    player_stats['total_matches'] = player_stats['wins'] + player_stats['losses']

    # Calculate the win/loss ratio for each player
    player_stats['wlr'] = player_stats['wins'] / player_stats['total_matches']

    return player_stats

def win_loss_data_annual(col):
    # Add win and loss indicators
    match_data['win'] = 1
    match_data['loss'] = 0
    match_data.loc[match_data.index, 'loss'] = 1

    # Separate wins and losses
    wins = match_data[['w_name', 't_year', col, 'win']]
    losses = match_data[['l_name', 't_year', col, 'loss']]

    # Rename columns for consistency
    wins.columns = ['player', 't_year', col, 'win']
    losses.columns = ['player', 't_year', col, 'loss']

    # Combine wins and losses
    performance = pd.concat([wins, losses])

    # Group by player, year, and  selected grouping
    performance_grouped = performance.groupby(['player', 't_year', col]).sum()
    performance_grouped.reset_index(inplace=True)

    # Calculate win/loss ratio
    performance_grouped['wlr'] = performance_grouped['win'] / (performance_grouped['win'] + performance_grouped['loss'])

    # Display the result
    return performance_grouped

#Nav section 
with col_1:
    nav_option= st.radio('Go to:',['Player Analysis','Tournament Analysis','Trend Analysis'])

#filter section
with col_3:

    if nav_option == 'Player Analysis':
        # Example: Filter by player
        player = st.selectbox("Select a Player", sorted(ply_data['name'].unique()))

        player_data = ply_data[(ply_data['name'] == player)]
        player_perfomance =perf_data[(perf_data['player'] == player)]
        player_matches = match_data[((match_data['w_name'] == player) | (match_data['l_name'] == player)) ].copy()

        # Add a 'result' column (1 for win, 0 for loss)
        player_matches['result'] = (player_matches['w_name'] == player).astype(int)

        # Sort matches by date
        player_matches = player_matches.sort_values('t_date')

        # Calculate streaks
        player_matches['streak'] = (player_matches['result'] != player_matches['result'].shift()).cumsum()

        # Group by streak and calculate streak lengths
        streak_lengths = player_matches.groupby(['streak', 'result']).size().reset_index(name='streak_length')

        # Identify longest win streak and longest losing streak
        longest_win_streak = streak_lengths[(streak_lengths['result'] == 1)]['streak_length'].max()
        longest_losing_streak = streak_lengths[(streak_lengths['result'] == 0)]['streak_length'].max()

        try:
            # Determine the current streak
            current_streak_length = streak_lengths.iloc[-1]['streak_length']
            current_streak_type = "Winning" if player_matches.iloc[-1]['result'] == 1 else "Losing"
        except IndexError:
            current_streak_length = None
            current_streak_type = None
        
        compare_players = st.checkbox(f'Compare Players')

        if compare_players:
            player_c = st.selectbox("Select a Player", sorted(ply_data['name'].unique()),key="compare_player")

            player_c_data = ply_data[(ply_data['name'] == player_c)]
            player_c_perfomance =perf_data[(perf_data['player'] == player_c)]
            player_c_matches =match_data[((match_data['w_name'] == player_c) | (match_data['l_name'] == player_c))]

            player_c_matches['result'] = (player_c_matches['w_name'] == player_c).astype(int)

            player_c_matches = player_c_matches.sort_values('t_date')
            player_c_matches['streak'] = (player_c_matches['result'] != player_c_matches['result'].shift()).cumsum()

            streak_lengths_c = player_c_matches.groupby(['streak', 'result']).size().reset_index(name='streak_length')

            longest_win_streak_c = streak_lengths_c[(streak_lengths_c['result'] == 1)]['streak_length'].max()
            longest_losing_streak_c = streak_lengths_c[(streak_lengths_c['result'] == 0)]['streak_length'].max()

            current_streak_length_c = streak_lengths_c.iloc[-1]['streak_length']
            current_streak_type_c = "Winning" if player_c_matches.iloc[-1]['result'] == 1 else "Losing"

        show5matches= st.checkbox(f'Show last 5 matches',key = 'matches')

        st.subheader("Filters:")
        filters = ['None','t_name','surface','t_level','best_of','round','t_year','t_month']
        filter_option= st.radio('Filter/Compare By:',filters)
    
    elif nav_option == 'Tournament Analysis':
        tournament = st.selectbox("Select a Tournament", sorted(tourn_data['name'].unique()))
        tournament_data = tourn_data[(tourn_data['name'] == tournament)]

        compare_tournaments = st.checkbox(f'Compare Tournaments')

        if compare_tournaments:
            tournament_c = st.selectbox("Select a Tournament", sorted(tourn_data['name'].unique()),key="compare_tournament")
            tournament_c_data = tourn_data[(tourn_data['name'] == tournament_c)]

    elif nav_option == 'Trend Analysis':
        #select only variables that compare winner-loser performance
        wl_vars = [x[2:] for x in match_data.columns if ((x.startswith('w_')) & (match_data[x].dtype == 'float64')) ]
        wl_var_option= st.radio("Players Variables",wl_vars)

        #select other variables that exclude player perfomance
        other_vars = [x for x in match_data.columns if ((not ((x.startswith('w_') | x.startswith('l_'))))  & (match_data[x].dtype == 'float64'))]
        other_var_option= st.radio("Other Variables",other_vars)

#content section
with col_2:

    if nav_option == 'Player Analysis':
        if compare_players:
            
            section_header = st.header(player + "/"+ player_c)
            col_p,col_c = st.columns([5,5])
            
            if show5matches:
                compare_matches = pd.concat([player_matches, player_c_matches],axis=0,ignore_index=True)
                compare_matches = compare_matches[((compare_matches['w_name'] == player) | (compare_matches['w_name'] == player_c))]
                compare_matches = compare_matches[((compare_matches['l_name'] == player) | (compare_matches['l_name'] == player_c))]
                st.dataframe(compare_matches.sort_values(by='t_year',ascending=False).head(5),hide_index=True)

            if filter_option == 'None':

                def display_player_metrics(player_data, player_perfomance, longest_win_streak, longest_losing_streak, current_streak_length, current_streak_type):
                    st.metric(label = "Country", value = player_data['country'].values[0])
                    st.metric(label = "Career Duration", value = str(player_data['career_duration'].values[0]) + " years")
                    st.metric(label= "Dominant Hand", value= player_data['hand'].values[0])
                    st.metric(label= "Date of Birth", value= player_data['birthdate'].values[0])
                    st.metric(label= "Gender", value = player_data['gender'].values[0].title())
                    st.metric(label='Total Matches', value=player_data['total_matches'].values[0])
                    st.metric(label='Total Wins', value=player_data['wins'].values[0])
                    st.metric(label='Win Percentage', value=str(round((player_data['wlr'].values[0]), 3)) + "%")
                    st.metric(label ='Longest Win Streak', value = longest_win_streak)
                    st.metric(label ='Longest Lose Streak', value = longest_losing_streak)
                    st.metric(label ="Current Streak", value = f'{current_streak_length} ({current_streak_type})')
                    highest_rank = min((player_perfomance['rank'].dropna().values))
                    st.metric(label = "Highest Ranking", value = f'{highest_rank} ({player_perfomance[player_perfomance['rank'] == highest_rank]['t_year'].values[0]})')

                def display_additional_stats(player_data, key_prefix):
                    if st.checkbox('Show more stats', key=f'more_stats_{key_prefix}'):
                        st.metric(label="Serve Games Won Percentage", value=str(round(player_data['serve_game_won%'].values[0], 1)) + "%")
                        st.metric(label="Break Points Saved Percentage", value=str(round(player_data['break_points_saved%'].values[0], 1)) + "%")
                        st.metric(label='Ace Dominance', value=str(player_data['ace_dominance'].values[0]) + "%")
                        st.metric(label="Break Points Per Match", value=player_data['breakpoints_permatch'].values[0])
                with col_p:
                    display_player_metrics(player_data, player_perfomance, longest_win_streak, longest_losing_streak, current_streak_length, current_streak_type)
                    display_additional_stats(player_data, 'p')

                with col_c:
                    display_player_metrics(player_c_data, player_c_perfomance, longest_win_streak_c, longest_losing_streak_c, current_streak_length_c, current_streak_type_c)
                    display_additional_stats(player_c_data, 'c')        


                def combine_and_plot_data(player_data, player_c_data, player_perfomance, player_c_perfomance):
                    combined_data = pd.concat([player_data, player_c_data], axis=0, ignore_index=True)
                    exclude = ['f_year', 'l_year', 'country', 'hand', 'gender', 'birthdate', 'wins', 'losses', 'wlr', 'career_duration', 'total_matches', 'serve_game_won%', 'break_points_saved%', 'breakpoints_permatch', "ace_dominance", 'svpt', '1stIn']
                    numeric_columns = [i for i in combined_data.columns if i not in exclude]
                    combined_data_num = combined_data[numeric_columns]

                    combined_data2 = combined_data_num.melt(id_vars='name', var_name='Metric', value_name='Value')
                    fig = px.bar(combined_data2, x='Metric', y='Value', color='name', barmode='group', title='Player Performance Comparison')
                    st.plotly_chart(fig)

                    combined_performance = pd.concat([player_perfomance, player_c_perfomance], axis=0, ignore_index=True)
                    combined_data_pct = combined_data[['name', 'break_points_saved%', 'serve_game_won%', 'wlr', 'ace_dominance']]
                    combined_data3 = combined_data_pct.melt(id_vars='name', var_name='Metric', value_name='Value')
                    fig = px.bar(combined_data3, x='Metric', y='Value', color='name', barmode='group', title='Player Performance Comparison')
                    st.plotly_chart(fig)

                    fig = px.line(combined_performance, x='t_year', y='wlr', color='player')
                    fig.update_layout(title='Win Percentage', xaxis_title="Year", yaxis_title='Win Percentage', showlegend=True)
                    st.plotly_chart(fig)

                    combined_performance['total_matches'] = combined_performance['win'] + combined_performance['loss']
                    fig = px.line(combined_performance, x='t_year', y='total_matches', color='player')
                    fig.update_layout(title='Total Matches', xaxis_title="Year", yaxis_title='Total Matches', showlegend=True)
                    st.plotly_chart(fig)

                    fig = px.line(combined_performance, x='t_year', y='win', color='player')
                    fig.update_layout(title='Wins', xaxis_title="Year", yaxis_title='Wins', showlegend=True)
                    st.plotly_chart(fig)

                    fig = px.line(combined_performance, x='t_year', y='rank', color='player')
                    fig.update_layout(title='Rank Comparison', xaxis_title="Year", yaxis_title='Rank', showlegend=True)
                    st.plotly_chart(fig)

                combine_and_plot_data(player_data, player_c_data, player_perfomance, player_c_perfomance)

            else:
                st.subheader(f'{filter_option.title()} Comparison')
                wld = win_loss_data(filter_option)
                wld = wld[wld['name'] == player].sort_values(by='wlr',ascending=False)

                wldc = win_loss_data(filter_option)
                wldc = wldc[wldc['name'] == player_c].sort_values(by='wlr',ascending=False)

                col_x,col_y = st.columns([2,2])
                with col_x:
                    st.metric(label=f'Best {filter_option}',value=wld[f'{filter_option}'].values[0])
                    st.metric(label='Win Percentage',value=str(round((wld['wlr'].values[0]*100),1)) + "%")
                    st.metric(label='Total Games',value=wld['total_matches'].values[0])
                    st.metric(label=f'2nd {filter_option}',value=wld[f'{filter_option}'].values[1])
                    st.metric(label='Win Percentage',value=str(round((wld['wlr'].values[1]*100 ),1)) + "%")
                    st.metric(label='Total Games',value=wld['total_matches'].values[1])

                with col_y:
                    st.metric(label=f'Best {filter_option}',value=wldc[f'{filter_option}'].values[0])
                    st.metric(label='Win Percentage',value=str(round((wldc['wlr'].values[0]*100),1)) + "%")
                    st.metric(label='Total Games',value=wldc['total_matches'].values[0])
                    st.metric(label=f'2nd {filter_option}',value=wldc[f'{filter_option}'].values[1])
                    st.metric(label='Win Percentage',value=str(round((wldc['wlr'].values[1]*100 ),1)) + "%")
                    st.metric(label='Total Games',value=wldc['total_matches'].values[1])


                combined_filter_data = pd.concat([wld, wldc],axis=0,ignore_index=True)
                fig = px.bar(combined_filter_data,x=filter_option, y='wlr',color='name',barmode='group',title=f'{filter_option} Comparison')
                fig.update_layout(
                    xaxis_title = filter_option,
                    yaxis_title = 'Win Percentage',
                    showlegend = True
                )
                st.plotly_chart(fig)

                 # Display raw data
                if st.checkbox(f"Show {filter_option} Data",key="wld compare"):
                    st.table(combined_filter_data)
        else:
            section_header = st.header(player)
            if show5matches:
                st.dataframe(player_matches.sort_values(by='t_year',ascending=False).head(5),hide_index=True)
            else:
                if filter_option != 'None':
                    wld = win_loss_data(filter_option)
                    wld = wld[wld['name'] == player].sort_values(by='wlr',ascending=False)
                    
                    col_x,col_y = st.columns([2,2])
                    with col_x:
                        st.metric(label=f'Best {filter_option}',value=wld[f'{filter_option}'].values[0])
                        st.metric(label='Win Percentage',value=str(round((wld['wlr'].values[0] * 100 ),1)) + "%")
                        st.metric(label='Total Games',value=wld['total_matches'].values[0])

                    with col_y:
                        st.metric(label=f'2nd {filter_option}',value=wld[f'{filter_option}'].values[1])
                        st.metric(label='Win Percentage',value=str(round((wld['wlr'].values[1] * 100),1)) + "%")
                        st.metric(label='Total Games',value=wld['total_matches'].values[1])

                    fig = px.bar(wld,x =filter_option,y='wlr')
                    st.plotly_chart(fig)

                    # Display raw data
                    if st.checkbox(f"Show {filter_option} Data",key="wld"):
                        st.table(wld)

                    
                    if filter_option != 't_year':
                        wlda = win_loss_data_annual(filter_option)
                        wlda = wlda[wlda['player'] == player].sort_values(by='wlr',ascending=False)

                        annual_filters =['surface','t_level','best_of']
                        if filter_option in annual_filters:
                            # Plotting the chart
                            plt.figure(figsize=(10, 7))
                            sns.lineplot(data=wlda, x='t_year', y='wlr', hue=filter_option, marker='o')
                            plt.title(f'Win Percentage Over Time for {player} by {filter_option}')
                            plt.xlabel('Year')
                            plt.ylabel('Win Percentage')
                            plt.legend(title=filter_option)

                            st.pyplot(plt)

                        # Display raw data
                    if st.checkbox(f"Show annual {filter_option} Data",key="wlda"):
                        st.table(wlda[wlda['player'] == player])
                    else:
                        pass
                else:
                    col_x,col_y = st.columns([2,2])
                    with col_x:
                        st.metric(label = "Country",value = player_data['country'].values[0])
                        st.metric(label = "Gender",value = player_data['gender'].values[0].title())
                        st.metric(label = "Dominant Hand",value= player_data['hand'].values[0])
                        st.metric(label = "Date of Birth",value = player_data['birthdate'].values[0])
                        st.metric(label ='Longest Win Streak',value =longest_win_streak)
                        st.metric(label ="Current Streak", value = f'{current_streak_length} ({current_streak_type})')

                    with col_y:
                        st.metric(label='Total Matches',value=player_data['total_matches'].values[0])
                        st.metric(label='Total Wins',value=player_data['wins'].values[0])
                        st.metric(label='Win Percentage',value=str(round((player_data['wlr'].values[0] ),1)) + "%")
                        st.metric(label = "Career Duration",value = str(player_data['career_duration'].values[0])+" years")
                        st.metric(label = "Longest Losing Streak", value = longest_losing_streak)
                        highest_rank = min((player_perfomance['rank'].dropna().values))
                        st.metric(label = "Highest Ranking", value = f'{highest_rank} ({player_perfomance[player_perfomance['rank'] == highest_rank]['t_year'].values[0]})')
                        
                        
                    if st.checkbox('Show more stats',key ='more_stats'):
                        col_x,col_y = st.columns([2,2])
                        with col_x:
                            st.metric(label = "Serve Games Wons Percentage",value = str(round(player_data['serve_game_won%'].values[0],1))+ "%")
                            st.metric(label = "Break Points Saved Percentage",value = str(round(player_data['break_points_saved%'].values[0],1))+ "%")
                            

                        with col_y:
                            st.metric(label='Ace Dominance',value=str(player_data['ace_dominance'].values[0]) + "%")
                            st.metric(label = "Break Points Per Match",value = player_data['breakpoints_permatch'].values[0])
                            
                    st.subheader("Win Percentage Over Time")
                    player_perfomance['t_year'] = player_perfomance['t_year'].astype(str)
                    st.line_chart(player_perfomance,x='t_year',y='wlr',x_label='Year',y_label='Win Percentage')

                    st.subheader("Rank Over Time")
                    st.line_chart(player_perfomance,x='t_year',y='rank',x_label='Year',y_label='Rank')

                    st.subheader("Wins Over Time")
                    st.line_chart(player_perfomance,x='t_year',y='win',x_label='Year',y_label='Wins')

                    st.subheader("Total Matches Played Over Time")
                    player_perfomance['total_matches'] = player_perfomance['win'] + player_perfomance['loss']
                    st.line_chart(player_perfomance,x='t_year',y='total_matches',x_label='Year',y_label='Matches Played')


                    # Display raw data
                    if st.checkbox("Show Raw Data",key="raw_data"):
                        st.dataframe(player_data,hide_index=True)
                        st.dataframe(player_perfomance,hide_index=True)

    elif nav_option == 'Tournament Analysis':
        if compare_tournaments:
            col_x,col_y = st.columns([2,2])
            with col_x:
                st.header(tournament)
                st.metric(label = "Surface",value = tournament_data['surface'].values[0])
                st.metric(label = "Best Of",value = tournament_data['best_of'].values[0])
                st.metric(label = "Average Match Duration",value = str(round(tournament_data['minutes'].values[0],1 ))+ ' minutes')
                st.metric(label='Most Wins',value=tournament_data['most_wins'].values[0])
                st.metric(label = "Month Played",value = tournament_data['t_month'].values[0])
                st.metric(label = "Tournament Duration",value = str(tournament_data['tournament_duration'].values[0])+" years")
                st.metric(label = "Total Double Faults",value = str(round(tournament_data['df'].values[0],1 )))
                st.metric(label = "Total Matches Played",value = tournament_data['total_matches'].values[0])

            with col_y:
                st.header(tournament_c)
                st.metric(label = "Surface",value = tournament_c_data['surface'].values[0])
                st.metric(label = "Best Of",value = tournament_c_data['best_of'].values[0])
                st.metric(label = "Average Match Duration",value = str(round(tournament_c_data['minutes'].values[0],1 ))+ ' minutes')
                st.metric(label='Most Wins',value=tournament_c_data['most_wins'].values[0])
                st.metric(label = "Month Played",value = tournament_c_data['t_month'].values[0])
                st.metric(label = "Tournament Duration",value = str(tournament_c_data['tournament_duration'].values[0])+" years")
                st.metric(label = "Total Double Faults",value = str(round(tournament_c_data['df'].values[0],1 )))
                st.metric(label = "Total Matches Played",value = tournament_c_data['total_matches'].values[0])
        else:   
            section_header = st.header(tournament)
            col_x,col_y = st.columns([2,2])
            with col_x:
                st.metric(label = "Surface",value = tournament_data['surface'].values[0])
                st.metric(label = "Best Of",value = tournament_data['best_of'].values[0])
                st.metric(label = "Average Match Duration",value = str(round(tournament_data['minutes'].values[0],1 ))+ ' minutes')
                st.metric(label='Most Wins',value=tournament_data['most_wins'].values[0])
                
            with col_y:
                st.metric(label = "Month Played",value = tournament_data['t_month'].values[0])
                st.metric(label = "Tournament Duration",value = str(tournament_data['tournament_duration'].values[0])+" years")
                st.metric(label = "Total Double Faults",value = str(round(tournament_data['df'].values[0],1 )))
                st.metric(label = "Total Matches Played",value = tournament_data['total_matches'].values[0])

            #line graph showing number of game sper tournament over the years
            tournament_yearly_stats = match_data[match_data['t_name'] == tournament].groupby('t_year').size().reset_index(name='Total Matches')
            fig = px.line(tournament_yearly_stats,x = 't_year',y='Total Matches',title = 'Total Matches Over Years')
            st.plotly_chart(fig)

            #Table showing number of tournament wins by player 
            player_performance = match_data[match_data['t_name'] == tournament]['w_name'].value_counts().reset_index()
            player_performance.columns = ['Player','Wins']
            st.table(player_performance.head(5))

            #surface
            surface_stats = match_data[match_data['t_name'] == tournament].groupby('surface').size().reset_index(name='Matches Played')
            fig = px.pie(surface_stats,names ='surface',values = 'Matches Played',title = 'Surface Distribution')
            st.plotly_chart(fig)

            #head to head comparison
            col_x,col_y = st.columns([2,2])
            with col_x:
                player1 = st.selectbox('Player 1',sorted(match_data['w_name'].unique()))

            with col_y:
                player2 = st.selectbox('Player 2',sorted(match_data['w_name'].unique()))

            head_to_head = match_data[(match_data['t_name'] == tournament) & ((match_data['w_name'] == player1) & (match_data['l_name'] == player2) | (match_data['w_name'] == player2) & (match_data['l_name'] == player1))]
            st.write(head_to_head)

    elif nav_option == 'Trend Analysis':
        st.subheader('Player Perfomance Trends')
        def compare_wl_trends(comp):
            '''This function returns a plt object(graph) of the trend of the variable provided as a parameter'''
            comp_trend = match_data.groupby(['t_year'])[[f'w_{comp}',f'l_{comp}']].mean().sort_values(by=f'w_{comp}',ascending=False).reset_index()
            comp_trend[f'avg_{comp}'] = (comp_trend[f'w_{comp}'] + comp_trend[f'l_{comp}'])/2
            plt.figure(figsize=(10, 7))
            sns.lineplot(data = comp_trend,x='t_year',y=f'w_{comp}',marker='x',label =f'w_{comp}');
            sns.lineplot(data = comp_trend,x='t_year',y=f'avg_{comp}',label =f'avg_{comp}');
            sns.lineplot(data = comp_trend,x='t_year',y=f'l_{comp}',marker='o', label=f'l_{comp}');
            plt.title(f'{comp.title()} over the Years')
            plt.xlabel('Year')
            plt.ylabel(f'{comp}')
            return plt
        st.pyplot(compare_wl_trends(comp = wl_var_option))
        
        st.subheader('Other Performance Trends')
        def metric_per_year(metric):
            len_per_yr = match_data.groupby(['t_year'])[metric].mean().sort_values(ascending=False).reset_index()
            plt.figure(figsize=(10, 7))
            sns.lineplot(data = len_per_yr,x='t_year',y=metric);

            plt.title(f'{metric.title()} over the Years')
            plt.xlabel('Year')
            plt.ylabel(f'Number of {metric} Played')
            plt.show()
            return plt
        st.pyplot(metric_per_year(metric=other_var_option))
        
