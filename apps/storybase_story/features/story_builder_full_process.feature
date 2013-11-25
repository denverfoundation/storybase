Feature: A user can create, edit and publish a story
        Scenario: A user can create, edit, publish and tag a story
                Given these topics exist
                    | name         |
                    | Children     |
                    | Demographics |
                Given these places exist
                    | name         |
                    | 80007        |
                    | 80207        |
                    | Athmar Park  |
                Given these organizations exist
                    | name                 |
                    | The Piton Foundation |
                Given these projects exist
                    | name                                |
                    | StoryCorps visits Denver and Aurora |
                Given a test user exists
                Given the user is logged in
                Given the user is a member of the organization "The Piton Foundation"
                Given the user is a member of the project "StoryCorps visits Denver and Aurora"
                Given the user navigates to "/build/"
                Given the user selects the "Sandbox" template

                # Set title and byline
                Given the user sets the title to "Test story"
                Given the user sets the byline to "Test User"
                Given the user selects the "Story Info" workflow step

                # Set summary
                Given the user inputs "My summary, so exciting!" for the "summary" textarea 

                # Change the title of a section
                Given the user selects the "Build" workflow step
                Given the user clicks on the first section in the section list
                Given the user inputs "Let's try an audio clip" for the section title
                Then the first section's title should be "Let's try an audio clip"

                # Add an audio asset
                Given the user clicks the "Audio" icon in the "center" container
                Given the user inputs "http://soundcloud.com/inews/long-term-care-for-kcfr-public-radio-day-1" in the "Enter audio URL" field
                Given the user clicks the "Save Changes" button
                Then the Soundcloud widget for "http://soundcloud.com/inews/long-term-care-for-kcfr-public-radio-day-1" is visible

                # Update the caption for an existing asset
                Given the user clicks the text "Edit Audio"
                Given the user inputs "This is a news story about Colorado disabled people living on their own" in the "caption" textarea
                Given the user clicks the "Save Changes" button

                # Add a new section
                Given the user adds a section after "Let's try an audio clip"
                Then the section "Untitled Section" should be after the section "Let's try an audio clip" in the section list
                Given the user inputs "This is another section" for the section title
                Then the section "This is another section" should be after the section "Let's try an audio clip" in the section list

                # Add an image asset by URL
                Given the user clicks the "Image" icon in the "center" container
                Given the user inputs "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" in the "Enter image URL" field
                Given the user clicks the "Save Changes" button
                Then the image "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" is visible in the "center" container
                Given the user clicks the text "Edit Image"
                Given the user inputs "This is a test image" in the "caption" textarea
                Given the user clicks the "Save Changes" button

                # Change the layout
                Given the user changes the layout to "Above/Below"
                Then the "top" container should be visible
                Then the "bottom" container should be visible
                Then the "center" container should not be visible
                Then the text "You removed an asset, but it's not gone forever" is present
                Given the user opens the asset drawer
                Then the image "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" is visible in the asset drawer

                # Add an asset from the drawer
                Given the user drags the image "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" from the asset drawer to the "top" container
                Then the image "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" is visible in the "top" container
                Then the image "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" is not visible in the asset drawer
                Given the user closes the asset drawer

                # Add a quotation asset
                Given the user clicks the "Quotation" icon in the "bottom" container
                Given the user inputs "Be curious. Read widely. Try new things. I think a lot of what people call intelligence just boils down to curiosity." in the "Enter the quotation text" textarea
                Given the user inputs "Aaron Swartz" in the "Attribution" textarea
                Given the user inputs "https://aaronsw.jottit.com/howtoget" into the "Source URL" field
                Given the user clicks the "Save Changes" button
                
                # Reorder sections   
                Given the user drags the "Let's try an audio clip" section after the "This is another section" section in the section list
                Then the section "This is another section" should be before the section "Let's try an audio clip" in the section list

                # Add a section with a side by side layout
                Given the user adds a section after "Let's try an audio clip"
                Then the section "Untitled Section" should be after the section "Let's try an audio clip" in the section list
                Given the user inputs "Yet another section" for the section title
                Then the section "Yet another section" should be after the section "Let's try an audio clip" in the section list

                Given the user changes the layout to "Side by Side"
                Then the "left" container should be visible
                Then the "right" container should be visible
                Then the "top" container should not be visible
                Then the "bottom" container should not be visible

                # Add a text asset
                Given the user clicks the "Text" icon in the "left" container
                Given the user inputs "This is my text asset" in the text asset textarea
                Given the user clicks the "Save Changes" button

                # Add a table asset via a Google Spreadsheet URL
                Given the user clicks the "Table" icon in the "right" container
                Given the user inputs "Chicago no heat 311 requests" in the "Title" input 
                Given the user inputs "https://docs.google.com/spreadsheet/pub?key=0AvaXS4x_XvJmdGthMFBSb1BJOUNPTnhaNWN4UDZnZkE&output=html" in the "Enter table URL" input
                Given the user clicks the "Save Changes" button
                Then "https://docs.google.com/spreadsheet/pub?key=0AvaXS4x_XvJmdGthMFBSb1BJOUNPTnhaNWN4UDZnZkE&output=html" should appear in an iframe

                Given the user drags the "Yet another section" section before the "Let's try an audio clip" section in the section list
                Then the section "Yet another section" should be before the section "Let's try an audio clip" in the section list

                # Changing a section title
                Given the user clicks on "Let's try an audio clip" in the section list
                Given the user inputs "Changing a section title" for the section title
                Given the user clicks the "Save" button
                Then "Changing a section title" should appear in the section list

                # Editing the call to action
                Given the user clicks "Call to Action" in the section list
                Given the user clicks on the text "Click to edit the call to action"
                Given the user inputs "Read the story! Do it!" in the call to action textarea
                Given the user clicks the "Make this a Connected Story" checkbox
                Given the user clicks in the connected story prompt textarea
                Given the user types "What is your favorite ice cream flavor" in the connected story prompt textarea

                # Add a data source
                Given the user clicks "Yet another section" in the section list
                Given the user clicks the "Data Sources" link 
                Given the user clicks the "Add Dataset" button
                Given the user inputs "FOIA No Heats 2011 to Present" in the "Data set name" input
                Given the user inputs "City of Chicago" in the "Data source" input
                Given the user inputs "https://docs.google.com/spreadsheet/ccc?key=0AvaXS4x_XvJmdGthMFBSb1BJOUNPTnhaNWN4UDZnZkE#gid=0" in the "Data URL" input
                Given the user clicks the "Save" button
                Then "FOIA No Heats 2011 to Present" appears in the dataset list below the asset content

                # Verify the default featured image and set a new featured image
                Given the user selects the "Story Info" workflow step
                Then the image "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" is selected as the featured image
                Given the user clicks the "Add a new image" link
                Given the user clicks the "choose file" button
                Given the user selects the image "test_image_2.png"
                Given the user clicks the "Save Changes" button
                Then the image "test_image_2.png" is selected as the featured image

                # Preview the story and verify that the build process works
                Given the user clicks the "Preview" link 
                Then the Story "Test story" opens in the viewer in a new tab 
                Then the text "Test story" is present
                Then the text "By Test User" is present
                Then the text "My summary, so exciting!" is present
                Then the image "test_image_2.png" is present
                Given the user clicks the "Next" button
                Then the text "This is another section" is present
                Then the image "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" is present in the "top" container 
                Then the text "Be curious. Read widely. Try new things. I think a lot of what people call intelligence just boils down to curiosity." is present in the "bottom" container
                Then the text "Aaron Swartz" is present in the "bottom" container
                Given the user clicks the "Next" button
                Then the text "Yet another section" is present
                Then the text "This my text assset." is present in the "left" container
                Then "https://docs.google.com/spreadsheet/pub?key=0AvaXS4x_XvJmdGthMFBSb1BJOUNPTnhaNWN4UDZnZkE&output=html" should appear in an iframe in the "right" container
                Given the user clicks the "Next" button
                Then the Soundcloud widget for "http://soundcloud.com/inews/long-term-care-for-kcfr-public-radio-day-1" is visible in the "center" container
                Given the user clicks the "Next" button
                Then the text "Read the story! Do it!" is present
                Then the text "What is your favorite ice cream flavor?" is present
                Given the user clicks the "Click here to contribute to this story" link
                Then the connected story builder for the story "Test story" opens in a new tab

                # Publish the story
                Given the user clicks on the story builder browser tab
                Given the user selects the "Publish/Share" workflow step
                Given the user clicks the "Publish My Story" button
                Then a "Story published" alert is shown
                Then a "View my story" button is present
                Then a "Unpublish My Story" button is present
                Then a "Share This Story" button is present

                # Add metadata to the story
                Given the user selects the "Tag" workflow step
                Given the user inputs the topics
                    | name         |
                    | Children     |
                    | Demographics |
                Given the user inputs the keywords
                    | name    |
                    | testing |
                    | dev     |
                Given the user selects these places
                    | name         |
                    | 80007        |
                    | Athmar Park  |
                Given the user selects these organizations
                    | name                 |
                    | The Piton Foundation |
                Given the user selects these projects
                    | name                                |
                    | StoryCorps visits Denver and Aurora |

                Given the user clicks the "Publish/Share" workflow step
                Given the user clicks the "View my story" button
                Then the Story "Test story" opens in the viewer in a new tab 
                Then the text "Test story" is present
                Then the text "By Test User" is present
                Then the text "My summary, so exciting!" is present
                Then the image "test_image_2.png" is present
                Given the user clicks the "Next" button
                Then the text "This is another section" is present
                Then the image "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" is present in the "top" container 
                Then the text "Be curious. Read widely. Try new things. I think a lot of what people call intelligence just boils down to curiosity." is present in the "bottom" container
                Then the text "Aaron Swartz" is present in the "bottom" container
                Given the user clicks the "Next" button
                Then the text "Yet another section" is present
                Then the text "This my text assset." is present in the "left" container
                Then "https://docs.google.com/spreadsheet/pub?key=0AvaXS4x_XvJmdGthMFBSb1BJOUNPTnhaNWN4UDZnZkE&output=html" should appear in an iframe in the "right" container
                Given the user clicks the "Next" button
                Then the Soundcloud widget for "http://soundcloud.com/inews/long-term-care-for-kcfr-public-radio-day-1" is visible in the "center" container
                Given the user clicks the "Next" button
                Then the text "Read the story! Do it!" is present
                Then the text "What is your favorite ice cream flavor?"is present

                Given the user navigates to the story detail page for "Test story"
                Then the image "test_image_2.png" is visible
                Then the text "Test story" is present
                Then these organizations are listed
                    | name                 |
                    | The Piton Foundation |
                Then these projects are listed
                    | name                                |
                    | StoryCorps visits Denver and Aurora |
                Then these topics are listed
                    | name         |
                    | Children     |
                    | Demographics |
                Given the user clicks the "Get the Data" button
                Then "FOIA No Heats 2011 to Present" appears in the dataset dropdown list
                Then the text "Read the story! Do it!" is present

        Scenario: Edit tags for an existing story
                # TODO: Figure out how to implement dependencies in Lettuce 
                # features such as this.  I asked about this on SO at
                # http://stackoverflow.com/questions/16344801/how-do-i-handle-dependencies-between-scenarios-in-lettuce
                Given the scenario "A user can create, edit and publish a story" has been run
                Given an admin creates the User "test_user@fakedomain.com"
                Given the user "test_user@fakedomain.com" is logged in
                Given the user navigates to "/"
                Given the user clicks the "My Account" link
                Given the user opens the story "Test story" in the builder
                Given the user clicks the "Build" button for "Test story"
                Given the user selects the "Tag" workflow step
                Then these tags are selected
                    | name    |
                    | testing |
                    | dev     |
                Then these topics are listed
                    | name         |
                    | Children     |
                    | Demographics |
                Then these places are selected
                    | name         |
                    | 80007        |
                    | Athmar Park  |
                Then these organizations are selected
                    | name                 |
                    | The Piton Foundation |
                Then these projects are selected
                    | name                                |
                    | StoryCorps visits Denver and Aurora |
                Given the user removes the topic "Demographics"
                Given the user removes the organization "The Piton Foundation"
                Given the user removes the place "80007"
                Given the user adds the place "80207"

                Given the user selects the "Story Info" workflow step
                Given the user inputs "My summary, so exciting! New summary!" for the "summary" textarea 
                Given the user clicks the "Save" button
                Given the user selects the "Tag" workflow step
                Then these topics are selected 
                    | name         |
                    | Children     |
                Then these places are selected
                    | name         |
                    | 80207        |
                    | Athmar Park  |
                Then these organizations are selected
                    | name |
                Then these projects are selected 
                    | name                                |
                    | StoryCorps visits Denver and Aurora |

                Given the user selects the "Build" workflow step
                Given the user clicks on "This is another section" in the section list 
                Then the image "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" is visible
                Given the user clicks the remove icon for the section "This is another section"
                Then a confirmation dialog is shown
                Given the user clicks the "Ok" button 
                Given the user clicks the add section button after "Yet another section"
                Given the user inputs "New section!!" for the section title
                Given the user drags the image "test_image2.png" from the asset drawer to the "left" container

                Given the user selects the "Story Info" workflow step
                Given the user clicks the "Select an image from the story" link
                Given the user clicks the thumbnail for the image "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg"
                Given the user clicks the "Save" button
                Given the user clicks the "Exit" link
                Given the user navigates to the story detail page for "Test story"
                Then the image "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" is visible
                Then these organizations are listed
                    | name                 |
                Then these projects are listed
                    | name                                |
                    | StoryCorps visits Denver and Aurora |
                Then these topics are listed
                    | name         |
                    | Children     |
