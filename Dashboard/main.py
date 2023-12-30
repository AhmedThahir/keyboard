from utils import *

import plotly.express as px
from glob import glob
import streamlit as st

import time

import streamlit as st
from streamlit_extras.no_default_selectbox import selectbox

import plotly.graph_objs as go
from plotly.subplots import make_subplots

import pandas as pd
import numpy as np
from collections import Counter
import os

from nltk import ngrams

def main():
	common_styles()

	views = ["Home", "Difficulty Scores", "Layout Mappings",
			 "Layouts Unigram Summary Difficulty", "Text File Difficulties"]

	view = st.sidebar.radio(
		"View",
		views,
		label_visibility="collapsed"
	)

	if view == views[0]:
		st.markdown("""
			# 👋 Welcome!

			👈 Use the sidebar to navigate.
			
			Feel to explore the data to your ❤️'s content
		""")
	else:
		# Importing Data
		mappings_unigram = get_mappings_unigram()
		mappings_bigram = get_mappings_bigram(mappings_unigram)

		data_unigram = get_data_unigram()

		data_bigram_raw = get_data_bigram()
		data_bigram = clean_data_bigram(data_bigram_raw)

		layout_difficulties = calc_unigram_difficulties(
			mappings_unigram, data_unigram)
		layout_summary = aggregate(layout_difficulties)

		bigram_penalties = calc_bigram_penalties(
			mappings_bigram, data_bigram, data_unigram)

		mappings_unigram = mappings_unigram.set_index("Required_Output")
		data_unigram = data_unigram.set_index("Key_Code")

		available_layouts = list(mappings_unigram.columns)  # [1:]

		if view != views[1]:
			with st.sidebar:
				st.divider()
				st.title("Filters")

			selected_layouts = st.sidebar.multiselect(
				label="Layouts",
				placeholder="All",
				options=available_layouts,
				format_func=lambda x: x.replace("_", " ")
			)

			if len(selected_layouts) == 0:
				layouts = available_layouts
			else:
				layouts = selected_layouts
			mappings_unigram = mappings_unigram[layouts]

		if view == views[1]:
			st.markdown(f"# {views[1]}")

			st.header("Unigram")

			heatmap = calc_data_unigram_heatmap(data_unigram.reset_index())
			heatmap_figure = go.Figure(go.Heatmap(
				# name = layout,
				x=heatmap["Col"],
				y=heatmap["Row"],
				z=heatmap["Difficulty"],
				hoverongaps=False,
				colorscale="OrRd",
				colorbar={"title": "Difficulty Score"},
			))

			heatmap_figure.update_layout(
				# title = "Unigram Difficulty Score",
				height=500,
				# plot_bgcolor=px.colors.sequential.OrRd[0]
			)
			heatmap_figure.update_xaxes(dict(
				ticklen=0,
				showgrid=False,
				tickmode='linear',
				tick0=1,
				dtick=1
			))
			heatmap_figure.update_yaxes(dict(
				ticklen=0,
				showgrid=False,
				tickmode='linear',
				tick0=1,
				dtick=1
			))

			st.plotly_chart(heatmap_figure, config=PLOTLY_CONFIG,
							use_container_width=True)
			st.dataframe(
				data_unigram,
				use_container_width=True
			)

			st.header("Bigram")
			st.dataframe(
				data_bigram_raw.set_index("Row"),
				use_container_width=True
			)
		elif view == views[2]:
			st.markdown(f"# {views[2]}")
			st.dataframe(
				mappings_unigram,
				use_container_width=True,
				height = 800
			)
		elif view == views[3]:
			st.markdown(f"# {views[3]}")

			st.markdown(r"""
			$$
			\Large
			\begin{aligned}
			\text{UD}_\text{Layout}
			&= \frac{
				\text{Total Unigram Penalty}
			}{
				\text{Number of Unigrams}
			} \\
			&= \frac{
				\sum \limits_{\text{Key } i} \Big( \text{Frequency}_i \times \text{Penalty}_{\text{Layout Key } i} \Big)
			}{
				\text{Number of Unigrams}
			}   
			\end{aligned}
			$$
			""")

			boxplot(layout_difficulties[layouts])
			st.dataframe(
				layout_summary,
				use_container_width=True
			)
		elif view == views[4]:
			st.markdown(f"# {views[4]}")

			t1, t2, t3 = st.tabs(["Scores", "Relative Usage", "Input Text Statistics"])

			input_folder = "./input_files"
			genres = os.listdir(input_folder)
			genres.sort()

			with st.sidebar:
				label = "Genres"
				selected_genres = st.multiselect(
					label=label,
					placeholder="All",
					options=genres,
				)

				if len(selected_genres) == 0:
					selected_genres = genres

				input_files = []
				for genre in selected_genres:
					# get_files()
					input_files += glob(
						f"./input_files/{genre}/*.txt", recursive=False)

				if len(input_files) == 0:
					st.stop()

				# input_files.sort()

				label = "Files"
				selected_files = st.multiselect(
					label=label,
					placeholder="All",
					options=input_files,
					format_func=get_file_name
				)

				if len(selected_files) == 0:
					selected_files = input_files  # st.stop()

				st.divider()

				accuracy = st.sidebar.slider(
					'Accuracy %',
					1, 100,
					92,
					step=1,
					format="%d%%"
				)
				accuracy /= 100

				# cpm = st.sidebar.slider(
				# 	'Characters Per Minute',
				# 	1, 600,
				# 	175,
				# 	step=10
				# )

				# spm = st.slider(
				# 	'Saves Per Minute',
				# 	1, 10,
				# 	1,
				# 	step=1
				# )

			text_content = get_text_content(selected_files)

			frequency_unigram, input_char_count = analyze_file_unigrams(
				text_content, accuracy #, cpm, spm
			)

			frequency_bigram = analyze_file_bigram(
				text_content
			)

			if input_char_count == 0:
				st.stop()

			merged_unigram = (
				frequency_unigram
				.merge(layout_difficulties, how="inner", left_index=True, right_index=True)
			)

			frequency_bigram = frequency_bigram.reset_index()
			frequency_bigram = frequency_bigram.rename(columns={
				"level_0": "Key_1",
				"level_1": "Key_2"
			}).set_index(["Key_1", "Key_2"])

			merged_bigram = frequency_bigram.merge(
				bigram_penalties,
				how="inner",  # inner since only same hand bigrams have penalties
				left_on=["Key_1", "Key_2"],
				right_on=["Key_1", "Key_2"],
			)

			merged_ngrams = pd.concat(
				[merged_unigram, merged_bigram]
			)
			frequency_ngrams = pd.concat(
				[frequency_unigram, frequency_bigram]
			)

			text_file_ngram_difficulties = merged_ngrams[layouts+["Frequency"]].pipe(
				analyze_total_ngram_difficulty, input_char_count)
			text_file_ngram_summary = text_file_ngram_difficulties[layouts].round(
				2).T.rename(columns={"sum": "Weighted_Average"}).sort_values("Weighted_Average")

			with t1:
				st.markdown(r"""
				$$
				\Large
				\begin{aligned}
				S_\text{Layout} &= \frac{
					\text{Total Penalty}_\text{Layout}
				}{
					\text{Input Character Count}
				} \\
				&= \frac{
					\sum \limits_{i=\text{Key}} \Big(
						\text{Frequency}_i \times \text{Penalty}_{\text{Layout Key } i}
					\Big)
				}{
					\text{Input Character Count}
				}
				\end{aligned}
				$$
				""")

				bar(text_file_ngram_difficulties)

				st.dataframe(
					text_file_ngram_summary,
					use_container_width=True
				)

			heatmap = calc_unigram_heatmap(
				mappings_unigram, frequency_unigram, input_char_count)

			# total_rows = 2
			total_cols = 2
			heatmap_figure = make_subplots(
				rows=(len(layouts)+1)//total_cols,
				cols=total_cols,
				# vertical_spacing = 0.5,
				# horizontal_spacing = 0.15,
				subplot_titles=[layout.replace(
					"_", " ") for layout in layouts]
			)

			row = 1
			col = 0
			for layout in layouts:
				if col == total_cols:
					col = 1
					row += 1
				else:
					col += 1

				heatmap_figure.add_trace(go.Heatmap(
					# name = layout,
					x=heatmap["Col"],
					y=heatmap["Row"],
					z=heatmap[layout],
					hoverongaps=False,
					colorscale="OrRd",
					colorbar={"title": "Relative Usage (%)"},
				), row=row, col=col)

			heatmap_figure.update_layout(
				title="Relative Usage (%) of Keys in different layouts",
				height=500,
				plot_bgcolor=px.colors.sequential.OrRd[0]
			)
			heatmap_figure.update_xaxes(dict(
				ticklen=0,
				showgrid=False,
				tickmode='linear',
				tick0=1,
				dtick=1
			))
			heatmap_figure.update_yaxes(dict(
				ticklen=0,
				showgrid=False,
				tickmode='linear',
				tick0=1,
				dtick=1
			))

			with t2:
				st.markdown(r"""
				$$
				\Large
				\begin{aligned}
				\text{RU}_{\text{Layout Key } i} 
				&= \frac{
					\text{Frequency}_i
				}{
					\text{Total Frequency of all keys}
				} \\
				&= \frac{
					\text{Frequency}_i
				}{
					\sum \limits_{j=\text{Key}} \text{Frequency}_j
				}
				\end{aligned}
				$$
				""")

				st.plotly_chart(heatmap_figure, config=PLOTLY_CONFIG,
								use_container_width=True)

				heatmap = heatmap.groupby("Row").sum().drop(columns="Col")
				heatmap = np.round(heatmap/heatmap.sum()*100, 1)
				heatmap = heatmap.sort_index(ascending=False)

				st.dataframe(heatmap)

			with t3:
				st.header("Input Character Count")
				st.markdown(f"{input_char_count:,}")

				with st.sidebar:
					percentage_frequency = st.toggle("Percentage", True)
					if percentage_frequency:
						frequency_unigram *= 100/frequency_unigram["Frequency"].sum()
						frequency_bigram *= 100/frequency_bigram["Frequency"].sum()
				
				st.header(f"Unigram Frequency{' %' if percentage_frequency else ''}")
				
				bar_unigram_frequency(frequency_unigram, 10)
				st.dataframe(
					frequency_unigram.sort_values("Frequency", ascending=False),
					use_container_width=True
				)

				st.header(f"Bigram Frequency{' %' if percentage_frequency else ''}")
				bar_bigram_frequency(frequency_bigram, 10)
				st.dataframe(
					frequency_bigram.sort_values("Frequency", ascending=False),
					use_container_width=True
				)

def bar_unigram_frequency(df, top_count=10):
	df = df.sort_values("Frequency", ascending=False).head(top_count).reset_index().sort_values("Frequency", ascending=True)

	title = f"Unigram Frequency (Top {top_count})"

	fig = go.Figure().update_layout(
		margin=dict(t=0, r=0, b=0, l=0),

		# Title and Subtitle
		title=dict(
			text=title + "<br><sup>" +
			"Lower is better" + "</sup>",
			x=0,
			y=0.97
		),

		# axes titles
		xaxis_title="",
		xaxis_side="top",
		xaxis_showline=True,
		xaxis_zeroline=True,
		xaxis_ticks="outside",

		yaxis_title=None,
		#xaxis_range = (0, 1.1*df.max().max()),

		# legend
		showlegend=False,
		legend=dict(
			groupclick="toggleitem",
			orientation='h',

			# positioning
			x=1,
			xanchor="right",

			y=1,
			yanchor="bottom",

			font=dict(
				size=10
			),
			itemsizing='constant'
		),
		#yaxis={'categoryorder':'total descending'}
	)

	fig.add_trace(go.Bar(
		x=df["Frequency"],
		y=df["Required_Output"],
		# name=df["Required_Output"],
		orientation='h',
		# legendgroup=layout_type,
		# legendgrouptitle_text=layout_type,
		text=df["Frequency"].round(1).astype(str),
		textfont=dict(size=25, color="white"),
		textangle=0,
		insidetextanchor="start",
		# marker_color=color
	))

	st.plotly_chart(
		fig,
		config=PLOTLY_CONFIG,
		use_container_width=True
	)

def bar_bigram_frequency(df, top_count=10):
	df = df.sort_values("Frequency", ascending=False).head(top_count).reset_index().sort_values("Frequency", ascending=True)

	title = f"Bigram Frequency (Top {top_count})"

	fig = go.Figure().update_layout(
		margin=dict(t=0, r=0, b=0, l=0),

		# Title and Subtitle
		title=dict(
			text=title + "<br><sup>" +
			"Lower is better" + "</sup>",
			x=0,
			y=0.97
		),

		# axes titles
		xaxis_title="",
		xaxis_side="top",
		xaxis_showline=True,
		xaxis_zeroline=True,
		xaxis_ticks="outside",

		yaxis_title=None,
		#xaxis_range = (0, 1.1*df.max().max()),

		# legend
		showlegend=False,
		legend=dict(
			groupclick="toggleitem",
			orientation='h',

			# positioning
			x=1,
			xanchor="right",

			y=1,
			yanchor="bottom",

			font=dict(
				size=10
			),
			itemsizing='constant'
		),
		#yaxis={'categoryorder':'total descending'}
	)

	fig.add_trace(go.Bar(
		x=df["Frequency"],
		y=df["Key_1"] + "→" + df["Key_2"],
		# name=df["Required_Output"],
		orientation='h',
		# legendgroup=layout_type,
		# legendgrouptitle_text=layout_type,
		text=df["Frequency"].round(1).astype(str),
		textfont=dict(size=25, color="white"),
		textangle=0,
		insidetextanchor="start",
		# marker_color=color
	))

	st.plotly_chart(
		fig,
		config=PLOTLY_CONFIG,
		use_container_width=True
	)

main()
