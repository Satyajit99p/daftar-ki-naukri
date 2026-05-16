CREATE TABLE job_openings
(
  id UUID PRIMARY KEY,
  government_body VARCHAR(100),
  job_tag VARCHAR(100),
  posted_date TIMESTAMP,
  url TEXT,
  created_date TIMESTAMP
);

CREATE INDEX idx_job_posted_date_desc 
ON job_openings (posted_date DESC);

CREATE INDEX idx_job_created_date_desc 
ON job_openings (created_date DESC);

CREATE INDEX idx_job_gov_posted 
ON job_openings (government_body, posted_date DESC);

CREATE INDEX idx_job_tag 
ON job_openings (job_tag);

CREATE INDEX idx_job_tag_posted 
ON job_openings (job_tag, posted_date DESC);

CREATE UNIQUE INDEX idx_job_url_unique 
ON job_openings (url);

ALTER TABLE job_openings
ADD Column Title text

ALTER Table job_openings
ADD column deadline timestamp