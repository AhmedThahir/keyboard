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

def common_styles():
	st.set_page_config(
		page_title="Layout Analyzer",
		page_icon="⌨️",
		layout="wide",
		initial_sidebar_state="expanded"
	)
	common_styles = """
		<style>
		#MainMenu,
		footer
		{visibility: hidden; !important}
		</style>
		"""

	st.markdown(common_styles, unsafe_allow_html=True)


PLOTLY_CONFIG = dict(
	# (ms) affects the single click delay; default = 300ms
	doubleClickDelay=400,
	# displayModeBar=False,
	displaylogo=False,
	showTips=False
)


def bar(df):
	df = df.copy()
	df = df.reindex(df.sum().sort_values(ascending=False).index, axis=1)

	title = "Comparison of Total Difficulty in each Layout (Corrected for input size)"

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

	for layout in df.columns:
		layout_split = layout.split("_")
		layout_type = layout_split[1]
		name = f"<b>{layout_split[2]}</b><br />{layout_split[0]} {layout_split[1]}"
		value = df[layout].sum()

		if "Qwerty" in name:
			color = "blue"
		elif "ColemakIm" in name or "ColemakIm" in name:
			color = "green"
		else:
			color = "grey"

		fig.add_trace(go.Bar(
			x=[value],
			y=[name],
			name=name,
			orientation='h',
			legendgroup=layout_type,
			legendgrouptitle_text=layout_type,
			text=f"{value:.1f}",
			textfont=dict(size=25, color="white"),
			textangle=0,
			insidetextanchor="start",
			marker_color=color
		))

	st.plotly_chart(
		fig,
		config=PLOTLY_CONFIG,
		use_container_width=True
	)


def boxplot(df):
	df = df.copy()
	df = df.reindex(df.sum().sort_values(ascending=False).index, axis=1)

	title = "Comparison of Unigram Difficulty in each Layout"

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
		xaxis_zeroline=True,
		xaxis_showline=True,
		xaxis_ticks="outside",
		xaxis_range=(0, 1.1*df.max().max()),
		xaxis_side="top",

		yaxis_title=None,

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
		)
	)

	for layout in df.columns:
		if "Qwerty" in layout:
			color = "blue"
		elif "ColemakIm" in layout or "ColemakIm" in layout:
			color = "green"
		else:
			color = "grey"
		layout_split = layout.split("_")
		layout_type = layout_split[1]
		fig.add_trace(go.Box(
			x=df[layout],
			name=f"<b>{layout_split[2]}</b><br />{layout_split[0]} {layout_split[1]}",
			marker_color=color,
			legendgroup=layout_type,
			legendgrouptitle_text=layout_type,
			boxpoints='suspectedoutliers',
			text="enst"
		))

	st.plotly_chart(
		fig,
		config=PLOTLY_CONFIG,
		use_container_width=True
	)


@st.cache_data(ttl=3600)
def get_data_bigram():
	return pd.read_csv("./data/bigram_penalties.csv")


@st.cache_data(ttl=3600)
def clean_data_bigram(bigram_penalties):
	bigram_penalties = pd.melt(bigram_penalties, id_vars="Row", var_name = "Finger", value_name = "Penalty")
	bigram_penalties = bigram_penalties[["Finger", "Row", "Penalty"]]

	bigram_penalties["Row"] = (
		bigram_penalties["Row"]
		.str.replace("top", "4")
			.str.replace("middle", "3")
			.str.replace("bottom", "2")
		# .str.replace("thumb", "1")
	)

	fingers = ["index", "middle", "ring", "pinky", "thumb"]
	rows = ["4", "3", "2"]  # ["top", "middle", "bottom"]

	new_observations = []


	same_fingers_or_rows_mask = (
		(bigram_penalties["Finger"].str.contains("same")) |
		(bigram_penalties["Row"].str.contains("same"))
	)

	same_fingers_or_rows_values = bigram_penalties[same_fingers_or_rows_mask].values.tolist(
	)


	for same_finger_combination, same_row_combination, bigram_difficulty in same_fingers_or_rows_values:
		if "same" in same_finger_combination:
			same_finger_combination = fingers
		else:
			same_finger_combination = [same_finger_combination]

		if "same" in same_row_combination:
			same_row_combination = rows
		else:
			same_row_combination = [same_row_combination]

		for finger in same_finger_combination:
			for row in same_row_combination:
				new_observations.append(
					[finger+"-"+finger, row+"-"+row, bigram_difficulty])

	bigram_penalties = pd.concat(
		[
			bigram_penalties[~ same_fingers_or_rows_mask],
			pd.DataFrame(new_observations, columns=bigram_penalties.columns)
		],
		axis=0
	)

	same_columns = ["Finger", "Row"]
	for parameter in same_columns:
		for i in range(2):
			bigram_penalties[f"{parameter}_{i+1}"] = bigram_penalties[f"{parameter}"].str.split(
				"-").str[i]

	bigram_penalties = bigram_penalties.drop(columns=same_columns)

	bigram_penalties[["Row_1", "Row_2"]] = bigram_penalties[[
		"Row_1", "Row_2"]].astype(np.int16)

	return bigram_penalties.reset_index(drop=True)


@st.cache_data(ttl=3600)
def calc_unigram_difficulties(required_output_mappings, unigram_difficulties):
	available_mappings = required_output_mappings.copy()
	available_mappings = available_mappings.melt(
		id_vars=['Required_Output'],
		var_name="Layout",
		value_name="Key_Code"
	)

	# Removing Duplicates
	available_mappings = available_mappings.dropna().copy()

	# Splitting List of keys
	available_mappings["Key_Code"] = available_mappings["Key_Code"].str.strip(
	).str.split(" ")

	# Splitting each key into different rows
	available_mappings = available_mappings.explode("Key_Code")

	available_mappings = available_mappings.dropna(subset="Key_Code")
	available_mappings["Key_Code"] = available_mappings["Key_Code"].astype(
		np.int16)

	# Join with difficulties table
	available_mappings = available_mappings.merge(
		unigram_difficulties, on="Key_Code", how="left")

	# Drop Empty Rows
	available_mappings = available_mappings.drop(columns="Key_Code")

	# Combine the corresponding rows
	# Get the total difficulty of getting an output, by pressing a key/combination of keys
	unigram_difficulties = available_mappings.groupby(
		["Required_Output", "Layout"]).sum().reset_index()

	# Revert from long to wide
	unigram_difficulties = unigram_difficulties.pivot(
		index="Required_Output", columns=["Layout"])
	unigram_difficulties = unigram_difficulties["Difficulty"].reset_index()
	unigram_difficulties = (
		required_output_mappings[["Required_Output"]]
		.merge(unigram_difficulties, how="inner")
		.set_index("Required_Output")
	)

	# Filling missing values with max difficulty; putting an arbitrary number will be biased
	unigram_difficulties = unigram_difficulties.fillna(
		unigram_difficulties
		.max()
		.max()  # for max difficulty of all layouts
	)

	return unigram_difficulties


@st.cache_data(ttl=3600)
def calc_unigram_heatmap(mappings_unigram, frequency_unigram, input_char_count):

	heatmap = frequency_unigram.merge(
		mappings_unigram,
		left_index=True,
		right_index=True
	)

	heatmap = heatmap.reset_index()
	heatmap = heatmap.drop(columns=["Required_Output"])

	heatmap = heatmap.melt(
		id_vars=['Frequency'],
		var_name="Layout",
		value_name="Key_Code"
	)

	# Removing Duplicates
	heatmap = heatmap.dropna()

	# Splitting List of keys
	heatmap["Key_Code"] = heatmap["Key_Code"].str.strip().str.split(" ")

	# # Splitting each key into different rows
	heatmap = heatmap.explode("Key_Code")

	heatmap = heatmap.dropna(subset="Key_Code")

	heatmap["Key_Code"] = heatmap["Key_Code"].astype(np.int16)

	heatmap = (
		heatmap
		.groupby(["Layout", "Key_Code"])
		["Frequency"].sum()
		.reset_index()
	)

	heatmap = (
		heatmap
		.pipe(add_key_rows)
		.pipe(add_key_cols)
		.drop(columns=["Key_Code"])
	)

	heatmap = (
		heatmap
		.pivot(index=["Row", "Col"], columns=["Layout"], values="Frequency")
		.fillna(0)
	)

	# converting into percentage
	heatmap = np.round(heatmap/input_char_count*100, 1)

	heatmap = heatmap.reset_index()

	return heatmap


@st.cache_data(ttl=3600)
def calc_data_unigram_heatmap(data_unigram):

	heatmap = data_unigram.copy()
	heatmap["Key_Code"] = heatmap["Key_Code"].astype(np.int16)

	heatmap = (
		heatmap
		.pipe(add_key_rows)
		.pipe(add_key_cols)
		.drop(columns=["Key_Code"])
	)

	return heatmap


def add_key_rows(df):
	df = df.copy()
	df["Row"] = df["Key_Code"].astype(str).str[0].astype(np.int16)
	return df


def add_key_cols(df):
	df = df.copy()
	df["Col"] = df["Key_Code"].astype(str).str[1:].astype(np.int16)
	return df


@st.cache_data(ttl=3600)
def calc_bigram_penalties(bigram_penalties, data_bigram, data_unigram):
	bigram_penalties = bigram_penalties.melt(
		id_vars=["Key_1", "Key_2"], var_name="Layout", value_name="Key_Code")

	mappings_bigram_mask = [None, None, None]
	for i in range(1, 2+1):
		mappings_bigram_mask[i] = bigram_penalties["Layout"].str.contains(
			f"{i}", regex=False)

	data_unigram["Key_Code"] = data_unigram["Key_Code"].astype(str)

	bigram_penalties = (
		bigram_penalties
		.merge(
			data_unigram,
			how="inner",
			left_on=["Key_Code"],
			right_on=["Key_Code"]
		)
	)
	bigram_penalties = bigram_penalties.pipe(add_key_rows)

	bigram_penalties["Layout"] = bigram_penalties["Layout"].str[:-2]
	bigram_penalties = bigram_penalties.drop(
		columns=["Key_Code", "Difficulty"]
	)

	bigram_penalties = pd.merge(
		bigram_penalties[mappings_bigram_mask[1]],
		bigram_penalties[mappings_bigram_mask[2]],
		left_on=["Key_1", "Key_2", "Layout"],
		right_on=["Key_1", "Key_2", "Layout"],
		how="inner",
		suffixes=["_1", "_2"]
	)

	bigram_penalties = bigram_penalties.dropna(how="any")

	# if different hands, no penalty
	# only filter rows with same hands
	bigram_penalties = bigram_penalties.query("Hand_1 == Hand_2")

	bigram_penalties = bigram_penalties.merge(
		data_bigram,
		how="inner"
	)

	# bigram_penalties = bigram_penalties.set_index(["Key_1", "Key_2"])
	# bigram_penalties = bigram_penalties[["Layout", "Penalty"]]

	bigram_penalties = bigram_penalties.pivot(
		index=["Key_1", "Key_2"], columns=["Layout"], values="Penalty")
	bigram_penalties = bigram_penalties.fillna(0)

	return bigram_penalties

# @st.cache_data(ttl=3600)


def analyze_file_unigrams(text_content, accuracy): # , cpm, spm
	c = Counter(text_content)

	input_char_count = sum(c.values())

	error_rate = 1 - accuracy

	c += {
		# words/minute * minute => words

		"Backspace": int(error_rate * input_char_count),
		# "Save": int(input_char_count/cpm * spm)
	}

	frequency = pd.DataFrame(
		data=pd.Series(dict(c), dtype='int'),
		columns=["Frequency"]
	).rename(
		index={
			' ': "Space",
			'\n': "Enter",
			"	": "Tab"
		}
	)
	frequency.index.name = "Required_Output"

	return frequency, input_char_count

# @st.cache_data(ttl=3600)


def analyze_file_bigram(text_content):
	bigram = list(ngrams(text_content, 2))
	c = Counter(bigram)

	frequency = pd.DataFrame(
		data=pd.Series(dict(c), dtype='int'),
		columns=["Frequency"]
	).rename(
		index={
			' ': "Space",
			'\n': "Enter",
			"	": "Tab"
		}
	)

	return frequency


def analyze_total_ngram_difficulty(df, char_count):
	df = df.copy()

	old_cols = df.drop(columns="Frequency").columns
	new_cols = old_cols  # + "_Total_Difficulty"

	df[new_cols] = df[old_cols].apply(lambda x: x*df["Frequency"].values)

	#df = df.drop(columns=old_cols)
	df = df.drop(columns="Frequency")

	df = df.agg(["sum"]).apply(lambda x: x/char_count)
	return df


def aggregate(df):
	df = df.copy()
	df = df.agg(["mean", "std"]).round(2).T.sort_values("mean")
	df["Aggregate Difficulty (Mean ± Std)"] = df["mean"].astype(str) + " ± " + df["std"].astype(str)
	df = df.drop(columns=["mean", "std"])
	return df


def get_file_name(file):
	return os.path.splitext(os.path.basename(file))[0]


@st.cache_data(ttl=3600)
def get_mappings_unigram():
	return pd.read_csv("./data/required_output_mappings.csv")


@st.cache_data(ttl=3600)
def get_mappings_bigram(mappings_unigram):
	unique_keys = mappings_unigram["Required_Output"]
	mappings_unigram = mappings_unigram.set_index("Required_Output")

	bigram = []
	for a in unique_keys:
		for b in unique_keys:
			bigram.append([a, b])
	mappings_bigram = pd.DataFrame(
		columns=["Key_1", "Key_2"],
		data=bigram
	).merge(
		mappings_unigram,
		how="inner",
		left_on=["Key_1"],
		right_on=["Required_Output"]
	).merge(
		mappings_unigram,
		how="inner",
		left_on=["Key_2"],
		right_on=["Required_Output"],
		suffixes=["_1", "_2"]
	)
	for col in mappings_bigram.drop(columns=["Key_1", "Key_1"]).columns:
		if "1" in col:
			mappings_bigram[col] = mappings_bigram[col].str.split(
				" ").str[-1]  # .astype(np.int16) # last key
		elif "2" in col:
			mappings_bigram[col] = mappings_bigram[col].str.split(
				" ").str[0]  # .astype(np.int16) # first key
		else:
			pass

	return mappings_bigram


@st.cache_data(ttl=3600)
def get_data_unigram():
	return pd.read_csv("./data/key_code_mappings.csv")


@st.cache_data(ttl=3600)
def get_files():
	return glob(os.getcwd(), recursive=False)

# @st.cache_data(ttl=3600)


def get_text_content(selected_files):
	text_content = ""
	for file in selected_files:
		with open(file, "r") as f:
			text_content += f.read()
	return text_content

