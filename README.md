# alert-bot
Alert reports on autopilot. :zap:
This alert bot generates and calculates randomized monthly [care management](https://www.ahrq.gov/ncepcr/care/coordination/mgmt.html) metrics for July 2019 to present along a fictitious facility set named after the [military alphabet](https://en.wikipedia.org/wiki/NATO_phonetic_alphabet). Metrics from any industry are fodder for an alert bot.

# The Goal
Report the two worst-performing facilities in the fiscal year variance, 3-month trend variance, and monthly variance categories and provide the KPIs for said facilities.

# The How
This bot ranks the metrics from lowest to highest (where lower is better) and from highest to lowest (where higher is worse), indicating the three lowest facilities as top performers and the three highest facilities as bottom performers for the current month. Next, it finds the percentage change from the previous month as compared to the current month for each metric and ranks the military alphabet facilities again based on the three greatest decreases and the three greatest increases (Best/Worst Progress) for the current month. From there, it finds the most recent 3-month trend as a comparison of the 4-month rolling average of the oldest month to the 4-month rolling average of the most recent month. 

The top six worst-performing records and their facility KPIs are stored in a dictionary and pushed via jinja to an HTML template inspired by [Creative Tim's Material Dashboard](https://demos.creative-tim.com/material-dashboard/examples/dashboard.html) Bootstrap components and elements and automated via a scheduler.

# Result 
![Watchlist Alert](https://user-images.githubusercontent.com/90014766/131950968-58e6e464-824d-4856-a88e-1f2ceb8678b1.png)

# To Run
Following the download and unzip, update the scheduler's frequency if needed (codebase set to run hourly), and launch the scheduler from the command line by cd'ing into the unzipped folder and running the command  `python scheduler.py`.


Questions? Find out more [here](https://www.beccamayers.com).
