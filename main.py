import pandas as pd
import streamlit as st
# select_team(expected_scores, prices, positions, clubs)
from PIL import Image
st.set_page_config(layout='wide')

from data import get_data, update_data, select_team, select_subs, select_main
df = pd.read_csv('fpldata.csv')
dff = pd.read_csv('fplstats.csv')

st.title('Fantasy PL-AI')
st.subheader("Fantasy Premier League - Artificial Intelligence")
menu = ["Team_Selection","Player_Analysis"]
choice = st.sidebar.selectbox("Select Menu", menu)

if choice == "Team_Selection":
    if st.sidebar.button('Update Data'):
        latest= update_data()
    try:
        st.sidebar.write(df['Latest_update'][0])
    except:
        pass
    # st.dataframe(df.sort_values(by='Total_Points',ascending=False))
    # st.dataframe(dff.sort_values(by='Score_index',ascending=False))
    c1,c2 = st.columns((1,1))
    with c1:
        st.subheader("Benchboost Strategy")
        names = dff['Name']
        scores = dff['Score_index']
        pos = dff['Pos_code']
        position = {1:'GKP',2:'DEF',3:'MID',4:'FWD'}
        # pos.append(position[i['element_type']])
        price = dff['Price']
        team = dff['Team_code']
        decisions, captains = select_team(scores.values,price.values,pos.values,team.values)
        total = 0.0
        Name =[]
        Score = []
        Price =[]
        Position =[]
        Pos_code=[]
        for i in range(dff.shape[0]):
            if decisions[i].value()!=0:
                Name.append(names[i])
                Score.append(scores[i])
                Price.append(price[i])
                Pos_code.append(pos[i])
                Position.append(position[pos[i]])
                total = total + float(price[i])

        dfdict = {'Player_Name':Name, 'Scores':Score, 'Price':Price, 'Pos_code': Pos_code,'Position':Position}
        dfteam = pd.DataFrame(dfdict)
        st.table(dfteam.sort_values(by='Pos_code'))
        # st.write(f'Player: {names[i],scores[i],price[i],position[pos[i]]}')
        st.write(f'Total Budget:{total}')
        for i in range(dff.shape[0]):
            if captains[i].value()==1:
                st.write(f'Captain: {names[i]}')
    with c2:
        st.subheader('Wildcard Strategy')

        subs = select_subs(scores.values,price.values,pos.values,team.values)
        subtotal = 0.0
        subName =[]
        subScore = []
        subPrice =[]
        subPosition =[]
        subPos_code=[]
        for i in range(dff.shape[0]):
            if subs[i].value()!=0:
                subName.append(names[i])
                subScore.append(scores[i])
                subPrice.append(price[i])
                subPos_code.append(pos[i])
                subPosition.append(position[pos[i]])
                subtotal = subtotal + float(price[i])

        dfdict2 = {'Player_Name':subName, 'Scores':subScore, 'Price':subPrice, 'Pos_code': subPos_code,'Position':subPosition}
        dfsubs = pd.DataFrame(dfdict2)
        st.write(f'Total Subs Budget:{subtotal}')
        st.table(dfsubs.sort_values(by='Pos_code'))
        # st.write(f'Player: {names[i],scores[i],price[i],position[pos[i]]}')
        tdf = len(dfsubs['Pos_code']==2)
        tmid = len(dfsubs['Pos_code']==3)
        tfw = len(dfsubs['Pos_code']==4)

        mains, captmain = select_main(scores.values,price.values,pos.values,team.values,subtotal,tdf,tmid,tfw)
        maintotal = 0.0
        mainName =[]
        mainScore = []
        mainPrice =[]
        mainPosition =[]
        mainPos_code=[]
        for i in range(dff.shape[0]):
            if mains[i].value()!=0:
                mainName.append(names[i])
                mainScore.append(scores[i])
                mainPrice.append(price[i])
                mainPos_code.append(pos[i])
                mainPosition.append(position[pos[i]])
                maintotal = maintotal + float(price[i])

        dfdict3 = {'Player_Name':mainName, 'Scores':mainScore, 'Price':mainPrice, 'Pos_code': mainPos_code,'Position':mainPosition}
        dfmain = pd.DataFrame(dfdict3)
        st.write(f'Total Main Budget:{maintotal}')
        st.table(dfmain.sort_values(by='Pos_code'))
        # st.write(f'Player: {names[i],scores[i],price[i],position[pos[i]]}')
        st.write(f'Total Budget:{maintotal+subtotal}')

        for i in range(dff.shape[0]):
            if captmain[i].value()==1:
                st.write(f'Captain: {names[i]}')

elif choice=="Player_Analysis":
    st.table(df)