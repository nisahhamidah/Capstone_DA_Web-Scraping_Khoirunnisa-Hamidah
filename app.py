from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup
import requests

# don't change this
matplotlib.use('Agg')
app = Flask(__name__)  # do not change this

# insert the scrapping here
url_get = requests.get('https://www.exchange-rates.org/history/IDR/USD/T')
soup = BeautifulSoup(url_get.content, "html.parser")

# find your right key here
table = soup.find('tbody')
tgl = table.find_all('a', attrs={'class': 'n'})
row_length = len(tgl)


temp = []  # initiating a list

for i in range(0, row_length):

    # scrapping process
    tgl = table.find_all('a', attrs={'class': 'n'})[i].text
    harga = table.find_all('span', attrs={'class': 'w'})[i].text

    temp.append((tgl, harga.replace('$1 = Rp', '').replace(',', '').strip()))

temp = temp[::-1]

# change into dataframe
df = pd.DataFrame(temp, columns=('tgl', 'harga'))

# insert data wrangling here
df['tgl'] = pd.to_datetime(df['tgl'])
df['tgl'].dt.to_period('M')
df['harga'] = df['harga'].astype(int)
df = df.set_index('tgl')

# end of data wranggling


@app.route("/")
def index():

    # be careful with the " and '
    card_data = f'{df["harga"].mean().round(2)}'

    # generate plot
    ax = df.plot(figsize=(10, 7))

    # Rendering plot
    # Do not change this
    figfile = BytesIO()
    plt.savefig(figfile, format='png', transparent=True)
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    plot_result = str(figdata_png)[2:-1]

    # render to html
    return render_template('index.html',
                           card_data=card_data,
                           plot_result=plot_result
                           )


if __name__ == "__main__":
    app.run(debug=True)
