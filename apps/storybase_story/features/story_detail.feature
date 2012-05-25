Feature: Viewing story metadata on the story detail page 

    # Acceptance test T0053
    Scenario: A user can view story metatadata on a story detail page 
        Given the user "admin" has first name "Jordan" and last name "Wirfs-Brock"
        Given the Organization "Mile High Connects" has been created
        Given the Project "The Metro Denver Regional Equity Atlas" has been created
        Given the following topics have been created:
            | name      |
            | Education |
        Given the Story "Transportation Challenges Limit Education Choices for Denver Parents" has been created
        Given the Story "Transportation Challenges Limit Education Choices for Denver Parents" has author "admin"
        Given the Story "Transportation Challenges Limit Education Choices for Denver Parents" is published
        Given the Story "Transportation Challenges Limit Education Choices for Denver Parents" has the following summary:
            """
            Many families in the Denver metro area use public
            transportation instead of a school bus because for them, a
            quality education is worth hours of daily commuting. Colorado's
            school choice program is meant to foster educational equity,
            but the families who benefit most are those who have time and
            money to travel. Low-income families are often left in a lurch.
            """
        Given the Story "Transportation Challenges Limit Education Choices for Denver Parents" has the byline "Mile High Connects"
        Given the Project "The Metro Denver Regional Equity Atlas" is associated with the Story "Transportation Challenges Limit Education Choices for Denver Parents"
        Given the Organization "Mile High Connects" is associated with the Story "Transportation Challenges Limit Education Choices for Denver Parents"
        Given the Story "Transportation Challenges Limit Education Choices for Denver Parents" has the following topics:
            | name      |
            | Education |
        Given the user navigates to "/stories/transportation-challenges-limit-education-choices"
        Then the Story's title should be "Transportation Challenges Limit Education Choices for Denver Parents"
        Then the Story's summary is listed as the following:
            """
            Many families in the Denver metro area use public
            transportation instead of a school bus because for them, a
            quality education is worth hours of daily commuting. Colorado's
            school choice program is meant to foster educational equity,
            but the families who benefit most are those who have time and
            money to travel. Low-income families are often left in a lurch.
            """
        Then the Story's byline should be "Mile High Connects"
        Then "Mile High Connects" should be listed in the Story's Organizations list
        Then "The Metro Denver Regional Equity Atlas" should be listed in the Story's Projects list
        Then the Story's published date should be set the current date
        Then the Story's last edited date should be set to the current date
        Then the Story's contributor is "Jordan W."
        Then the following the following topics are listed in the Story's Topics list:
            | name      |
            | Education |
