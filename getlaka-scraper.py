from babel.numbers import format_currency
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

page = 1
companies = []

for i in range(1, 5001):
    print(f'Scraping page {page}...')
    # Create a BeautifulSoup object
    url = 'https://getlatka.com/saas-companies?page=' + str(page)
    html_result = requests.get(url)
    soup = BeautifulSoup(html_result.text, 'html.parser')

    # Find the script tag containing the JSON data
    script_tag = soup.find('script', {'id': '__NEXT_DATA__'})

    # Extract the JSON data from the script tag
    json_data = script_tag.string.strip()

    # Parse the JSON data
    data = json.loads(json_data)

    # Extract the "props" data
    props_data = data['props']['pageProps']['records']

    # SELECT ELEMENT IN COMPANY LIST
    list_datable = soup.select('div > div:nth-child(2) > div > div.data-table_container__pPKXQ > table > tbody > tr')

    for details, datable in zip(props_data, list_datable):
        company_name = details['record']['name']
        company_url = details['record']['domain']
        year_founded = details['record']['year_founded']

        founder_name = datable.select_one('div > div:nth-child(2) > div > div.data-table_container__pPKXQ > table > '
                                          'tbody > tr > td:nth-child(7) > div > a').text
        founder_linkedin = ''
        founder_email = ''
        for founder in details['record']['people']:
            if founder['isCEO'] is True:
                founder_linkedin = founder['linkedin_profile']
                founder_email = founder['email']

        # TODO
        revenue = details['record']['stats']['ARR']
        if revenue == 0:
            formatted_revenue = None
        else:
            formatted_revenue = format_currency(revenue, 'USD', locale='en_US')

        funding = details['record']['stats']['total_raised']

        if funding == 0:
            formatted_funding = None
        else:
            formatted_funding = format_currency(funding, 'USD', locale='en_US')
        valuation = details['record']['stats']['valuation']
        if valuation == 0:
            formatted_valuation = None
        else:
            formatted_valuation = format_currency(valuation, 'USD', locale='en_US')

        cash_flow = datable.select_one('div > div:nth-child(2) > div > div.data-table_container__pPKXQ > table > '
                                       'tbody > tr > td:nth-child(6) > span').text
        team_size = datable.select_one('div > div:nth-child(2) > div > div.data-table_container__pPKXQ > table > '
                                       'tbody > tr> td:nth-child(8) > p').text

        age = datable.select_one('div > div:nth-child(2) > div > div.data-table_container__pPKXQ > table > '
                                 'tbody > tr > td:nth-child(9) > p').text

        location = datable.select_one('div > div:nth-child(2) > div > div.data-table_container__pPKXQ > table > tbody '
                                      '> tr> td:nth-child(10) > a').text
        industry = datable.select_one('div > div:nth-child(2) > div > div.data-table_container__pPKXQ > table > tbody '
                                      '> tr > td:nth-child(11) > a').text

        as_of = datable.select_one('div > div:nth-child(2) > div > div.data-table_container__pPKXQ > table > tbody > '
                                   'tr> td:nth-child(12) > p').text

        companies.append({
            'Company Name': company_name,
            'Company URL': company_url,
            'Revenue': formatted_revenue,
            'Funding': formatted_funding,
            'Valuation': formatted_valuation,
            'Cash Flow': cash_flow,
            'Year Founded': year_founded,
            'Founder Name': founder_name,
            'Founder LinkedIn': founder_linkedin,
            'Founder Email': founder_email,
            'Team Size': team_size,
            'Age': age,
            'Location': location,
            'Industry': industry,
            'As Of': as_of,
        })
    print(f'{page} scraped!')
    page += 1

# Create a DataFrame from the companies list
df = pd.DataFrame(companies)

# Save the DataFrame to an Excel file
df.to_excel('result/company-details.xlsx', index=False)
