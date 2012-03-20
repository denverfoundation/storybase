Feature: Associating stories to projects

    # Acceptance test T0023
    Scenario: Associate multiple stories to a project
        Given the admin user is logged in
        Given the Project "The Metro Denver Regional Equity Atlas" exists
        Given the user visits the admin edit page for Project "The Metro Denver Regional Equity Atlas"
        Given the user clicks the "Add another Story" link
        Given the user selects the Story "Transportation Challenges Limit Education Choices for Denver Parents" from the drop-down menu
        Given the user clicks the "Add another Story" link
        Given the user selects the Story "Connecting the Dots Between Transit And Other Regional Priorities" from the drop-down menu
        Given the user clicks the save button
        Given the user navigates to the Project's detail page
        Then the Project's stories list should list these stories
            | title |
            | Transportation Challenges Limit Education Choices for Denver Parents |
            | Connecting the Dots Between Transit And Other Regional Priorities |
        Then the Project's last edited field should be set to within 1 minute of the current date and time
        Then all other fields of the Project are unchanged
