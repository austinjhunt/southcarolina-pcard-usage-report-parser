"""
Turn the PDFs provided by SC Comptroller General website for Monthly Credit Card Usage tracking
into more dynamic data that can be searched and used in a web-friendly way. Convert PDF data into a JSON format. 
Example PDF provided in this repo to give idea of structure. 
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import PyPDF2
import re

"""
Pulled from SC Comptroller General Website 
---------------  REPORT SUMMARY  ---------------
This webpage provides detailed charge card usage reports 
for state agencies, four-year public colleges and universities, 
and South Carolina's technical colleges that have arranged for 
limited-use charge cards issued under a contract between state 
government and Bank of America (BOA Purchase Cards). Not all 
state agencies or institutions of higher learning have chosen 
to use these cards.

The charge card usage reports that follow, arranged by cardholder 
within each entity, are being posted monthly starting with January 
2010 transactions. The information being reported is similar to
what would be included on monthly credit card statements from your 
bank, so each purchase indicates the vendor – but not the purpose or
explanation for the purchase.

An agency’s purpose or explanation for purchases can be found in 
reports of “monthly detailed spending”. These reports include 
both cash and charge card spending by state agencies. In 
showing an agency’s monthly payment for its charge card 
purchases, the vendor on our “monthly detailed spending” 
reports will be Bank of America, the card issuer receiving 
the actual monthly payment – rather than the individual 
vendors or merchants that accept the BOA Purchase Card as 
payment for a purchase. 
---------------  END REPORT SUMMARY  ---------------
"""


class SCPcardReportParser:
    def __init__(self):
        self.base_url = 'https://cg.sc.gov'
        self.table_url = 'https://cg.sc.gov/fiscal-transparency/monthly-charge-card-usage'
        self.web_response = requests.get(self.table_url)
        self.soup = BeautifulSoup(self.web_response.content, 'html.parser')

    def _ensure_directory_exists(self, directory_path=''):
        if not os.path.exists(directory_path):
            os.mkdir(directory_path)
        elif not os.path.isdir(directory_path):
            raise Exception(
                f'Path {directory_path} exists but is not a directory')
        return True

    def get_monthly_charge_card_usage_chart(self):
        """ Use BeautifulSoup4 to extract the PDF links from the table at the table URL. 
        Convert table into a JSON format that can be used to extract PDF links for a given month & year."""
        table = self.soup.find('table')
        # each key is a year starting from most recent, e.g. 2022
        data = [{'year': th.getText(), 'links': []}
                for th in table.find('thead').find_all('th')]
        # remove the generic Year element
        data.remove({'year': 'Year', 'links': []})
        for i, month_row in enumerate(table.find('tbody').find_all('tr')):
            month = month_row.find('th').getText()
            for j, month_year_cell in enumerate(month_row.find_all('td')):
                anchor_elem = month_year_cell.find('a')
                if anchor_elem:
                    link = month_year_cell.find('a').get('href')
                else:
                    link = None
                data[j]['links'].append({
                    # link is site relative
                    month: f'{self.base_url}{link}'
                })
        self.data = data
        return data

    def save_json_data_to_json_file(self, data, json_filename):
        """ Save JSON data to a JSON file using json.dump """
        with open(json_filename, 'w') as f:
            json.dump(data, f)

    def get_month_year_pdf_link(self, pdf_links_data={}, month='January', year='2022'):
        """ Pull the PDF link for a given month/year combination from the PDF links JSON data created by
        get_monthly_charge_card_usage_chart() """
        pdf_link = None
        year_matches = [x for x in self.data if x['year'] == year]
        if len(year_matches) > 0:
            year_match = year_matches[0]
            month_matches = [
                x for x in year_match['links'] if month in x.keys()]
            if len(month_matches) > 0:
                pdf_link = month_matches[0][month]
        return pdf_link

    def download_pdf(self, pdf_link, pdf_filename):
        """ Given a PDF link and a filename to use, download and save the PDF with that filename"""
        success = False
        try:
            response = requests.get(pdf_link)
            pdf = open(pdf_filename, 'wb')
            pdf.write(response.content)
            pdf.close()
            success = True
        except:
            pass
        return success

    def generate_text_files_from_pdf_url(self, link):
        """ Provided a PDF URL, extract PDF text; create one text file for each page in 
        a folder named after the pdf (minus .pdf extension); return list of paths to those text files """
        filename = link.split('/')[-1].lower()
        foldername = filename.split('.pdf')[0]
        text_file_paths = []
        if self.download_pdf(pdf_link=link, pdf_filename=filename):
            # If download successful
            with open(filename, 'rb') as pdf_file_obj:
                reader = PyPDF2.PdfFileReader(pdf_file_obj)
                for i in range(reader.numPages):
                    page = reader.getPage(i)
                    text = page.extractText()
                    self._ensure_directory_exists(foldername)
                    text_file = f'{foldername}/{i}.txt'
                    with open(text_file, 'w') as f2:
                        f2.write(text)
                    text_file_paths.append(os.path.abspath(text_file))
        return text_file_paths

    def parse_page_text_file(self, text_file_path):
        """ given a text file path (a text file corresponds to one page of the usage report pdf) 
        generate and return a dictionary with the key components of the file """
        content = None
        text_file_path = text_file_path.replace('\\', '\\')
        try:
            with open(text_file_path, 'r') as f:
                content = f.read()
        except Exception as e:
            print(e)

        page_data = []
        vendors = []

        if content:
            date_regex = re.compile('[0-9]{1,2}\/[0-9]{2}\/[0-9]{4}')
            dollar_amount_regex = re.compile('(\$([0-9]+.?)+\.[0-9]?[0-9]?)')
            # regex for pulling the vendor name before the date in one of the vda strings
            # (get everything before the date pattern, where the date is the second part of the
            # vda element)
            vendor_exclusive_regex_without_cardholder = re.compile(
                r'((.|\s)+?)(?=([0-9]{1,2}\/[0-9]{2}\/[0-9]{4}))')
            vendor_exclusive_regex_with_cardholder = re.compile(
                r'(Cardholder)((.|\s)+?)(?=([0-9]{1,2}\/[0-9]{2}\/[0-9]{4}))'
            )
            pagenum = re.compile(r'Page [0-9].* of [0-9]*').findall(content)
            agency = re.compile(
                r'Page [0-9].* of [0-9]*(.*)\s*.*Vendor Name').findall(content)
            vendor_date_amount = re.compile(
                r'( [a-zA-Z0-9_ \&\#.\-\/\s,]*(\s|.)([0-9]{2}\/[0-9]{2}\/[0-9]{4})(\$([0-9]+.?)+\.[0-9]?[0-9]?))'
            ).findall(content)
            if len(agency) > 0:
                agency = agency[0]
            else:
                agency = 'unknown'
            if len(pagenum) > 0:
                pagenum = int(pagenum[0].split()[1])
            else:
                pagenum = 'unknown'
            for vda in vendor_date_amount:
                print(vda)
                try:
                    vda = vda[0]
                    print(f'vda = {vda}')
                    amount = dollar_amount_regex.findall(vda)[0][0]

                    date = date_regex.findall(vda)[0]
                    if 'Cardholder' in vda:
                        print(f'Cardholder in {vda}')
                        vendor = vendor_exclusive_regex_with_cardholder.findall(
                            vda)
                        # vendor is second group (index 1) in this pattern
                        vendor_index = 1
                        for v in vendor:
                            if v[1].strip() != '':
                                vendor = v[1]
                                break
                    else:
                        vendor = vendor_exclusive_regex_without_cardholder.findall(
                            vda)
                        # vendor is first group (index 1) in this pattern
                        vendor_index = 0
                    for v in vendor:
                        if v[vendor_index].strip() != '':
                            vendor = v[vendor_index]
                            break
                    vendor = vendor.strip().replace('\n', '')
                    print(f'vendor: {vendor}')
                except Exception as e:
                    print(e)
                    print(f'vda = {vda}')

                record = {
                    'vendor': vendor,
                    'date': date,
                    'amount': amount,
                    'page': pagenum,
                    'agency': agency
                }
                page_data.append(record)

        return page_data


def main():
    # parser = SCPcardReportParser()
    # data = parser.get_monthly_charge_card_usage_chart()
    # parser.save_json_data_to_json_file(
    #     data=data, json_filename='data/pcard-usage-pdf-links.json')
    # jan_2022_pdf_link = parser.get_month_year_pdf_link(
    #     month='January', year='2022')
    # text_files = parser.generate_text_files_from_pdf_url(
    #     link=jan_2022_pdf_link)
    # all_page_data = {}
    # for i, f in enumerate(text_files):
    #     page_data = parser.parse_page_text_file(f)
    #     all_page_data[i] = page_data
    # with open('data/page_data.json', 'w') as f:
    #     json.dump(all_page_data, f)

    # vendors = []
    # for i, page_records_list in all_page_data.items():
    #     for record in page_records_list:
    #         vendors.append(record['vendor'])

    # with open('data/vendors.json', 'w') as f:
    #     json.dump(vendors, f)

    with open('data/vendors.json', 'r') as f:
        data = json.load(f)
        vendors = []
        for vendor in data:
            vendors.append(vendor.split()[0])
        with open('data/vendors2.json', 'w') as f2:
            json.dump(vendors, f2)


if __name__ == "__main__":
    main()
