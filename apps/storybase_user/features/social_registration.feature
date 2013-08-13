Feature: A user can register using social Twitter and Facebook
        Scenario: A user registers using their Twitter account when not logged in to Twitter
                # Activating "Private Browsing" in Firefox or
                # opening an "Incognito Window" in Chrome is a good way to
                # ensure your'e not logged in to other accounts
                Given the user is not logged in to Twitter
                Given the user navigates to "/"
                Given the user clicks the "Sign In" link
                Given the user clicks the "Don't have an account? Join now." link
                Given the user clicks the "Sign up with Twitter" button
                Then the user is redirected to a Twitter page prompting for login information and to authorize the app
                Given the user enters their Twitter credentials
                Given the user submits the form
                Then the user is redirected to "/accounts/extradetails/"
                Given the user enters a valid email address in the "Email" input
                Given the user clicks the "I agree to the terms of service" checkbox
                Given the user clicks the "Submit" button
                Then the user should be redirected to the "My Stories" page
                # In the upper-right-hand corner
                Then the text "<firstname>" should be present, where "<firstname>" is the first name specified in the profile of the user's Twitter account

        Scenario: A user registers using their Facebook account when not logged in to Facebook
                # Activating "Private Browsing" in Firefox or
                # opening an "Incognito Window" in Chrome is a good way to
                # ensure your'e not logged in to other accounts
                Given the user is not logged in to Facebook 
                Given the user navigates to "/"
                Given the user clicks the "Sign In" link
                Given the user clicks the "Don't have an account? Join now." link
                Given the user clicks the "Sign up with Facebook" button
                Then the user is redirected to a Facebook login page
                Given the user enters their Facebook credentials
                Given the user submits the form
                Then the user is prompted to authorize the app
                Given the user submits the form 
                Then the user is redirected to "/accounts/extradetails/"
                Given the user clicks the "I agree to the terms of service" checkbox
                Given the user clicks the "Submit" button
                Then the user should be redirected to the "My Stories" page
                # In the upper-right-hand corner
                Then the text "<firstname>" should be present, where "<firstname>" is the first name specified in the profile of the user's Facebook account

        Scenario: A user registers using their Twitter account when logged in to Twitter
                Given the  is logged in to Twitter
                Given the user navigates to "/"
                Given the user clicks the "Sign In" link
                Given the user clicks the "Don't have an account? Join now." link
                Given the user clicks the "Sign up with Twitter" button
                Then the user is redirected to a Twitter page prompting them to authorize the app
                Given the user submits the form
                Then the user is redirected to "/accounts/extradetails/"
                Given the user enters a valid email address in the "Email" input
                Given the user clicks the "I agree to the terms of service" checkbox
                Given the user clicks the "Submit" button
                Then the user should be redirected to the "My Stories" page
                # In the upper-right-hand corner
                Then the text "<firstname>" should be present, where "<firstname>" is the first name specified in the profile of the user's Twitter account

        Scenario: A user registers using their Facebook account when logged in to Facebook
                Given the user is logged in to Facebook 
                Given the user navigates to "/"
                Given the user clicks the "Sign In" link
                Given the user clicks the "Don't have an account? Join now." link
                Given the user clicks the "Sign up with Facebook" button
                Then the user is redirected to a Facebook page
                Then the user is prompted to authorize the app
                Given the user submits the form
                Then the user is redirected to "/accounts/extradetails/"
                Given the user clicks the "I agree to the terms of service" checkbox
                Given the user clicks the "Submit" button
                Then the user should be redirected to the "My Stories" page
                # In the upper-right-hand corner
                Then the text "<firstname>" should be present, where "<firstname>" is the first name specified in the profile of the user's Facebook account

        Scenario: A user logs in with Twitter when not logged in to Twitter
                Given the user has an account associated with their Twitter account 
                Given the user is logged out
                Given the user is not logged in to Twitter
                Given the user navigates to "/"
                Given the user clicks the "Sign In" link
                Given the user clicks the "Sign in with Twitter" button
                Then the user is redirected to a Twitter page prompting for login information and to authorize the app
                Given the user enters their Twitter credentials
                Given the user submits the form
                Then the user should be redirected to the "My Stories" page
                # In the upper-right-hand corner
                Then the text "<firstname>" should be present, where "<firstname>" is the first name specified in the profile of the user's Twitter account

        Scenario: A user logs in with Twitter when logged in to Twitter
                Given the user has an account associated with their Twitter account 
                Given the user is logged out
                Given the user is logged in to Twitter
                Given the user navigates to "/"
                Given the user clicks the "Sign In" link
                Given the user clicks the "Sign in with Twitter" button
                Then the user should be redirected to the "My Stories" page
                # In the upper-right-hand corner
                Then the text "<firstname>" should be present, where "<firstname>" is the first name specified in the profile of the user's Twitter account

        Scenario: A user logs in with Facebook when not logged in to Facebook
                Given the user has an account associated with their Facebook account
                Given the user is logged out
                Given the user is not logged in to Facebook 
                Given the user navigates to "/"
                Given the user clicks the "Sign In" link
                Given the user clicks the "Sign in with Facebook" button
                Then the user is redirected to a Facebook login page
                Given the user enters their Facebook credentials
                Given the user submits the form
                Then the user should be redirected to the "My Stories" page
                # In the upper-right-hand corner
                Then the text "<firstname>" should be present, where "<firstname>" is the first name specified in the profile of the user's Facebook account

        Scenario: A user logs in with Facebook when logged in to Facebook
                Given the user has an account associated with their Facebook account
                Given the user is logged out
                Given the user is logged in to Facebook 
                Given the user navigates to "/"
                Given the user clicks the "Sign In" link
                Given the user clicks the "Sign in with Facebook" button
                Then the user should be redirected to the "My Stories" page
                # In the upper-right-hand corner
                Then the text "<firstname>" should be present, where "<firstname>" is the first name specified in the profile of the user's Facebook account
