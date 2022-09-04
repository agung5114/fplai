import pandas as pd
pd.options.display.float_format = '{:,.2f}'.format
import streamlit as st
# select_team(expected_scores, prices, positions, clubs)
from PIL import Image
st.set_page_config(layout='wide')
from st_aggrid import AgGrid

from data import get_data, update_data, select_team, select_subs, select_main,select_subs2, select_main2,select_subs3, select_main3

@st.cache
def fetch(url):
    df = pd.read_csv(url)
    return df
df = fetch('fpldata.csv')
dff = pd.read_csv('fplstats.csv')

# import base64
# def get_base64(bin_file):
#     with open(bin_file, 'rb') as f:
#         data = f.read()
#     return base64.b64encode(data).decode()
# def set_background(png_file):
#     bin_str = get_base64(png_file)
#     page_bg_img = '''
#     <style>
#     .stApp {
#     background-image: url("data:image/png;base64,%s");
#     background-size: cover;
#     }
#     </style>
#     ''' % bin_str
#     st.markdown(page_bg_img, unsafe_allow_html=True)
# set_background('pitch.jpg')
# st.title('Fantasy PL-AI')
st.image(Image.open('header.png'))
st.title("Fantasy Premier League - Artificial Intelligence")
st.sidebar.image(Image.open('Fantasy PL-ai-logos_transparent.png'))
menu = ["Team_Selection","Player_Analysis"]
choice = st.sidebar.selectbox("Select Menu", menu)

if choice == "Team_Selection":
    try:
        st.sidebar.write('Last Update: '+df['Latest_update'][0])
    except:
        pass
    if st.sidebar.button('Update Data'):
        latest= update_data()
    # st.dataframe(df.sort_values(by='Total_Points',ascending=False))
    # st.dataframe(dff.sort_values(by='Score_index',ascending=False))
    c1,c2 = st.columns((1,1))
    with c1:
        st.subheader("Benchboost Strategy")
        st.text('Maximizing score from all players within the total budget')
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
        dfteam = dfteam.sort_values(by='Pos_code')
        totalscore = dfteam.Scores.sum()
        dfteam.loc[:, "Scores"] = dfteam["Scores"].map('{:.2f}'.format)
        AgGrid(dfteam[['Player_Name','Scores','Price','Position']],fit_columns_on_grid_load=True)
        # st.table(dfteam[['Player_Name','Scores','Price','Position']])
        # st.table(dfteam.sort_values(by='Pos_code'))
        # st.write(f'Player: {names[i],scores[i],price[i],position[pos[i]]}')
        st.write(f'Total Budget : {total}')
        st.write(f'Total Scores Generated : '+'{:.2f}'.format(totalscore))
        for i in range(dff.shape[0]):
            if captains[i].value()==1:
                st.write(f'Captain: {names[i]}')
    with c2:
        st.subheader('Wildcard Strategy')
        st.text('Maximizing score from playing players while minimizing the budget for substitutes')
        formation = ["442","343","433"]
        selectForm = st.selectbox("Select Formation", formation)
        if selectForm =='442':
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
            dfsubs = dfsubs.sort_values(by='Pos_code')
            dfsubs.loc[:, "Scores"] = dfsubs["Scores"].map('{:.2f}'.format)
            AgGrid(dfsubs[['Player_Name','Scores','Price','Position']],fit_columns_on_grid_load=True)

            mains, captmain = select_main(scores.values,price.values,pos.values,team.values,subtotal)
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
            dfmain = dfmain.sort_values(by='Pos_code')
            totalmain = dfmain.Scores.sum()
            dfmain.loc[:, "Scores"] = dfmain["Scores"].map('{:.2f}'.format)
            AgGrid(dfmain[['Player_Name','Scores','Price','Position']],fit_columns_on_grid_load=True)
            st.write(f'Total Budget:{maintotal + subtotal}')
            st.write(f'Total Scores Generated : ' + '{:.2f}'.format(totalmain))

            for i in range(dff.shape[0]):
                if captmain[i].value()==1:
                    st.write(f'Captain: {names[i]}')
        elif selectForm =='343':
            subs = select_subs2(scores.values, price.values, pos.values, team.values)
            subtotal = 0.0
            subName = []
            subScore = []
            subPrice = []
            subPosition = []
            subPos_code = []
            for i in range(dff.shape[0]):
                if subs[i].value() != 0:
                    subName.append(names[i])
                    subScore.append(scores[i])
                    subPrice.append(price[i])
                    subPos_code.append(pos[i])
                    subPosition.append(position[pos[i]])
                    subtotal = subtotal + float(price[i])

            dfdict2 = {'Player_Name': subName, 'Scores': subScore, 'Price': subPrice, 'Pos_code': subPos_code,
                       'Position': subPosition}
            dfsubs = pd.DataFrame(dfdict2)
            st.write(f'Total Subs Budget:{subtotal}')
            dfsubs = dfsubs.sort_values(by='Pos_code')
            dfsubs.loc[:, "Scores"] = dfsubs["Scores"].map('{:.2f}'.format)
            AgGrid(dfsubs[['Player_Name','Scores','Price','Position']],fit_columns_on_grid_load=True)

            mains, captmain = select_main2(scores.values, price.values, pos.values, team.values, subtotal)
            maintotal = 0.0
            mainName = []
            mainScore = []
            mainPrice = []
            mainPosition = []
            mainPos_code = []
            for i in range(dff.shape[0]):
                if mains[i].value() != 0:
                    mainName.append(names[i])
                    mainScore.append(scores[i])
                    mainPrice.append(price[i])
                    mainPos_code.append(pos[i])
                    mainPosition.append(position[pos[i]])
                    maintotal = maintotal + float(price[i])

            dfdict3 = {'Player_Name': mainName, 'Scores': mainScore, 'Price': mainPrice, 'Pos_code': mainPos_code,
                       'Position': mainPosition}
            dfmain = pd.DataFrame(dfdict3)
            st.write(f'Total Main Budget:{maintotal}')
            dfmain = dfmain.sort_values(by='Pos_code')
            totalmain = dfmain.Scores.sum()
            dfmain.loc[:, "Scores"] = dfmain["Scores"].map('{:.2f}'.format)
            AgGrid(dfmain[['Player_Name','Scores','Price','Position']],fit_columns_on_grid_load=True)
            st.write(f'Total Budget:{maintotal + subtotal}')
            st.write(f'Total Scores Generated : ' + '{:.2f}'.format(totalmain))

            for i in range(dff.shape[0]):
                if captmain[i].value() == 1:
                    st.write(f'Captain: {names[i]}')
        elif selectForm =='433':
            subs = select_subs3(scores.values, price.values, pos.values, team.values)
            subtotal = 0.0
            subName = []
            subScore = []
            subPrice = []
            subPosition = []
            subPos_code = []
            for i in range(dff.shape[0]):
                if subs[i].value() != 0:
                    subName.append(names[i])
                    subScore.append(scores[i])
                    subPrice.append(price[i])
                    subPos_code.append(pos[i])
                    subPosition.append(position[pos[i]])
                    subtotal = subtotal + float(price[i])

            dfdict2 = {'Player_Name': subName, 'Scores': subScore, 'Price': subPrice, 'Pos_code': subPos_code,
                       'Position': subPosition}
            dfsubs = pd.DataFrame(dfdict2)
            st.write(f'Total Subs Budget:{subtotal}')
            dfsubs = dfsubs.sort_values(by='Pos_code')
            dfsubs.loc[:, "Scores"] = dfsubs["Scores"].map('{:.2f}'.format)
            AgGrid(dfsubs[['Player_Name','Scores','Price','Position']],fit_columns_on_grid_load=True)

            mains, captmain = select_main3(scores.values, price.values, pos.values, team.values, subtotal)
            maintotal = 0.0
            mainName = []
            mainScore = []
            mainPrice = []
            mainPosition = []
            mainPos_code = []
            for i in range(dff.shape[0]):
                if mains[i].value() != 0:
                    mainName.append(names[i])
                    mainScore.append(scores[i])
                    mainPrice.append(price[i])
                    mainPos_code.append(pos[i])
                    mainPosition.append(position[pos[i]])
                    maintotal = maintotal + float(price[i])

            dfdict3 = {'Player_Name': mainName, 'Scores': mainScore, 'Price': mainPrice, 'Pos_code': mainPos_code,
                       'Position': mainPosition}
            dfmain = pd.DataFrame(dfdict3)
            st.write(f'Total Main Budget:{maintotal}')
            dfmain = dfmain.sort_values(by='Pos_code')
            totalmain = dfmain.Scores.sum()
            dfmain.loc[:, "Scores"] = dfmain["Scores"].map('{:.2f}'.format)
            AgGrid(dfmain[['Player_Name','Scores','Price','Position']])
            st.write(f'Total Budget:{maintotal + subtotal}')
            st.write(f'Total Scores Generated : ' + '{:.2f}'.format(totalmain))


            for i in range(dff.shape[0]):
                if captmain[i].value() == 1:
                    st.write(f'Captain: {names[i]}')

elif choice=="Player_Analysis":
    AgGrid(df,fit_columns_on_grid_load=True)
    # st.dataframe(df)
    # st._arrow_dataframe(df.style.highlight_max(axis=0))