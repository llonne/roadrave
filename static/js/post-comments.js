// <!-- Init jquery-comments -->

var usersArray = [];
var commentsArray = [];

// var usersArray = [
//    {
//       id: 1,
//       fullname: "Current User",
//       email: "current.user@viima.com",
//       profile_picture_url: "https://app.viima.com/static/media/user_profiles/user-icon.png"
//    },
//    {
//       id: 2,
//       fullname: "Jack Hemsworth",
//       email: "jack.hemsworth@viima.com",
//       profile_picture_url: "https://app.viima.com/static/media/user_profiles/user-icon.png"
//    }
// ];
// var commentsArray = [
// {
//    "id": 1,
//    "parent": null,
//    "created": "2015-01-01",
//    "modified": "2015-01-01",
//    "content": "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Sed posuere interdum sem. Quisque ligula eros ullamcorper quis, lacinia quis facilisis sed sapien. Mauris varius diam vitae arcu.",
//    "pings": [],
//    "creator": 6,
//    "fullname": "Simon Powell",
//    "profile_picture_url": "https://app.viima.com/static/media/user_profiles/user-icon.png",
//    "created_by_admin": false,
//    "created_by_current_user": false,
//    "upvote_count": 3,
//    "user_has_upvoted": false
// },
// {
//    "id": 2,
//    "parent": null,
//    "created": "2015-01-02",
//    "modified": "2015-01-02",
//    "content": "Sed posuere interdum sem. Quisque ligula eros ullamcorper quis, lacinia quis facilisis sed sapien. Mauris varius diam vitae arcu.",
//    "pings": [],
//    "creator": 5,
//    "fullname": "Administrator",
//    "profile_picture_url": "https://app.viima.com/static/media/user_profiles/admin-user-icon.png",
//    "created_by_admin": true,
//    "created_by_current_user": false,
//    "upvote_count": 2,
//    "user_has_upvoted": false
// }
// ]
      $(function() {
        var saveComment = function(data) {

          // Convert pings to human readable format
          $(data.pings).each(function(index, id) {
            var user = usersArray.filter(function(user){return user.id == id})[0];
            data.content = data.content.replace('@' + id, '@' + user.fullname);
          });

          return data;
        }
        $('#comments-container').comments({
          profilePictureURL: 'https://viima-app.s3.amazonaws.com/media/user_profiles/user-icon.png',
          currentUserId: 1,
          enableUpvoting: false,
          enableReplying: true,
          roundProfilePictures: true,
          textareaRows: 1,
          enableAttachments: false,
          enableHashtags: false,
          enablePinging: false,
//     fieldMappings: {
//         id: 'comment_id',
//         parent: 'parent',
//         created: 'date_created',
//         modified: 'date_modified',
//         content: 'content',
//         // file: 'file',  disable option to upload attachments
//         fileURL: 'file_url',
//         // fileMimeType: 'file_mime_type',
//         pings: 'pings',
//         creator: 'user_id',
//         fullname: 'username',
//         profileURL: 'profile_url',
//         // profilePictureURL: 'profile_picture_url',
//         // createdByAdmin: 'created_by_admin',
//         createdByCurrentUser: 'created_by_current_user',
//         upvoteCount: 'upvote_count',
//         userHasUpvoted: 'user_has_upvoted'
//     }
          getUsers: function(success, error) {
            setTimeout(function() {
              success(usersArray);
            }, 500);
          },
          getComments: function(success, error) {
            setTimeout(function() {
              success(commentsArray);
            }, 500);
          },
          postComment: function(data, success, error) {
            setTimeout(function() {
              success(saveComment(data));
            }, 500);
          },
          // https://github.com/Viima/jquery-comments/issues/2
          // postComment: function (commentJSON, success, error) { $.ajax({ 
          //   type: 'post', url: '', 
          //   dataType: 'json', 
          //   contentType: "application/json; charset=utf-8", 
          //   data: JSON.stringify(commentJSON), 
          //   success: setTimeout(function () { 
          //   success(commentJSON); }, 500), error: error }); },
          putComment: function(data, success, error) {
            setTimeout(function() {
              success(saveComment(data));
            }, 500);
          },
          deleteComment: function(data, success, error) {
            setTimeout(function() {
              success();
            }, 500);
          },
          upvoteComment: function(data, success, error) {
            setTimeout(function() {
              success(data);
            }, 500);
          },
          uploadAttachments: function(dataArray, success, error) {
            setTimeout(function() {
              success(dataArray);
            }, 500);
          },
        });
      });
    // </script>