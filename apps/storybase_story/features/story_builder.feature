Feature: Story builder
        Scenario: Users see a menu of available templates when accessing the story builder
                Given an admin creates the User "test_user@fakedomain.com"
                Given the user "test_user@fakedomain.com" is logged in
                Given the user navigates to "/build/"
                Then the text "PhotoVoice" is present 

        Scenario: Clicking on a template in the menu opens a new story using the template
                Given an admin creates the User "test_user@fakedomain.com"
                Given the user "test_user@fakedomain.com" is logged in
                Given the user navigates to "/build/"
                Given the user clicks the "PhotoVoice" link
                Then the title input is present
                Then the byline input is present
                Then the "summary" text area is present
                Then the "Story Information" section is present in the table of contents
                Then the "Image and Text" section is present in the table of contents
                Then the "Call to Action" section is present in the table of contents
                Then the "BUILD" workflow step button is present
                Then the "ADD DATA" workflow step button is present
                Then the "TAG" workflow step button is present
                Then the "PUBLISH/SHARE" workflow step button is present

        Scenario: Editing the title of a new story auto-saves the story and assigns a story ID
                Given an admin creates the User "test_user@fakedomain.com"
                Given the user "test_user@fakedomain.com" is logged in
                Given the user navigates to "/build/"
                Given the user clicks the "PhotoVoice" link
                Given the user inputs "Test story" for the "title" field 
                Given the user inputs "Test User" for the "byline" field 
                Then the Story "Test story" exists
                Then the browser location should include the story ID for the Story "Test story"

Feature: Image uploads
        # TODO: Implement steps for this scenario
        Scenario: Submitting the image asset form with no file or URL shows an error
                Given an admin creates the User "test_user@fakedomain.com"
                Given the user "test_user@fakedomain.com" is logged in
                Given the user navigates to "/build/"
                Given the user clicks the "PhotoVoice" link
                Given the user inputs "Test Story" for the "title" field
                Given the user clicks the "Untitled Section" section icon in the section list
                Given the user clicks the "image" icon in the "left" container
                Given the user clicks the "Save Changes" button
                Then the user should see an error message

        # TODO: Implement steps for this scenario
        Scenario: Adding an image to a section and container where an image is already assigned shows an error
                Given an admin creates the User "test_user@fakedomain.com"
                Given the user "test_user@fakedomain.com" is logged in
                Given the user navigates to "/build/"
                Given the user clicks the "PhotoVoice" link
                Given the user inputs "Test Story" for the "title" field
                Given the user opens the story "Test Story" in the builder in a separate tab
                Given the user clicks the "Unititled Section" section icon in the section list in the first tab
                Given the user clicks the "image" icon in the "left" container in the first tab
                Given the user selects the file "test_image.jpg" for the "image" field in the first tab
                Given the user clicks the "Save Changes" button in the first tab
                Given the user clicks the "Unititled Section" section icon in the section list in the second tab
                Given the user clicks the "image" icon in the "left" container in the second tab
                Given the user selects the file "test_image2.jpg" for the "image" field in the second tab
                Given the user clicks the "Save Changes" button in the second tab
                Then the user should see an error message in the second tab
                Then the user should see the image "test_image.jpg" in the "left" container in the second tab
