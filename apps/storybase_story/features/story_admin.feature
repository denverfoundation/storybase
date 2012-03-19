Feature: Editing stories in Django Admin

    # Acceptance test T0003
    Scenario: An admin can create a story and it's core metadata in English
        Given the admin user is logged in
        Given the user navigates to the "Stories" addition page
        Given the user adds a new "English" "Story" translation
        Given the user sets the "English" "title" of the "Story" to "Transportation Challenges Limit Education Choices for Denver Parents"
        Given the user sets the "English" "summary" of the "Story" to the following: 
            """
            Many families in the Denver metro area use public
            transportation instead of a school bus because for them, a
            quality education is worth hours of daily commuting. Colorado's
            school choice program is meant to foster educational equity,
            but the families who benefit most are those who have time and
            money to travel. Low-income families are often left in a lurch.
            """
        Given the user sets the "byline" of the "Story" to "Mile High Connects"
        Given the user selects "The Metro Denver Regional Equity Atlas" from the list of available Projects
        Given the user clicks the Add Project icon
        Given the user selects "Mile High Connects" from the list of available organizations 
        Given the user clicks the Add Organization icon
        Given the user clicks the save button
        Then the Story "Transportation Challenges Limit Education Choices for Denver Parents" exists 
        Then the Story "Transportation Challenges Limit Education Choices for Denver Parents" should have a canonical URL 
        Given the user navigates to the Story's detail page
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
        Then the Story's last edited field should be set to within 1 minute of the current date and time
        Then the Story's status should be "draft"
        Then the Story's published date should be blank

    # Acceptance test #T0003
#    Scenario: Access the English canonical URL for a Story with an English translation
#        Given the Story "Transportation Challenges Limit Education Choices for Denver Parents" exists
#        Given the user navigates to the Story's "English" detail page
#        Then the Story's summary is listed as the following:
#            """
#            Many families in the Denver metro area use public
#            transportation instead of a school bus because for them, a
#            quality education is worth hours of daily commuting. Colorado’s
#            school choice program is meant to foster educational equity,
#            but the families who benefit most are those who have time and
#            money to travel.  Low-income families are often left in a lurch.
#            """
#        Then the Story's byline should be "Mile High Connects"
#        Then "Mile High Connects" should be listed in the Story's Organizations list
#        Then "The Metro Denver Regional Equity Atlas" should be listed in the Story's Projects list
#        Then the Story's last edited field should be set to within 1 minute of the current date and time
#        Then the Story's status should be "draft"
#        Then the Story's published date should be blank

    # Accepance test #T0003
#    Scenario: Acess the Spanish canonical URL for a Story with only an English translation 
#        Given the Story "Transportation Challenges Limit Education Choices for Denver Parents" exists
#        Given the user navigates to the Story's "Spanish" detail page
#        Then the user is redirected to the Story's "English" detail page
