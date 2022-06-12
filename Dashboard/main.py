import streamlit as st

import streamlit as st
from streamlit_extras.no_default_selectbox import selectbox
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from collections import Counter
import os

def common_styles():
	st.set_page_config(
		page_title = "Welcome",
		page_icon = "👋",
		layout="wide"
	)
	common_styles = """
		<style>
		#MainMenu,
		footer
		{visibility: hidden; !important}
		</style>
		"""

	st.markdown(common_styles, unsafe_allow_html=True)

config = dict(
	doubleClickDelay = 400, # (ms) affects the single click delay; default = 300ms
	displayModeBar = False,
	displaylogo = False,
	showTips = False
)

def bar(df):
	df = df.copy()
	df = df.reindex(df.sum().sort_values(ascending=False).index, axis=1)

	title = "Weighted Average of Difficulty of Layouts"

	fig = go.Figure().update_layout(
	  margin=dict(t=0, r=0, b=0, l=0),

	  # Title and Subtitle
	  title = dict(
		text =
			title + "<br><sup>" +
			"Lower is better" + "</sup>",
		x = 0,
		y = 0.95
	  ),

	  # axes titles
	  xaxis_title = "Difficulty",
	  yaxis_title = "",
	  #xaxis_range = (0, 1.1*df.max().max()),

	  # legend
	  showlegend = True,
	  legend = dict(
		groupclick="toggleitem",
		orientation = 'h',

		# positioning
		x = 1,
		xanchor = "right",

		y = 1,
		yanchor = "bottom",

		font = dict(
			  size = 10
		),
		itemsizing = 'constant'
	  ),
	  #yaxis={'categoryorder':'total descending'}
	)

	for layout in df.columns:
		layout_split = layout.split("_")
		layout_type = layout_split[1]
		name = f"{layout_split[0]} {layout_split[1]}<br /><b>{layout_split[2]}</b>"
		value = df[layout].sum()
		fig.add_trace(go.Bar(
			x = [value],
			y = [name],
			name = name,
			orientation='h',
			legendgroup = layout_type,
			legendgrouptitle_text = layout_type,
			text = f"{value:.1f}",
			insidetextanchor = "start"
		))
			
	# fig.update_layout(showlegend = False).write_image(f"{title}.png")
	# fig.update_layout(showlegend = False).write_image(f"{title}.svg")

	# fig.update_layout(showlegend = True).show(config=config)
	st.plotly_chart(
		fig,
		config=config,
		use_container_width=True
	)

def boxplot(df):
	df = df.copy()
	df = df.reindex(df.sum().sort_values(ascending=False).index, axis=1)
	
	title = "Difficulty of Layouts"

	fig = go.Figure().update_layout(
	  margin=dict(t=0, r=0, b=0, l=0),

	  # Title and Subtitle
	  title = dict(
		text =
			title + "<br><sup>" +
			"Lower is better" + "</sup>",
		x = 0,
		y = 0.95
	  ),

	  # axes titles
	  xaxis_title = "Difficulty",
	  yaxis_title = "",
	  xaxis_range = (0, 1.1*df.max().max()),

	  # legend
	  showlegend = True,
	  legend = dict(
		groupclick="toggleitem",
		orientation = 'h',

		# positioning
		x = 1,
		xanchor = "right",

		y = 1,
		yanchor = "bottom",

		font = dict(
			  size = 10
		),
		itemsizing = 'constant'
	  )
	)

	for layout in df.columns:
		layout_split = layout.split("_")
		layout_type = layout_split[1]
		fig.add_trace(go.Box(
			x = df[layout],
			name = f"{layout_split[0]} {layout_split[1]}<br /><b>{layout_split[2]}</b>",
			legendgroup = layout_type,
			legendgrouptitle_text = layout_type,
			boxpoints=False
		))
	
	# fig.update_layout(showlegend = False).write_image(f"{title}.png")
	# fig.update_layout(showlegend = False).write_image(f"{title}.svg")

	# fig.update_layout(showlegend = True).show(config=config)
	st.plotly_chart(
		fig,
		config=config,
		use_container_width=True
	)

@st.cache_data
def calc_difficulty_scores(mappings, difficulties):
	# Transforming from wide to long format 
	available_mappings = mappings.melt(
		id_vars = ['Required_Output'],
		var_name = "Layout",
		value_name = "Key_Code"
	)

	# Removing Duplicates
	available_mappings = available_mappings.dropna().copy()

	# Splitting List of keys
	available_mappings["Key_Code"] = available_mappings["Key_Code"].str.strip().str.split(" ")

	# Splitting each key into different rows
	available_mappings = available_mappings.explode("Key_Code")
	available_mappings["Key_Code"] = available_mappings["Key_Code"].astype(np.int16)

	# Join with difficulties table
	available_mappings = available_mappings.merge(difficulties, on="Key_Code", how="left")

	# Drop Empty Rows
	available_mappings = available_mappings.drop(columns="Key_Code")

	# Combine the corresponding rows
	# Get the total difficulty of getting an output, by pressing a key/combination of keys	
	difficulties = available_mappings.groupby(["Required_Output", "Layout"]).sum().reset_index()

	# Revert from long to wide
	difficulties = difficulties.pivot(index="Required_Output", columns=["Layout"])
	difficulties = difficulties["Difficulty"].reset_index()
	difficulties = (
		mappings[["Required_Output"]]
		.merge(difficulties, how="inner")
		.set_index("Required_Output")
	)

	# Filling missing values with max difficulty
	difficulties = difficulties.fillna(
		difficulties.max().max()
	)

	return difficulties

@st.cache_data
def analyze_file(file, accuracy, cpm, spm):
	with open(file) as f:
		c = Counter()
		for line in f:
			c += Counter(line)
	
	input_char_count = sum(c.values())
	
	error_rate = 1 - accuracy
	
	c += {
		"Backspace": int(error_rate * input_char_count),
		"Save": int(input_char_count/cpm * spm) # words/minute * minute => words
	}

	frequency = pd.DataFrame(
			data = pd.Series(dict(c), dtype='int'),
			columns = ["Frequency"]
	).rename(
		index = {
			' ': "Space",
			'\n': "Enter",
			"	": "Tab"
		}
	)

	return frequency, input_char_count

@st.cache_data
def analyze_total_difficulty(df, char_count):
	df = df.copy()
	
	old_cols = df.drop(columns="Frequency").columns
	new_cols = old_cols # + "_Total_Difficulty"
	
	
	df[new_cols] = df[old_cols].apply(lambda x: x*df["Frequency"].values)

	#df = df.drop(columns=old_cols)
	df = df.drop(columns="Frequency")

	df = df.agg(["sum"]).apply(lambda x: x/char_count)
	
	return df

def aggregate(df):
	return df.agg(["median", "mean", "std", "min", "max"]).round(2).T.sort_values("median")

def get_file_name(file):
	return os.path.splitext(os.path.basename(file))[0]

def main():
	common_styles()

	views = ["Home", "Difficulty Scores", "Layout Mappings", "Layouts Overall Difficulties", "Text File Difficulties"]
	
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
		st.sidebar.divider()
	
		# Importing Data
		mappings = pd.read_csv("./data/mappings.csv")
		difficulties = pd.read_csv("./data/difficulties.csv")

		available_layouts = list(mappings.columns)[1:]
		selected_layouts = st.sidebar.multiselect(
			"Filter Layouts (optional)",
			available_layouts
		)

		if len(selected_layouts) == 0:
			layouts = available_layouts
		else:
			layouts = selected_layouts
			layouts.append("Required_Output")
			mappings = mappings[layouts]
		
		layout_difficulties = calc_difficulty_scores(mappings, difficulties)
		layout_summary = aggregate(layout_difficulties)

		mappings = mappings.set_index("Required_Output")
		difficulties = difficulties.set_index("Key_Code")
		
		if view == views[1]:
			st.markdown(f"# {views[1]}")
			st.dataframe(
				difficulties,
				use_container_width=True
			)
		elif view == views[2]:
			st.markdown(f"# {views[2]}")
			st.dataframe(
				mappings,
				use_container_width=True
			)
		elif view == views[3]:
			st.markdown(f"# {views[3]}")
			st.dataframe(
				layout_summary,
				use_container_width=True
			)
			boxplot(layout_difficulties)
		elif view == views[4]:
			st.markdown(f"# {views[4]}")

			st.sidebar.divider()
			
			cpm = st.sidebar.slider(
				'Characters Per Minute',
				100, 600,
				175,
				step=10
			)
			
			accuracy = st.sidebar.slider(
				'Accuracy %',
				80, 100,
				92,
				step=2,
				format = "%d%%"
			)
			accuracy /= 100

			st.sidebar.divider()

			spm = st.sidebar.slider(
				'Saves Per Minute',
				1, 10,
				1,
				step=1
			)

			c1, c2 = st.columns([1, 4])

			input_folder = "./input_files"
			genres = os.listdir(input_folder)
			genres.sort()

			with c1:
				genre = selectbox(
					"Genre",
					genres
				)
			
			if genre is None:
				input_files = []
			else:
				genre_folder = os.path.join(input_folder, genre)
				input_files = os.listdir(genre_folder)
				input_files.sort()

			with c2:
				file = selectbox(
					"Text File",
					input_files,
					format_func = get_file_name
				)

			if file is None:
				return

			frequency, input_char_count = analyze_file(os.path.join(genre_folder, file), accuracy, cpm, spm)

			st.write(f"Input Character Count = {input_char_count}")

			if input_char_count == 0:
				return
			
			st.divider()

			merged = (
				frequency
				.merge(layout_difficulties, how="inner", left_index=True, right_index=True)
			)

			text_file_difficulties = merged.pipe(analyze_total_difficulty, input_char_count)
			text_file_summary = text_file_difficulties.round(2).T.rename(columns={"sum": "Weighted_Average"}).sort_values("Weighted_Average")
					
			bar(text_file_difficulties)
			
			st.dataframe(
				text_file_summary,
				use_container_width=True
			)

			st.dataframe(
				frequency.sort_values("Frequency", ascending=False),
				use_container_width=True
			)

main()
