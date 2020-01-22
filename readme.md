## Warwick CATulator

Warwick CATulator is an online tool for Univeristy of Warwick students to log, calculate and predict their module and year grades. The motivation for the site came after hours of meticulous spreadsheeting, research of assessments and formuals just to get an idea of how i'm progressing in my degree. When a friend asked me to do the same thing for them, I knew that there had to be a better way of doing things. 

#### What makes Warwick CATulator special?

There is no short supply of online tools for calculating weighted grades on the internet but what makes my website stand head and shoulders above the rest is that, once a student has logged in with their Warwick IT account, all their modules, assessments and previous grades are automatically displayed meaning that all a student has to do is simply enter the result for each assessment when they get it. Then all module grades are automatically calculated with the correct weightings. No more spreadsheets and complicated formulas needed again.

#### Why the name?

The CATS (Credit Accumulation and Transfer Scheme) points system is recognised by many UK Higher Education institutions as a method of quantifying credit for a particular course. The name is simply a play on words with this.

#### Implementation

I made this website using the Python web framework Django. I have made several other sites using Django and love everything about it. An overview of the concepts/tech I used on this project are:
- OAuth: Integrate SSO with Warwick's Tabula. Access Keys obtained for each user which are they used to make requests to the Tabula API on the user's behalf. 
- REST APIs: Using the Tabula REST API to get a user's course data. This is then parsed and saved to the database.
- Web Scraping: To get the infomation about each module (assessment groups, assessments, weights, cats e.t.c). Over 6000 modules logged in my database, spanning 4 academic years. 
- AJAX: used for pulling module data to the front end asynchronously for a smooth user experience.
- Nginx, Gunicorn, Supervisor, Postgres, Ubuntu: what I used for the hosting of the web server.
- Cron: Nightly backups of the database with these dumps uploaded to Dropbox.
- Front end: Used bootstrap to make the site fully responsive. 
- I tried to follow Django best practices throughout this project. 

#### Screenshots
## Dashboard
![Dashboard PC](/screenshots/dashboard_pc.PNG)
![Dashboard Mobile](/screenshots/dashboard_mobile.PNG)
## View Module
![View Module PC](/screenshots/view_module_pc.PNG)
![View Module Mobile](/screenshots/view_module_mobile.PNG)
## View Module (Experimental Mode)
![View Module PC](/screenshots/view_module_experimental_pc.PNG)
![View Module Mobile](/screenshots/view_module_experimental_mobile.PNG)