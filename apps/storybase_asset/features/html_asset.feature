Feature: A user can create assets containing HTML 

    # T0035
    Scenario: User creates an Asset representing a Quotation 
        Given the admin user is logged in
        Given the user navigates to the "Html assets" addition page
        Given the user sets the "English" "title" of the "Html asset" to "Success Express"
        Given the user selects "quotation" for the "type" of the "Html asset"
        Given the user sets the "Attribution" of the "Html asset" to "Ed Brennan, EdNews Colorado"
        Given the user sets the "Source URL" of the "Html asset" to "http://www.ednewsparent.org/teaching-learning/5534-denvers-success-express-rolls-out-of-the-station"
        Given the user sets the "Html asset" "Asset Created" date to "2011-06-03" and time to "00:00"
        Given the user selects "published" for the "Status" of the "Html asset"
        Given the user uses the TinyMCE editor to set the "English" "Body" of the "Html asset" to the following:
        """
        In both the Far Northeast and the Near Northeast, school buses will
        no longer make a traditional series of stops in neighborhoods -
        once in the morning and once in the afternoon. Instead, a fleet of
        DPS buses will circulate between area schools, offering students up
        to three chances to catch the one that will get them to their
        school of choice on time.
         
        Martha Carranza, who has a child at Bruce Randolph, said that for
        students who have depended on RTD, “I was very worried because it
        is very dangerous for the children coming from Globeville and also
        from Swansea ... the kids were arriving late and sometimes missing 
        classes altogether."
         
        And, said Carranza, "... we are very happy that with the new
        transportation system, no child will have any excuse to miss 
        school."
        """ 
        Given the user clicks the save button
        Then the HTML Asset "Success Express" should have a canonical URL 
        Then the Asset's body should be the following:
        """
        In both the Far Northeast and the Near Northeast, school buses will
        no longer make a traditional series of stops in neighborhoods -
        once in the morning and once in the afternoon. Instead, a fleet of
        DPS buses will circulate between area schools, offering students up
        to three chances to catch the one that will get them to their
        school of choice on time.
         
        Martha Carranza, who has a child at Bruce Randolph, said that for
        students who have depended on RTD, “I was very worried because it
        is very dangerous for the children coming from Globeville and also
        from Swansea ... the kids were arriving late and sometimes missing 
        classes altogether."
         
        And, said Carranza, "... we are very happy that with the new
        transportation system, no child will have any excuse to miss 
        school."
        """ 
        Then the Asset's title should be "Success Express"
        Then the Asset's type should be "quotation"
        Then the Asset's attribution should be "Ed Brennan, EdNews Colorado"
        Then the Asset's license should be "Attribution-NonCommercial-ShareAlike Creative Commons"
        Then the Asset's status should be "published"
        Then the Asset's creation date should be "June 3, 2011"
        Then the Asset's last edited field should be set to within 1 minute of the current date and time
        Then the Asset's owner should be "admin"

    # T0036
    Scenario: User creates an Asset representing text

        Given the admin user is logged in
        Given the user navigates to the "Html assets" addition page
        Given the user selects "text" for the "type" of the "Html asset"
        Given the user sets the "Source URL" of the "Html asset" to "http://www.ednewsparent.org/teaching-learning/5534-denvers-success-express-rolls-out-of-the-station"
        Given the user sets the "Html asset" "Asset Created" date to "2011-06-03" and time to "00:00"
        Given the user selects "published" for the "Status" of the "Html asset"
        Given the user uses the TinyMCE editor to set the "English" "Body" of the "Html asset" to the following:
        """
        Eboney Brown’s kids range from age one to age nine, so it helps
        that her daycare center, Early Excellence, is just a short walk
        from Wyatt-Edison Charter School, where her older kids go. Early
        Excellence, which welcomes guests with a mural of a white Denver
        skyline set against a backdrop of blue mountains, serves families
        from as far away as Thornton and Green Valley Ranch. And many of
        those families, says Early Excellence director Jennifer Luke, are
        caught in a cycle of poverty and depend daily on regional
        transportation. "I know they can’t put a bus on every corner," says
        Luke, who knows many parents who combine public transportation with
        long walks - year round, no matter the weather. 
        """ 
        Given the user clicks the save button
        Then the HTML Asset "Eboney Brown’s kids range ..." should have a canonical URL 
        Then the Asset's body should be the following:
        """
        Eboney Brown’s kids range from age one to age nine, so it helps
        that her daycare center, Early Excellence, is just a short walk
        from Wyatt-Edison Charter School, where her older kids go. Early
        Excellence, which welcomes guests with a mural of a white Denver
        skyline set against a backdrop of blue mountains, serves families
        from as far away as Thornton and Green Valley Ranch. And many of
        those families, says Early Excellence director Jennifer Luke, are
        caught in a cycle of poverty and depend daily on regional
        transportation. "I know they can’t put a bus on every corner," says
        Luke, who knows many parents who combine public transportation with
        long walks - year round, no matter the weather. 
        """ 
        Then the Asset's title should be ""
        Then the Asset's type should be "text"
        Then the Asset's license should be "Attribution-NonCommercial-ShareAlike Creative Commons"
        Then the Asset's status should be "published"
        Then the Asset's last edited field should be set to within 1 minute of the current date and time
        Then the Asset's owner should be "admin"
