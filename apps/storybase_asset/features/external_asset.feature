Feature: User can create an Asset for oEmbedable media 

    Scenario: User creates an Asset for a YouTube video
        Given the admin user is logged in
        Given the user navigates to the "External assets" addition page
        Given the user sets the "Attribution" of the "External asset" to "Geoffrey Hing"
        Given the user sets the License of the "External asset" to "Attribution-NonCommercial-ShareAlike Creative Commons"
        Given the user sets the "Asset Created" date to "2007-04-11" and time to "00:00"
        Given the user sets the "English" "title" of the "External asset" to "Large Flock of birds in pomona, CA"
        Given the user sets the "English" "caption" of the "External asset" to "An intense flock of birds outside a theater in Pomona, CA"
        Given the user sets the "English" "url" of the "External asset" to "http://www.youtube.com/watch?v=BJQycHkddhA"
        Given the user clicks the save button
        Then the External asset "Large Flock of birds in pomona, CA" should have a canonical URL 
        Given the user navigates to the Asset's detail page
        Then the Asset's title should be "Large Flock of birds in pomona, CA"
        Then the Asset's caption should be "An intense flock of birds outside a theater in Pomona, CA"
        Then the Asset's attribution should be "Geoffrey Hing"
        Then the Asset's creation date should be "April 11, 2007"
        Then the YouTube video should be embedded

    Scenario: User creates an Asset for SoundCloud audio
        Given the admin user is logged in
        Given the user navigates to the "External assets" addition page
        Given the user sets the "Attribution" of the "External asset" to "Geoffrey Hing"
        Given the user sets the License of the "External asset" to "Attribution-NonCommercial-ShareAlike Creative Commons"
        Given the user sets the "Asset Created" date to "2011-11-08" and time to "00:00"
        Given the user sets the "English" "title" of the "External asset" to "The Calling"
        Given the user sets the "English" "caption" of the "External asset" to "Finished version of \"The Calling\" for the DIY CHI comp"
        Given the user sets the "English" "url" of the "External asset" to "http://soundcloud.com/ghing/the-calling-for-diychi-comp"
        Given the user clicks the save button
        Then the External asset "The Calling" should have a canonical URL 
        Given the user navigates to the Asset's detail page
        Then the Asset's title should be "The Calling"
        Then the Asset's caption should be "Finished version of \"The Calling\" for the DIY CHI comp"
        Then the Asset's attribution should be "Geoffrey Hing"
        Then the Asset's creation date should be "November 8, 2011"
        Then the SoundCloud audio should be embedded
