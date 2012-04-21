Feature: Sharing content with AddThis
    # Acceptance test T0047
    Scenario: An admin can share a story from the story detail page using the AddThis widget
        Given the Story "Transportation Challenges Limit Education Choices for Denver Parents" has been created
        Given the Story "Transportation Challenges Limit Education Choices for Denver Parents" is published
        Given the user navigates to "/stories/transportation-challenges-limit-education-choices"
        Then an AddThis widget should appear
        Then the AddThis widget should be the 32x32 style
        Then a Twitter button should be in the AddThis widget
        Then a Facebook button should be in the AddThis widget
        Then a email button should be in the AddThis widget
        Then the generic button should be in the AddThis widget
        Then the counter should be in the AddThis widget
