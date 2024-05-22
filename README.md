# ytj-data

1. First accessed to ytj-data -> only 300 companies per search, so changed to the BIS open data. Took company code 28990 for search because of the Haptronics Oy secondment.

https://avoindata.prh.fi/bis/v1?totalResults=false&maxResults=1000&resultsFrom=0&businessLineCode=28990&companyRegistrationFrom=1900-02-28

2. Put every data to the business_data.csv file to find URLs for each one.

3. Some websites in business_data.csv pool can not load -> so needs to check that before running scrape function on every instance.

4. Some issues when scraping were: absence of company code as an entity, sometimes wrong website presented or website is no longer accessible due unpaid domain, change of the website name, etc. Because of those things, I relied on manual approach and use combination of scraping from [yjs.fi](https://tietopalvelu.ytj.fi/) and its' API and with assistance of https://vainu.io/ (their API was paid and I only used company search). 