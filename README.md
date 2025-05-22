# CS2660- Catamount Community Bank Final Project
Maddie Kosten
Spring 2025

## Objective
 
To create a login and registration page for a user to have different authorized access to several different pages. Some users can have access to pages other users do not have access to. There is a basic level, in which all users have access to a specific page. The user should have the ability to create an account, and use an automatically generated password during the creation. If creating their own password it has to pass requirements and have at least one lowercase, one uppercase, one digit, and one symbol. The same username is not allowed. Upon logging in, the usere can attempt clicking and seeing pages. If they have access they get to the page, otherwise they are redirected back to the menu. The whole system should have salted passwords, and protect from varius sql attacks.

## Sourced Code

The basis of this code is sourced from James Eddy. This consists of a lot of the app, database information, and some of the setup information.

## Requirements

Make sure sqlite3, and flask are installed.
Database set up is all done within bank.py, nothing additional needs to be done.

## Instructions to Test
1. If you do not already have the directory like ''instance/var/db', run setup.py. This can be done either in terminal or through the IDE.
2. To begin the testing, run werk.py in your IDE or command line. Continue to the site it suggests you to go to. Upon reaching the home page, click register. Register with the username admin. Try entering a password that does not meet the requirments of 1 lowercase, 1 uppercase, 1 digit, and 1 special character. You can try different variations of not meeting the requirements. After testing passwords, create one that meets the requirements.
3. Login using the username and password created in the previous step. This will take you to a menu. Attempt to click the accounting page, then attempt the engineering page, then attempt the reports page. These should all flash an error as the basic level access only has access to the time report page. Finally click the time report page and ensure it gets you into that page without an issue. 
4. At the bottom of the screen there will be a logout button. Click logout. This will log you out and return you back to the login page. Now you will attempt to get to the accounting, home_menu, engineering, time, and reports page without logging in. To do so after the 8097 add '/' followed by either accounting, home_menu, engineering, time, login_success, reports. These should all deny you and return you back to the login page. 
5. Now either stop running werk.py or run test.py in another browser. This will make the admin account have access to all the pages.
6. Restart werk.py or refresh the browser if kept it running while you did that. Login with the credentials you made for the admin account and retest getting into the accounting, engineering, reports, and timing pages. This time you should be able to get into them all. 
7. Logout again. Click the register button from the login page. This should redirect to the login page. Click the generate password button. You will see a password appear, to see it click the show button on the right. Create a username to go with the password. Make sure to copy the password for reference for later. Then create the account.
8. Attempt a login with the information you just put into the registration, using the generated password. You should login successfully. Logout once again. 
9. From the login page attempt a sql injection attack using "' OR '1'=1" and password put anything. This should create a invalid username or password indication. 
10. Now we will attempt the lockout. Try logging in with the admin username and any password, purposely inserting the wrong password. This will show invalid password. Try this 2 more times. On the 3rd total attempt a warning showing you failed too many times should appear. It will then time you out from attempting to login for 1 minute. You can try logging in before the 1 minute, it should fail and indicate try again in a minute. After a minute is up, you can try logging in 3 more times incorrectly to get the attempt wait time again. After attempting the attempt limit again or if you decided not to, try just logging in with the correct credentials to make sure a successful login works after failed attempts. 
11. Finally we will attempt to make sure the same username is not allowed. Click the logout button. Then click the regtistration button. Attempt to create an account with the admin username. The password can be whatever you want as long as it meets the requirements. This will indicate the username is already in the database and need to change it. 



