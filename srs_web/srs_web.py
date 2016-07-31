from flask import Flask, url_for, request, redirect, render_template, send_file
from srs.sentiment_plot import sentimentBoxPlot, sentimentBoxPlot_Compare
from srs.srs_local import fill_in_db
from srs.utilities import loadScraperDataFromDB
from srs.scraper import createAmazonScraper
from srs.scraper import scrape_reviews_hard
from srs.database import select_for_product_id
import json
import numpy as np

from bokeh.embed import file_html, components

app = Flask(__name__)

@app.route('/')
def home():
	return render_template('home.html')

@app.route('/scrape_reviews', methods=['GET', 'POST'])
def scrape_reviews():
	# from time import sleep
	# sleep(3) 

	if request.method == 'POST':
		product_id = request.form["product_id"]
		product_id2 = request.form["product_id2"]
		if not product_id2:		
			print 'product_id is ' + product_id			
			db_status = fill_in_db(product_id)
			if db_status == True:
				return str(product_id)
			else: 
				return "1"
		else:
			print 'product_id are ' + product_id	+ ' and '+ product_id2
			db_status = fill_in_db(product_id,scrape_time_limit=20)
			db_status2 = fill_in_db(product_id2,scrape_time_limit=20)
			if db_status==True and db_status2==True:
				return str(product_id) + "&" + str(product_id2)
			elif db_status==False and db_status2==True:
				return "1"
			elif db_status==True and db_status2==False:
				return "2"
			else: 
				return "12"
	else:
		return render_template('home.html')

@app.route('/srs_result/<product_id>')
def showResultWithProductId(product_id): #B00HZE2PYI
	
	_, ft_score_dict, _ = loadScraperDataFromDB(product_id)
	ft_score_ave = []
	for ft in ft_score_dict:
		average_score = np.mean(np.array(ft_score_dict[ft]))
		ft_score_ave.append({"feature": ft, "score":average_score})

	return render_template('srs_result_bar.html', ft_score_ave=json.dumps(ft_score_ave))

@app.route('/srs_result_box/<product_id>')
def showBoxResultWithProductId(product_id): #B00HZE2PYI
	
	_, ft_score_dict, _ = loadScraperDataFromDB(product_id)
	ft_scorelist = []
	for ft in ft_score_dict:
		ft_scorelist.append([ft, ft_score_dict[ft]])

	return render_template('srs_result_box.html', ft_scorelist=json.dumps(ft_scorelist))

@app.route('/srs_result_box_bokeh/<product_id>')
def showBokehBoxResultWithProductId(product_id):
	# generate data for plotting
	contents, ft_score_dict, ft_senIdx_dict = loadScraperDataFromDB(product_id)

	# do plotting
	plots = sentimentBoxPlot(contents, ft_score_dict, ft_senIdx_dict)

	#query product name
	res = select_for_product_id(product_id)
	prod_name =  res[0]["product_name"]
	prod_name=prod_name[:70]
	ind_ = prod_name.rfind(' ')
	prod_name=prod_name[:ind_]+" ..."

	# create the HTML elements to pass to template
	figJS,figDivs = components(plots)
	return render_template('srs_result_box_bokeh.html', prod1Title=prod_name, dsp='None', figJS=figJS,figDiv=figDivs[0],figDiv2=figDivs[1])

@app.route('/srs_result_box_bokeh/<product_id>&<product_id2>')
def showBokehBoxResultWithTwoProductIds(product_id, product_id2):
	# generate data for plotting
	contents1, ft_score_dict1, ft_senIdx_dict1 = loadScraperDataFromDB(product_id)
	contents2, ft_score_dict2, ft_senIdx_dict2 = loadScraperDataFromDB(product_id2)

	# do plotting
	plots = sentimentBoxPlot_Compare(contents1, ft_score_dict1, ft_senIdx_dict1, 
		contents2, ft_score_dict2, ft_senIdx_dict2)
	
	#query product name
	res = select_for_product_id(product_id)
	prod_name =  res[0]["product_name"]
	prod_name=prod_name[:70]
	ind_ = prod_name.rfind(' ')
	prod_name=prod_name[:ind_]+" ..."

	res = select_for_product_id(product_id2)
	prod2_name =  res[0]["product_name"]
	prod2_name=prod2_name[:70]
	ind_ = prod2_name.rfind(' ')
	prod2_name=prod2_name[:ind_]+" ..."

	# create the HTML elements to pass to template
	figJS,figDivs = components(plots)
	return render_template('srs_result_box_bokeh.html', prod1Title=prod_name,dsp='block', prod2Title=prod2_name,figJS=figJS,figDiv=figDivs[0],figDiv2=figDivs[1])

if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0', port=80,threaded=True)
	# app.run(port=5000)