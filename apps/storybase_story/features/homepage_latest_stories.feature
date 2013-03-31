Feature: A list of recently published stories appears on the homepage
        Scenario: A newly published story is promoted to the top of the latest stories list on the homepage

        Scenario: Publishing a connected story promotes its seed story to the top of the latest stories list on the homepage
                Given an admin creates the User "test_user@floodlightproject.org"
                Given the user "test_user@floodlightproject.org" exists
                Given the seed Story "Test Seed Story" has been created with prompt "Tell your story."
                Given the Story "Test Seed Story" is published
                Given the Story "Test Connected Story" has been created
                Given the Story "Test Connected Story" is a connected story to "Test Seed Story"
                Given the Story "Test Story 1" has been created
                Given the Story "Test Story 1" is published
                Given the Story "Test Story 2" has been created
                Given the Story "Test Story 2" is published
                Given the Story "Test Story 3" has been created
                Given the Story "Test Story 3" is published
                Then "Test Story 1" appears in the latest stories list
                Then "Test Story 2" appears in the latest stories list
                Then "Test Story 3" appears in the latest stories list
                Then "Test Seed Story" does not appear in the latest stories list
                Given "Test Connected Story" is published
                Then "Test Seed Story" appears in the latest stories list

        Scenario: Publishing a connected story does not cause it to be promoted to the latest stories list on the homepage
                Given an admin creates the User "test_user@floodlightproject.org"
                Given the user "test_user@floodlightproject.org" exists
                Given the Story "Test Story 1" has been created with author "test_user@floodlightproject.org"
                Given the Story "Test Story 1" is published
                Given the Story "Test Story 1" is featured on the homepage
                Given the Story "Test Story 2" has been created
                Given the Story "Test Story 2" is published
                Given the Story "Test Story 3" has been created
                Given the Story "Test Story 3" is published
                Given the Story "Test Story 4" has been created
                Given the Story "Test Story 4" is published
                Then "Test Story 1" does not appear in the latest stories list
                Then "Test Story 2" appears in the latest stories list
                Then "Test Story 3" appears in the latest stories list
                Then "Test Story 4" appears in the latest stories list
                Given the Story "Test Story 1" is not featured on the homepage
                Then "Test Story 1" does not appear in the latest stories list

        Scenario: Removing a story from the featured box does not cause it to be promoted to the latest stories list on the homepage
