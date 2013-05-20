Feature: A user can associate data sets with assets 
        Scenario: Add an external data set to a new table asset
                Given an admin creates the User "test_user@fakedomain.com"
                Given the user "test_user@fakedomain.com" is logged in
                Given the user navigates to "/build/"
                Given the user clicks the "Sandbox" link
                Given the user inputs "Test story" for the "title" field 
                Given the user inputs "Test User" for the "byline" field 
                Given the user inputs "My summary, so exciting!" for the "summary" textarea 
                Given the user clicks on "Untitled Section" in the section list
                Given the user clicks the "Table" icon in the "center" container
                Given the user inputs "https://docs.google.com/spreadsheet/pub?key=0AvaXS4x_XvJmdGthMFBSb1BJOUNPTnhaNWN4UDZnZkE&output=html" in the "Enter table URL" input
                Given the user clicks the "Save Changes" button
                Given the user hovers over the asset in the "center" container
                # TODO: Update this with finalized UI
                Given the user clicks on the "edit data" icon
                Given the user clicks on the "Add Dataset" button
                Given the user inputs "FOIA No Heats 2011 to Present" in the "Data set name" input
                Given the user inputs "City of Chicago" in the "Data source" input
                Given the user inputs "https://docs.google.com/spreadsheet/ccc?key=0AvaXS4x_XvJmdGthMFBSb1BJOUNPTnhaNWN4UDZnZkE#gid=0" in the "Link to a data set" input
                Given the user clicks the "Save" button
                Then "FOIA No Heats 2011 to Present" appears in the data set list
                Given the user refreshes the browser
                Given the user clicks on "Untitled Section" in the section list
                Given the user hovers over the asset in the "center" container
                Given the user clicks on the "edit data" icon
                Then "FOIA No Heats 2011 to Present" appears in the data set list


        Scenario: Add an uploaded CSV file data set to a new table asset
                Given an admin creates the User "test_user@fakedomain.com"
                Given the user "test_user@fakedomain.com" is logged in
                Given the user navigates to "/build/"
                Given the user clicks the "Sandbox" link
                Given the user inputs "Test story" for the "title" field 
                Given the user inputs "Test User" for the "byline" field 
                Given the user inputs "My summary, so exciting!" for the "summary" textarea 
                Given the user clicks on "Untitled Section" in the section list
                Given the user clicks the "Table" icon in the "center" container
                Given the user inputs "https://docs.google.com/spreadsheet/pub?key=0AvaXS4x_XvJmdGthMFBSb1BJOUNPTnhaNWN4UDZnZkE&output=html" in the "Enter table URL" input
                Given the user clicks the "Save Changes" button
                Given the user hovers over the asset in the "center" container
                # TODO: Update this with finalized UI
                Given the user clicks on the "edit data" icon
                Given the user clicks on the "Add Dataset" button
                Given the user inputs "Test CSV Data" in the "Data set name" input
                Given the user inputs "City of Chicago" in the "Data source" input
                Given the user clicks the "choose file" button
                Given the user selects the file "test_data.csv"
                Given the user clicks the "Save" button
                Then "Test CSV Data" appears in the data set list
                Given the user refreshes the browser
                Given the user clicks on "Untitled Section" in the section list
                Given the user hovers over the asset in the "center" container
                Given the user clicks on the "edit data" icon
                Then "Test CSV Data" appears in the data set list


        Scenario: Add a dataset to an existing table asset
                Given an admin creates the User "test_user@fakedomain.com"
                Given the user "test_user@fakedomain.com" is logged in
                Given the user navigates to "/build/"
                Given the user clicks the "Sandbox" link
                Given the user inputs "Test story" for the "title" field 
                Given the user inputs "Test User" for the "byline" field 
                Given the user inputs "My summary, so exciting!" for the "summary" textarea 
                Given the user clicks on "Untitled Section" in the section list
                Given the user clicks the "Table" icon in the "center" container
                Given the user inputs "https://docs.google.com/spreadsheet/pub?key=0AvaXS4x_XvJmdGthMFBSb1BJOUNPTnhaNWN4UDZnZkE&output=html" in the "Enter table URL" input
                Given the user clicks the "Save Changes" button
                Given the user refreshes the browser
                Given the user clicks on "Untitled Section" in the section list
                Given the user hovers over the asset in the "center" container
                Given the user clicks on the "edit data" icon
                Given the user clicks on the "Add Dataset" button
                Given the user inputs "FOIA No Heats 2011 to Present" in the "Data set name" input
                Given the user inputs "City of Chicago" in the "Data source" input
                Given the user inputs "https://docs.google.com/spreadsheet/ccc?key=0AvaXS4x_XvJmdGthMFBSb1BJOUNPTnhaNWN4UDZnZkE#gid=0" in the "Link to a data set" input
                Given the user clicks the "Save" button
                Then "FOIA No Heats 2011 to Present" appears in the data set list
                Given the user refreshes the browser
                Given the user clicks on "Untitled Section" in the section list
                Given the user hovers over the asset in the "center" container
                Given the user clicks on the "edit data" icon
                Then "FOIA No Heats 2011 to Present" appears in the data set list

        Scenario: Add an additional data set to a table asset
                Given the scenario "Add an external data set to a new table asset" has been run
                Given the user clicks on the "Add Dataset" button
                Given the user inputs "Test CSV Data" in the "Data set name" input
                Given the user inputs "City of Chicago" in the "Data source" input
                Given the user clicks the "choose file" button
                Given the user selects the file "test_data.csv"
                Given the user clicks the "Save" button
                Then "Test CSV Data" appears in the data set list
                Then "FOIA No Heats 2011 to Present" appears in the data set list
                Given the user refreshes the browser
                Given the user clicks on "Untitled Section" in the section list
                Given the user hovers over the asset in the "center" container
                Given the user clicks on the "edit data" icon
                Then "Test CSV Data" appears in the data set list
                Then "FOIA No Heats 2011 to Present" appears in the data set list

        Scenario: Add an additional data set to a table asset after re-adding it to a section 
                Given the scenario "Add an external data set to a new table asset" has been run
                Given the user clicks the "Cancel" button
                Given the user hovers over the asset in the "center" container
                Given the user clicks the remove icon for asset in the "center" container
                Given the user opens the asset drawer
                Given the user drags the asset "https://docs.google.com/spreadsheet/pub?key=0AvaXS4x_XvJmdGthMFBSb1BJOUNPTnhaNWN4UDZnZkE&output=html" from the asset drawer to the "center" container 
                Given the user hovers over the asset in the "center" container
                Given the user clicks on the "edit data" icon
                Then "FOIA No Heats 2011 to Present" appears in the data set list
                Given the user clicks on the "Add Dataset" button
                Given the user inputs "Test CSV Data" in the "Data set name" input
                Given the user clicks the "choose file" button
                Given the user selects the file "test_data.csv"
                Given the user clicks the "Save" button
                Then "Test CSV Data" appears in the data set list
                Then "FOIA No Heats 2011 to Present" appears in the data set list
                Given the user refreshes the browser
                Given the user clicks on "Untitled Section" in the section list
                Given the user hovers over the asset in the "center" container
                Given the user clicks on the "edit data" icon
                Then "Test CSV Data" appears in the data set list
                Then "FOIA No Heats 2011 to Present" appears in the data set list

        Scenario: Add an external data set to a table asset after re-adding it to a section
                Given the scenario "Add an external data set to a new table asset" has been run
                Given the user clicks the "Cancel" button
                Given the user hovers over the asset in the "center" container
                Given the user clicks the remove icon for asset in the "center" container
                Given the user clicks the "Table" icon in the "center" container
                Given the user enters the following in the "Or, paste the embed code for the table" field:
                """
                <table>
                  <tr>
                    <th>Col 1</th>
                    <th>Col 2</th>
                  </tr>
                  <tr>
                    <td>Blah</td>
                    <td>20.231</td>
                  </tr>
                </table>
                """
                Given the user clicks the "Save Changes" button
                Given the user hovers over the asset in the "center" container
                Given the user clicks on the "edit data" icon
                Then no data sets should be listed
                Given the user clicks the "Cancel" button
                Given the user hovers over the asset in the "center" container
                Given the user clicks the remove icon for asset in the "center" container
                Given the user opens the asset drawer
                Given the user drags the last removed asset from the asset drawer to the "center" container
                Given the user hovers over the asset in the "center" container
                Given the user clicks on the "edit data" icon
                Then no data sets should be listed
                Given the user clicks on the "edit data" icon
                Given the user clicks on the "Add Dataset" button
                Given the user inputs "Fake Data Set" in the "Data set name" input
                Given the user inputs "Fake source" in the "Data source" input
                Given the user inputs "http://data.gov/fake.csv" in the "Link to a data set" input
                Given the user clicks the "Save" button
                Then "Fake Data Set" appears in the data set list

        Scenario: Add an additional data set to a table asset after the layout has been changed
                Given the scenario "Add an external data set to a new table asset" has been run
                Given the user clicks the "Cancel" button
                Given the user changes the layout to "Side by Side"
                Given the user opens the asset drawer
                Given the user drags the asset "https://docs.google.com/spreadsheet/pub?key=0AvaXS4x_XvJmdGthMFBSb1BJOUNPTnhaNWN4UDZnZkE&output=html" from the asset drawer to the "left" container 
                Given the user hovers over the asset in the "left" container
                Given the user clicks on the "edit data" icon
                Then "FOIA No Heats 2011 to Present" appears in the data set list
                Given the user clicks on the "Add Dataset" button
                Given the user inputs "Fake Data Set" in the "Data set name" input
                Given the user inputs "Fake source" in the "Data source" input
                Given the user inputs "http://data.gov/fake.csv" in the "Link to a data set" input
                Given the user clicks the "Save" button
                Then "FOIA No Heats 2011 to Present" appears in the data set list
                Then "Fake Data Set" appears in the data set list
