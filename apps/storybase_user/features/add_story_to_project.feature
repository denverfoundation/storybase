Feature: Associating stories to projects

    # Acceptance test T0023
    Scenario: Associate multiple stories to a project
        Given the admin user is logged in
        Given the Project "The Metro Denver Regional Equity Atlas" has been created
        Given the Project "The Metro Denver Regional Equity Atlas" has the following description:
            """
            Test project description.
            """
        Given the Story "Transportation Challenges Limit Education Choices for Denver Parents" has been created
        Given the Story "Transportation Challenges Limit Education Choices for Denver Parents" has the following summary:
            """
            Many families in the Denver metro area use public
            transportation instead of a school bus because for them, a
            quality education is worth hours of daily commuting. Colorado's
            school choice program is meant to foster educational equity,
            but the families who benefit most are those who have time and
            money to travel. Low-income families are often left in a lurch.
            """
        Given the Story "Transportation Challenges Limit Education Choices for Denver Parents" is published 
        Given the Story "Connecting the Dots Between Transit And Other Regional Priorities" has been created
        Given the Story "Connecting the Dots Between Transit And Other Regional Priorities" has the following summary:
            """
            Test story summary
            """
        Given the Story "Connecting the Dots Between Transit And Other Regional Priorities" is published
        Given the Project "The Metro Denver Regional Equity Atlas" is associated with the Story "Transportation Challenges Limit Education Choices for Denver Parents"
        Given the user visits the admin edit page for Project "The Metro Denver Regional Equity Atlas"
        Given the user clicks the "Add another Story" link
        Given the user selects the Story "Connecting the Dots Between Transit And Other Regional Priorities" from the drop-down menu
        Given the user clicks the save button
        Given the user navigates to the Project's detail page
        Then the Project's featured story should be "Connecting the Dots Between Transit And Other Regional Priorities"
        Then the Project's stories list should list these stories
            | title |
            | Transportation Challenges Limit Education Choices for Denver Parents |
        Then the "The Metro Denver Regional Equity Atlas" Project's last edited field should be set to within 1 minute of the current date and time
        Then all other fields of the Project are unchanged

    Scenario: Change featured story for a project
        Given the admin user is logged in
        Given the Project "The Metro Denver Regional Equity Atlas" has been created 
        Given the Project "The Metro Denver Regional Equity Atlas" has the following description:
            """
            Test project description.
            """
        Given the Story "Transportation Challenges Limit Education Choices for Denver Parents" has been created
        Given the Story "Transportation Challenges Limit Education Choices for Denver Parents" has the following summary:
            """
            Many families in the Denver metro area use public
            transportation instead of a school bus because for them, a
            quality education is worth hours of daily commuting. Colorado's
            school choice program is meant to foster educational equity,
            but the families who benefit most are those who have time and
            money to travel. Low-income families are often left in a lurch.
            """
        Given the Story "Transportation Challenges Limit Education Choices for Denver Parents" is published 
        Given the Story "Connecting the Dots Between Transit And Other Regional Priorities" has been created
        Given the Story "Connecting the Dots Between Transit And Other Regional Priorities" has the following summary:
            """
            Test story summary
            """
        Given the Story "Connecting the Dots Between Transit And Other Regional Priorities" is published
        Given the Story "Connecting the Dots Between Transit And Other Regional Priorities" is the featured story for the Project "The Metro Denver Regional Equity Atlas"
        Given the user visits the admin edit page for Project "The Metro Denver Regional Equity Atlas"
        Given the user removes the Story "Connecting the Dots Between Transit And Other Regional Priorities" from the Project
        Given the user clicks the "Add another Story" link
        Given the user selects the Story "Transportation Challenges Limit Education Choices for Denver Parents" from the drop-down menu
        Given the user clicks the save button
        Given the user navigates to the Project's detail page
        Then the Project's featured story should be "Transportation Challenges Limit Education Choices for Denver Parents"
        Then the "The Metro Denver Regional Equity Atlas" Project's last edited field should be set to within 1 minute of the current date and time
        Then all other fields of the Project are unchanged
