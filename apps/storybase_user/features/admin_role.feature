Feature: Assigning user to the CA Admin group

    Scenario: Admin can assign a user to the CA Admin group
        Given the admin user is logged in
        Given an admin creates the user "newadmin@floodlightproject.org"
        Given an admin creates the group "CA Admin"
        Given an admin assigns "newadmin@floodlightproject.org" user to the "CA Admin" group in the Django admin
        Then "newadmin" shows up in a listing of "CA Admin" users in the Django admin

    Scenario: Admin can unassign a user from the CA Admin group
        Given the admin user is logged in
        Given an admin creates the user "newadmin@floodlightproject.org"
        Given an admin creates the group "CA Admin"
        Given an admin assigns "newadmin@floodlightproject.org" user to the "CA Admin" group
        Given an admin unassigns the user "newadmin@floodlightproject.org" from the "CA Admin" group in the Django admin
        Then "newadmin@floodlightproject.org" doesn't show up in a listing of "CA Admin" users in the Django admin 
