Feature: Story viewer
        In order to learn about issues in my community
        As a site visitor
        I want to view the sections of a story in my browser

Scenario: Switching to next section after a long section
        Given a story with the title "Test story for long section scrolling in the viewer" exists
        And the story has two sections
        And the first section has content that requires scrolling to view the entire section
        When a site visitor opens the story "Test story for long section scrolling in the viewer"
        And the user navigates to the first section
        And the user scrolls to the bottom of the section
        And the user clicks the "Next" button
        Then the browser should be scrolled to the top of the content for the next section 
