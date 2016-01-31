employers = {
    'hr', 'humanresources', 'recruiting', 'rtjobs', 'jobangels', 'leadership',
    'hrtech', 'hru', 'socialrecruiting'
}
job_seekers = {
    'careers', 'employment', 'gethired', 'hiring', 'nowhiring', 'jobfairy', 'joblisting',
    'jobopening', 'jobposting', 'jobs', 'tweetmyjobs', 'job', 'hireme', 'unemployed', 'needajob',
    'opportunity'
}
job_tips = {
    'interviewtips', 'jobadvice', 'jobsearch', 'jobsearchtips', 'jobtips', 'jobhunt', 'jobseekers'
}
career_tips = {
    'career', 'careeradvice', 'careerchange', 'cv', 'resume', 'resumes', 'resumeadvice',
    'resumetips', 'resumewriting'
}

all_hashtags = employers | job_seekers | job_tips | career_tips
text_capture_hashtags = employers

max_hashtag_length = len(max(all_hashtags, key=len)) + 1  # plus 1 for the hashtag-mark
