Feature: Creating connected stories
    # Acceptance test T0164
    Scenario: A logged-in user can launch the connected story builder from the story detail page
        Given an admin creates the User "test_user@fakedomain.com"
        Given the user "test_user@fakedomain.com" is logged in
        Given the connected story "Save the numbats" has been created with prompt "Help us save the numbats by uploading your favorite numbat picture and describing what you like about it."
        Given the user navigates to the story detail page for the story "Save the numbats"
        Given the user clicks the "Contribute to this story" link
        Then the connected story builder is launched for the story "Save the numbats"
        Then the text "Help us save the numbats by uploading your favorite numbat picture and describing what you like about it." is present
        Then the title input is present
        Then the byline input is present
        Then the section list is not present
        Then the text "Add Data" is not present
        Then the text "Review" is not present
        Then the text "Tag" is not present
