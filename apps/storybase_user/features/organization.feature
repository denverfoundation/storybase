Feature: Organizations 

    # Acceptance Test T0007
    Scenario: Admin can create a new Organization
        Given an admin user creates the Organization "Mile High Connects" with website URL "http://www.urbanlandc.org/collaboratives/mile-high-connects/"
        Then the Organization should have a canonical URL 
        Then the Organization's website should be listed as "http://www.urbanlandc.org/collaboratives/mile-high-connects/"
        Then the Organization's members list should be blank
        Then the Organization's created on field should be set to the current date
        Then the Organization's last edited field should be set to within 1 minute of the current date and time
        Then the Organization's description should be blank

    # Acceptance Test T0009
    Scenario: Admin can edit the description for an Organization
        Given the Organization "Mile High Connects" exists
        Given the Organization "Mile High Connects" has website URL "http://www.urbanlandc.org/collaboratives/mile-high-connects/"
        Given the admin visits the admin edit page for Organization "Mile High Connects"
        Given the admin user edits the description for the Organization "Mile High Connects" to be "Mile High Connects (formerly know as the Mile High Transit Opportunity Collaborative) is an emerging collaborative of nonprofit and philanthropic organizations working together to ensure the creation of the region’s $6.7 billion FasTracks transit system benefits all communities in the region, including low-income populations."
        Then the Organization's description is listed as "Mile High Connects (formerly know as the Mile High Transit Opportunity Collaborative) is an emerging collaborative of nonprofit and philanthropic organizations working together to ensure the creation of the region’s $6.7 billion FasTracks transit system benefits all communities in the region, including low-income populations."
        Then the Organization's last edited field should be set to within 1 minute of the current date and time
        Then all other fields of the Organization are unchanged

    # Acceptance Test T0012
    Scenario: Admin can assign a User to an Organization
        Given an admin creates the User "newuser"
        Given the Organization "Mile High Connects" exists
        Given an admin assigns "newuser" to the Organization "Mile High Connects"
        Then "newuser" is listed in the members list for Organization "Mile High Connects"
        Then "Mile High Connects" is selected on the "newuser" User admin page

    # Acceptance Test T0008
    Scenario: Admin can remove a User from an Organization
        Given the Organization "Mile High Connects" exists
        Given the User "newuser" exists
        Given "newuser" is listed in the members list for Organization "Mile High Connects"
        Given the admin visits the admin edit page for Organization "Mile High Connects"
        Given an admin removes "newuser" from the Organization "Mile High Connects"
        Then "newuser" is not listed in the members list for Organization "Mile High Connects"
        Then "Mile High Connects" is not selected on the "newuser" User admin page

    # Acceptance Test T0022
#    Scenario: Admin can edit Organization information
#        Given the Organization "Mile High Connects" exists
#        Given an admin edits the name of the Organization "Mile High Connects" to "Mile High Transit Opportunities Collaborative"
#        Given the admin user edits the description of the Organization to be "Our primary goal is to ensure that the creation of FasTracks improves accessibility to affordable housing, good-paying jobs, essential services, educational opportunities, improved health, and other elements of a high quality of life for all of Metro Denver’s residents, especially those with lower-incomes."
#        Then the Organization's name is listed as "Mile High Transit Opportunities Collaborative"
#        Then the Organization's description is listed as "Our primary goal is to ensure that the creation of FasTracks improves accessibility to affordable housing, good-paying jobs, essential services, educational opportunities, improved health, and other elements of a high quality of life for all of Metro Denver’s residents, especially those with lower-incomes."
#        Then the Organization's last edited field should be set to within 1 minute of the current date and time
#        Then all other fields of the Organization are unchanged
