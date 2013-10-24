Feature: Edit text assets in the story builder
        In order to add text to my story
        As an authenticated user
        I want to add and edit text in the story builder

        Scenario: Autosave a new text asset
                Given the user is logged in
                When the user navigates to "/build/"
                And the user clicks the "Sandbox" link
                And the user inputs "Test story for autosaving a new text asset" for the "title" field 
                And the user inputs "Test User" for the "byline" field 
                And the user inputs "My summary, so exciting!" for the "summary" textarea 
                # That is, the first "real section" not "Story Information"
                And the user clicks on the first section in the section list
                And the user adds a "text" asset in the "center" container
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

        Scenario: Autosave a new text asset by changing sections
                Given the user is logged in
                When the user navigates to "/build/"
                And the user clicks the "Sandbox" link
                And the user inputs "Test story for autosaving a new text asset" for the "title" field 
                And the user inputs "Test User" for the "byline" field 
                And the user inputs "My summary, so exciting!" for the "summary" textarea 
                And the user creates a section
                # That is, the first "real section" not "Story Information"
                And the user clicks on the first section in the section list
                And the user adds a "text" asset in the "center" container
                And the user inputs the following text in the rich text editor: 
                        """
                        Test text for asset. This is cool. 
                        """
                And the user clicks the second section in the section list
                And the user inputs "New section title" for the "title" field
                And the user refreshes the browser
                And the user clicks on the first section in the section list
                Then the following text is present:
                        """
                        Test text for asset. This is cool. 
                        """

        Scenario: Autosave an existing text asset
                Given the user is logged in
                When the user navigates to "/build/"
                And the user clicks the "Sandbox" link
                And the user inputs "Test story for autosaving an existing text asset" for the "title" field 
                And the user inputs "Test User" for the "byline" field 
                And the user inputs "My summary, so exciting!" for the "summary" textarea 
                # That is, the first "real section" not "Story Information"
                And the user clicks on the first section in the section list
                And the user adds a "text" asset in the "center" container
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
        Scenario: Autosave an existing text asset by changing sections
                Given the user is logged in
                When the user navigates to "/build/"
                And the user clicks the "Sandbox" link
                And the user inputs "Test story for autosaving an existing text asset" for the "title" field 
                And the user inputs "Test User" for the "byline" field 
                And the user inputs "My summary, so exciting!" for the "summary" textarea 
                And the user creates a section
                # That is, the first "real section" not "Story Information"
                And the user clicks on the first section in the section list
                And the user adds a "text" asset in the "center" container
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
                And the user clicks the second section in the section list
                And the user inputs "New section title" for the "title" field
                And the user refreshes the browser
                And the user clicks on the first section in the section list
                Then the following text is present:
                        """
                        Test text for asset. This is cool. New text for test asset!
                        """

        Scenario: Cancel editing a new text asset
                Given the user is logged in
                When the user navigates to "/build/"
                And the user clicks the "Sandbox" link
                And the user inputs "Test story for canceling editing of a new text asset" for the "title" field 
                And the user inputs "Test User" for the "byline" field 
                And the user inputs "My summary, so exciting!" for the "summary" textarea 
                And the user clicks on the first section in the section list
                And the user adds a "text" asset in the "center" container
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
                Given the user is logged in
                When the user navigates to "/build/"
                And the user clicks the "Sandbox" link
                And the user inputs "Test story for canceling editing of an existing text asset" for the "title" field 
                And the user inputs "Test User" for the "byline" field 
                And the user inputs "My summary, so exciting!" for the "summary" textarea 
                And the user clicks on the first section in the section list
                And the user adds a "text" asset in the "center" container
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
                Given the user is logged in
                When the user navigates to "/build/"
                And the user clicks the "Sandbox" link
                And the user inputs "Test story for manually saving a new text asset" for the "title" field 
                And the user inputs "Test User" for the "byline" field 
                And the user inputs "My summary, so exciting!" for the "summary" textarea 
                And the user clicks on the first section in the section list
                And the user adds a "text" asset in the "center" container
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
                Given the user is logged in
                When the user navigates to "/build/"
                And the user clicks the "Sandbox" link
                And the user inputs "Test story for manually saving a new text asset" for the "title" field 
                And the user inputs "Test User" for the "byline" field 
                And the user inputs "My summary, so exciting!" for the "summary" textarea 
                And the user clicks on the first section in the section list
                And the user adds a "text" asset in the "center" container
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

        Scenario: Autosave when switching section layouts
                Given the user creates a new "Sandbox" story with title "Test story for autosave when switching section layouts"
                When the user clicks on the first section in the section list
                And the user adds a "text" asset in the "center" container
                And the user inputs the following text in the rich text editor:
                        """
                        Test text for asset. This is cool.
                        """
                And the user changes the layout to "Side by Side"
                When the user opens the asset drawer
                Then the following text is present:
                        """
                        Test text for asset. This is cool.
                        """

        Scenario: Autosave when creating a new section
                Given the user creates a new "Sandbox" story with title "Test story for autosave when creating a new section"
                When the user clicks on the first section in the section list
                And the user adds a "text" asset in the "center" container
                And the user inputs the following text in the rich text editor:
                        """
                        Test text for asset. This is cool.
                        """
                And the user creates a section
                And the user inputs "New section title" for the "title" field
                And the user refreshes the browser
                And the user clicks on the first section in the section list
                Then the following text is present:
                        """
                        Test text for asset. This is cool. 
                        """

        Scenario: Autosave when moving a section
                Given the user creates a new "Sandbox" story with title "Test story for autosave when creating a new section"
                And the user creates a section
                When the user clicks on the first section in the section list
                And the user adds a "text" asset in the "center" container
                And the user inputs the following text in the rich text editor:
                        """
                        Test text for asset. This is cool.
                        """
                And the user moves the first section to the end of the story
                And the user refreshes the browser
                And the user clicks on the last section in the section list
                Then the following text is present:
                        """
                        Test text for asset. This is cool. 
                        """

        Scenario: Autosave when editing another asset
                Given the user creates a new "Sandbox" story with title "Test story for autosave when creating a new section"
                And the user clicks on the first section in the section list
                And the user changes the layout to "Side by Side"
                When the user adds a "text" asset in the "left" container
                And the user inputs the following text in the rich text editor:
                        """
                        Test text for left asset. This is cool.
                        """
                And the user adds a "text" asset in the "right" container
                And the user inputs the following text in the rich text editor:
                        """
                        Test text for the right asset.
                        """
                And the user clicks the "Save" button
                And the user refreshes the browser
                And the user clicks on the first section in the section list
                Then the following text is present:
                        """
                        Test text for left asset. This is cool.
                        """
                Then the following text is present:
                        """
                        Test text for the right asset.
                        """
