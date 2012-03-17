Feature: Projects

    # Acceptance test T0020
    Scenario: Admin can create a new Project 
        Given the admin user is logged in
        Given the user navigates to the "Projects" admin
        Given the user navigates to the "Projects" addition page
        Given the admin sets the Project name to  "The Metro Denver Regional Equity Atlas"
        Given the admin selects "Mile High Connects" from the list of available organizations 
        Given the admin clicks the Add icon
        # Leave the URL and Description fields blank
        Given the admin clicks the save button
        Then the Project named "The Metro Denver Regional Equity Atlas" should have a canonical URL 
        Then the Project's name should be "The Metro Denver Regional Equity Atlas"
        Then "Mile High Connects" should be listed in the Project's Organizations list
        Then the Organization's created on field should be set to the current date
        Then the Organization's last edited field should be set to within 1 minute of the current date and time
        Then the Organization's description should be blank
        Then the Organization's stories list should be blank
