from flask import Flask, url_for, request, redirect, render_template, send_file
from srs.sentiment_plot import sentimentBoxPlot, sentimentBoxPlot_Compare
from srs.srs_local import fill_in_db, get_reviews_num_and_registered_category
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
	if request.method == 'POST':
		user_input1 = request.form["product_id"]
		user_input2 = request.form["product_id2"]

		#filter out product ID from Amazon http link as input 
		key_word = ["/product/","/dp/","/product-reviews/"]
		match = next((s for s in key_word if s in user_input1), False)
		if match and "http" in user_input1:
		    idx =  user_input1.find(match) + len(match) 
		    idx2 = user_input1[idx:].find('/')
		    product_id =  user_input1[idx:idx+idx2]
		else: 
			product_id = user_input1

		match = next((s for s in key_word if s in user_input2), False)
		if match and "http" in user_input2:
		    idx =  user_input2.find(match) + len(match) 
		    idx2 = user_input2[idx:].find('/')
		    product_id2 =  user_input2[idx:idx+idx2]
		else: 
			product_id2 = user_input2

		# the case that both id1 and id2 are empty were checked

		if not product_id2:	# one product case
			print 'product_id is ' + product_id			
			_ , prod_cat =get_reviews_num_and_registered_category(product_id)
			if len(prod_cat)==0: #empty case
				return "0" # code name for not having category in the db 
			else: 
				db_status = fill_in_db(product_id)
				if db_status == True:
					return str(product_id)
				else: 
					return "1" # code name for unable to retrieve product 1 review from Amazon
		
		else: # two product case 
			print 'product_id are ' + product_id	+ ' and '+ product_id2
			_ ,prod_cat = get_reviews_num_and_registered_category(product_id)
			_ ,prod2_cat = get_reviews_num_and_registered_category(product_id2)

			if len(prod_cat)==0 and len(prod2_cat)==0: 
				return "00" #both products are valid but are not in db category
			if len(prod2_cat)==0 and len(prod_cat)>0: # 2 is empty, but 1 is not 
				db_status = fill_in_db(product_id,scrape_time_limit=20)
				if db_status == True:
					return str(product_id)
				else: 
					return "10" # code name for unable to retrieve product 1 review from Amazon
			if len(prod_cat)==0 and len(prod2_cat)>0: # 1 is empty, but 2 is not  
				db_status = fill_in_db(product_id2,scrape_time_limit=20)
				if db_status == True:
					return str(product_id2)
				else: 
					return "02" # code name for unable to retrieve product 1 review from Amazon
			if len(prod_cat)>=0 and len(prod2_cat)>0:
				# both product in cat 
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
	maxChar = 70
	res = select_for_product_id(product_id)
	prod_name =  res[0]["product_name"]
	nChar = len(prod_name)
	prod_name=prod_name[:maxChar]
	ind_ = prod_name.rfind(' ')
	prod_name=prod_name[:ind_]
	if nChar > maxChar:
		prod_name = prod_name +" ..."

	res = select_for_product_id(product_id2)
	prod2_name =  res[0]["product_name"]
	nChar = len(prod2_name)
	prod2_name=prod2_name[:maxChar]
	ind_ = prod2_name.rfind(' ')
	prod2_name=prod2_name[:ind_]
	if nChar > maxChar:
		prod2_name = prod2_name +" ..."

	# create the HTML elements to pass to template
	figJS,figDivs = components(plots)
	return render_template('srs_result_box_bokeh.html', prod1Title=prod_name,dsp='block', prod2Title=prod2_name,figJS=figJS,figDiv=figDivs[0],figDiv2=figDivs[1])

@app.route('/about')
def aboutPage():
	return render_template('about.html')

@app.route('/project')
def projectPage():
	return render_template('project.html')

if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0', port=80,threaded=True)
	# app.run(port=5000)