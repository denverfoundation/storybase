Feature: Password reset
        Scenario: A user resets their password
                Given the user has an account
                Given the user navigates to "/"
                Given the user clicks the "Sign In" link
                Given the user clicks the "Forgot password?" link
                Given the user enters the email address associated with their account in the "Email" field
                Given the user clicks the "Reset my password" button
                Then the user should receive a password reset email
                Given the user visits the link in the password reset email
                Given the user enters "test_password2" in the "New password" input
                Given the user enters "test_password2" in the "Confirm password" input
                Given the user clicks the "Change my password" button
                Given the user navigates to "/accounts/login/"
                Given the user enters their email address in the "Email" input
                Given the user enters "test_password2" in the "Password" input
                Given the user clicks the "Sign In" button
                Then the user should be redirected to the "My Stories" page
