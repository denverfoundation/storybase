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
