# South Carolina PCard Usage Report Parser

This app is built to take the public pcard (credit card) usage reports in PDF format on the [SC Comptroller website](https://cg.sc.gov/fiscal-transparency/monthly-charge-card-usage) and convert them into meaningful JSON format such that one can group the the data by agency, by vendor, by date, etc without having to manually parse through thousands of pages of a PDF document.

The big picture goal with this project is to provide financial departments within SC agencies to see common spending patterns, or identify places where money is being misused or wasted.

For example, working in higher education, one becomes familiar with the problem of many solutions being paid for by "siloed" departments where each of those solutions is providing the same service.

The ability to quickly find common services that are being paid for across an institution can provide an opportunity for consolidation and thus saving of financial resources.

# Tools Used

- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) for extracting the month/year table from the Comptroller website and generating a JSON data structure allowing for quick PDF report access by month & year
- [PyPDF2](https://pythonhosted.org/PyPDF2/) for PDF to text conversion
- [Regex](https://docs.python.org/3/howto/regex.html#) for parsing key components from the converted text which is largely very randomly organized
