Feature: A user receives e-mail notifications about stories 
	Scenario: A user receives an e-mail notification shortly after publishing a story
		# If walking through this test script manually, the user should use an
		# account with a real e-mail address in order to confirm receipt of the
		# message.
                Given an admin creates the User "test_user@fakedomain.com"
                Given the user "test_user@fakedomain.com" is logged in
                Given the user navigates to "/build/"
                Given the user clicks the "Photovoice" link
                Given the user inputs "Test story for published story notifications" for the "title" field 
                Given the user inputs "Test User" for the "byline" field 
                Given the user inputs "My summary, so exciting!" for the "summary" textarea 
                Given the user clicks on "Image and Text" in the section list
                Given the user clicks the "Image" icon in the "left" container
		# The test_image.jpg file can be downloaded from
		# https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg
		# or be found in the apps/storybase_asset/test_files directory of a cloned copy
		# of the repo
                Given the user selects the file "test_image.jpg" for the "image" input
		Given the user clicks the "Save Changes" button
                Given the user clicks the "Text" icon in the "right" container
		Given the user inputs the following for the "body" textarea:
		    """
		    bot Robin Sloan Nick Denton Zite DocumentCloud libel lawyer afternoon
		    paper attracting young readers Nick Denton, rubber cement information
		    wants to be free The Printing Press as an Agent of Change Marshall
		    McLuhan Gawker WaPo Foursquare, digital circulation strategy cops beat
		    innovation attracting young readers afternoon paper newspaper West
		    Seattle Blog.
		    """
		Given the user clicks the "Save Changes" button
                Given the user clicks the "Publish" workflow tab
		Given the user clicks the "Select an image from the story" link
		Given the user clicks the image "text_image.jpg"
		Given the user clicks the "Publish My Story" button
		Then the user should receive an email within 5 minutes
		Then "Test story for published story notifications" should be in the email's subject
		Then "Test story for published story notifications" should be in the email's body
		Then "Test User" should be in the email's body
		Then "My summary, so exciting!" should be in the email's body
		Then the image "test_image.jpg" should appear in the email's body
		Then the story detail page url for the story "Test story for published story notifications" should be in the email's body
