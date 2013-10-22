Feature: Edit text assets in the story builder
        In order to add text to my story
        As an authenticated user
        I want to add and edit text in the story builder

        Scenario: Autosave a new text asset
                Given the user "test_user@fakedomain.com" is logged in
                When the user navigates to "/build/"
                And the user clicks the "Sandbox" link
                And the user inputs "Test story for autosaving a new text asset" for the "title" field 
                And the user inputs "Test User" for the "byline" field 
                And the user inputs "My summary, so exciting!" for the "summary" textarea 
                # That is, the first "real section" not "Story Information"
                And the user clicks on the first section in the section list
                And the user clicks the "Text" icon in the "center" container
                And the user inputs the following text in the rich text editor: 
                        """
                        Test text for asset. This is cool. 
                        """
                And the user clicks "Story Information" in the section list
                And the user inputs "Test story for autosaving a new text asset - updated" for the "title" field 
                And the user refreshes the browser
                And the user clicks on the first section in the section list
                Then the following text is present:
                        """
                        Test text for asset. This is cool. 
                        """

        Scenario: Autosave an existing text asset
                Given the user "test_user@fakedomain.com" is logged in
                When the user navigates to "/build/"
                And the user clicks the "Sandbox" link
                And the user inputs "Test story for autosaving an existing text asset" for the "title" field 
                And the user inputs "Test User" for the "byline" field 
                And the user inputs "My summary, so exciting!" for the "summary" textarea 
                # That is, the first "real section" not "Story Information"
                And the user clicks on the first section in the section list
                And the user clicks the "Text" icon in the "center" container
                And the user inputs the following text in the rich text editor: 
                        """
                        Test text for asset. This is cool. 
                        """
                And the user clicks the "save" button
                And the user clicks the "Edit Text" link 
                And the user adds the following text in the rich text editor: 
                        """
                        New text for test asset! 
                        """
                And the user clicks "Story Information" in the section list
                And the user refreshes the browser
                And the user clicks on the first section in the section list
                Then the following text is present:
                        """
                        Test text for asset. This is cool. New text for test asset!
                        """

        Scenario: Cancel editing a new text asset
                Given the user "test_user@fakedomain.com" is logged in
                When the user navigates to "/build/"
                And the user clicks the "Sandbox" link
                And the user inputs "Test story for canceling editing of a new text asset" for the "title" field 
                And the user inputs "Test User" for the "byline" field 
                And the user inputs "My summary, so exciting!" for the "summary" textarea 
                And the user clicks on the first section in the section list
                And the user clicks the "Text" icon in the "center" container
                And the user inputs the following text in the rich text editor: 
                        """
                        Test text for asset. This is cool. 
                        """
                And the user clicks the "cancel" button
                Then the following text is not present:
                        """
                        Test text for asset. This is cool. 
                        """
                And the "Image" icon is present
                And the "Text" icon is present
                When the user refreshes the browser 
                And the user clicks on the first section in the section list
                Then the following text is not present:
                        """
                        Test text for asset. This is cool. 
                        """
                When the user opens the asset drawer
                Then the following text is not present:
                        """
                        Test text for asset. This is cool. 
                        """

        Scenario: Cancel editing an existing text asset
                Given the user "test_user@fakedomain.com" is logged in
                When the user navigates to "/build/"
                And the user clicks the "Sandbox" link
                And the user inputs "Test story for canceling editing of an existing text asset" for the "title" field 
                And the user inputs "Test User" for the "byline" field 
                And the user inputs "My summary, so exciting!" for the "summary" textarea 
                And the user clicks on the first section in the section list
                And the user clicks the "Text" icon in the "center" container
                And the user inputs the following text in the rich text editor: 
                        """
                        Test text for asset. This is cool. 
                        """
                And the user clicks the "save" button
                And the user clicks the text "Edit Text"
                And the user inputs the following text in the rich text editor: 
                        """
                        New text for asset.
                        """
                And the user clicks the "cancel" button
                Then the following text is present:
                        """
                        Test text for asset. This is cool. 
                        """
                And the following text is not present:
                        """
                        New text for asset.
                        """
                When the user refreshes the browser 
                And the user clicks on the first section in the section list
                Then the following text is present:
                        """
                        Test text for asset. This is cool. 
                        """
                And the following text is not present:
                        """
                        New text for asset.
                        """

        Scenario: Manually save a new text asset
                Given the user "test_user@fakedomain.com" is logged in
                When the user navigates to "/build/"
                And the user clicks the "Sandbox" link
                And the user inputs "Test story for manually saving a new text asset" for the "title" field 
                And the user inputs "Test User" for the "byline" field 
                And the user inputs "My summary, so exciting!" for the "summary" textarea 
                And the user clicks on the first section in the section list
                And the user clicks the "Text" icon in the "center" container
                And the user inputs the following text in the rich text editor: 
                        """
                        Test text for asset. This is cool. 
                        """
                And the user clicks the "save" button
                Then the following text is present: 
                        """
                        Test text for asset. This is cool. 
                        """
                And the text "Edit Text" is present
                When the user refreshes the browser 
                And the user clicks on the first section in the section list
                Then the following text is present:
                        """
                        Test text for asset. This is cool. 
                        """

        Scenario: Manually save an existing text asset
                Given the user "test_user@fakedomain.com" is logged in
                When the user navigates to "/build/"
                And the user clicks the "Sandbox" link
                And the user inputs "Test story for manually saving a new text asset" for the "title" field 
                And the user inputs "Test User" for the "byline" field 
                And the user inputs "My summary, so exciting!" for the "summary" textarea 
                And the user clicks on the first section in the section list
                And the user clicks the "Text" icon in the "center" container
                And the user inputs the following text in the rich text editor: 
                        """
                        Test text for asset. This is cool. 
                        """
                And the user clicks the "save" button
                And the user clicks the "Edit Text" link 
                And the user inputs the following text in the rich text editor: 
                        """
                        New text for test asset! 
                        """
                And the user clicks the "save" button
                Then the text "Edit Text" is present
                And the following text is present:
                        """
                        New text for test asset! 
                        """
                When the user refreshes the browser 
                And the user clicks on the first section in the section list
                Then the following text is not present:
                        """
                        Test text for asset. This is cool. 
                        """
                And the following text is present:
                        """
                        New text for asset.
                        """
