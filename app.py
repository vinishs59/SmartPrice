from flask import Flask, render_template, url_for , redirect , request
from form import searchForm
from selectorlib import Extractor
import requests
import json
from json2html import *
from time import sleep

import pandas as pd
app = Flask(__name__)


e = Extractor.from_yaml_file('Testing.yml')
amazon_ext = Extractor.from_yaml_file('search_results.yml')
#pd.set_option('display.max_colwidth',None)

def scrape(url,str):

    headers = {
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.amazon.in/',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }

    # Download the page using requests
    r = requests.get(url, headers=headers)
    # Simple check to check if page was blocked (Usually 503)
    if r.status_code > 500:
        if "To discuss automated access to Amazon data please contact" in r.text:
            print("Page %s was blocked by Amazon. Please try using better proxies\n"%url)
        else:
            print("Page %s must have been blocked by Amazon as the status code was %d"%(url,r.status_code))
        return None
    # Pass the HTML of the page and create
    if str == 'amazon':
        #st.subheader('Flipkart available Price')
        return amazon_ext.extract(r.text)
    if str == 'flipkart':
        ret = e.extract(r.text)
        if (ret['Products']) is not None:
            return e.extract(r.text)
        else:
            ext =Extractor.from_yaml_file('flipkartNew.yml')
            return ext.extract(r.text)


key = ""
app.config['SECRET_KEY']='409554a17d5227b87075bd9a4ed3bde7'
posts = [
    {
        'author': 'Corey Schafer',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
    }
]


#@app.route("/")
@app.route('/', methods= ['GET', 'POST'])

def login():
    form = searchForm()
    print(f'request is {request.data}')
    search=""
    if form.search.data is not None:
        words = form.search.data.split()
        for i in words:
            search = search + i + '+'
        search = search[:-1]
        print(f'search string is {search}')
    if form.validate_on_submit():
        # if form.email.data == 'admin@blog.com' and form.password.data == 'password':
        #     flash('You have been logged in!', 'success')
        return redirect(url_for('home'))
        # else:
        #     flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('index.html', title='Login', form=form)

@app.route("/home",methods= ['GET', 'POST'])
def home():
    form = searchForm()
    search=""
    adf=""
    if form.search.data is not None:
        words = form.search.data.split()
        for i in words:
            search = search + i + '+'
        search = search[:-1]
        print(f'search string is {search}')

        flipkart_url= 'https://www.flipkart.com/search?q='+str(search)
        amazon_url= 'https://www.amazon.in/s?k='+str(search)
        data = scrape(amazon_url,'amazon')
        adf,fdf = pd.DataFrame(),pd.DataFrame()
        if data['Products'] is not None:
            adf = pd.json_normalize(data['Products'])
            #df = df.iloc[:10]
            amazonlink = "https://www.amazon.in"
            adf['url'] = amazonlink+adf['url'].astype(str)
            adf.sort_values(by=['price'])

        fdata = scrape(flipkart_url,'flipkart')
        if fdata['Products'] is not None:
            fdf = pd.json_normalize(fdata['Products'])
            #fdf = df.iloc[:10]
                #fp_df = fp_df.iloc[:10]
            link = "https://www.flipkart.com"
            fdf['url'] = link+fdf['url'].astype(str)
            fdf.sort_values(by=['price'])
            #fdf['url'] = fdf['url'].apply(make_clickable)
        #print(f'returned jason data is {data}')
        final = pd.concat([adf,fdf])
        final = final.sort_values(by=['price'])
        adf = final.to_json(orient='records')
        adf = json.loads(adf)
        #adf = data['Products']
        print(f'the data is{adf}')
    return render_template('home.html', posts=adf)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


if __name__ == '__main__':
    app.run(debug=True)
