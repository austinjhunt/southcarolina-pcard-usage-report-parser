# Greenville County SC Sortable & Searchable Tax Sale List

This lightweight app makes the Greenville County Tax Sale list found at https://gvl-tax-sales-api.herokuapp.com searchable and sortable to help you find the sales that match your preferences. It's the same data, scraped from that webpage, but presented with more options. The original list unfortunately does not offer the ability to sort by the amount due, for example; with this app, you can quickly find the sales that are cheapest.

## Architecture

The front end of this app is built with [React](https://reactjs.org/) and [Tailwind CSS](https://tailwindcss.com/). The backend is a [Flask API](https://flask.palletsprojects.com/en/2.1.x/) that uses [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) to parse the existing Tax Sales list for Greenville, SC and convert it into a JSON response for the React app to consume and re-present with new features.

## Resources

The following resources were really helpful for this project, completed over the course of 4 hours on a Friday night, March 2022.

- For creating sortable tables with React: https://www.smashingmagazine.com/2020/03/sortable-tables-react/
- For splitting the app into a front and back end with React and Flask: https://www.youtube.com/watch?v=h96KP3JMX7Q (i.e. avoiding CORS errors seen when trying to fetch another site's data with vanilla JS)
