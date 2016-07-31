from math import pi
import pandas as pd
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, TapTool, CustomJS, HoverTool, FixedTicker, PrintfTickFormatter
import numpy as np
from matplotlib import pyplot as plt

def prepareDataForRectPlot(feature_scorelist_dict, sort=True, spanTop=75, spanBottom=25):
	"""
	INPUT: feature_scorelist_dict
	OUTPUT: mids, spans
	"""

	features = feature_scorelist_dict.keys()
	if sort:
		features = sorted(features)
	
	mids = []
	spans = []
	features_to_plot = []
	for feature in features:
		scorelist = feature_scorelist_dict[feature]
		if len(scorelist) > 2:
			scorearray = np.array(scorelist)
			mean = np.mean(scorearray)
			span = np.percentile(scorearray, spanTop) - np.percentile(scorearray, spanBottom)

			mids.append(mean)
			spans.append(span)
			features_to_plot.append(feature)

	return features_to_plot, mids, spans

def prepareDataForHistPlotAndSampleSentences(
	feature_scorelist_dict, feature_senIdxlist_dict, contents, sort=True, exampleSentences_size=3):
	"""
	INPUT: feature_scorelist_dict, feature_senIdxlist_dict, contents
	OUTPUT: histTops, histLefts, histRights, sampleSentences_dict
	"""

	features = feature_scorelist_dict.keys()
	if sort:
		features = sorted(features)

	histTops = []
	histLefts = []
	histRights = []
	sampleSentences_dict = {}
	for feature in features:
		# get raw data: scorelist
		scorelist = feature_scorelist_dict[feature]
		senIdxlist = feature_senIdxlist_dict[feature]

		score_num = len(scorelist)
		min_score = min(scorelist)
		max_score = max(scorelist)
		
		# determine bin_num
		bin_num = 4
		if score_num <= 10: bin_num = 2
		elif score_num <= 30: bin_num = 3
		elif score_num <= 100: bin_num = 4
		else: bin_num = 5

		# initialize histTop
		histTop = [0 for _ in range(bin_num)]
		exampleSentences = [[] for _ in range(bin_num)]

		delimiter = np.linspace(min_score, max_score, bin_num+1)
		
		for senIdx, score in zip(senIdxlist, scorelist):
			for j in range(bin_num):
				if score >= delimiter[j] and score <= delimiter[j+1]:
					histTop[j] += 1
					if len(exampleSentences[j]) < exampleSentences_size:
						content = contents[senIdx]
						exampleSentences[j].append(content)

					break
		histLeft = list(delimiter[0:bin_num])
		histRight = list(delimiter[1:bin_num+1])
		
		histTops.append(histTop)
		histLefts.append(histLeft)
		histRights.append(histRight)
		sampleSentences_dict[feature] = exampleSentences

	hist_cds = ColumnDataSource(data=dict(tops=histTops, lefts=histLefts, rights=histRights, features=features))
	sampleSentences_cds = ColumnDataSource(data=sampleSentences_dict)

	return hist_cds, sampleSentences_cds

def getRectPlot(features, mids, spans, w=0.3, fill_color="#4286F5", hover_color="#4286F5",
	plot_width=650, plot_height=450, major_label_orientation=pi/4, 
	grid_line_alpha=0.0, axis_label_text_font_size='12pt'):
	
	print features
	feature_num = len(features)

	color_list = [fill_color]*feature_num
	# plot rectPlot
	rectPlot = figure(tools="", plot_width=plot_width, plot_height=plot_height, 
		x_range=sorted(list(set(features))),title_text_font_size='16pt')
	rectPlot.yaxis.axis_label_text_font_size = axis_label_text_font_size
	rectPlot.xaxis.axis_label_text_font_size = axis_label_text_font_size
	rectPlot.xaxis.major_label_orientation = major_label_orientation
	rectPlot.grid.grid_line_alpha=grid_line_alpha
	rectPlot.logo = None
	rectPlot.toolbar_location = None
	rectPlot.yaxis[0].ticker=FixedTicker(ticks=[0])
	rectPlot.yaxis[0].formatter = PrintfTickFormatter(format="Neutral")
	# http://stackoverflow.com/questions/37173230/how-do-i-use-custom-labels-for-ticks-in-bokeh
	# open issue allow users to specify explicit tick labels: https://github.com/bokeh/bokeh/issues/1671	
	# rectPlot.text([1,1],[0.15,-0.05], text=['Positive','Negative'], alpha=1, text_font_size="12pt", text_baseline="middle", text_align="center")
	rectPlot_rect=rectPlot.rect(features, mids, w, spans, color=color_list, alpha = 0.5, hover_color=hover_color, hover_alpha=1.0)

	return rectPlot, rectPlot_rect

def getRectPlot_compare(features1, mids1, spans1, features2, mids2, spans2, w=0.3,
 	color1="#4286F5",color2="#DC4439", hover_color1="#4286F5",hover_color2="#DC4439",
	plot_width=650, plot_height=450, major_label_orientation=pi/4, 
	grid_line_alpha=0.0, axis_label_text_font_size='12pt'):
	
	# plot rectPlot
	rectPlot = figure(tools="", plot_width=plot_width, plot_height=plot_height, 
		x_range=sorted(list(set(features1+features2))),title_text_font_size='16pt')
	rectPlot.yaxis.axis_label_text_font_size = axis_label_text_font_size
	rectPlot.xaxis.axis_label_text_font_size = axis_label_text_font_size
	rectPlot.xaxis.major_label_orientation = major_label_orientation
	rectPlot.grid.grid_line_alpha=grid_line_alpha
	rectPlot.logo = None
	rectPlot.toolbar_location = None
	rectPlot.yaxis[0].ticker=FixedTicker(ticks=[0])
	rectPlot.yaxis[0].formatter = PrintfTickFormatter(format="Neutral")

	color_list1 = [color1]*len(features1)
	color_list2 = [color2]*len(features2)	

	rectPlot_rect1 = rectPlot.rect(features1, mids1, w, spans1, 
		color=color_list1,alpha = 0.5,hover_color=hover_color1, hover_alpha=1.0)

	rectPlot_rect2 = rectPlot.rect(features2, mids2, w, spans2, 
		color=color_list2, alpha = 0.5,hover_color=hover_color2, hover_alpha=1.0)

	return rectPlot, rectPlot_rect1, rectPlot_rect2

def getHistPlot(histPlot_cds, color="#4286F5",
	grid_line_alpha=0.0, axis_label_text_font_size='12pt'):

	histPlot = figure(tools="", plot_width=400, plot_height=250,y_axis_label='# of sentences',x_axis_label="Sentiment Score")
	histPlot.xaxis.axis_label_text_font_size = axis_label_text_font_size
	histPlot.yaxis.axis_label_text_font_size = axis_label_text_font_size
	histPlot.grid.grid_line_alpha = grid_line_alpha
	histPlot.logo = None
	histPlot.toolbar_location = None

	# initialize plot
	histPlot_quad = histPlot.quad(top='top',bottom='bottom',left='left',right='right', source=histPlot_cds,line_width=2,fill_alpha=0.8,color=color)

	return histPlot, histPlot_quad

def getHistPlot_compare(histPlot_cds1, histPlot_cds2, color1="#4286F5",color2="#DC4439",
	grid_line_alpha=0.0, axis_label_text_font_size='12pt'):

	histPlot = figure(tools="", plot_width=400, plot_height=250,
		y_axis_label='# of sentences',x_axis_label="Sentiment Score")
	
	histPlot.xaxis.axis_label_text_font_size = axis_label_text_font_size
	histPlot.yaxis.axis_label_text_font_size = axis_label_text_font_size
	histPlot.grid.grid_line_alpha = grid_line_alpha
	histPlot.logo = None
	histPlot.toolbar_location = None

	# initialize plot
	histPlot_quad1 = histPlot.quad(top='top',bottom='bottom',left='left',right='right', 
		source=histPlot_cds1,line_width=2,fill_alpha=0.5,color=color1)

	histPlot_quad2 = histPlot.quad(top='top',bottom='bottom',left='left',right='right', 
		source=histPlot_cds2,line_width=2,fill_alpha=0.5,color=color2)

	return histPlot, histPlot_quad1, histPlot_quad2

def getInitialHistPlotData(hist_cds):

	top = hist_cds.data["tops"][0]
	left = hist_cds.data["lefts"][0]
	right = hist_cds.data["rights"][0]
	bottom = [0 for _ in top]
	feature = hist_cds.data["features"][0]
	histPlot_data = dict(top=top, bottom=bottom, left=left, right=right, feature=feature)
	histPlot_cds=ColumnDataSource(data=histPlot_data)

	return histPlot_cds

def sentimentBoxPlot(contents, feature_scorelist_dict, feature_senIdxlist_dict):

	# get data for rectPlot
	features, mids, spans = prepareDataForRectPlot(feature_scorelist_dict, sort=True)
	feature_scorelist_dict_to_plot = {}
	feature_senIdxlist_dict_to_plot = {}
	for feature in features:
		feature_scorelist_dict_to_plot[feature] = feature_scorelist_dict[feature]
		feature_senIdxlist_dict_to_plot[feature] = feature_senIdxlist_dict[feature]

	print feature_scorelist_dict_to_plot
	# get data for histPlot and sample reviews
	hist_cds, sampleSentences_cds = prepareDataForHistPlotAndSampleSentences(
	feature_scorelist_dict_to_plot, feature_senIdxlist_dict_to_plot, contents, sort=True)

	# plot rectPlot
	rectPlot, rectPlot_rect = getRectPlot(features, mids, spans)

	# plot histPlot
	histPlot_cds = getInitialHistPlotData(hist_cds)
	histPlot, histPlot_quad = getHistPlot(histPlot_cds)

	# add interaction between rectPlot and histPlot
	hoverJS="""
		var histPlot_data = histPlot_cds.get('data');
		var features = hist_cds.get('data')['features'];
		var hist_data = hist_cds.get('data');

		//get current hovering index
		fillHistData(cb_data, histPlot_data, features, hist_data);		
		histPlot_cds.trigger('change');
        
		"""

	hoverCallBack=CustomJS(args={'histPlot_cds':histPlot_cds, 'hist_cds':hist_cds},code=hoverJS)
	rectPlot.add_tools(HoverTool(renderers=[rectPlot_rect],callback=hoverCallBack,tooltips=None))

	# add interaction between histPlot and sample reviews
	hoverJS2="""
		var sampleSentences_dict = sampleSentences_cds.get('data');
		
		var feature = histPlot_cds.get('data')['feature'];
		fillSampleReviews(cb_data, sampleSentences_dict, feature);
        
		""" 

	hoverCallBack2=CustomJS(args={'sampleSentences_cds':sampleSentences_cds, 'histPlot_cds': histPlot_cds}, code=hoverJS2)
	histPlot.add_tools(HoverTool(renderers=[histPlot_quad],callback=hoverCallBack2,tooltips=None))

	return (rectPlot,histPlot)

def sentimentBoxPlot_Compare(contents1, feature_scorelist_dict1, feature_senIdxlist_dict1, 
	contents2, feature_scorelist_dict2, feature_senIdxlist_dict2):

	# get data for rectPlot
	features1, mids1, spans1 = prepareDataForRectPlot(feature_scorelist_dict1, sort=True)
	features2, mids2, spans2 = prepareDataForRectPlot(feature_scorelist_dict2, sort=True)

	feature_scorelist_dict_to_plot1 = {}
	feature_senIdxlist_dict_to_plot1 = {}
	feature_scorelist_dict_to_plot2 = {}
	feature_senIdxlist_dict_to_plot2 = {}
	common_features = []
	for feature in features1:
		if feature in features2:
			feature_scorelist_dict_to_plot1[feature] = feature_scorelist_dict1[feature]
			feature_senIdxlist_dict_to_plot1[feature] = feature_senIdxlist_dict1[feature]
			feature_scorelist_dict_to_plot2[feature] = feature_scorelist_dict2[feature]
			feature_senIdxlist_dict_to_plot2[feature] = feature_senIdxlist_dict2[feature]
			common_features.append(feature)

	# get data for histPlot and sample reviews
	hist_cds1, sampleSentences_cds1 = prepareDataForHistPlotAndSampleSentences(
	feature_scorelist_dict_to_plot1, feature_senIdxlist_dict_to_plot1, contents1, sort=True)
	hist_cds2, sampleSentences_cds2 = prepareDataForHistPlotAndSampleSentences(
	feature_scorelist_dict_to_plot2, feature_senIdxlist_dict_to_plot2, contents2, sort=True)

	# plot rectPlot
	rectPlot, rectPlot_rect1, rectPlot_rect2 = getRectPlot_compare(common_features, mids1, spans1, 
		common_features, mids2, spans2)

	# plot histPlot
	histPlot_cds1 = getInitialHistPlotData(hist_cds1)
	histPlot_cds2 = getInitialHistPlotData(hist_cds2)
	histPlot, histPlot_quad1, histPlot_quad2= getHistPlot_compare(histPlot_cds1, histPlot_cds2)

	# add interaction between rectPlot and histPlot
	hoverJS="""
		var histPlot_data1 = histPlot_cds1.get('data');
		var hist_data1 = hist_cds1.get('data');
		var histPlot_data2 = histPlot_cds2.get('data');
		var hist_data2 = hist_cds2.get('data');

		var features = hist_cds1.get('data')['features'];

		//get current hovering index
		fillHistData_compare(cb_data, histPlot_data1, hist_data1, histPlot_data2, hist_data2, features);		
		histPlot_cds1.trigger('change');
		histPlot_cds2.trigger('change');
        
		"""

	hoverCallBack=CustomJS(
		args={'histPlot_cds1':histPlot_cds1, 'hist_cds1':hist_cds1, 
		'histPlot_cds2':histPlot_cds2, 'hist_cds2':hist_cds2},
		code=hoverJS)
	rectPlot.add_tools(
		HoverTool(
			renderers=[rectPlot_rect1],
			callback=hoverCallBack,
			tooltips=None))
	rectPlot.add_tools(
		HoverTool(
			renderers=[rectPlot_rect2],
			callback=hoverCallBack,
			tooltips=None))

	# add interaction between histPlot and sample reviews
	hoverJS2="""
		var sampleSentences_dict = sampleSentences_cds.get('data');
		
		var feature = histPlot_cds.get('data')['feature'];
		fillSampleReviews(cb_data, sampleSentences_dict, feature);
        
		""" 

	hoverCallBack2_1=CustomJS(
		args={'sampleSentences_cds':sampleSentences_cds1, 'histPlot_cds': histPlot_cds1}, 
		code=hoverJS2)
	
	histPlot.add_tools(
		HoverTool(
			renderers=[histPlot_quad1],
			callback=hoverCallBack2_1,
			tooltips=None))

	hoverCallBack2_2=CustomJS(
		args={'sampleSentences_cds':sampleSentences_cds2, 'histPlot_cds': histPlot_cds2}, 
		code=hoverJS2)
	
	histPlot.add_tools(
		HoverTool(
			renderers=[histPlot_quad2],
			callback=hoverCallBack2_2,
			tooltips=None))

	return (rectPlot,histPlot)

# function for setting the colors of the box plots pairs
def set_box_color(bp, color):
    plt.setp(bp['boxes'], color=color)
    plt.setp(bp['whiskers'], color=color,alpha=0)
    plt.setp(bp['caps'], color=color,alpha=0)
    plt.setp(bp['medians'], color=color,alpha=0)

def box_plot(prod1score,filename,prod1ID):
    ticks = prod1score.keys()
    
    prod1score_list = []
    for ft in ticks:
        prod1score_list.append(prod1score[ft])

    plt.figure(figsize=(7, 7))

    bpl = plt.boxplot(prod1score_list, positions=np.array(xrange(len(ticks)))*2.0, sym='', widths=0.6)
    set_box_color(bpl, '#D7191C') # colors are from http://colorbrewer2.org/

    plt.plot([], c='#D7191C', label=prod1ID)
    plt.legend()

    locs, labels = plt.xticks(xrange(0, len(ticks) * 2, 2), ticks)
    plt.xlim(-2, len(ticks)*2)
    plt.setp(labels, rotation=90)
    plt.axhline(y=0.0,xmin=0,xmax=3,c="blue",linewidth=0.5,zorder=0)
    plt.tight_layout()
    plt.savefig(filename)

def box_plot_compare(prod1score,prod2score,filename,prod1ID,prod2ID):
    ticks = prod1score.keys()
    
    prod1score_list = []
    for ft in ticks:
        prod1score_list.append(prod1score[ft])

    prod2score_list = []
    for ft in ticks:
        prod2score_list.append(prod2score[ft])

    plt.figure(figsize=(7, 7))

    bpl = plt.boxplot(prod1score_list, positions=np.array(xrange(len(ticks)))*2.0-0.4, sym='', widths=0.6)
    bpr = plt.boxplot(prod2score_list, positions=np.array(xrange(len(ticks)))*2.0+0.4, sym='', widths=0.6)
    set_box_color(bpl, '#D7191C') # colors are from http://colorbrewer2.org/
    set_box_color(bpr, '#2C7BB6')

    plt.plot([], c='#D7191C', label=prod1ID)
    plt.plot([], c='#2C7BB6', label=prod2ID)
    plt.legend()

    locs, labels = plt.xticks(xrange(0, len(ticks) * 2, 2), ticks)
    plt.xlim(-2, len(ticks)*2)
    plt.setp(labels, rotation=90)
    # plt.ylim(-0.5, 0.5)
    plt.axhline(y=0.0,xmin=0,xmax=3,c="blue",linewidth=0.5,zorder=0)
    plt.tight_layout()
    plt.savefig(filename)

