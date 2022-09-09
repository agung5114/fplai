import pandas as pd
pd.options.display.float_format = '{:,.2f}'.format
import streamlit as st
# select_team(expected_scores, prices, positions, clubs)
from PIL import Image
st.set_page_config(layout='wide')
from st_aggrid import AgGrid
import plotly_express as px
from data import get_data, update_data, select_team, select_subs, select_main,select_subs2, select_main2,select_subs3, select_main3

# @st.cache
# def fetch(url):
#     df = pd.read_csv(url)
#     return df
# df = fetch('fpldata.csv')
df = pd.read_csv('fpldata2.csv')
dff = pd.read_csv('fplstats2.csv')
# Converting links to html tags
def path_to_image_html(path):
    return '<img src="' + path + '" width="60" >'

def photo_html(path):
    return '<img src="' + path + '" width="250" >'

@st.cache
def convert_df(input_df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return input_df.to_html(escape=False, formatters=dict(Photo=path_to_image_html))

st.image(Image.open('header.png'))
st.title("Fantasy Premier League - Artificial Intelligence")
st.sidebar.image(Image.open('Fantasy PL-ai-logos_transparent.png'))
menu = ["Team_Selection","Player_Stats","Compare_Players"]
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
        photo = dff['Photo']
        decisions, captains = select_team(scores.values,price.values,pos.values,team.values)
        total = 0.0
        Name =[]
        Score = []
        Price =[]
        Position =[]
        Pos_code=[]
        Photo =[]
        for i in range(dff.shape[0]):
            if decisions[i].value()!=0:
                Name.append(names[i])
                Score.append(scores[i])
                Price.append(price[i])
                Pos_code.append(pos[i])
                Position.append(position[pos[i]])
                Photo.append((photo[i]))
                total = total + float(price[i])

        dfdict = {'Player_Name':Name, 'Scores':Score, 'Price':Price, 'Pos_code': Pos_code,'Position':Position,'Photo':Photo}
        dfteam = pd.DataFrame(dfdict)
        dfteam = dfteam.sort_values(by='Pos_code')
        totalscore = dfteam.Scores.sum()
        dfteam.loc[:, "Scores"] = dfteam["Scores"].map('{:.2f}'.format)
        # AgGrid(dfteam[['Player_Name','Scores','Price','Position']],fit_columns_on_grid_load=True)
        html1 = convert_df(dfteam)
        st.markdown(
            html1,
            unsafe_allow_html=True
        )
        st.write(f'Total Budget : '+'{:.2f}'.format(total))
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
        elif selectForm =='343':
            subs = select_subs2(scores.values, price.values, pos.values, team.values)
        elif selectForm =='433':
            subs = select_subs3(scores.values, price.values, pos.values, team.values)

        subtotal = 0.0
        subName =[]
        subScore = []
        subPrice =[]
        subPosition =[]
        subPos_code=[]
        subPhoto=[]
        for i in range(dff.shape[0]):
            if subs[i].value()!=0:
                subName.append(names[i])
                subScore.append(scores[i])
                subPrice.append(price[i])
                subPos_code.append(pos[i])
                subPosition.append(position[pos[i]])
                subtotal = subtotal + float(price[i])
                subPhoto.append(photo[i])

        dfdict2 = {'Player_Name':subName, 'Scores':subScore, 'Price':subPrice, 'Pos_code': subPos_code,'Position':subPosition,'Photo':subPhoto}
        dfsubs = pd.DataFrame(dfdict2)
        dfsubs = dfsubs.sort_values(by='Pos_code')
        dfsubs.loc[:, "Scores"] = dfsubs["Scores"].map('{:.2f}'.format)
        # AgGrid(dfsubs[['Player_Name','Scores','Price','Position']],fit_columns_on_grid_load=True)
        mains, captmain = select_main(scores.values,price.values,pos.values,team.values,subtotal)
        maintotal = 0.0
        mainName =[]
        mainScore = []
        mainPrice =[]
        mainPosition =[]
        mainPos_code=[]
        mainPhoto=[]
        for i in range(dff.shape[0]):
            if mains[i].value()!=0:
                mainName.append(names[i])
                mainScore.append(scores[i])
                mainPrice.append(price[i])
                mainPos_code.append(pos[i])
                mainPosition.append(position[pos[i]])
                maintotal = maintotal + float(price[i])
                mainPhoto.append(photo[i])

        dfdict3 = {'Player_Name':mainName, 'Scores':mainScore, 'Price':mainPrice, 'Pos_code': mainPos_code,'Position':mainPosition,'Photo':mainPhoto}
        dfmain = pd.DataFrame(dfdict3)
        dfmain = dfmain.sort_values(by='Pos_code')
        totalmain = dfmain.Scores.sum()
        dfmain.loc[:, "Scores"] = dfmain["Scores"].map('{:.2f}'.format)
        # AgGrid(dfmain[['Player_Name','Scores','Price','Position']],fit_columns_on_grid_load=True)
        html2 = convert_df(dfmain)
        st.write(f'Total Main Budget:{maintotal}')
        st.markdown(
            html2,
            unsafe_allow_html=True
        )
        st.write(f'Total Subs Budget:{subtotal}')
        html3 = convert_df(dfsubs)
        st.markdown(
            html3,
            unsafe_allow_html=True
        )
        st.write(f'Total Budget:{maintotal + subtotal}')
        st.write(f'Total Scores Generated : ' + '{:.2f}'.format(totalmain))

        for i in range(dff.shape[0]):
            if captmain[i].value()==1:
                st.write(f'Captain: {names[i]}')

elif choice == "Player_Stats":
    k1, k2 = st.columns((1, 1))
    with k1:
        dfpoint = df.nlargest(5, 'Total_Points')
        dfpoint = dfpoint.sort_values('Total_Points', ascending=True)
        fig1a = px.bar(dfpoint, y='Name', x='Total_Points', orientation='h',title='Top Points')
        st.plotly_chart(fig1a)
        # dfgoal = df.nlargest(5, 'Form')
        # dfgoal = dfgoal.sort_values('Goals', ascending=True)
        # fig1b = px.bar(dfgoal, y='Name', x='Goals', orientation='h', title='Top Goals')
        # st.plotly_chart(fig1b)
    with k2:
        dfform = df.nlargest(5, 'Form')
        dfform = dfform.sort_values('Form', ascending=True)
        fig2a = px.bar(dfform, y='Name', x='Form', orientation='h', title='Top Forms')
        st.plotly_chart(fig2a)
        # dfassist = df.nlargest(5, 'Assists')
        # dfassist = dfassist.sort_values('Assists', ascending=True)
        # fig2b = px.bar(dfassist, y='Name', x='Assists', orientation='h', title='Top Assists')
        # st.plotly_chart(fig2b)
    df['Points'] = df['Total_Points']
    df1 = df.drop(['Photo','Total_Points'], axis=1)
    # AgGrid(df1,fit_columns_on_grid_load=True)
    st.dataframe(df1)
elif choice=="Compare_Players":
    from plotly import graph_objects as go
    p1,p2 = st.columns((1,1))
    with p1:
        pl = st.selectbox('Select Player 1',df['Name'])
        if pl == []:
            st.write('Please Select A Player')
        else:
           df2 = df[df['Name']==pl]
           dff2 = dff[dff['Name']==pl]
           st.markdown(
               photo_html(df2['Photo'].tolist()[0]),
               unsafe_allow_html=True
           )
           # st.write(dff2)
           fig = go.Figure()
           categories = ['goals','assists','clean_sheets','inv_fdr','ppg']
           fig.add_trace(go.Scatterpolar(
               r=[df2['Goals'].tolist()[0],df2['Assists'].tolist()[0],df2['Clean_Sheets'].tolist()[0],dff2['Inv_FDR'].tolist()[0],dff2['Point_per_game'].tolist()[0]],
               theta=categories,
               fill='toself',
               name='Product A'
           ))
           fig.update_layout(
               polar=dict(
                   radialaxis=dict(
                       visible=True,
                       range=[0, dff['Point_per_game'].max()]
                   )),
               showlegend=False
           )
           st.plotly_chart(fig)
           df_merged = df2[['Total_Points','Goals','Assists','Clean_Sheets']].melt().append(dff2[['Inv_FDR','Point_per_game','ICT_index']].melt())
           st.table(df_merged[['variable','value']])
    with p2:
        pl2 = st.selectbox('Select Player 2',df['Name'])
        # if pl2!=[]:
        if pl2==[]:
           st.write('Please Select A Player')
        else:
           df2a = df[df['Name']==pl2]
           dff2a = dff[dff['Name']==pl2]
           st.markdown(
               photo_html(df2a['Photo'].tolist()[0]),
               unsafe_allow_html=True
           )
           # st.write(dff2)
           fig2 = go.Figure()
           categories = ['goals','assists','clean_sheets','inv_fdr','ppg']
           fig2.add_trace(go.Scatterpolar(
               r=[df2a['Goals'].tolist()[0],df2a['Assists'].tolist()[0],df2a['Clean_Sheets'].tolist()[0],dff2a['Inv_FDR'].tolist()[0],dff2a['Point_per_game'].tolist()[0]],
               theta=categories,
               fill='toself',
               name='Product A'
           ))
           fig2.update_layout(
               polar=dict(
                   radialaxis=dict(
                       visible=True,
                       range=[0, dff['Point_per_game'].max()]
                   )),
               showlegend=False
           )
           st.plotly_chart(fig2)
           df_merged2 = df2a[['Total_Points','Goals','Assists','Clean_Sheets']].melt().append(dff2a[['Inv_FDR','Point_per_game','ICT_index']].melt())
           st.table(df_merged2[['variable','value']])

