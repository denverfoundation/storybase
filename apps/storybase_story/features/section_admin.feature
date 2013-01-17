Feature: Editing Story Sections in Django Admin 

    # Acceptance test T0014
    Scenario: An admin can create multiple Story Sections 
        Given the admin user is logged in
        Given the user navigates to the "Sections" addition page
        Given the user sets the "English" "title" of the "Section" to "Children and Affordable Housing"
        Given the user selects "Transportation Challenges Limit Education Choices for Denver Parents" for the "story" of the "Html asset"
        Given the user clicks the Save and add another button
        Given the user sets the "English" "title" of the "Section" to "School Quality"
        Given the user selects "Transportation Challenges Limit Education Choices for Denver Parents" for the "story" of the "Html asset"
        Given the user clicks the Save and add another button
        Given the user sets the "English" "title" of the "Section" to "Early Childhood Education"
        Given the user selects "Transportation Challenges Limit Education Choices for Denver Parents" for the "story" of the "Html asset"
        Given the user clicks the Save and add another button
        Given the user sets the "English" "title" of the "Section" to "Low-Income Families and FRL"
        Given the user selects "Transportation Challenges Limit Education Choices for Denver Parents" for the "story" of the "Html asset"
        Given the user clicks the Save and add another button
        Given the user sets the "English" "title" of the "Section" to "Transportation Spending"
        Given the user selects "Transportation Challenges Limit Education Choices for Denver Parents" for the "story" of the "Html asset"
        Given the user clicks the Save and add another button
        Given the user sets the "English" "title" of the "Section" to "The Choice System"
        Given the user selects "Transportation Challenges Limit Education Choices for Denver Parents" for the "story" of the "Html asset"
        Given the user clicks the save button
        Given the Story "Transportation Challenges Limit Education Choices for Denver Parents" should has a canonical URL 
        Given the user navigates to the Story's detail page
        # The following titles appear under the Sections list:
        #    Children and Affordable Housing
        #    School Quality
        #    Early Childhood Education
        #    Low-Income Families and FRL
        #    Transportation Spending
        #    The Choice System 
