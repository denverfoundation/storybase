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
        },
        // Explainer template sections
        "0b2b9e3f38e3422ea3899ee66d1e334b": {
          "meta": {
            "limit": 20,
            "next": null,
            "offset": 0,
            "previous": null,
            "total_count": 7
          },
          "objects": [
            {
              "help": {
                "body": "<p>Your introduction gives a general overview of the topic and summarizes what your can expect from this story, including what he or she will learn and what sections will follow.<\/p>\r\n<p>It could include:<\/p>\r\n<ul>\r\n<li>a picture or visual asset<\/li>\r\n<li>a paragraph describing the system and the sections in this story (like an abstract or outline)<\/li>\r\n<\/ul>",
                "help_id": "aa734ce35077482c946b5821470b6da1",
                "title": "Introduction"
              },
              "languages": [
                {
                  "id": "en",
                  "name": "English"
                }
              ],
              "layout": "26c81c9dd24c4aecab7ab4eb1cc9e2fb",
              "layout_template": "\n<div class=\"section-layout side-by-side\">\n    <div class=\"left\">\n        <div class=\"storybase-container-placeholder\" id=\"left\"><\/div>\n    <\/div>\n    <div class=\"right\">\n        <div class=\"storybase-container-placeholder\" id=\"right\"><\/div>\n    <\/div>\n<\/div>\n",
              "resource_uri": "\/api\/0.1\/stories\/0b2b9e3f38e3422ea3899ee66d1e334b\/sections\/9cd532d3f93c4ba59fb93694dbaf7b04\/",
              "root": true,
              "section_id": "9cd532d3f93c4ba59fb93694dbaf7b04",
              "story": "\/api\/0.1\/stories\/0b2b9e3f38e3422ea3899ee66d1e334b\/",
              "title": "Introduction",
              "weight": 1
            },
            {
              "help": {
                "body": "<p>Don&rsquo;t forget to define what it is you are trying to explain. Before you answer &ldquo;how does it work?&rdquo; you need to answer &ldquo;what is it?&rdquo; This is a simple step, but one that many people overlook.<\/p>\r\n<p>It could include:<\/p>\r\n<ul>\r\n<li>a two to three sentence definition of your system<\/li>\r\n<li>a diagram (sketch, chart, etc.)<\/li>\r\n<\/ul>",
                "help_id": "c3c74143479d4f968b88664d86e074ff",
                "title": "Definition"
              },
              "languages": [
                {
                  "id": "en",
                  "name": "English"
                }
              ],
              "layout": "ccaea5bac5c7467eb014baf6f7476ccb",
              "layout_template": "\n<div class=\"section-layout one-up\">\n    <div class=\"center\">\n        <div class=\"storybase-container-placeholder\" id=\"center\"><\/div>\n    <\/div>\n<\/div>\n",
              "resource_uri": "\/api\/0.1\/stories\/0b2b9e3f38e3422ea3899ee66d1e334b\/sections\/28f1ed62877c42cb9cc6ad317b410ae8\/",
              "root": true,
              "section_id": "28f1ed62877c42cb9cc6ad317b410ae8",
              "story": "\/api\/0.1\/stories\/0b2b9e3f38e3422ea3899ee66d1e334b\/",
              "title": "Definition",
              "weight": 2
            },
            {
              "help": {
                "body": "<p>Break down your system into simpler parts or sub-components and describe how each part works in its own section. These could be a series of frequently asked questions, a list of programs, or a step-by-step guide to completing a task.<\/p>\r\n<p>Shoot for two to six sections. Try to use a variety of content. You could use:<\/p>\r\n<ul>\r\n<li>visual assets (a photo or diagram)<\/li>\r\n<li>data assets (a graph, chart or table)<\/li>\r\n<li>geo assets (a map)<\/li>\r\n<li>audio or video assets (video or audio recording)<\/li>\r\n<\/ul>\r\n<p>Some tips:<\/p>\r\n<ul>\r\n<li>Sections work best if you only have one or two points of visual focus. <\/li>\r\n<li>Combine text and visual elements. If you use a picture, include a caption. If you use a graph, describe the most interesting piece of information the graph reveals. <\/li>\r\n<li>Don&rsquo;t try to squeeze too much into any one section &ndash; if it barely fits, break it up into two.<\/li>\r\n<\/ul>",
                "help_id": "13272f58fd164e59bf7bc7c3c8b8397d",
                "title": "Elements"
              },
              "languages": [
                {
                  "id": "en",
                  "name": "English"
                }
              ],
              "layout": "ccaea5bac5c7467eb014baf6f7476ccb",
              "layout_template": "\n<div class=\"section-layout one-up\">\n    <div class=\"center\">\n        <div class=\"storybase-container-placeholder\" id=\"center\"><\/div>\n    <\/div>\n<\/div>\n",
              "resource_uri": "\/api\/0.1\/stories\/0b2b9e3f38e3422ea3899ee66d1e334b\/sections\/72a8215649054734a0d316063e69eb5a\/",
              "root": true,
              "section_id": "72a8215649054734a0d316063e69eb5a",
              "story": "\/api\/0.1\/stories\/0b2b9e3f38e3422ea3899ee66d1e334b\/",
              "title": "Element 1",
              "weight": 3
            },
            {
              "help": {
                "body": "<p>Break down your system into simpler parts or sub-components and describe how each part works in its own section. These could be a series of frequently asked questions, a list of programs, or a step-by-step guide to completing a task.<\/p>\r\n<p>Shoot for two to six sections. Try to use a variety of content. You could use:<\/p>\r\n<ul>\r\n<li>visual assets (a photo or diagram)<\/li>\r\n<li>data assets (a graph, chart or table)<\/li>\r\n<li>geo assets (a map)<\/li>\r\n<li>audio or video assets (video or audio recording)<\/li>\r\n<\/ul>\r\n<p>Some tips:<\/p>\r\n<ul>\r\n<li>Sections work best if you only have one or two points of visual focus. <\/li>\r\n<li>Combine text and visual elements. If you use a picture, include a caption. If you use a graph, describe the most interesting piece of information the graph reveals. <\/li>\r\n<li>Don&rsquo;t try to squeeze too much into any one section &ndash; if it barely fits, break it up into two.<\/li>\r\n<\/ul>",
                "help_id": "13272f58fd164e59bf7bc7c3c8b8397d",
                "title": "Elements"
              },
              "languages": [
                {
                  "id": "en",
                  "name": "English"
                }
              ],
              "layout": "ccaea5bac5c7467eb014baf6f7476ccb",
              "layout_template": "\n<div class=\"section-layout one-up\">\n    <div class=\"center\">\n        <div class=\"storybase-container-placeholder\" id=\"center\"><\/div>\n    <\/div>\n<\/div>\n",
              "resource_uri": "\/api\/0.1\/stories\/0b2b9e3f38e3422ea3899ee66d1e334b\/sections\/97ffc13f50bc4a6b9f52b5895355b75e\/",
              "root": true,
              "section_id": "97ffc13f50bc4a6b9f52b5895355b75e",
              "story": "\/api\/0.1\/stories\/0b2b9e3f38e3422ea3899ee66d1e334b\/",
              "title": "Element 2",
              "weight": 4
            },
            {
              "help": {
                "body": "<p>Break down your system into simpler parts or sub-components and describe how each part works in its own section. These could be a series of frequently asked questions, a list of programs, or a step-by-step guide to completing a task.<\/p>\r\n<p>Shoot for two to six sections. Try to use a variety of content. You could use:<\/p>\r\n<ul>\r\n<li>visual assets (a photo or diagram)<\/li>\r\n<li>data assets (a graph, chart or table)<\/li>\r\n<li>geo assets (a map)<\/li>\r\n<li>audio or video assets (video or audio recording)<\/li>\r\n<\/ul>\r\n<p>Some tips:<\/p>\r\n<ul>\r\n<li>Sections work best if you only have one or two points of visual focus. <\/li>\r\n<li>Combine text and visual elements. If you use a picture, include a caption. If you use a graph, describe the most interesting piece of information the graph reveals. <\/li>\r\n<li>Don&rsquo;t try to squeeze too much into any one section &ndash; if it barely fits, break it up into two.<\/li>\r\n<\/ul>",
                "help_id": "13272f58fd164e59bf7bc7c3c8b8397d",
                "title": "Elements"
              },
              "languages": [
                {
                  "id": "en",
                  "name": "English"
                }
              ],
              "layout": "ccaea5bac5c7467eb014baf6f7476ccb",
              "layout_template": "\n<div class=\"section-layout one-up\">\n    <div class=\"center\">\n        <div class=\"storybase-container-placeholder\" id=\"center\"><\/div>\n    <\/div>\n<\/div>\n",
              "resource_uri": "\/api\/0.1\/stories\/0b2b9e3f38e3422ea3899ee66d1e334b\/sections\/9a8125bf78b04ef6b7de22eb0576011b\/",
              "root": true,
              "section_id": "9a8125bf78b04ef6b7de22eb0576011b",
              "story": "\/api\/0.1\/stories\/0b2b9e3f38e3422ea3899ee66d1e334b\/",
              "title": "Element 3",
              "weight": 5
            },
            {
              "help": {
                "body": "<p>Break down your system into simpler parts or sub-components and describe how each part works in its own section. These could be a series of frequently asked questions, a list of programs, or a step-by-step guide to completing a task.<\/p>\r\n<p>Shoot for two to six sections. Try to use a variety of content. You could use:<\/p>\r\n<ul>\r\n<li>visual assets (a photo or diagram)<\/li>\r\n<li>data assets (a graph, chart or table)<\/li>\r\n<li>geo assets (a map)<\/li>\r\n<li>audio or video assets (video or audio recording)<\/li>\r\n<\/ul>\r\n<p>Some tips:<\/p>\r\n<ul>\r\n<li>Sections work best if you only have one or two points of visual focus. <\/li>\r\n<li>Combine text and visual elements. If you use a picture, include a caption. If you use a graph, describe the most interesting piece of information the graph reveals. <\/li>\r\n<li>Don&rsquo;t try to squeeze too much into any one section &ndash; if it barely fits, break it up into two.<\/li>\r\n<\/ul>",
                "help_id": "13272f58fd164e59bf7bc7c3c8b8397d",
                "title": "Elements"
              },
              "languages": [
                {
                  "id": "en",
                  "name": "English"
                }
              ],
              "layout": "ccaea5bac5c7467eb014baf6f7476ccb",
              "layout_template": "\n<div class=\"section-layout one-up\">\n    <div class=\"center\">\n        <div class=\"storybase-container-placeholder\" id=\"center\"><\/div>\n    <\/div>\n<\/div>\n",
              "resource_uri": "\/api\/0.1\/stories\/0b2b9e3f38e3422ea3899ee66d1e334b\/sections\/78313edffa8343b3b1cfa96d6de94557\/",
              "root": true,
              "section_id": "78313edffa8343b3b1cfa96d6de94557",
              "story": "\/api\/0.1\/stories\/0b2b9e3f38e3422ea3899ee66d1e334b\/",
              "title": "Element 4",
              "weight": 6
            },
            {
              "help": {
                "body": "<p>This is where you put the pieces back together. This section summarizes the information you&rsquo;ve presented so far and explains how it relates to your reader. Give your reader some takeaway points\/conclusions.<\/p>\r\n<p>It could include:<\/p>\r\n<ul>\r\n<li>&nbsp;three main takeaway points (one sentence each)<\/li>\r\n<\/ul>",
                "help_id": "5ca21eeea12b4a66b31b709d81e7a93e",
                "title": "Synthesis"
              },
              "languages": [
                {
                  "id": "en",
                  "name": "English"
                }
              ],
              "layout": "ccaea5bac5c7467eb014baf6f7476ccb",
              "layout_template": "\n<div class=\"section-layout one-up\">\n    <div class=\"center\">\n        <div class=\"storybase-container-placeholder\" id=\"center\"><\/div>\n    <\/div>\n<\/div>\n",
              "resource_uri": "\/api\/0.1\/stories\/0b2b9e3f38e3422ea3899ee66d1e334b\/sections\/72b60c39caee4d9293b29fa574deb361\/",
              "root": true,
              "section_id": "72b60c39caee4d9293b29fa574deb361",
              "story": "\/api\/0.1\/stories\/0b2b9e3f38e3422ea3899ee66d1e334b\/",
              "title": "Synthesis",
              "weight": 7
            }
          ]
        },
        // A simple story with 2 sections and 4 assets
        "6c8bfeaa6bb145e791b410e3ca5e9053": {
          "meta": {
            "limit": 20,
            "next": null,
            "offset": 0,
            "previous": null,
            "total_count": 2
          },
          "objects": [
            {
              "help": {
                "body": "Sample help text for the Image and Text section.",
                "help_id": "e296af8d957e423091759a3cd067c68c",
                "title": "Image and Text"
              },
              "languages": [
                {
                  "id": "en",
                  "name": "English"
                }
              ],
              "layout": "26c81c9dd24c4aecab7ab4eb1cc9e2fb",
              "layout_template": "\n<div class=\"section-layout side-by-side\">\n    <div class=\"left\">\n        <div class=\"storybase-container-placeholder\" id=\"left\"><\/div>\n    <\/div>\n    <div class=\"right\">\n        <div class=\"storybase-container-placeholder\" id=\"right\"><\/div>\n    <\/div>\n<\/div>\n",
              "resource_uri": "\/api\/0.1\/stories\/6c8bfeaa6bb145e791b410e3ca5e9053\/sections\/bba19cd38f0d4d789143e74f2a5a3acd\/",
              "root": true,
              "section_id": "bba19cd38f0d4d789143e74f2a5a3acd",
              "story": "\/api\/0.1\/stories\/6c8bfeaa6bb145e791b410e3ca5e9053\/",
              "title": "Section 1",
              "weight": 0
            },
            {
              "help": null,
              "languages": [
                {
                  "id": "en",
                  "name": "English"
                }
              ],
              "layout": "26c81c9dd24c4aecab7ab4eb1cc9e2fb",
              "layout_template": "\n<div class=\"section-layout side-by-side\">\n    <div class=\"left\">\n        <div class=\"storybase-container-placeholder\" id=\"left\"><\/div>\n    <\/div>\n    <div class=\"right\">\n        <div class=\"storybase-container-placeholder\" id=\"right\"><\/div>\n    <\/div>\n<\/div>\n",
              "resource_uri": "\/api\/0.1\/stories\/6c8bfeaa6bb145e791b410e3ca5e9053\/sections\/f7294fa28fbc4e9d85a87b4b79d32137\/",
              "root": true,
              "section_id": "f7294fa28fbc4e9d85a87b4b79d32137",
              "story": "\/api\/0.1\/stories\/6c8bfeaa6bb145e791b410e3ca5e9053\/",
              "title": "Section 2",
              "weight": 1
            }
          ]
        }
      }
    },

    SectionAssets: {
      getList: {
        "dc044f23e93649d6b1bd48625fc301cd": {
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
        },
        // A simple story with 2 sections and 4 assets
        "bba19cd38f0d4d789143e74f2a5a3acd": {
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
                "asset_id": "624e3120e4a54b5589ee3cb4b3b77600",
                "attribution": "",
                "body": "Asset 1<br>",
                "caption": "",
                "content": "Asset 1<br>",
                "created": "2012-08-22T15:45:39.790800",
                "display_title": "Asset 1",
                "image": null,
                "language": "en",
                "languages": [
                  {
                    "id": "en",
                    "name": "English",
                    "url": "\/en\/assets\/624e3120e4a54b5589ee3cb4b3b77600\/"
                  }
                ],
                "last_edited": "2012-08-22T15:45:39.936538",
                "license": "CC BY-NC-SA",
                "published": null,
                "resource_uri": "\/api\/0.1\/assets\/624e3120e4a54b5589ee3cb4b3b77600\/",
                "section_specific": false,
                "source_url": "",
                "status": "draft",
                "thumbnail_url": null,
                "title": "",
                "type": "text",
                "url": null
              },
              "container": "left",
              "resource_uri": "\/api\/0.1\/stories\/6c8bfeaa6bb145e791b410e3ca5e9053\/sections\/bba19cd38f0d4d789143e74f2a5a3acd\/assets\/624e3120e4a54b5589ee3cb4b3b77600\/",
              "weight": 0
            },
            {
              "asset": {
                "asset_created": null,
                "asset_id": "3e2c04fe47cd45d6bdd13bfb64fdcd47",
                "attribution": "",
                "body": "Asset 2<br>",
                "caption": "",
                "content": "Asset 2<br>",
                "created": "2012-08-22T15:45:45.462269",
                "display_title": "Asset 2",
                "image": null,
                "language": "en",
                "languages": [
                  {
                    "id": "en",
                    "name": "English",
                    "url": "\/en\/assets\/3e2c04fe47cd45d6bdd13bfb64fdcd47\/"
                  }
                ],
                "last_edited": "2012-08-22T15:45:45.625038",
                "license": "CC BY-NC-SA",
                "published": null,
                "resource_uri": "\/api\/0.1\/assets\/3e2c04fe47cd45d6bdd13bfb64fdcd47\/",
                "section_specific": false,
                "source_url": "",
                "status": "draft",
                "thumbnail_url": null,
                "title": "",
                "type": "text",
                "url": null
              },
              "container": "right",
              "resource_uri": "\/api\/0.1\/stories\/6c8bfeaa6bb145e791b410e3ca5e9053\/sections\/bba19cd38f0d4d789143e74f2a5a3acd\/assets\/3e2c04fe47cd45d6bdd13bfb64fdcd47\/",
              "weight": 0
            }
          ]
        },
        "f7294fa28fbc4e9d85a87b4b79d32137": {
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
                "asset_id": "2cfc227004d647dfa5dbeca417d68750",
                "attribution": "",
                "body": "Asset 3<br>",
                "caption": "",
                "content": "Asset 3<br>",
                "created": "2012-08-22T15:45:51.882536",
                "display_title": "Asset 3",
                "image": null,
                "language": "en",
                "languages": [
                  {
                    "id": "en",
                    "name": "English",
                    "url": "\/en\/assets\/2cfc227004d647dfa5dbeca417d68750\/"
                  }
                ],
                "last_edited": "2012-08-22T15:45:52.033701",
                "license": "CC BY-NC-SA",
                "published": null,
                "resource_uri": "\/api\/0.1\/assets\/2cfc227004d647dfa5dbeca417d68750\/",
                "section_specific": false,
                "source_url": "",
                "status": "draft",
                "thumbnail_url": null,
                "title": "",
                "type": "text",
                "url": null
              },
              "container": "left",
              "resource_uri": "\/api\/0.1\/stories\/6c8bfeaa6bb145e791b410e3ca5e9053\/sections\/f7294fa28fbc4e9d85a87b4b79d32137\/assets\/2cfc227004d647dfa5dbeca417d68750\/",
              "weight": 0
            },
            {
              "asset": {
                "asset_created": null,
                "asset_id": "e6f1d21977924b7b83320510609b853b",
                "attribution": "",
                "body": "Asset 4<br>",
                "caption": "",
                "content": "Asset 4<br>",
                "created": "2012-08-22T15:45:57.631099",
                "display_title": "Asset 4",
                "image": null,
                "language": "en",
                "languages": [
                  {
                    "id": "en",
                    "name": "English",
                    "url": "\/en\/assets\/e6f1d21977924b7b83320510609b853b\/"
                  }
                ],
                "last_edited": "2012-08-22T15:45:57.816346",
                "license": "CC BY-NC-SA",
                "published": null,
                "resource_uri": "\/api\/0.1\/assets\/e6f1d21977924b7b83320510609b853b\/",
                "section_specific": false,
                "source_url": "",
                "status": "draft",
                "thumbnail_url": null,
                "title": "",
                "type": "text",
                "url": null
              },
              "container": "right",
              "resource_uri": "\/api\/0.1\/stories\/6c8bfeaa6bb145e791b410e3ca5e9053\/sections\/f7294fa28fbc4e9d85a87b4b79d32137\/assets\/e6f1d21977924b7b83320510609b853b\/",
              "weight": 0
            }
          ]
        }
      }
    },

    Stories : {
      getDetail: {
        // Explorer template
        "0b2b9e3f38e3422ea3899ee66d1e334b": {
          "byline": "Your name here",
          "call_to_action": "",
          "contact_info": "",
          "created": "2012-07-23T11:40:56",
          "is_template": true,
          "languages": [{"id": "en", "name": "English", "url": "/en/stories/explainer-story/"}],
          "last_edited": "2012-08-20T10:11:46.927765-05:00",
          "license": "CC BY-NC-SA",
          "on_homepage": false,
          "organizations": [],
          "places": [],
          "points": [],
          "projects": [],
          "published": "2012-08-20T10:11:46.653452",
          "resource_uri": "/api/0.1/stories/0b2b9e3f38e3422ea3899ee66d1e334b/",
          "slug": "explainer-story",
          "status": "published",
          "story_id": "0b2b9e3f38e3422ea3899ee66d1e334b",
          "structure_type": "linear",
          "summary": "",
          "title": "Explainer Story",
          "topics": [],
          "url": "/stories/explainer-story/"
        },
        // A simple story with 2 sections and 4 assets
        "6c8bfeaa6bb145e791b410e3ca5e9053": {
          "byline": "",
          "call_to_action": "",
          "contact_info": "",
          "created": "2012-08-22T15:45:03.091171",
          "is_template": false,
          "languages": [
            {
              "id": "en",
              "name": "English",
              "url": "\/en\/stories\/test-story-2-sections\/"
            }
          ],
          "last_edited": "2012-08-22T15:45:57.856019-05:00",
          "license": "CC BY-NC-SA",
          "on_homepage": false,
          "organizations": [

          ],
          "places": [

          ],
          "points": [

          ],
          "projects": [

          ],
          "published": null,
          "resource_uri": "\/api\/0.1\/stories\/6c8bfeaa6bb145e791b410e3ca5e9053\/",
          "slug": "test-story-2-sections",
          "status": "draft",
          "story_id": "6c8bfeaa6bb145e791b410e3ca5e9053",
          "structure_type": "linear",
          "summary": "",
          "title": "Test Story - 2 Sections",
          "topics": [

          ],
          "url": "\/stories\/test-story-2-sections\/"
        }
      }
    }
  };
});
