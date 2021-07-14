// This code was tested on a TikTok video with over 3000 comment. It got a little bit laggy during the loading phase, but it
// worked out very good at the end. But even on a high-end machine, I wouldn't recommend running this on any TikTok with more than 10k comments
with({
    copy
}) {
    /* 
        This is the critical section. Every selector that contains 'jsx' (so almost everyone) is subject to change in the future,
        since TikTok decides to changes those random numbers after 'jsx-'. If they start to break again,
        instead of trying to update them with the new number, just remove the 'jsx-.+' class entirely, because the selector
        specified in the trailing comment should suffice (not tested at all).
    */

    var repliedToSelector                   = 'a.user-info.jsx-1935869581.comment-pc';
    var AllCommentsSelector                 = 'div.jsx-966068288.comment-item.comment-pc';               // = '.comment-item'
    var commentChildDivSelector             = 'div.jsx-365602788.comment-content.level-1.comment-pc';    // = '.level-1'
    var commentChildDivExtraSelector        = 'div.jsx-966068288.more-contents.more-style-2';            // = '.more-style-2'
    var level2CommentsSelector              = 'div.jsx-365602788.comment-content.level-2.comment-pc';    // = '.level-2'

    var publisherProfileUrlSelector         = 'a.user-info-link.jsx-1040045378';                         // = '.user-info-link'
    var nicknameAndTimePublishedAgoSelector = 'h2.jsx-2829469314.jsx-932449746.user-nickname';           // = '.user-nickname'
    var level2CommentsSelector              = 'div.jsx-365602788.comment-content.level-2.comment-pc';    // = '.level-2.comment-pc'

    var postUrlSelector                     = 'div.jsx-2335988431.link-container';                       // = '.link-container'
    var likeCountSelector                   = 'strong.jsx-956042027.like-text';                          // = '.like-text'
    var descriptionSelector                 = 'h1.jsx-2936247622.video-meta-title';                      // = '.video-meta-title'
    var tiktokNumberOfCommentsSelector      = 'strong.jsx-956042027.comment-text';                       // = '.strong.comment-text'

    var usernameSelector                    = 'span.jsx-365602788.username';                             // = '.username'
    var timeCommentedAgoSelector            = 'span.jsx-365602788.comment-time';                         // = '.comment-time'
    var commentLikesCountSelector           = 'span.jsx-365602788.count';                                // = '.count'
    var commentParagraphSelector            = 'p.jsx-365602788.comment-text';                            // = '.comment-text'
    var commentTextSelector                 = ':not(.bottom-container):not(.reply):not(.comment-time)';
    var userProfileUrlSelector              = 'a.user-info.jsx-1935869581.comment-pc';

    // readMoreDivSelector selects all the outermost divs of a read more paragraph.
    // From there, the following 2 selectors combined select the paragraph.
    var readMoreDivSelector                 = 'div.jsx-966068288.more-contents.more-style-2';
    var readMoreDivSelector2                = 'div.jsx-4265445291.view-more';
    var readMoreParagraphSelector           = 'p.jsx-4265445291:not(.hidden):not(.hide)';


    // Function definitions
    function getAllComments(){
        return document.querySelectorAll(AllCommentsSelector);
    }

    function quoteString(s) {
        return '"' + String(s).replaceAll('"', '""') + '"';
    }

    function formatDate(strDate) {
        if (typeof(strDate) != 'undefined' && strDate != null) {
            f = strDate.split('-');
            if (f.length == 1) {
                return strDate;
            } else if (f.length == 2) {
                return f[1] + '-' + f[0] + '-' + (new Date().getFullYear());
            } else if (f.length == 3) {
                return f[2] + '-' + f[1] + '-' + f[0];
            } else {
                return 'Malformed Date';
            }
        } else {
            return 'No date';
        }
    }

    function csvFromComment(comment) {
        nickname = comment.querySelector(usernameSelector).outerText;
        userProfileUrl = comment.querySelector(userProfileUrlSelector)['href'].split('?')[0];
        user = userProfileUrl.split('/')[3].substring(1);
        commentText = "";
        comment.querySelector(commentParagraphSelector).querySelectorAll(commentTextSelector).forEach(element => commentText += element.outerText);
        timeCommentedAgo = formatDate(comment.querySelector(timeCommentedAgoSelector).outerText);
        commentLikesCount = comment.querySelector(commentLikesCountSelector).outerText;
        pic = comment.querySelector('img')['src'];
        return quoteString(nickname) + ',' + quoteString(user) + ',' + quoteString(userProfileUrl) + ',' + quoteString(commentText) + ',' + timeCommentedAgo + ',' + commentLikesCount + ',' + quoteString(pic);
    }


    // Loading 1st level comments
    var loadingCommentsBuffer = 30;
    var numOfcommentsBeforeScroll = getAllComments().length;
    while (loadingCommentsBuffer > 0) {

        allComments = getAllComments();
        lastComment = allComments[allComments.length - 1];
        // Scroll last element into view = scrolling to bottom of comment page
        lastComment.scrollIntoView(false);

        numOfcommentsAftScroll = getAllComments().length;

        // If number of comments doesn't change after 5 iterations, break the loop.
        if (numOfcommentsAftScroll !== numOfcommentsBeforeScroll) {
            loadingCommentsBuffer = 30;
        } else {
            loadingCommentsBuffer--;
        };
        numOfcommentsBeforeScroll = numOfcommentsAftScroll;
        console.log('Loading 1st level comment number ' + numOfcommentsAftScroll);

        // Wait 0.3 seconds.
        await new Promise(r => setTimeout(r, 300));
    }
    console.log('Openend all 1st level comments');

    // Loading 2nd level comments
    var openingCommentsBuffer = 5;
    while (openingCommentsBuffer > 0) {
        readMoreDivs = document.querySelectorAll(readMoreDivSelector);
        for (var i = 0; i < readMoreDivs.length; i++) {
            readMoreDiv2 = readMoreDivs[i].querySelector(readMoreDivSelector2);
            if (typeof(readMoreDiv2) != 'undefined' && readMoreDiv2 != null) {
                readMoreParagraph = readMoreDiv2.querySelector(readMoreParagraphSelector);
                if (typeof(readMoreParagraph) != 'undefined' && readMoreParagraph != null) {
                    readMoreParagraph.scrollIntoView(false);
                    readMoreParagraph.click();
                    console.log('Opening 2nd level comment ' + i);
                    openingCommentsBuffer = 5;
                }
            }
        }
        openingCommentsBuffer--;
        console.log('Buffer: ' + openingCommentsBuffer);

        console.log("Ignore occasional blank lines:")
        await new Promise(r => setTimeout(r, 1000));
    }
    console.log('Openened all 2nd level comments');


    // Reading all comments, extracting and converting the data to csv
    var comments = getAllComments();

    var publisherProfileUrl = document.querySelector(publisherProfileUrlSelector)['href'].split('?')[0];
    var nicknameAndPublishedAgoTime = document.querySelector(nicknameAndTimePublishedAgoSelector).outerText.split(' · ');
    var level2commentsLength = document.querySelectorAll(level2CommentsSelector).length;

    var commentNumberDifference = Math.abs(document.querySelector(tiktokNumberOfCommentsSelector).outerText - (comments.length + level2commentsLength))

    var csv = 'Now,' + Date() + '\n';
    csv += 'Post URL,' + document.querySelector(postUrlSelector).outerText.split('?')[0] + '\n';
    csv += 'Publisher Nickname,' + nicknameAndPublishedAgoTime[0] + '\n';
    csv += 'Publisher URL,' + publisherProfileUrl + '\n';
    csv += 'Publisher @,' + publisherProfileUrl.split('/')[3] + '\n';
    csv += 'Publish Time,' + formatDate(nicknameAndPublishedAgoTime[1]) + '\n'; // jsx removable
    csv += 'Post Likes,' + document.querySelector(likeCountSelector).outerText + '\n'; // jsx removable
    csv += 'Description,' + quoteString(document.querySelector(descriptionSelector).outerText) + '\n';
    csv += 'Number of 1st level comments,' + comments.length + '\n';
    csv += 'Number of 2nd level comments,' + level2commentsLength + '\n';
    csv += '"Total Comments (actual, in this list, rendered in the comment section (needs all comments to be loaded!))",' + (comments.length + level2commentsLength) + '\n';
    csv += "Total Comments (which TikTok tells you; it's too high most of the time when dealing with many comments OR way too low because TikTok limits the number of comments suddenly)," + document.querySelector(tiktokNumberOfCommentsSelector).outerText + '\n';
    csv += "Difference," + commentNumberDifference + '\n';
    csv += 'Comment Number (ID),Nickname,User @,User URL,Comment Text,Time,Likes,Profile Picture URL,Is 2nd Level Comment,Replied To,Number of replies\n';
    var count = 1;

    for (var i = 0; i < comments.length; i++) {
        comment = comments[i].querySelector(commentChildDivSelector);
        more = comments[i].querySelector(commentChildDivExtraSelector).querySelectorAll(level2CommentsSelector);
        numberOfReplies = more.length;
        csv += count + ',' + csvFromComment(comment) + ',No,---,' + numberOfReplies + '\n';
        repliedTo = comment.querySelector(repliedToSelector)['href'].split('?')[0].split('/')[3];
        for (j = 0; j < numberOfReplies; j++) {
            count++;
            csv += count + ',' + csvFromComment(more[j]) + ',Yes,' + repliedTo + ',---\n';
        }
        count++;
        console.log('Generating CSV for 1st level comment ' + i);
    }
    var apparentCommentNumber = document.querySelector(tiktokNumberOfCommentsSelector).outerText;
    console.log('Number of magically missing comments (not rendered in the comment section): ' + (apparentCommentNumber - count + 1) + ' (you have ' + (count - 1) + ' of ' + apparentCommentNumber + ')');
    console.log('CSV copied to clipboard!');

    copy(csv);
}