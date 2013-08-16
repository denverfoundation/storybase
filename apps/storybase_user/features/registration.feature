Feature: User can register for an account using their email address
        # Much of the functionality for this feature is derived from the
        # django-registration package, which has its own test suite. Here
        # we're only concerned about testing custom functionality.
        Scenario: User doesn't provide a correctly formatted email address
                Given the user navigates to "/"
                Given the user clicks the "Sign In" link
                Given the user clicks the "Don't have an account? Join now." link
                Given the user enters "ada" in the "E-mail" input
                Given the user enters "test_password" in the "Password" input
                Given the user enters "test_password" in the "Password (again)" input
                Given the user enters "Ada" in the "First name" input
                Given the user enters "Lovelace" in the "Last name" input
                Given the user clicks the "I agree to the terms of service" checkbox
                Given the user clicks the "Sign Up" button
                Then an error message is shown above the "E-mail" input
                Then "ada" should appear in the "E-mail" input
                Then "Ada" should appear in the "First name" input
                Then "Lovelace" should appear in the "Last name" input
                Then the "I agree to the terms of service" input should be checked

        Scenario: User doesn't provide a first name
                Given the user navigates to "/"
                Given the user clicks the "Sign In" link
                Given the user clicks the "Don't have an account? Join now." link
                Given the user enters a valid email address in the "E-mail" input
                Given the user enters "test_password" in the "Password" input
                Given the user enters "test_password" in the "Password (again)" input
                Given the user clicks the "I agree to the terms of service" checkbox
                Given the user clicks the "Sign Up" button
                Then the email address should appear in the "E-mail" input
                Then an error message is shown above the "First name" input 
                Then the "I agree to the terms of service" input should be checked

        # For this to pass the django-passwords package must be installed
        # And the setting PASSWORD_MIN_LENGTH must be set to 8
        Scenario: User provides a password less than 8 characters long
                Given the user navigates to "/"
                Given the user clicks the "Sign In" link
                Given the user clicks the "Don't have an account? Join now." link
                Given the user enters a valid email address in the "E-mail" input
                Given the user enters "test_pw" in the "Password" input
                Given the user enters "test_pw" in the "Password (again)" input
                Given the user enters "Ada" in the "First name" input
                Given the user enters "Lovelace" in the "Last name" input
                Given the user clicks the "I agree to the terms of service" checkbox
                Given the user clicks the "Sign Up" button
                Then an error message is shown above the "Password" input
                Then "Ada" should appear in the "First name" input
                Then "Lovelace" should appear in the "Last name" input
                Then the "I agree to the terms of service" input should be checked

        Scenario: User provides passwords that don't match
                Given the user navigates to "/"
                Given the user clicks the "Sign In" link
                Given the user clicks the "Don't have an account? Join now." link
                Given the user enters a valid email address in the "E-mail" input
                Given the user enters "test_pw1" in the "Password" input
                Given the user enters "test_pw2" in the "Password (again)" input
                Given the user enters "Ada" in the "First name" input
                Given the user enters "Lovelace" in the "Last name" input
                Given the user clicks the "I agree to the terms of service" checkbox
                Given the user clicks the "Sign Up" button
                Then an error message is shown above the form 
                Then the email address should appear in the "E-mail" input
                Then "Ada" should appear in the "First name" input
                Then "Lovelace" should appear in the "Last name" input
                Then the "I agree to the terms of service" input should be checked

        Scenario: User follows mangled activation link            
                Given the user navigates to "/"
                Given the user clicks the "Sign In" link
                Given the user clicks the "Don't have an account? Join now." link
                Given the user enters a valid email address in the "E-mail" input
                Given the user enters "test_password" in the "Password" input
                Given the user enters "test_password" in the "Password (again)" input
                Given the user enters "Ada" in the "First name" input
                Given the user enters "Lovelace" in the "Last name" input
                Given the user clicks the "I agree to the terms of service" checkbox
                Given the user clicks the "Sign Up" button
                Then the text "We’ve sent you a confirmation email. Click the link in that email to verify your account and log in." is present
                Then the user should receive an activation email
                Given the user navigates to "/accounts/activate/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/"
                Then an error message is visible

        Scenario: User registers with an email address
                Given the user navigates to "/"
                Given the user clicks the "Sign In" link
                Given the user clicks the "Don't have an account? Join now." link
                Given the user enters a valid email address in the "E-mail" input
                Given the user enters "test_password" in the "Password" input
                Given the user enters "test_password" in the "Password (again)" input
                Given the user enters "Ada" in the "First name" input
                Given the user enters "Lovelace" in the "Last name" input
                Given the user clicks the "I agree to the terms of service" checkbox
                Given the user clicks the "Sign Up" button
                Then the text "We’ve sent you a confirmation email. Click the link in that email to verify your account and log in." is present
                Then the user should receive an activation email
                Given the user visits the link in the activation email
                Then the user should be redirected to "/accounts/login/"
                Then the text "activation succeeded" is present
                Given the user enters their email address in the "Email" input
                Given the user enters "test_password" in the "Password" input
                Given the user clicks the "Sign In" button
                Then the user should be redirected to the "My Stories" page
                # In the upper-right-hand corner
                Then the text "Hi, Ada" should be present

        Scenario: User tries to register with an already-registered email address
                Given the scenario "User registers with an email address" has been run
                Given the user navigates to "/"
                Given the user clicks the "Sign In" link
                Given the user clicks the "Don't have an account? Join now." link
                Given the user enters a previously registered email address in the "E-mail" input
                Given the user enters "test_password" in the "Password" input
                Given the user enters "test_password" in the "Password (again)" input
                Given the user enters "Ada" in the "First name" input
                Given the user enters "Lovelace" in the "Last name" input
                Given the user clicks the "I agree to the terms of service" checkbox
                Given the user clicks the "Sign Up" button
                Then an error message is shown above the "E-mail" input

        Scenario: User visits the link in the activation email multiple times                 
                Given the scenario "User registers with an email address" has been run
                Given the user is logged out
                Given the user visits the link in the activation email
                Then an error message is visible
                Then a link to the login page is present
