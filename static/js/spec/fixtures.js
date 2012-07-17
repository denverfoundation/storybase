beforeEach(function() {
  this.fixtures = {
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
    },

    Sections: {
      getList: {
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

    SectionAssets: {
      getList: {
          "meta": {
              "limit": 20, 
              "next": null, 
              "offset": 0, 
              "previous": null, 
              "total_count": 2
          }, 
          "objects": [
              {
                  "asset": {
                      "asset_created": null, 
                      "asset_id": "e01a81861f164a66ac30fe8e3e43c8c8", 
                      "attribution": "", 
                      "body": null, 
                      "caption": "", 
                      "content": "Test Asset", 
                      "created": "2012-07-16T18:56:12.074058", 
                      "id": 1, 
                      "image": null, 
                      "language": "en", 
                      "languages": [
                          {
                              "id": "en", 
                              "name": "English", 
                              "url": "/en/assets/e01a81861f164a66ac30fe8e3e43c8c8/"
                          }
                      ], 
                      "last_edited": "2012-07-16T18:56:12.074086", 
                      "license": "CC BY-NC-SA", 
                      "published": null, 
                      "resource_uri": "/api/0.1/assets/e01a81861f164a66ac30fe8e3e43c8c8/", 
                      "section_specific": false, 
                      "source_url": "", 
                      "status": "draft", 
                      "title": "Test Asset", 
                      "type": "text", 
                      "url": null
                  }, 
                  "container": "left", 
                  "resource_uri": "/api/0.1/stories/e4514b8ae56a4ac5985527018686e2bf/sections/ae4813c6f3b94e78a6d6d467324531cc/assets/e01a81861f164a66ac30fe8e3e43c8c8/"
              }, 
              {
                  "asset": {
                      "asset_created": null, 
                      "asset_id": "cc238d3b02204b3988818be166da33f2", 
                      "attribution": "", 
                      "body": null, 
                      "caption": "", 
                      "content": "Test Asset 2", 
                      "created": "2012-07-16T18:56:12.077148", 
                      "id": 2, 
                      "image": null, 
                      "language": "en", 
                      "languages": [
                          {
                              "id": "en", 
                              "name": "English", 
                              "url": "/en/assets/cc238d3b02204b3988818be166da33f2/"
                          }
                      ], 
                      "last_edited": "2012-07-16T18:56:12.077171", 
                      "license": "CC BY-NC-SA", 
                      "published": null, 
                      "resource_uri": "/api/0.1/assets/cc238d3b02204b3988818be166da33f2/", 
                      "section_specific": false, 
                      "source_url": "", 
                      "status": "draft", 
                      "title": "Test Asset 2", 
                      "type": "text", 
                      "url": null
                  }, 
                  "container": "right", 
                  "resource_uri": "/api/0.1/stories/e4514b8ae56a4ac5985527018686e2bf/sections/ae4813c6f3b94e78a6d6d467324531cc/assets/cc238d3b02204b3988818be166da33f2/"
              }
          ]
      }
    }
  };
});
