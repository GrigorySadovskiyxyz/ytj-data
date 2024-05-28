# ytj-data

1. First accessed to ytj-data -> only 300 companies per search, so changed to the BIS open data. Took company code 28990 for search because of the Haptronics Oy secondment.

2. Put every data to the business_data.csv file to find URLs for each one.

3. Some websites in business_data.csv pool can not load -> so needs to check that before running scrape function on every instance.

4. Some issues when scraping were: absence of company code as an entity, sometimes wrong website presented or website is no longer accessible due unpaid domain, change of the website name, etc. Because of those things, I relied on manual approach and use combination of scraping from [yjs.fi](https://tietopalvelu.ytj.fi/) and its' API and with assistance of https://vainu.io/ (their API was paid and I only used company search). Initial set of the company codes were retrived from the https://avoindata.prh.fi/ API call refering to the specific sector (https://avoindata.prh.fi/bis/v1?totalResults=false&maxResults=1000&resultsFrom=0&businessLineCode=28990&companyRegistrationFrom=1900-02-28).

5. Some companies in order to simplify the group structure, change business line or if their business got aquired by other instances (like for instance the Bevenic group) has decided to implement the merger of the some companies doing business into one company. It affects the search and text mining to some extent because formerly known companies might not have updated those things explictly or reported to the database about such changes. Some companies registered as a stock company (Osakeyhtiöl Oy), Finnish limited company (e.g., Ltd, LLC, or GmbH) as a part of a bigger company holding, so those companies are not merely Finnish but international. Nevertheless they are included in text mining.

6. When refining data for 622 company names in the list only 320 were found to have website respectively. Then duplicates of website were removed. The non working domains were also rejected from the scraping.

7. When scraping every company's website, we made sure that coding were on point (UTF-8) and only grabbed Finnish version of the webpage and/or English (if presented). Subpages of the first level containing the Facebook, Linkdin, other refererals to the external sources were also excluded from the scraping.

8. Main URLs of the webpages were checked for the security connection (some of them have https, others have http).

9. Data were gathered on 27/06/2024

10. 