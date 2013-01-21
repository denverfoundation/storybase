Feature: Organizations 

    # Acceptance Test T0007
    Scenario: Admin can create a new Organization
        Given the admin user is logged in
        Given an admin user creates the Organization "Mile High Connects" with website URL "http://www.urbanlandc.org/collaboratives/mile-high-connects/" and description "Test organization description" in the Django admin
        Then the Organization "Mile High Connects" should have a canonical URL 
        Then the Organization's website should be listed as "http://www.urbanlandc.org/collaboratives/mile-high-connects/"
        Then the Organization's contributors list should be blank
        Then the "Mile High Connects" Organization's created field should be set to within 1 minute of the current date and time
        Then the "Mile High Connects" Organization's last edited field should be set to within 1 minute of the current date and time

    # Acceptance Test T0009
    Scenario: Admin can edit the description for an Organization
        Given the admin user is logged in
        Given the Organization "Mile High Connects" has been created
        Given the Organization "Mile High Connects" has website URL "http://www.urbanlandc.org/collaboratives/mile-high-connects/"
        Given the Organization "Mile High Connects" is visible in the Django admin 
        Given the user visits the admin edit page for Organization "Mile High Connects"
        Then the Organization has the website URL "http://www.urbanlandc.org/collaboratives/mile-high-connects/" in the Django admin
        Given the user sets the "description" of the "Organization" to "Mile High Connects (formerly know as the Mile High Transit Opportunity Collaborative) is an emerging collaborative of nonprofit and philanthropic organizations working together to ensure the creation of the region’s $6.7 billion FasTracks transit system benefits all communities in the region, including low-income populations."
        Given the user clicks the save button
        Given the user navigates to the Organization's detail page
        Then the Organization's description is listed as "Mile High Connects (formerly know as the Mile High Transit Opportunity Collaborative) is an emerging collaborative of nonprofit and philanthropic organizations working together to ensure the creation of the region’s $6.7 billion FasTracks transit system benefits all communities in the region, including low-income populations."
        Then the "Mile High Connects" Organization's last edited field should be set to within 1 minute of the current date and time
        Then all other fields of the Organization are unchanged

    # Acceptance Test T0012
    Scenario: Admin can assign a User to an Organization
        Given the admin user is logged in
        Given an admin creates the User "newuser@floodlightproject.org"
        Given the User "newuser@floodlightproject.org" has the first name "Jane" and last name "Doe"
        Given the Organization "Mile High Connects" has been created
        Given the Organization "Mile High Connects" is visible in the Django admin 
        Given an admin assigns "newuser@floodlightproject.org" to the Organization "Mile High Connects" in the Django admin
        Then "newuser@floodlightproject.org" is listed in the contributors list for Organization "Mile High Connects" on its detail page
        Then "Mile High Connects" is selected on the "newuser@floodlightproject.org" User admin page

    # Acceptance Test T0008
    Scenario: Admin can remove a User from an Organization
        Given the admin user is logged in
        Given an admin creates the User "newuser@floodlightproject.org"
        Given the User "newuser@floodlightproject.org" has the first name "Jane" and last name "Doe"
        Given the Organization "Mile High Connects" has been created
        Given the Organization "Mile High Connects" has the following description:
            """
            Mile High Connects (formerly know as the Mile High Transit Opportunity Collaborative) is an emerging collaborative of nonprofit and philanthropic organizations working together to ensure the creation of the region’s $6.7 billion FasTracks transit system benefits all communities in the region, including low-income populations.
            """
        Given the Organization "Mile High Connects" is visible in the Django admin 
        Given the User "newuser@floodlightproject.org" is associated with the Organization "Mile High Connects"
        Given "newuser@floodlightproject.org" is listed in the contributors list for Organization "Mile High Connects" on its detail page
        Given the user visits the admin edit page for Organization "Mile High Connects"
        Given an admin removes "newuser@floodlightproject.org" from the Organization "Mile High Connects"
        Then "newuser@floodlightproject.org" is not listed in the contributors list for Organization "Mile High Connects" on its detail page
        Then "Mile High Connects" is not selected on the "newuser@floodlightproject.org" User admin page

    # Acceptance Test T0022
    Scenario: Admin can edit Organization information
        Given the admin user is logged in
        Given the Organization "Mile High Connects" has been created
        Given the Organization "Mile High Connects" has the following description:
            """
            Mile High Connects (formerly know as the Mile High Transit Opportunity Collaborative) is an emerging collaborative of nonprofit and philanthropic organizations working together to ensure the creation of the region’s $6.7 billion FasTracks transit system benefits all communities in the region, including low-income populations.
            """
        Given the Organization "Mile High Connects" is visible in the Django admin 
        Given the user visits the admin edit page for Organization "Mile High Connects"
        Given the user sets the "name" of the "Organization" to "Mile High Transit Opportunities Collaborative"
        Given the user sets the "description" of the "Organization" to "Our primary goal is to ensure that the creation of FasTracks improves accessibility to affordable housing, good-paying jobs, essential services, educational opportunities, improved health, and other elements of a high quality of life for all of Metro Denver’s residents, especially those with lower-incomes."
        Given the user clicks the save button
        Given the user navigates to the Organization's detail page
        Then the Organization's name is listed as "Mile High Transit Opportunities Collaborative"
        Then the Organization's description is listed as "Our primary goal is to ensure that the creation of FasTracks improves accessibility to affordable housing, good-paying jobs, essential services, educational opportunities, improved health, and other elements of a high quality of life for all of Metro Denver’s residents, especially those with lower-incomes."
        Then the "Mile High Transit Opportunities Collaborative" Organization's last edited field should be set to within 1 minute of the current date and time
        Then all other fields of the Organization are unchanged
