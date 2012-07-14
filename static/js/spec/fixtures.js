beforeEach(function() {
  this.fixtures = {
    Sections: {
      getDetail: {
        "357c5885c4e844cb8a4cd4eebe912a1c": {
          "meta": {
              "limit": 20, 
              "next": null, 
              "offset": 0, 
              "previous": null, 
              "total_count": 2
          }, 
          "objects": [
              {
                  "languages": [
                      {
                          "id": "en", 
                          "name": "English"
                      }
                  ], 
                  "resource_uri": "/api/0.1/stories/357c5885c4e844cb8a4cd4eebe912a1c/sections/dc044f23e93649d6b1bd48625fc301cd/", 
                  "root": false, 
                  "section_id": "dc044f23e93649d6b1bd48625fc301cd", 
                  "story": "/api/0.1/stories/357c5885c4e844cb8a4cd4eebe912a1c/", 
                  "title": "Title", 
                  "weight": 0
              }, 
              {
                  "languages": [
                      {
                          "id": "en", 
                          "name": "English"
                      }
                  ], 
                  "resource_uri": "/api/0.1/stories/357c5885c4e844cb8a4cd4eebe912a1c/sections/4dc57c4bc7a44d97bd5d0ed4861b1401/", 
                  "root": false, 
                  "section_id": "4dc57c4bc7a44d97bd5d0ed4861b1401", 
                  "story": "/api/0.1/stories/357c5885c4e844cb8a4cd4eebe912a1c/", 
                  "title": "Image and Text", 
                  "weight": 1
              }
          ]
        }
      }
    },

    Assets: {
      postList: {
        text: {
          "asset_created": null,
          "asset_id": "acfda3df93f84250a90aa6a2b34fd9cf", 
          "attribution": "", 
          "body": "", 
          "caption": "", 
          "content": "",
          "created": "2012-07-14T12:35:58.648461",
          "image": null, 
          "language": "en",
          "languages": [{"id": "en", "name": "English", "url": "/en/assets/acfda3df93f84250a90aa6a2b34fd9cf/"}], 
          "last_edited": "2012-07-14T12:35:58.648488", 
          "license": "CC BY-NC-SA", 
          "published": "2012-07-14T12:35:58.648397", 
          "resource_uri": "/api/0.1/assets/acfda3df93f84250a90aa6a2b34fd9cf/", 
          "section_specific": false, 
          "source_url": "", 
          "status": "published", 
          "title": "", 
          "type": "text", 
          "url": null
        }
      }
    }
  };
});
