// This code was tested on a TikTok video with over 3000 comment. It got a little bit laggy during the loading phase, but it
// worked out very good at the end. But even on a high-end machine, I wouldn't recommend running this on any TikTok with more than 10k comments
with({
    copy
}) {

    var repliedToXPath                   = 'a.user-info.comment-pc';
    var AllCommentsXPath                 = '/html/body/div[1]/div[2]/div[3]/div[2]/div[3]';
    var commentChildDivXPath             = 'div.comment-content.level-1.comment-pc';
    var commentChildDivExtraXPath        = 'div.more-contents.more-style-2';
    var level2CommentsXPath              = 'div.comment-content.level-2.comment-pc';

    var publisherProfileUrlXPath         = '/html/body/div[1]/div[2]/div[3]/div[2]/div[1]/a[1]';
    var nicknameAndTimePublishedAgoXPath = '/html/body/div[1]/div[2]/div[3]/div[2]/div[1]/a[2]/span[2]';

    var postUrlXPath                     = 'div.link-container';
    var likeCountXPath                   = 'strong.like-text';
    var descriptionXPath                 = 'h1.video-meta-title';
    var tiktokNumberOfCommentsXPath      = 'strong.comment-text';

    var usernameXPath                    = 'span.username';
    var timeCommentedAgoXPath            = 'span.comment-time';
    var commentLikesCountXPath           = 'span.count';
    var commentParagraphXPath            = 'p.comment-text';
    var commentTextXPath                 = ':not(.bottom-container):not(.reply):not(.comment-time)';
    var userProfileUrlXPath              = 'a.user-info.comment-pc';

    // readMoreDivXPath selects all the outermost divs of a read more paragraph.
    // From there, the following 2 XPaths combined select the paragraph.
    var readMoreDivXPath                 = '/html/body/div[1]/div[2]/div[3]/div[2]/div[3]/div/div[2]/div/p';
    var readMoreDivXPath2                = '/html/body/div[1]/div[2]/div[3]/div[2]/div[3]/div/div[2]/div[4]/p[1]';
    var readMoreParagraphXPath           = 'p:not(.hidden):not(.hide)';


    // More reliable than selector
    function getElementsByXPath(xpath, parent)
    {
        let results = [];
        let query = document.evaluate(xpath, parent || document,
            null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
        for (let i = 0, length = query.snapshotLength; i < length; ++i) {
            results.push(query.snapshotItem(i));
        }
        return results;
    }

    function getAllComments(){
        return getElementsByXPath(AllCommentsXPath)[0].children;
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
        nickname = getElementsByXPath(usernameSelector, comment)[0].outerText;
        userProfileUrl = getElementsByXPath(userProfileUrlSelector, comment)[0]['href'].split('?')[0];
        user = userProfileUrl.split('/')[3].substring(1);
        commentText = "";
        getElementsByXPath(commentTextSelector, getElementsByXPath(commentParagraphSelector, comment)[0]).forEach(element => commentText += element.outerText);
        timeCommentedAgo = formatDate(comment.querySelector(timeCommentedAgoSelector).outerText);
        commentLikesCount = getElementsByXPath(commentLikesCountSelector, comment)[0].outerText;
        pic = getElementsByXPath('/img', comment)['src'];
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
        readMoreDivs = getElementsByXPath(readMoreDivXPath);
        for (var i = 0; i < readMoreDivs.length; i++) {
            readMoreDiv2 = getElementsByXPath(readMoreDivXPath2, readMoreDivs[i])[0];
            if (typeof(readMoreDiv2) != 'undefined' && readMoreDiv2 != null) {
                readMoreParagraph = getElementsByXPath(readMoreParagraphXPath, readMoreDiv2);
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

    var publisherProfileUrl = getElementsByXPath(publisherProfileUrlXPath)[0]['href'].split('?')[0];
    var nicknameAndPublishedAgoTime = document.querySelector(nicknameAndTimePublishedAgoSelector).outerText.replaceAll('\n', ' ').split(' · ');
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