Feature: Asset creation and editing form
        # There's a bunch of common setup that needs to happen that I'm
        # going to leave off for now

        # Image type asset

        Scenario: Create an image asset by specifying a URL
                Given the user clicks the "Image" icon in the "center" container
                Given the user inputs "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" for the "url" input
                Given the user clicks the "Save Changes" button
                Then the image "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" is visible in the "center" container

        Scenario: Create an image asset by uploading an image file
                Given the user clicks the "Image" icon in the "center" container
                Given the user clicks the "Upload an image" link
		# The test_image.jpg file can be downloaded from
		# https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg
		# or be found in the apps/storybase_asset/test_files directory of a cloned copy
		# of the repo
                Given the user selects the file "test_image.jpg" for the "image" input
		Given the user clicks the "Save Changes" button
                Then the image "test_image.jpg" is visible in the "center" container

        Scenario: Create an image asset by specifying a URL and adding a caption
                Given the user clicks the "Image" icon in the "center" container
                Given the user inputs "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" for the "url" input
                Given the user inputs "Test caption!" in the "caption" textarea
                Given the user clicks the "Save Changes" button
                Then the image "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" is visible in the "center" container
                Then "Test caption!" is visible in the "center" container

        Scenario: Create an image asset by uploading an image file and adding a caption
                Given the user clicks the "Image" icon in the "center" container
                Given the user clicks the "Upload an image" link
                Given the user selects the file "test_image.jpg" for the "image" input
                Given the user inputs "Test caption!" in the "caption" textarea
		Given the user clicks the "Save Changes" button
                Then the image "test_image.jpg" is visible in the "center" container
                Then "Test caption!" is visible in the "center" container

        Scenario: Submit image asset form with no URL or image specified
                Given the user clicks the "Image" icon in the "center" container
                Given the user clicks the "Save Changes" button
                Then an error message is shown above the form

        Scenario: Submit image asset form with both URL and image specified, while in URL tab
                Given the user clicks the "Image" icon in the "center" container
                Given the user inputs "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" for the "url" input
                Given the user clicks the "Upload an image" link
                Given the user selects the file "test_image_2." for the "image" input
                Given the user clicks the "Enter image URL" link
		Given the user clicks the "Save Changes" button
                Then the image "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" is visible in the "center" container

        Scenario: Submit image asset form with both URL and image specified, while in image tab
                Given the user clicks the "Image" icon in the "center" container
                Given the user inputs "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" for the "url" input
                Given the user clicks the "Upload an image" link
                Given the user selects the file "test_image_2." for the "image" input
		Given the user clicks the "Save Changes" button
                Then the image "test_image_2.png" is visible in the "center" container

        Scenario: Submit image asset form with invalid URL
                Given the user clicks the "Image" icon in the "center" container
                Given the user inputs "this is not a URL" for the "url" input
                Given the user clicks the "Save Changes" button
                Then an error message is shown below the "url" input

        Scenario: Update the URL of an image asset
                Given the user clicks the "Image" icon in the "center" container
                Given the user inputs "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" for the "url" input
                Given the user clicks the "Save Changes" button
                Given the user clicks the "Edit Image" link in the "center" container
                Then the "image" input is not visible
                Given the user inputs "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image_2.png" for the "url" input
                Then the image "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image_2.png" is visible in the "center" container

        Scenario: Replace the uploaded image file of an image asset
                Given the user clicks the "Image" icon in the "center" container
                Given the user clicks the "Upload an image" link
                Given the user selects the file "test_image.jpg" for the "image" input
		Given the user clicks the "Save Changes" button
                Given the user clicks the "Edit Image" link in the "center" container
                Then the "url" input is not visible
                # TODO: Add check for thumbnail/filename once this interface is finished
                Given the user selects the file "test_image_2.png" for the "image" input
		Given the user clicks the "Save Changes" button
                Then the image "test_image_2.png" is visible in the "center" container

        Scenario: Replace the uploaded image file of an image asset after removing and re-adding the asset
                Given the user clicks the "Image" icon in the "center" container
                Given the user clicks the "Upload an image" link
                Given the user selects the file "test_image.jpg" for the "image" input
		Given the user clicks the "Save Changes" button
                Given the user changes the layout to "Side by Side"
                Given the user opens the asset drawer
                Given the user drags the image "test_image.jpg" from the asset drawer to the "right" container
                Given the user closes the asset drawer
                Given the user clicks the "Edit Image" link in the "right" container
                Given the user selects the file "test_image_2.png" for the "image" input
		Given the user clicks the "Save Changes" button
                Then the image "test_image_2.png" is visible in the "right" container

        Scenario: Update the caption of an image asset created by uploading and image file
                Given the user clicks the "Image" icon in the "center" container
                Given the user clicks the "Upload an image" link
                Given the user selects the file "test_image.jpg" for the "image" input
		Given the user clicks the "Save Changes" button
                Given the user clicks the "Edit Image" link in the "center" container
                Given the user inputs "Test caption, edited later" for the "caption" textarea
                Then the image "test_image.jpg" is visible in the "center" container
                Then the text "Test caption, edited later" is visible in the "center" container

        Scenario: Update the caption of an image asset created by specifying a URL
                Given the user clicks the "Image" icon in the "center" container
                Given the user inputs "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" for the "url" input
                Given the user inputs "Test caption!" in the "caption" textarea
                Given the user clicks the "Save Changes" button
                Given the user clicks the "Edit Image" link in the "center" container
                Given the user inputs "Test caption, edited later" for the "caption" textarea
                Then the image "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" is visible in the "center" container
                Then the text "Test caption, edited later" is visible in the "center" container

        Scenario: Update the URL and caption of an image asset
                Given the user clicks the "Image" icon in the "center" container
                Given the user inputs "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" for the "url" input
                Given the user inputs "Test caption!" for the "caption" textarea
                Given the user clicks the "Save Changes" button
                Given the user clicks the "Edit Image" link in the "center" container
                Given the user inputs "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image_2.png" for the "url" input
                Given the user inputs "Test caption, edited later" for the "caption" textarea
                Given the user clicks the "Save Changes" button
                Then the image "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image_2.png" is visible in the "center" container
                Then the text "Test caption, edited later" is visible in the "center" container

        Scenario: Replace the uploaded image file and update the caption of an image asset
                Given the user clicks the "Image" icon in the "center" container
                Given the user clicks the "Upload an image" link
                Given the user selects the file "test_image.jpg" for the "image" input
                Given the user inputs "Test caption!" in the "caption" textarea
		Given the user clicks the "Save Changes" button
                Given the user clicks the "Edit Image" link in the "center" container
                Given the user selects the file "test_image_2." for the "image" input
                Given the user inputs "Test caption, edited later" for the "caption" textarea
                Then the image "test_image_2.png" is visible in the "center" container
                Then the text "Test caption, edited later" is visible in the "center" container

        # Chart type asset
        
        # We don't test supporting a chart asset by specifying a URL
        # or image because this should be functionally the same as 

	Scenario: Create a chart asset by specifying a HTML snippet
                Given the user clicks the "Chart" icon in the "center" container
                Given the user clicks the "Paste embed code for the chart" link
                Given the user inputs the following text in the "body" textarea:
                        """
                        <iframe src="//e.infogr.am/-geoffhing_1351202894" width="550" height="741" scrolling="no" frameborder="0" style="border:none;"></iframe><div style="width:550px;border-top:1px solid #acacac;padding-top:3px;font-family:Arial;font-size:10px;text-align:center;"><a style="color:#acacac;text-decoration:none;" href="//infogr.am" target="_blank">Infographics</a></div>
                        """
		Given the user clicks the "Save Changes" button
                Then the URL "http://e.infogr.am/-geoffhing_1351202894" is visible in an iframe in the "center" container
                
	Scenario: Create a chart asset by specifying a HTML snippet, caption and attribution
                Given the user clicks the "Chart" icon in the "center" container
                Given the user clicks the "Paste embed code for the chart" link
                Given the user inputs the following text in the "body" textarea:
                        """
                        <iframe src="//e.infogr.am/-geoffhing_1351202894" width="550" height="741" scrolling="no" frameborder="0" style="border:none;"></iframe><div style="width:550px;border-top:1px solid #acacac;padding-top:3px;font-family:Arial;font-size:10px;text-align:center;"><a style="color:#acacac;text-decoration:none;" href="//infogr.am" target="_blank">Infographics</a></div>
                        """
                Given the user inputs "Test caption!" in the "caption" textarea
                Given the user inputs "Test Attribution" in the "attribution" textarea
		Given the user clicks the "Save Changes" button
                Then the URL "http://e.infogr.am/-geoffhing_1351202894" is visible in an iframe in the "center" container
                Then the text "Test caption!" is visible in the "center" container
                Then the text "Test Attribution" is visible in the "center" container

	Scenario: Submit chart asset form with no URL, image or HTML snippet specified 
                Given the user clicks the "Chart" icon in the "center" container
		Given the user clicks the "Save Changes" button
                Then an error message is shown above the form

	Scenario: Submit chart asset form with URL, image and HTML snippet specified, while in URL tab
                Given the user clicks the "Chart" icon in the "center" container
                Given the user inputs "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" for the "url" input
                Given the user clicks the "Upload an image" link
                Given the user selects the file "test_image_2.png" for the "image" input
                Given the user clicks the "Paste embed code for the chart" link
                Given the user inputs the following text in the "body" textarea:
                        """
                        <iframe src="//e.infogr.am/-geoffhing_1351202894" width="550" height="741" scrolling="no" frameborder="0" style="border:none;"></iframe><div style="width:550px;border-top:1px solid #acacac;padding-top:3px;font-family:Arial;font-size:10px;text-align:center;"><a style="color:#acacac;text-decoration:none;" href="//infogr.am" target="_blank">Infographics</a></div>
                        """
                Given the user clicks the "Enter chart URL" link
		Given the user clicks the "Save Changes" button
                Then the image "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" is visible in the "center" container

	Scenario: Submit chart asset form with URL, image and HTML snippet specified, while in image tab
                Given the user clicks the "Chart" icon in the "center" container
                Given the user inputs "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" for the "url" input
                Given the user clicks the "Upload an image" link
                Given the user selects the file "test_image_2.png" for the "image" input
                Given the user clicks the "Paste embed code for the chart" link
                Given the user inputs the following text in the "body" textarea:
                        """
                        <iframe src="//e.infogr.am/-geoffhing_1351202894" width="550" height="741" scrolling="no" frameborder="0" style="border:none;"></iframe><div style="width:550px;border-top:1px solid #acacac;padding-top:3px;font-family:Arial;font-size:10px;text-align:center;"><a style="color:#acacac;text-decoration:none;" href="//infogr.am" target="_blank">Infographics</a></div>
                        """
                Given the user clicks the "Upload an image" link
		Given the user clicks the "Save Changes" button
                Then the image "test_image_2.png" is visible in the "center" container

	Scenario: Submit chart asset form with URL, image and HTML snippet specified, while in embed code tab 
                Given the user clicks the "Chart" icon in the "center" container
                Given the user inputs "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" for the "url" input
                Given the user clicks the "Upload an image" link
                Given the user selects the file "test_image_2.png" for the "image" input
                Given the user clicks the "Paste embed code for the chart" link
                Given the user inputs the following text in the "body" textarea:
                        """
                        <iframe src="//e.infogr.am/-geoffhing_1351202894" width="550" height="741" scrolling="no" frameborder="0" style="border:none;"></iframe><div style="width:550px;border-top:1px solid #acacac;padding-top:3px;font-family:Arial;font-size:10px;text-align:center;"><a style="color:#acacac;text-decoration:none;" href="//infogr.am" target="_blank">Infographics</a></div>
                        """
		Given the user clicks the "Save Changes" button
                Then the URL "http://e.infogr.am/-geoffhing_1351202894" is visible in an iframe in the "center" container

	Scenario: Replace the HTML snippet of a chart asset 
                Given the user clicks the "Chart" icon in the "center" container
                Given the user clicks the "Paste embed code for the chart" link
                Given the user inputs the following text in the "body" textarea:
                        """
                        <iframe src="//e.infogr.am/-geoffhing_1351202894" width="550" height="741" scrolling="no" frameborder="0" style="border:none;"></iframe><div style="width:550px;border-top:1px solid #acacac;padding-top:3px;font-family:Arial;font-size:10px;text-align:center;"><a style="color:#acacac;text-decoration:none;" href="//infogr.am" target="_blank">Infographics</a></div>
                        """

                Given the user clicks the "Edit Chart" link in the "center" container
                Given the user inputs the following text in the "body" textarea:
                        """
                        <iframe src="//e.infogr.am/test-geoffhing_1351202558" width="550" height="668" scrolling="no" frameborder="0" style="border:none;"></iframe><div style="width:550px;border-top:1px solid #acacac;padding-top:3px;font-family:Arial;font-size:10px;text-align:center;"><a style="color:#acacac;text-decoration:none;" href="//infogr.am" target="_blank">Create infographics</a></div>
                        """
		Given the user clicks the "Save Changes" button
                # The embedded chart should change
                Then the URL "http://e.infogr.am/test-geoffhing_1351202558" is visible in an iframe in the "center" container


	Scenario: Update the HTML snippet, caption and attribution of a chart asset
                Given the user clicks the "Chart" icon in the "center" container
                Given the user clicks the "Paste embed code for the chart" link
                Given the user inputs the following text in the "body" textarea:
                        """
                        <iframe src="//e.infogr.am/-geoffhing_1351202894" width="550" height="741" scrolling="no" frameborder="0" style="border:none;"></iframe><div style="width:550px;border-top:1px solid #acacac;padding-top:3px;font-family:Arial;font-size:10px;text-align:center;"><a style="color:#acacac;text-decoration:none;" href="//infogr.am" target="_blank">Infographics</a></div>
                        """
                Given the user inputs "Test caption!" in the "caption" textarea
                Given the user inputs "Test Attribution" in the "attribution" textarea
		Given the user clicks the "Save Changes" button
                Given the user clicks the "Edit Chart" link in the "center" container
                Given the user inputs the following text in the "body" textarea:
                        """
                        <iframe src="//e.infogr.am/test-geoffhing_1351202558" width="550" height="668" scrolling="no" frameborder="0" style="border:none;"></iframe><div style="width:550px;border-top:1px solid #acacac;padding-top:3px;font-family:Arial;font-size:10px;text-align:center;"><a style="color:#acacac;text-decoration:none;" href="//infogr.am" target="_blank">Create infographics</a></div>
                        """
                Given the user inputs "Test caption, edited later" in the "caption" textarea
                Given the user inputs "New Attribution" in the "attribution" textarea
		Given the user clicks the "Save Changes" button
                # The embedded chart should change
                Then the URL "http://e.infogr.am/test-geoffhing_1351202558" is visible in an iframe in the "center" container
                Then the text "Test caption, edited later" is visible in the "center" container
                Then the text "New Attribution" is visible in the "center" container

	Scenario: Create a chart asset in a container previously occupied by an image asset
                Given the user clicks the "Image" icon in the "center" container
                Given the user inputs "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" for the "url" input
                Given the user clicks the "Save Changes" button
                Then the image "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" is visible in the "center" container
                Given the user clicks the "Remove" link
                Given the user clicks the "Chart" icon in the "center" container
                Given the user clicks the "Paste embed code for the chart" link
                Given the user inputs the following text in the "body" textarea:
                        """
                        <iframe src="//e.infogr.am/-geoffhing_1351202894" width="550" height="741" scrolling="no" frameborder="0" style="border:none;"></iframe><div style="width:550px;border-top:1px solid #acacac;padding-top:3px;font-family:Arial;font-size:10px;text-align:center;"><a style="color:#acacac;text-decoration:none;" href="//infogr.am" target="_blank">Infographics</a></div>
                        """
		Given the user clicks the "Save Changes" button
                Then the URL "http://e.infogr.am/-geoffhing_1351202894" is visible in an iframe in the "center" container
                
	Scenario: Create an image asset after switching workflow steps
                Given the user clicks the "Publish/Share" workflow tab
                Given the user clicks the "Build" workflow tab
                Given the user clicks the "Section 1" section icon in the section list
                Given the user clicks the "Image" icon in the "center" container
                Given the user clicks the "Upload an image" link
                Given the user selects the file "test_image.jpg" for the "image" input
                Given the user clicks the "Save Changes" button
                Then the image "test_image.jpg" is visible in the "center" container

        Scenario: Create an image asset alongside a chart asset
                Given the user changes the layout to "Side by Side"
                Given the user clicks the "Chart" icon in the "left" container
                Given the user clicks the "Paste embed code for the chart" link
                Given the user inputs the following text in the "body" textarea:
                        """
                        <iframe src="//e.infogr.am/-geoffhing_1351202894" width="550" height="741" scrolling="no" frameborder="0" style="border:none;"></iframe><div style="width:550px;border-top:1px solid #acacac;padding-top:3px;font-family:Arial;font-size:10px;text-align:center;"><a style="color:#acacac;text-decoration:none;" href="//infogr.am" target="_blank">Infographics</a></div>
                        """
		Given the user clicks the "Save Changes" button
                Then the URL "http://e.infogr.am/-geoffhing_1351202894" is visible in an iframe in the "left" container
                Given the user clicks the "Image" icon in the "right" container
                Given the user inputs "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" for the "url" input
                Given the user clicks the "Save Changes" button
                Then the image "https://raw.github.com/PitonFoundation/atlas/develop/apps/storybase_asset/test_files/test_image.jpg" is visible in the "right" container
