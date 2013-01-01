# Regression test for #417 (Cannot load a previously saved story in builder
# when accessing through a hash-based URL)
Feature: Load a story in the story builder with a hashed story ID
        Scenario: A user can load a story in the builder when accessed with a URL using a hashed story ID
                Given an admin creates the User "test_user@fakedomain.com"
                Given the Story "Transportation Challenges Limit Education Choices for Denver Parents" has been created with author "test_user@fakedomain.com"
                Given the user "test_user@fakedomain.com" is logged in
                Given the user opens the Story "Transportation Challenges Limit Education Choices for Denver Parents" in the story builder with a hashed story ID
                Then the user should be redirected to the story builder for the Story "Transportation Challenges Limit Education Choices for Denver Parents" without a hashed story ID in the URL
                Then the title input is present
                Then the byline input is present

        Scenario: A user can load a connected story in the builder when accessed with a URL using a hashed story ID
                Given an admin creates the User "test_user@fakedomain.com"
                Given the user "test_user@fakedomain.com" is logged in
                Given the connected story "Save the numbats" has been created with prompt "Help us save the numbats by uploading your favorite numbat picture and describing what you like about it."
                Given the user navigates to the story detail page for the story "Save the numbats"
                Given the user clicks the "Contribute to this story" link
                Given the user inputs "Test connected story" for the "title" field 
                Given the user inputs "Test User" for the "byline" field
                Given the user clicks the "Save" button
                Given the user opens the connected Story "Test connected story" in the story builder with a hashed story ID
                Then the user should be redirected to the connected story builder for the Story "Test connected story" without a hashed story ID in the URL
                Then the title input is present
                Then the byline input is present
