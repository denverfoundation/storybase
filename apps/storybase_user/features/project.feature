Feature: Projects

    # Acceptance test T0020
    Scenario: Admin can create a new Project 
        # Setup:
        # Create an Organization named Mile High Connects 
        Given the admin user is logged in
        Given the user navigates to the "Projects" admin
        Given the user navigates to the "Projects" addition page
        Given the user sets the name of the "Project" to "The Metro Denver Regional Equity Atlas"
        Given the admin selects "Mile High Connects" from the list of available organizations 
        Given the admin clicks the Add icon
        # Leave the URL and Description fields blank
        Given the admin clicks the save button
        Then the Project named "The Metro Denver Regional Equity Atlas" should have a canonical URL 
        Then the Project's name should be "The Metro Denver Regional Equity Atlas"
        Then "Mile High Connects" should be listed in the Project's Organizations list
        Then the Project's created on field should be set to the current date
        Then the Project's last edited field should be set to within 1 minute of the current date and time
        Then the Project's description should be blank
        Then the Project's stories list should be blank

    # Acceptance test T0026
    Scenario: An admin can edit the information for a Project
        Given the admin user is logged in
        Given the Project "The Metro Denver Regional Equity Atlas" exists
        Given the user navigates to the "Projects" admin
        Given the user navigates to the "The Metro Denver Regional Equity Atlas" Project edit admin
       Given the user sets the name of the "Project" to "Reqional Equity Atlas"
        Given the user edits the description of the "Project" to be the following: 
            """
            The Denver Regional Equity Atlas is a product of Mile High
            Connects (MHC), which came together in 2011 to ensure that 
            the region’s significant investment in new rail and bus
            service will provide greater access to opportunity and a
            higher quality of life for all of the region’s residents, but
            especially for economically disadvantaged populations who
            would benefit the most from safe, convenient transit service.

            The Atlas visually documents the Metro Denver region’s
            demographic, educational, employment, health and housing
            characteristics in relation to transit, with the goal of
            identifying areas of opportunity as well as challenges to
            creating and preserving quality communities near transit.
            """
        Given the admin clicks the save button
        Given the user navigates to the Project's detail page
        Then the Project's name should be "Regional Equity Atlas"
        Then "Mile High Connects" should be listed in the Project's Organizations list
        Then the Project's last edited field should be set to within 1 minute of the current date and time
        Then the Project's description is listed as the following:
            """
            The Denver Regional Equity Atlas is a product of Mile High
            Connects (MHC), which came together in 2011 to ensure that 
            the region’s significant investment in new rail and bus
            service will provide greater access to opportunity and a
            higher quality of life for all of the region’s residents, but
            especially for economically disadvantaged populations who
            would benefit the most from safe, convenient transit service.

            The Atlas visually documents the Metro Denver region’s
            demographic, educational, employment, health and housing
            characteristics in relation to transit, with the goal of
            identifying areas of opportunity as well as challenges to
            creating and preserving quality communities near transit.
            """
        Then the Project's stories list should be blank
        Then all other fields of the Project are unchanged
