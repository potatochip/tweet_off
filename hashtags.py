employers = {
    'hr',
    'humanresources',
    'recruiting',
    'hiring',
    'talentacquisition',
    'leadership',
    'hrtech',
    'hru',
    'socialrecruiting',
    'sourcing',
    'recruitingtrends'
}
job_seekers = {
    'careers',
    'employment',
    'gethired',
    'hiring',
    'hiringcontractors',
    'nowhiring',
    'jobfairy',
    'joblisting',
    'jobopening',
    'jobposting',
    'jobs',
    'tweetmyjobs',
    'job',
    'unemployed',
    'needajob',
    'rtjobs',
    'jobsearch',
    'hireme'
}
job_tips = {
    'interviewtips',
    'jobadvice',
    'jobsearchtips',
    'jobtips',
    'jobhunt',
    'jobseekers',
}
career_tips = {
    'careeradvice',
    'careerchange',
    'cv',
    'resume',
    'resumes',
    'resumeadvice',
    'resumetips',
    'resumewriting'
}

all_hashtags = employers | job_seekers | job_tips | career_tips
text_capture_hashtags = employers | job_tips | career_tips

max_hashtag_length = len(max(all_hashtags, key=len)) + 1  # plus 1 for the hashtag-mark
