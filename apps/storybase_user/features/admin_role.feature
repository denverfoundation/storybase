Feature: Assigning user to the CA Admin group

    Scenario: Admin can assign a user to the CA Admin group
        Given an admin user assigns "newadmin" user to the "CA Admin" group
        Then "newadmin" shows up in a listing of "CA Admin" users
