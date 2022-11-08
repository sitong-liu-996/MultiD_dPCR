import tkinter as tk
import math
import json
import pandas as pd
import streamlit as st
import hiplot as hip
import holoviews as hv, colorcet as cc
from holoviews.operation.datashader import rasterize

st.set_page_config(layout="wide")
st.markdown("""
<style>
.big-font {
    font-size:50px !important;
}
</style>
""", unsafe_allow_html=True)

st.header('Multi-Dimension dPCR dataset Analysis Dashboard')

st.markdown('''
This is dashboard showing the multiple ways of plots for large scale dPCR dataset
''')

st.header('Upload dataset')

# uploaded dataset
uploaded_file = st.file_uploader("Choose a Run's partition_summary_table.csv file", type='.csv')
data = pd.read_csv(uploaded_file)

# unstack dataset
df1 = data[['Run', 'Sample','Index','Channel', 'C40']]

df = df1.set_index(['Run','Sample', 'Index', 'Channel'])['C40'].unstack()\
  .add_prefix('C40_').rename_axis([None], axis=1).reset_index()
df = df.reindex(['Run', 'Sample', 'Index', 'C40_FAM', 'C40_VIC', 'C40_ABY', 'C40_JUN', 'C40_ROX'], axis=1)

st.dataframe(df)

# multi-D plot
st.header('Multi-Dimension Parallel Plot')

multiD_df = df.reindex(['Run', 'Sample', 'C40_FAM', 'C40_VIC', 'C40_ABY', 'C40_JUN', 'C40_ROX'], axis=1)

sample_slider1 = st.multiselect("Enter Sample Input For Sample Groups",
                                ['A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4',
                                 'C1', 'C2', 'C3', 'C4', 'D1', 'D2', 'D3', 'D4'],
                                ['A1', 'B1', 'C1', 'D1'])
st.write("You entered: ", sample_slider1)

multiD_df1 = multiD_df[multiD_df['Sample'].isin(sample_slider1)]

multiD_plot = hip.Experiment.from_dataframe(multiD_df1)
multiD_plot.to_streamlit(ret="selected_uids", key="hip1").display()


# 2D plot
st.header('2D Plot with sample overlay')
#enter sample array that want to plot on 2D
sample_slider = st.multiselect("Enter Sample Input For 2D plot",
                                ['A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4',
                                 'C1', 'C2', 'C3', 'C4', 'D1', 'D2', 'D3', 'D4'],
                                ['A1', 'B1', 'C1', 'D1'])
st.write("You entered: ", sample_slider)

data1 = df[df['Sample'].isin(sample_slider)]

# enter 2 dye name that want to plot
channel_option = st.selectbox('Choose Dye Combination for 2D Scatter Plot',
                              ('FAM/VIC', 'FAM/ABY', 'FAM/JUN', 'VIC/FAM', 'VIC/ABY', 'VIC/JUN',
                               'JUN/FAM', 'JUN/VIC', 'JUN/ABY', 'ABY/FAM', 'ABY/VIC', 'ABY/JUN'))
channel = ['C40_' + x for x in list(channel_option.split("/")) if isinstance(x, str)]

data2 = data1[['Run', 'Sample','Index', channel[0], channel[1]]]

#plotting
# screen_width = (tk.Tk()).winfo_screenwidth()
# max_width = math.floor(96 * screen_width / 100)  # buffer to adjust
# p1_width = 0.8*max_width
# p2_height = 0.53*p1_width
#points2 = df.hvplot(x='C40_FAM', y='C40_VIC', kind='scatter')
points2 = hv.Points(data2, channel)
ropts2 = dict(tools=['hover'], colorbar=True, colorbar_position='bottom', cmap=cc.rainbow, cnorm='eq_hist',
              xlabel=channel[0], ylabel=channel[1],
              title = (channel[0] + ' vs ' + channel[1] + ' on Selected Arrays'),
              alpha=0.5, width = 900, height = 480)
FAM_VIC2 = rasterize(points2).opts(**ropts2)
st.bokeh_chart(hv.render(FAM_VIC2, backend='bokeh'))
st.dataframe(data2)
