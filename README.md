# django-supasurvey

### Why SupaSurvey
We just want something that is easy to configure and fast without having to implement a caching strategy.  It works for us, and it might work for you, too.

### Requirements
This is being open-sourced from a specific application, so there are currently certain dependencies and limitations that I would like to remove, in favor of a more pluggable architecture.
- mezzanine == 3.1.9
- jsonfield == 1.0.0

### Install
~~pip install supasurvey~~ (not yet!)

### Usage
Coming soon.

### Advanced Usage
Coming soon.

## Features
##### Supa-easy static surveys
Hardcode a survey using the supasurvey form classes and form field classes.  Very similar to hardcoding a django form.

##### Supa-easy dynamic surveys
Create a form schema using CSS or json and feed it to the SupaSurvey FormBuilder.  The Formbuilder manages validation, pagination, ordering and it will make you breakfast, too.  Best of all, it's fast!

##### Question dependencies
Questions can be dependent on previous questions; a question will be disabled unless previous requirements are met.

##### Question scoring
Scores are assigned to questions.  Each question can be assigned a max_score.  Depending on the question type, scoring will be slightly different.  For examples, a simple textarea will resolve to the max_score if it is not empty and validates.

##### AJAX save-as-you-go
Users responses are saved dynamically as the users progress through the survey.  The response-set is released once the user explicetly submits the form as completed.

##### Track survey history
Change your survey and view the progression and stats of user completion, etc.  Great for a/b testing.  

##### Response-Set templates
If configured, users response-sets are also tracked over time.  Users can choose to answer a new survey using their previous response-set as a template.  This is usefull for giant corporate surveys where nothing ever changes.

If the survey has changed since the previous response-set (based on the survey hash) the questions that have been modified are reported to the user, asking for review.  Questions that are new are reported to the user, asking for responses.  Orphaned responses (those whos questions have been deleted/removed) are simply ignored.

##### Django Admin actions
Some simple stuff to make the surveys easy to review and process through the django Admin.

##### Export as PDF (Stretch Goal)
This probably will not happen :)
