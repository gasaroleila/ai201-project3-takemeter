# TakeMeter

# Project Scope
This project analyzes the r/unpopularopinion reddit community where different people share opinion, ideas and scenarios they think are unpopular or have been ignored. Though there's a wide range of perspectives in this community, because people think differently and it's interesting, most opinions align under defined categories.


## Label Definition
### 1. Salt-post
This label defines a post where the author is expressing frustration or complaining about an experience they had.

Example:
[The 'literary classics' that grade school makes you read destroys any desire for kids to read recreationally](https://www.reddit.com/r/unpopularopinion/comments/1twsj53/the_literary_classics_that_grade_school_makes_you/)
[Having bad grammar/not knowing the difference between words like "their", "they're", "there" IS that deep](https://www.reddit.com/r/unpopularopinion/comments/1u43y1x/having_bad_grammarnot_knowing_the_difference/)

Hard Edge Case:
[People have the wrong idea about math and the benefit of learning math.](https://www.reddit.com/r/unpopularopinion/comments/1ud8de5/people_have_the_wrong_idea_about_math_and_the/)

Some posts like this one above are frustration by people but also educating people about facts. I'll annotate it by analyzing the motive underlying some frustration that might have been shown.

### 2. Alternative perspective
This label is for a post that proposes a different way of looking at something that is widely thought off in one way.

Example:
[Growing older is not the curse people make it out to be. It's actually a blessing.](https://www.reddit.com/r/unpopularopinion/comments/1udfupa/growing_older_is_not_the_curse_people_make_it_out/)
[Unconditional love is the biggest lie](https://www.reddit.com/r/unpopularopinion/comments/1ucywid/unconditional_love_is_the_biggest_lie/)

Hard Edge Case:
[Sleepovers should be normal for adults, they’re way better than parties.](https://www.reddit.com/r/unpopularopinion/comments/1naitq1/sleepovers_should_be_normal_for_adults_theyre_way/) This post is not too wild to be classified as a wild take but also seems unconventional? 

### 3. Restating the obvious
This is the opposite of label 2, it just restates what everyone thinks is true. It’s more of a “popular opinion” than it is unpopular

Example:
[All People Should Shave their Armpits](https://www.reddit.com/r/unpopularopinion/comments/1mamsxg/all_people_should_shave_their_armpits/)
[Streaming services killed movie nights and made everything bland as hell](https://www.reddit.com/r/unpopularopinion/comments/1mhdmn5/streaming_services_killed_movie_nights_and_made/)

Hard Edge Case: 
[Work-life balance doesn’t exist and chasing it is making you miserable](https://www.reddit.com/r/unpopularopinion/comments/1u5siyb/worklife_balance_doesnt_exist_and_chasing_it_is/)
(Sounds like alternative perspective, but also restating that work-life is not much of a thing)

### 4. Wild takes
This is for posts that suggest trying unconventional things just to get a certain experience the author had or imagined.

Example:
[I think everyone should take part or see an animal be slaughtered in real life, or take part in hunting](https://www.reddit.com/r/unpopularopinion/comments/1ttmc1r/i_think_everyone_should_take_part_or_see_an/)
[Everyone capable should sit on the floor every now and again](https://www.reddit.com/r/unpopularopinion/comments/1nvj93a/everyone_capable_should_sit_on_the_floor_every/)

Hard Edge Case:
[FIFA should host a US States Cup similar to the World Cup!!](https://www.reddit.com/r/unpopularopinion/comments/1udycpg/fifa_should_host_a_us_states_cup_similar_to_the/)

## More Hard Edge Cases:



## Data Collection Plan
I'll use reddit and collect posts without comments as json objects with atleast 50 examples per label. If a label is underrepresented after 200 examples then it might be worth combining that label with its next best similar label.

[NOTE] STARTED WITH 50 EXAMPLES FOR TEST IF TIME ALLOWS CONTINUE WITH ALL 200 EXAMPLES, BUT INTENTION IS TO HAVE 200 EXAMPLES

## Evaluation Plan

### Metrics To Use
#### 1. Macro-average F1 Score
To help evaluate how well the model is learning all the labels and not just the common ones, regardless of the per label frequency.

##### Expectation: 0.5-0.6+

#### 2. Confusion Matrix
It provides a score of how the model is confusing the 4 labels

##### Expectation: Posts that without reading too much details are obvious to belong to one label are expected to done out correctly, if something requires reading the entire post before being able to label then that is an acceptable confusion.

#### ADDITIONAL 3. Precison & Recall for each label
This would communicate how often the model is labeling posts as a specific label and in those times how right it is. It's also useful for seeing if label Wild takes forexample is being consistely marked as alternative perspective.

##### Expectation: 
Wild takes having high precision but lower recall is fine.
Alternative perspective having slightly lower precision is tolerable
Any label with both precision and recall below 0.40 is too low to be tolerated.

## AI Tool Plan

### Data Collection & Annotation assistance
I provided Claude with my label definitions and asked it to collect 200 examples on the subreddit community and label them accordingly. I'll manually review the examples and correct any mistakes

### Label Stres-testing
Before reviewing the pre-labeled data, I'll have it generate a few posts that can be classified as two labels and test the definitions

### Failure Analysis
I'll have Claude predict patterns of the predictions that where wrong. I'll look for mixed up classes and pay attention to patterns both across all labels and on hard labels such as wild takes vs alternative perspective. I'll care about repeating patterns over multiple examples, a pattern with 1 examples won't be useful. I'll verify patterns I can fix not those including only hard edge case-like examples.
