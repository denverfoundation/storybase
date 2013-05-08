Feature: A user can create, edit and publish a story
        Scenario: A user can create, edit and publish a story
                Given these topics exist
                    | name         |
                    | Children     |
                    | Demographics |
                Given these places exist
                    | name         |
                    | 80007        |
                    | Athmar Park  |
                Given these organizations exist
                    | name                 |
                    | The Piton Foundation |
                Given these projects exist
                    | name                                |
                    | StoryCorps visits Denver and Aurora |
                Given an admin creates the User "test_user@fakedomain.com"
                Given the user "test_user@fakedomain.com" is logged in
                Given the user navigates to "/build/"
                Given the user clicks the "Sandbox" link
                Given the user inputs "Test story" for the "title" field 
                Given the user inputs "Test User" for the "byline" field 
                Given the user inputs "My summary, so exciting!" for the "summary" textarea 
                Given the user clicks on "Untitled Section" in the section list
                Given the user inputs "Let's try an audio clip" for the section title
                Given the user clicks the "Audio" icon in the "center" container
                Given the user inputs "http://soundcloud.com/inews/long-term-care-for-kcfr-public-radio-day-1" in the "Enter audio URL" field
                Given the user clicks the "Save Changes" button
                Then the Soundcloud widget for "http://soundcloud.com/inews/long-term-care-for-kcfr-public-radio-day-1" is visible
                Given the user clicks the text "Click to edit caption"
                Given the user inputs "This is a news story about Colorado disabled people living on their own" in the caption textarea
                Given the user clicks the "Save" button
                Given the user clicks the add section button after "Let's try an audio clip"
                Given the user inputs "This is another section" for the section title
                Given the user clicks the "Image" icon in the "center" container
                Given the user inputs "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" in the "Enter image URL" field
                Given the user clicks the "Save Changes" button
                Then the image "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" is visible
                Given the user clicks the text "Click to edit caption"
                Given the user inputs "This is a test image" in the caption textarea
                Given the user clicks the "Save" button
                Given the user changes the layout to "Above/Below"
                Then the text "You removed an asset, but it's not gone forever" is present
                Given the user drags the image "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" from the asset drawer to the "top" container
                Then the image "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" is visible
                Given the user clicks the "Quotation" icon in the "bottom" container
                Given the user inputs "Be curious. Read widely. Try new things. I think a lot of what people call intelligence just boils down to curiosity." in the "Enter the quotation text" textarea
                Given the user inputs "Aaron Swartz" in the "Attribution" textarea
                Given the user inputs "https://aaronsw.jottit.com/howtoget" into the "Source URL" field
                Given the user clicks the "Save Changes" button
                Given the user drags the "Let's try an audio clip" section after the "This is another section" section in the section list
                Then the section "This is another section" should be before the section "Let's try an audio clip" in the section list
                Given the user clicks the add section button after "Let's try an audio clip"
                Then the section "Untitled Section" should be after the section "Let's try an audio clip" in the section list
                Given the user inputs "Yet another section ..." for the section title
                Given the user changes the layout to "Side by Side"
                Given the user clicks the "Text" icon in the "left" container
                Given the user inputs "This is my text asset" in the text asset textarea
                Given the user clicks the "Save Changes" button
                Given the user clicks the "Table" icon in the "right" container
                Given the user inputs "https://docs.google.com/spreadsheet/pub?key=0AvaXS4x_XvJmdGthMFBSb1BJOUNPTnhaNWN4UDZnZkE&output=html" in the "Enter table URL" input
                Given the user inputs "Chicago no heat 311 requests" in the "Title" input 
                Given the user clicks the "Save Changes" button
                Then "https://docs.google.com/spreadsheet/pub?key=0AvaXS4x_XvJmdGthMFBSb1BJOUNPTnhaNWN4UDZnZkE&output=html" should appear in an iframe
                Given the user drags the "Yet another section" section before the "Let's try an audio clip" section in the section list
                Then the section "Yet another section" should be before the section "Let's try an audio clip" in the section list
                Given the user clicks on "Let's try an audio clip" in the section list
                Given the user inputs "Changing a section title" for the section title
                Given the user clicks the "Save" button
                Then "Let's try an audio clip" should appear in the section list
                Given the user clicks "Call to Action" in the section list
                Given the user clicks on the text "Click to edit the call to action"
                Given the user inputs "Read the story! Do it!" in the call to action textarea
                Given the user clicks the "Make this a Connected Story" checkbox
                Given the user clicks in the connected story prompt textarea
                Given the user types "What is your favorite ice cream flavor" in the connected story prompt textarea
                Given the user clicks the "Add Data" workflow tab
                Given the user clicks the "Add Data" button 
                Given the user inputs "FOIA No Heats 2011 to Present" in the "Data set name" input
                Given the user inputs "City of Chicago" in the "Data source" input
                Given the user inputs "https://docs.google.com/spreadsheet/ccc?key=0AvaXS4x_XvJmdGthMFBSb1BJOUNPTnhaNWN4UDZnZkE#gid=0" in the "Link to a data set" input
                Given the user clicks the "Save" button
                Then "FOIA No Heats 2011 to Present" appears in the data set list
                Given the user clicks the "Tag" workflow tab
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
                Given the user clicks the "Review" workflow tab
                Given the user clicks the "Preview Story" button
                Then the Story "Test story" opens in the viewer in a new tab 
                Then the text "Test story" is present
                Then the text "By Test User" is present
                Then the text "My summary, so exciting!" is present
                Given the user clicks the "Next" button
                Then the text "This is another section" is present
                Then the image "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" is present in the "top" container 
                Then the text "Be curious. Read widely. Try new things. I think a lot of what people call intelligence just boils down to curiosity." is present in the "bottom" container
                Then the text "Aaron Swartz" is present in the "bottom" container
                Given the user clicks the "Next" button
                Then the text "Yet another section ..." is present
                Then the text "This my text assset." is present in the "left" container
                Then "https://docs.google.com/spreadsheet/pub?key=0AvaXS4x_XvJmdGthMFBSb1BJOUNPTnhaNWN4UDZnZkE&output=html" should appear in an iframe in the "right" container
                Given the user clicks the "Next" button
                Then the Soundcloud widget for "http://soundcloud.com/inews/long-term-care-for-kcfr-public-radio-day-1" is visible in the "center" container
                Given the user clicks the "Next" button
                Then the text "Read the story! Do it!" is present
                Then the text "What is your favorite ice cream flavor?" is present
                Given the user clicks the "Click her to contribute to this story" link
                Then the connected story builder for the story "Test story" opens in a new tab
                Given the user clicks on the story builder tab
                Given the user clicks the "Publish/Share" workflow tab
                Then the image "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" is selected as the featured image
                Given the user clicks the "Add a new image" link
                Given the user clicks the "choose file" button
                Given the user selects the image "test_image2.png"
                Given the user clicks the "Save Changes" button
                Then the image "test_image2.png" is selected as the featured image
                Given the user clicks the "Publish your story" button
                Then a "Story published" alert is shown
                Given the user clicks the "View my story" button
                Then the Story "Test story" opens in the viewer in a new tab 
                Then the text "Test story" is present
                Then the text "By Test User" is present
                Then the text "My summary, so exciting!" is present
                Given the user clicks the "Next" button
                Then the text "This is another section" is present
                Then the image "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" is present in the "top" container 
                Then the text "Be curious. Read widely. Try new things. I think a lot of what people call intelligence just boils down to curiosity." is present in the "bottom" container
                Then the text "Aaron Swartz" is present in the "bottom" container
                Given the user clicks the "Next" button
                Then the text "Yet another section ..." is present
                Then the text "This my text assset." is present in the "left" container
                Then "https://docs.google.com/spreadsheet/pub?key=0AvaXS4x_XvJmdGthMFBSb1BJOUNPTnhaNWN4UDZnZkE&output=html" should appear in an iframe in the "right" container
                Given the user clicks the "Next" button
                Then the Soundcloud widget for "http://soundcloud.com/inews/long-term-care-for-kcfr-public-radio-day-1" is visible in the "center" container
                Given the user clicks the "Next" button
                Then the text "Read the story! Do it!" is present
                Then the text "What is your favorite ice cream flavor?"is present
                Given the user navigates to the story detail page for "Test story"
                Then the image "test_image2.png" is visible
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
                Then these data sets are listed
                    | name                          |
                    | FOIA No Heats 2011 to Present |
                Then the text "Read the story! Do it!" is present

        Scenario: Edit tags for an existing story
                # TODO: Figure out how to implement this.  I asked about this on SO at
                # http://stackoverflow.com/questions/16344801/how-do-i-handle-dependencies-between-scenarios-in-lettuce
                Given the scenario "A user can create, edit and publish a story" has been run
                Given an admin creates the User "test_user@fakedomain.com"
                Given the user "test_user@fakedomain.com" is logged in
                Given the user navigates to "/"
                Given the user clicks the "My Account" link
                Given the user opens the story "Test story" in the builder
                Given the user clicks the "Build" button for "Test story"
                Given the user clicks the "Tag" workflow tab
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
                Givem the user adds the place "80207"
                Given the user clicks the "Build" workflow tab
                Given the user inputs "My summary, so exciting! New summary!" for the "summary" textarea 
                Given the user clicks the "Save" button
                Given the user clicks the "Tag" workflow tab
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
                Given the user clicks the "Build" workflow tab
                Given the user inputs "This is another section" for the section title
                Then the image "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" is visible
                Given the user clicks the remove icon for the section "This is another section"
                Then a confirmation dialog is shown
                Given the user clicks the "Ok" button 
                Given the user clicks the add section button after "Yet another section ..."
                Given the user inputs "New section!!" for the section title
                Given the user drags the image "test_image2.png" from the asset drawer to the "left" container
                Given the user clicks the "Publish/Share" workflow tab
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
                Then these data sets are listed
                    | name                          |
                    | FOIA No Heats 2011 to Present |
                # BOOKMARK
